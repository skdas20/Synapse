import httpx  # Use httpx for async requests
import json
import logging
import os
import re
from typing import Dict, List, Any
import asyncio

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class TaskPlannerAgent:
    def __init__(self, api_key: str):
        self.api_key = api_key
        gemini_key = os.getenv('GEMINI_API_KEY')
        if not gemini_key:
            logger.error("GEMINI_API_KEY environment variable not set!")
        # Use gemini-1.5-flash model and v1 API endpoint
        self.endpoint = f"https://generativelanguage.googleapis.com/v1/models/gemini-1.5-flash:generateContent?key={gemini_key}"
        self.client = httpx.AsyncClient(timeout=60.0)

    async def _call_gemini(self, prompt: str, request_json: bool = False) -> Dict:
        payload = {
            "contents": [{"parts": [{"text": prompt}]}],
            "generationConfig": {
                "temperature": 0.4, # Adjusted temperature slightly
                "topP": 0.9,
                "maxOutputTokens": 2048
            },
             "safetySettings": [
                {"category": "HARM_CATEGORY_HARASSMENT", "threshold": "BLOCK_MEDIUM_AND_ABOVE"},
                {"category": "HARM_CATEGORY_HATE_SPEECH", "threshold": "BLOCK_MEDIUM_AND_ABOVE"},
                {"category": "HARM_CATEGORY_SEXUALLY_EXPLICIT", "threshold": "BLOCK_MEDIUM_AND_ABOVE"},
                {"category": "HARM_CATEGORY_DANGEROUS_CONTENT", "threshold": "BLOCK_MEDIUM_AND_ABOVE"},
            ]
        }
        # Removed "responseMimeType" as it causes errors with some models/versions
        # The prompt itself requests JSON format.
        # if request_json:
        #     payload["generationConfig"]["responseMimeType"] = "application/json"

        headers = {"Content-Type": "application/json"}

        logger.info(f"Sending request to Gemini API (Endpoint: {self.endpoint.split('?')[0]}...). Requesting JSON: {request_json}")
        # Avoid logging the full prompt if it's too long or sensitive
        # logger.info(f"Sending prompt: {prompt[:200]}...")

        try:
            response = await self.client.post(self.endpoint, headers=headers, json=payload)
            logger.info(f"Gemini API Response Status Code: {response.status_code}")
            response.raise_for_status() # Raise HTTPError for bad responses (4xx or 5xx)
            return response.json()
        except httpx.RequestError as e:
            logger.error(f"Error connecting to Gemini API: {str(e)}")
            raise ConnectionError(f"Error connecting to Gemini API: {str(e)}") from e
        except httpx.HTTPStatusError as e:
            logger.error(f"Gemini API error: {e.response.status_code} - {e.response.text[:500]}...")
            raise ValueError(f"Gemini API error: {e.response.status_code}") from e # Don't expose full error text potentially
        except Exception as e:
            logger.error(f"Unexpected error during Gemini API call: {str(e)}", exc_info=True)
            raise

    def _extract_text_from_response(self, result: Dict) -> str:
        """Safely extracts text content from Gemini response."""
        try:
            # Access the nested structure
            text = result['candidates'][0]['content']['parts'][0]['text']
            return text.strip()
        except (KeyError, IndexError, TypeError) as e:
            logger.error(f"Error extracting text from Gemini response: {e}. Response: {result}")
            raise ValueError("Could not extract text from Gemini response structure.") from e

    def _clean_json_string(self, text: str) -> str:
        """Removes markdown fences and leading/trailing whitespace from a potential JSON string."""
        # Regex to find JSON possibly wrapped in ```json ... ``` or ``` ... ```
        match = re.search(r"```(?:json)?\s*(\{.*?\})\s*```", text, re.DOTALL | re.IGNORECASE)
        if match:
            return match.group(1).strip()
        # Fallback for JSON not wrapped in fences but might have surrounding whitespace
        return text.strip()

    async def break_down_tasks(self, requirement: str) -> Dict:
        tech_stack = {'language': 'Unknown', 'frameworks': [], 'app_type': 'Unknown'}
        # Provide more generic default goals
        goals = [
            "1. Define project requirements and scope.",
            "2. Set up the development environment and project structure.",
            "3. Implement core features based on requirements.",
            "4. Develop necessary utility functions or modules.",
            "5. Integrate external services or APIs if needed.",
            "6. Implement user interface (if applicable).",
            "7. Write unit and integration tests.",
            "8. Add comprehensive error handling and logging.",
            "9. Create documentation (README, code comments).",
            "10. Prepare for deployment."
        ]

        try:
            # 1. Analyze Tech Stack (Requesting JSON response)
            tech_prompt = f"""Analyze this project requirement and determine the technical stack.
Project Requirement: {requirement}

Rules:
1. Identify the main programming language (e.g., Python, JavaScript, Java).
2. List key frameworks or libraries needed (e.g., Flask, React, Spring).
3. Determine the type of application (e.g., Web API, Frontend Web App, CLI Tool).

Your response MUST be a valid JSON object following this exact structure:
{{
    "language": "string",
    "frameworks": ["string"],
    "app_type": "string"
}}"""
            logger.info("Requesting tech stack analysis from Gemini...")
            tech_result = await self._call_gemini(tech_prompt, request_json=True)

            # Extract and parse tech stack JSON
            raw_tech_text = self._extract_text_from_response(tech_result)
            logger.info(f"Raw tech analysis response text: {raw_tech_text[:500]}...") # Log beginning of text
            cleaned_tech_json_str = self._clean_json_string(raw_tech_text)
            try:
                parsed_json = json.loads(cleaned_tech_json_str)
                # Basic validation
                if isinstance(parsed_json.get("language"), str) and \
                   isinstance(parsed_json.get("frameworks"), list) and \
                   isinstance(parsed_json.get("app_type"), str):
                    tech_stack = parsed_json
                    logger.info(f"Successfully parsed tech stack: {tech_stack}")
                else:
                    raise ValueError("Parsed JSON does not match expected structure.")
            except (json.JSONDecodeError, ValueError) as e:
                 logger.error(f"Failed to parse tech stack JSON: {e}. Raw text: {tech_text}")
                 # Keep default tech_stack on error


            # 2. Generate Goals based on Tech Stack (Requesting text response)
            goal_prompt = f"""Based on this project requirement and tech stack, break it down into 5-10 high-level, actionable development goals.
Project Requirement: {requirement}
Tech Stack: {json.dumps(tech_stack)}

Return ONLY a numbered list of goals, one goal per line. Start numbering from 1.
Example:
1. Setup project with {tech_stack.get('language', 'the language')}.
2. Implement user authentication.
3. Develop API endpoints for core features.
..."""
            logger.info("Requesting goal generation from Gemini...")
            goal_result = await self._call_gemini(goal_prompt, request_json=False)

            goals_text = self._extract_text_from_response(goal_result)
            logger.info(f"Raw goals response text:\n---\n{goals_text}\n---")

            # Extract numbered list items
            parsed_goals = []
            for line in goals_text.strip().split('\n'):
                line = line.strip()
                # Match lines starting with a number and a dot, followed by space
                match = re.match(r"^\d+\.\s+(.*)", line)
                if match:
                    parsed_goals.append(match.group(1).strip()) # Add the task text

            if parsed_goals:
                # Re-number the goals consistently
                goals = [f"{i+1}. {task}" for i, task in enumerate(parsed_goals)]
                logger.info(f"Successfully parsed {len(goals)} goals.")
            else:
                logger.warning("Could not parse numbered goals from response, using default goals.")
                # Keep default goals if parsing fails

        except (ConnectionError, ValueError) as e:
            logger.error(f"Error processing requirement in break_down_tasks: {e}")
            # Keep default goals/tech_stack on error
        except Exception as e:
            logger.error(f"Unexpected error in break_down_tasks: {e}", exc_info=True)
            # Keep default goals/tech_stack on error

        return {'goals': goals, 'tech_stack': tech_stack}

    async def close(self):
        """Close the httpx client."""
        if hasattr(self, 'client') and self.client:
            await self.client.aclose()
            logger.info("TaskPlannerAgent client closed.")
