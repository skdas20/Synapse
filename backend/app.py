from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse, FileResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
from typing import List, Dict, Optional
from agents.task_planner import TaskPlannerAgent
from agents.dev_bot import DevBot
from agents.github_agent import GitHubAgent
from pymongo import MongoClient
import os
import datetime
from dotenv import load_dotenv
import asyncio
from asgiref.sync import sync_to_async
from pathlib import Path
import atexit
from contextlib import asynccontextmanager # Import asynccontextmanager for lifespan

# Load environment variables from parent directory
env_path = Path(__file__).parent.parent / '.env'
load_dotenv(dotenv_path=env_path)

# Initialize FastAPI app
app = FastAPI()

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mount static files and frontend assets
static_dir = Path(__file__).parent / "templates"
frontend_dir = Path(__file__).parent.parent  # Go up one level to project root

# Mount the templates directory for images
app.mount("/static", StaticFiles(directory=static_dir), name="static")

# Initialize services with proper error handling
services = {
    'mongodb': None,
    'github': None,
    'task_planner': None,
    'dev_bot': None
}

# Initialize MongoDB
try:
    mongo_client = MongoClient(os.getenv('MONGODB_URI'), serverSelectionTimeoutMS=5000)
    mongo_client.server_info()  # Test connection
    db = mongo_client.synapse
    services['mongodb'] = db
    print("MongoDB connection successful")
except Exception as e:
    print(f"Warning: MongoDB connection failed: {e}")
    db = None

# Initialize other services (moved DevBot initialization to lifespan)
try:
    gemini_api_key = os.getenv('GEMINI_API_KEY')
    if not gemini_api_key:
        print("Warning: GEMINI_API_KEY not found in environment variables.")
        # Handle missing key appropriately, maybe disable AI features

    services['task_planner'] = TaskPlannerAgent(gemini_api_key)
    # services['dev_bot'] will be initialized in lifespan

    # Initialize GitHub agent with validation
    github_token = os.getenv('GITHUB_TOKEN')
    if github_token and len(github_token) > 0:
        github_agent = GitHubAgent(github_token)
        # Test the token by trying to get the authenticated user
        github_agent.github.get_user().login
        services['github'] = github_agent
        print("GitHub authentication successful")
    else:
        print("Warning: Invalid or missing GitHub token")
except Exception as e:
    print(f"Error initializing services: {e}")

# Convert MongoDB operations to async
async def safe_insert_one(document):
    if services['mongodb'] is not None:
        return await sync_to_async(services['mongodb'].files.insert_one)(document)
    return None

async def safe_find_one(sort_params=None):
    if services['mongodb'] is not None:
        return await sync_to_async(services['mongodb'].files.find_one)(sort=sort_params)
    return None

# --- Lifespan Management ---
@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup: Initialize services that need async cleanup
    print("Application startup...")
    gemini_api_key = os.getenv('GEMINI_API_KEY')
    if gemini_api_key:
        services['dev_bot'] = DevBot(gemini_api_key)
        print("DevBot initialized.")
    else:
        print("Warning: DevBot not initialized due to missing GEMINI_API_KEY.")
        services['dev_bot'] = None # Ensure it's None if not initialized

    # MongoDB client is managed by pymongo's connection pool,
    # but explicit close on shutdown is good practice if needed elsewhere.
    # atexit handles the current MongoDB cleanup.

    yield # Application runs here

    # Shutdown: Cleanup resources
    print("Application shutdown...")
    if services.get('dev_bot'):
        try:
            await services['dev_bot'].close()
            print("DevBot client closed.")
        except Exception as e:
            print(f"Error closing DevBot client: {e}")

    if 'mongodb' in services and services['mongodb'] is not None:
         # mongo_client is defined outside, accessible here
         try:
            mongo_client.close()
            print("MongoDB connection closed.")
         except Exception as e:
            print(f"Error closing MongoDB connection: {e}")
    print("Shutdown complete.")

# Assign lifespan to the app
app.router.lifespan_context = lifespan

# Request Models
class RequirementRequest(BaseModel):
    requirement: str

class TasksRequest(BaseModel):
    tasks: List[str]
    project_type: Optional[str] = None # Add project_type field

class GitHubRequest(BaseModel):
    repoName: str
    tasks: Optional[List[str]] = []

class GitHubTokenRequest(BaseModel):
    token: str

