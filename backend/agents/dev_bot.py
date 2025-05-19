import httpx  # Use httpx for async requests
import httpx  # Use httpx for async requests
import json
import logging
import os
import re # Import regex module
import zipfile
import shutil
from typing import Dict, List, Any
import asyncio

logger = logging.getLogger(__name__)

class DevBot:
    def __init__(self, api_key: str):
        self.api_key = api_key
        # Ensure GEMINI_API_KEY is loaded correctly
        gemini_key = os.getenv('GEMINI_API_KEY')
        if not gemini_key:
            logger.error("GEMINI_API_KEY environment variable not set!")
            # Optionally raise an error or handle appropriately
        # Use gemini-1.5-flash model and v1 API endpoint
        self.endpoint = f"https://generativelanguage.googleapis.com/v1/models/gemini-1.5-flash:generateContent?key={gemini_key}"
        self.client = httpx.AsyncClient(timeout=120.0) # Increased timeout

    async def generate_project(self, tasks: List[str], project_type: str) -> Dict[str, Any]:
        try:
            logger.info(f"Generating project with type: {project_type}, tasks: {tasks}")

            # Construct the improved code generation prompt asking for JSON
            code_prompt = f"""
Generate a complete {project_type} project based on the following tasks:
{chr(10).join(f"- {task}" for task in tasks)}

Please provide the output as a JSON object containing a list named "files".
Each item in the "files" list should be an object with two keys:
1. "name": The full path of the file (e.g., "src/main.py", "index.html", "requirements.txt").
2. "content": The complete code/text content for that file.

Example JSON structure:
{{
  "files": [
    {{
      "name": "main.py",
      "content": "# Python code here\\nprint('Hello World')"
    }},
    {{
      "name": "requirements.txt",
      "content": "flask\\nrequests"
    }},
    {{
      "name": "static/style.css",
      "content": "body {{ background-color: #f0f0f0; }}"
    }}
  ]
}}

Ensure the file content is properly escaped for JSON, especially newlines (\\n) and quotes (\\").
Include necessary configuration files (like requirements.txt or package.json) if applicable for the project type.
"""

            payload = {
                "contents": [{"parts": [{"text": code_prompt}]}],
                # Removed "responseMimeType": "application/json" as it causes errors with some models/versions
                "generationConfig": {"temperature": 0.5, "topP": 0.9, "maxOutputTokens": 8192},
                "safetySettings": [
                    {"category": "HARM_CATEGORY_HARASSMENT", "threshold": "BLOCK_MEDIUM_AND_ABOVE"},
                    {"category": "HARM_CATEGORY_HATE_SPEECH", "threshold": "BLOCK_MEDIUM_AND_ABOVE"},
                    {"category": "HARM_CATEGORY_SEXUALLY_EXPLICIT", "threshold": "BLOCK_MEDIUM_AND_ABOVE"},
                    {"category": "HARM_CATEGORY_DANGEROUS_CONTENT", "threshold": "BLOCK_MEDIUM_AND_ABOVE"},
                ]
            }

            headers = {"Content-Type": "application/json"}

            logger.info("Sending request to Gemini API...")
            try:
                response = await self.client.post(self.endpoint, headers=headers, json=payload)
                logger.info(f"Gemini API Response Status Code: {response.status_code}")
                # Avoid logging potentially large response content directly unless debugging
                # logger.info(f"Gemini API Response Content: {response.text}")

                response.raise_for_status() # Raise HTTPError for bad responses (4xx or 5xx)

            except httpx.RequestError as e:
                error_msg = f"Error connecting to Gemini API: {str(e)}"
                logger.error(error_msg)
                return {"success": False, "error": error_msg}
            except httpx.HTTPStatusError as e:
                error_msg = f"Gemini API error: {e.response.status_code} - {e.response.text}"
                logger.error(error_msg)
                return {"success": False, "error": error_msg}

            logger.info("Gemini API call successful")
            try:
                # Extract text from the nested response structure
                result_json = response.json()
                raw_generated_text = result_json.get('candidates', [{}])[0].get('content', {}).get('parts', [{}])[0].get('text', '{}')

                # Clean potential markdown fences before parsing
                cleaned_json_str = self._clean_json_string(raw_generated_text)
                logger.info(f"Cleaned JSON string for parsing: {cleaned_json_str[:500]}...") # Log beginning

                generated_data = json.loads(cleaned_json_str)

                if not isinstance(generated_data, dict) or "files" not in generated_data or not isinstance(generated_data["files"], list):
                    raise ValueError("Invalid JSON structure received from AI after cleaning. Expected {'files': [...]} ")

                files_to_create = generated_data["files"]
                logger.info(f"Received {len(files_to_create)} files from Gemini API")

            except (KeyError, IndexError, json.JSONDecodeError, ValueError) as e:
                error_msg = f"Error parsing JSON response from Gemini: {str(e)}. Response text: {response.text[:500]}..." # Log beginning of response
                logger.error(error_msg)
                return {"success": False, "error": error_msg}
            except Exception as e: # Catch unexpected errors during parsing
                error_msg = f"Unexpected error processing Gemini response: {str(e)}. Response text: {response.text[:500]}..."
                logger.error(error_msg)
                return {"success": False, "error": error_msg}


            # --- File and Directory Handling ---
            base_project_dir = os.path.dirname(os.path.dirname(__file__)) # backend/
            project_dir = os.path.join(base_project_dir, "generated_project")
            zip_filename = "generated_project.zip"
            zip_path = os.path.join(base_project_dir, zip_filename)
            logger.info(f"Project directory: {project_dir}")
            logger.info(f"Zip file path: {zip_path}")

            try:
                # Clean up old directory and zip file
                if os.path.exists(project_dir):
                    shutil.rmtree(project_dir)
                    logger.info(f"Removed existing project directory: {project_dir}")
                if os.path.exists(zip_path):
                    os.remove(zip_path)
                    logger.info(f"Removed existing zip file: {zip_path}")

                os.makedirs(project_dir, exist_ok=True) # Create base directory
                logger.info(f"Ensured project directory exists: {project_dir}")

                files_content_dict = {} # To store path: content
                created_file_paths_for_zip = [] # Still need this for zipping by relative path

                for file_info in files_to_create:
                    if not isinstance(file_info, dict) or "name" not in file_info or "content" not in file_info:
                        logger.warning(f"Skipping invalid file entry in JSON: {file_info}")
                        continue

                    file_name = file_info["name"]
                    file_content = file_info["content"]
                    # Sanitize file path to prevent directory traversal
                    # Normalize path separators and remove leading slashes
                    sanitized_name = os.path.normpath(file_name.lstrip('/\\'))
                    # Ensure the path stays within the project directory
                    file_path = os.path.abspath(os.path.join(project_dir, sanitized_name))
                    if not file_path.startswith(os.path.abspath(project_dir)):
                         logger.warning(f"Skipping potentially unsafe file path: {file_name}")
                         continue

                    # Create subdirectories if they don't exist
                    file_dir = os.path.dirname(file_path)
                    if not os.path.exists(file_dir):
                        os.makedirs(file_dir)
                        logger.info(f"Created subdirectory: {file_dir}")

                    # Write file content
                    try:
                        with open(file_path, "w", encoding="utf-8") as f:
                            f.write(file_content)
                        logger.info(f"Created file: {file_path}")
                        files_content_dict[sanitized_name] = file_content # Store content for push
                        created_file_paths_for_zip.append(sanitized_name) # Store relative path for zip
                    except OSError as e:
                        logger.error(f"Failed to write file {file_path}: {e}")
                        # Decide if one file error should stop the whole process or just be skipped
                        # For now, let's skip and log
                        continue
                    except Exception as e: # Catch other potential writing errors
                        logger.error(f"Unexpected error writing file {file_path}: {e}")
                        continue


                # --- Zipping ---
                if not created_file_paths_for_zip: # Check against paths for zip
                     logger.warning("No valid files were generated by the AI to zip.")
                     # If no files to zip, it might still be okay if files_content_dict has data for push
                     # However, if files_content_dict is also empty, then it's a true failure.
                     if not files_content_dict:
                        logger.error("AI did not generate any valid files for zipping or pushing.")
                        return {"success": False, "error": "AI did not generate any valid files."}
                     # If there's content to push but nothing to zip (e.g. only one file at root), proceed
                     # but log that zip will be empty or not created if that's the case.
                     # For now, let's assume if created_file_paths_for_zip is empty, we might not want to create an empty zip.
                     # This logic might need refinement based on desired behavior for "no files".
                     # If we must return a zip, we might create an empty one or one with a placeholder.
                     # For now, if no files to zip, we might skip zipping or return an error if zip is mandatory.
                     # Let's assume for now that if created_file_paths_for_zip is empty, we still proceed if files_content_dict is not.

                if created_file_paths_for_zip: # Only create zip if there are files
                    logger.info(f"Creating ZIP file: {zip_path}")
                    with zipfile.ZipFile(zip_path, "w", zipfile.ZIP_DEFLATED) as zipf:
                        for file_rel_path in created_file_paths_for_zip:
                             file_abs_path = os.path.join(project_dir, file_rel_path)
                             # Add file to zip using its relative path within generated_project
                             zipf.write(file_abs_path, file_rel_path)
                             logger.info(f"Added to zip: {file_rel_path}")
                    logger.info(f"Successfully created ZIP file: {zip_path}")
                else:
                    logger.warning("No files to zip. Zip file will not be created or will be empty.")
                    # zip_path might not exist or be empty, handle accordingly in return if zip is always expected

            except OSError as e:
                error_msg = f"File/Directory operation failed: {str(e)}"
                logger.error(error_msg)
                return {"success": False, "error": error_msg}
            except zipfile.BadZipFile as e:
                 error_msg = f"Error creating ZIP file: {str(e)}"
                 logger.error(error_msg)
                 return {"success": False, "error": error_msg}
            except Exception as e: # Catch unexpected errors during file ops/zipping
                error_msg = f"Unexpected error during file operations or zipping: {str(e)}"
                logger.error(error_msg, exc_info=True)
                return {"success": False, "error": error_msg}

            return {
                "success": True,
                "zip_file": zip_path if os.path.exists(zip_path) else None, # Return None if zip wasn't created
                "files_created": files_content_dict # Dict of path: content
            }

        except Exception as e:
            # Catch-all for any unexpected error at the top level
            error_msg = f"Critical error in generate_project: {str(e)}"
            logger.error(error_msg, exc_info=True)
            return {"success": False, "error": error_msg}

    def _clean_json_string(self, text: str) -> str:
        """Removes markdown fences and leading/trailing whitespace from a potential JSON string."""
        # Regex to find JSON possibly wrapped in ```json ... ``` or ``` ... ```
        match = re.search(r"```(?:json)?\s*(\{.*?\})\s*```", text, re.DOTALL | re.IGNORECASE)
        if match:
            logger.info("Found JSON wrapped in markdown fences, extracting.")
            return match.group(1).strip()
        # Fallback for JSON not wrapped in fences but might have surrounding whitespace
        logger.info("No markdown fences found around JSON, returning stripped text.")
        return text.strip()

    async def close(self):
        """Close the httpx client."""
        if hasattr(self, 'client') and self.client:
            await self.client.aclose()
            logger.info("DevBot client closed.")

# Optional: Add cleanup for the client if the application lifecycle allows
# For FastAPI, you might use lifespan events
# async def lifespan(app: FastAPI):
#     # Startup logic if needed
#     yield
#     # Shutdown logic
#     if services.get('dev_bot'):
#         await services['dev_bot'].close()

# app.router.lifespan_context = lifespan