@app.post("/api/process-requirement")
async def process_requirement(req: RequirementRequest):
    try:
        print(f"Processing requirement: {req.requirement}")
        if not services['task_planner']:
            raise ValueError("Task planner service is not initialized")
            
        result = await services['task_planner'].break_down_tasks(req.requirement)
        print(f"Generated analysis: {result}")
        
        return {
            'success': True,
            'tasks': result['goals'],  # Using the new 'goals' key
            'techStack': result['tech_stack']
        }
    except Exception as e:
        print(f"Error processing requirement: {str(e)}")
        import traceback
        traceback.print_exc()
        return JSONResponse(
            status_code=500,
            content={"success": False, "error": str(e)}
        )

@app.post("/api/generate-code")
async def generate_code(req: TasksRequest):
    try:
        if not req.tasks:
            return JSONResponse(
                status_code=400,
                content={"success": False, "error": "No tasks provided"}
            )

        print(f"Generating code for tasks: {req.tasks}")

        # Check if DevBot is initialized
        if not services.get('dev_bot'):
             return JSONResponse(
                status_code=503, # Service Unavailable
                content={"success": False, "error": "Code generation service (DevBot) is not available. Check API key."}
            )

        # Determine project type: Prioritize request body, fallback to generic
        project_type = req.project_type if req.project_type else 'generic'
        print(f"Using project type: {project_type}")

        # Generate project files using the determined project_type
        result = await services['dev_bot'].generate_project(req.tasks, project_type)
        # Avoid logging potentially large result content unless debugging
        print(f"generate_project result success: {result.get('success')}")
        if result.get('error'):
             print(f"generate_project error: {result.get('error')}")


        if not result.get('success'):
            return JSONResponse(
                status_code=500,
                content={"success": False, "error": "Failed to generate project files"}
            )

        # Save info to MongoDB
        try:
            raw_files_created = result.get('files_created')
            processed_files_created = raw_files_created if isinstance(raw_files_created, dict) else {}
            await safe_insert_one({
                'tasks': req.tasks,
                'generated_at': datetime.datetime.utcnow(),
                'files_created': processed_files_created
            })
            print("Saved project details to MongoDB successfully")
        except Exception as mongo_error:
            print(f"MongoDB error: {str(mongo_error)}")

        # Return the ZIP file for download
        zip_path = result['zip_file']
        if os.path.exists(zip_path):
            response = FileResponse(
                path=zip_path,
                media_type='application/zip',
                filename=os.path.basename(zip_path),
                headers={
                    "Content-Disposition": f"attachment; filename={os.path.basename(zip_path)}",
                    "Access-Control-Expose-Headers": "Content-Disposition"
                }
            )
            
            # Clean up the ZIP file after sending
            def cleanup_zip(zip_path=zip_path):
                try:
                    if os.path.exists(zip_path):
                        os.remove(zip_path)
                        print(f"Cleaned up ZIP file: {zip_path}")
                except Exception as e:
                    print(f"Error cleaning up ZIP file: {str(e)}")
            
            response.background = cleanup_zip
            return response
        else:
            return JSONResponse(
                status_code=500,
                content={"success": False, "error": "ZIP file not found"}
            )

    except Exception as e:
        print(f"Error generating code: {str(e)}")
        import traceback
        traceback.print_exc()
        return JSONResponse(
            status_code=500,
            content={"success": False, "error": str(e)}
        )

@app.post("/api/generate-project")
async def generate_project(req: TasksRequest):
    try:
        if not req.tasks:
            return JSONResponse(
                status_code=400,
                content={"success": False, "error": "No tasks provided"}
            )

        print(f"Generating project for tasks: {req.tasks}")

        # Check if DevBot is initialized
        if not services.get('dev_bot'):
             return JSONResponse(
                status_code=503, # Service Unavailable
                content={"success": False, "error": "Code generation service (DevBot) is not available. Check API key."}
            )

        # Get the latest analysis from MongoDB to determine project type
        try:
            latest_analysis = await safe_find_one(sort_params=[('_id', -1)])
            if latest_analysis:
                project_type = latest_analysis.get('tech_stack', {}).get('app_type', 'generic')
                print(f"Retrieved project type: {project_type}")
            else:
                project_type = 'generic'
        except Exception as mongo_error:
            print(f"MongoDB error: {str(mongo_error)}")
            project_type = 'generic'

        # Generate project structure and code
        result = await services['dev_bot'].generate_project(req.tasks, project_type)

        # Save to MongoDB
        try:
            raw_files_created_project = result.get('files_created')
            processed_files_created_project = raw_files_created_project if isinstance(raw_files_created_project, dict) else {}
            await safe_insert_one({
                'tasks': req.tasks,
                'tree_structure': result.get('tree_structure'), # Use .get for safety
                'zip_file': result.get('zip_file'),         # Use .get for safety
                'files_created': processed_files_created_project # Add files_created here, ensuring it's a dict
            })
            print("Saved project details to MongoDB successfully")
        except Exception as mongo_error:
            print(f"MongoDB error: {str(mongo_error)}")

        # Provide the ZIP file for download
        zip_path = result['zip_file']
        if os.path.exists(zip_path):
            return FileResponse(zip_path, media_type='application/zip', filename=os.path.basename(zip_path))
        else:
            return JSONResponse(
                status_code=500,
                content={"success": False, "error": "ZIP file not found"}
            )

    except Exception as e:
        print(f"Error generating project: {str(e)}")
        import traceback
        traceback.print_exc()
        return JSONResponse(
            status_code=500,
            content={"success": False, "error": str(e)}
        )

@app.post("/api/push-to-github")
async def push_to_github(req: GitHubRequest):
    try:
        if not req.repoName:
            return JSONResponse(
                status_code=400,
                content={"success": False, "error": "No repository name provided"}
            )

        print(f"Pushing to GitHub repo: {req.repoName}")
        
        # Get latest files from MongoDB
        try:
            latest_files = await safe_find_one(sort_params=[('_id', -1)])
            if not latest_files:
                return JSONResponse(
                    status_code=404,
                    content={"success": False, "error": "No files found to push"}
                )
        except Exception as mongo_error:
            print(f"MongoDB error: {str(mongo_error)}")
            return JSONResponse(
                status_code=500,
                content={"success": False, "error": f"MongoDB error: {str(mongo_error)}"}
            )

        # Create repository and push files
        repo_url = await services['github'].create_repository(req.repoName)
        
        # Check for 'files_created' key and ensure it's a dictionary
        files_to_push = latest_files.get('files_created')
        if not files_to_push or not isinstance(files_to_push, dict):
            return JSONResponse(
                status_code=404, # Or 400 Bad Request if the data format is wrong
                content={"success": False, "error": "No valid file data (files_created) found in the latest record to push."}
            )
            
        await services['github'].push_files(req.repoName, files_to_push)
        
        # Create issues for tasks
        if req.tasks:
            await services['github'].create_issues(req.repoName, req.tasks)
        
        print(f"Successfully pushed to GitHub: {repo_url}")
        return {
            'success': True,
            'repoUrl': repo_url
        }
    except Exception as e:
        print(f"Error pushing to GitHub: {str(e)}")
        import traceback
        traceback.print_exc()
        return JSONResponse(
            status_code=500,
            content={"success": False, "error": str(e)}
        )

@app.post("/api/update-github-token")
async def update_github_token(req: GitHubTokenRequest):
    try:
        # Initialize new GitHub agent with the token
        github_agent = GitHubAgent(req.token)
        # Verify token by trying to get the authenticated user
        github_agent.github.get_user().login
        
        # If we got here, token is valid
        services['github'] = github_agent
        return {
            'success': True,
            'message': 'GitHub token updated successfully'
        }
    except Exception as e:
        print(f"Error updating GitHub token: {str(e)}")
        return JSONResponse(
            status_code=400,
            content={
                "success": False,
                "error": "Invalid GitHub token. Please check your token and try again."
            }
        )

@app.post('/api/generate')
async def generate_project(tasks: List[str], project_type: str):
    try:
        if not tasks or not project_type:
            raise HTTPException(status_code=400, detail='Missing required fields')

        # Use the initialized DevBot from services
        if not services.get('dev_bot'):
             raise HTTPException(status_code=503, detail="Code generation service (DevBot) is not available.")

        result = await services['dev_bot'].generate_project(tasks, project_type)

        if not result.get('success'):
            raise HTTPException(status_code=500, detail=result.get('error', 'Unknown error during project generation'))

        # Check if the ZIP file exists
        if not os.path.exists(result['zip_file']):
            raise HTTPException(status_code=500, detail='Failed to create ZIP file')

        try:
            return FileResponse(
                path=result['zip_file'],
                media_type='application/zip',
                filename='generated_project.zip'
            )
        except Exception as e:
            app.logger.error(f"Error sending file: {str(e)}")
            raise HTTPException(status_code=500, detail='Failed to send generated files')

    except Exception as e:
        app.logger.error(f"Error in generate_project route: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))

# Serve the main frontend HTML page
# Health check endpoint
@app.get("/health")
async def health_check():
    """Health check endpoint for monitoring"""
    return {
        "status": "healthy",
        "mongodb": services['mongodb'] is not None,
        "task_planner": services['task_planner'] is not None,
        "dev_bot": services['dev_bot'] is not None,
        "github": services['github'] is not None
    }

# Mount frontend files (CSS, JS, HTML) at the end to avoid conflicts with API routes
app.mount("/", StaticFiles(directory=str(frontend_dir), html=True), name="frontend")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="127.0.0.1", port=8000)
