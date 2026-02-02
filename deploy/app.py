"""
FastAPI wrapper for Podcast Summariser Agent
Deploy on Render as a Web Service
"""

import os
import sys
from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from typing import Optional

# Add parent directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from agent import PodcastSummariser

app = FastAPI(
    title="Podcast Summariser Agent",
    description="Summarize YouTube podcasts using AI",
    version="1.0.0"
)


class AgentRequest(BaseModel):
    command: str
    context: Optional[str] = None
    user_id: Optional[str] = None


class AgentResponse(BaseModel):
    success: bool
    result: Optional[str] = None
    error: Optional[str] = None


@app.get("/health")
async def health():
    """Health check endpoint for Render."""
    return {"status": "healthy", "agent": "podcast-summariser", "version": "1.0.0"}


@app.post("/", response_model=AgentResponse)
async def handle_command(request: AgentRequest, raw_request: Request):
    """
    Main endpoint for Friday to call.

    The command should contain a YouTube URL, either:
    - Direct URL: "https://youtube.com/watch?v=..."
    - Natural language: "summarize https://youtube.com/watch?v=..."
    """
    # Check for API key override in headers (from Friday desktop)
    api_key = raw_request.headers.get("X-OpenRouter-Api-Key")
    if api_key:
        os.environ["OPENROUTER_API_KEY"] = api_key

    command = request.command.strip()

    if not command:
        return AgentResponse(success=False, error="Missing command")

    # Extract URL from command
    url = extract_url(command)

    if not url:
        return AgentResponse(
            success=False,
            error="No YouTube URL found in command. Please provide a YouTube URL."
        )

    try:
        agent = PodcastSummariser()
        result = agent.run(url)

        # Check if result is an error
        if result.startswith("Error:"):
            return AgentResponse(success=False, error=result)

        return AgentResponse(success=True, result=result)

    except ValueError as e:
        return AgentResponse(success=False, error=str(e))
    except Exception as e:
        return AgentResponse(success=False, error=f"Unexpected error: {str(e)}")


def extract_url(text: str) -> Optional[str]:
    """Extract YouTube URL from text."""
    import re

    # Pattern to match YouTube URLs
    patterns = [
        r'(https?://(?:www\.)?youtube\.com/watch\?v=[a-zA-Z0-9_-]+(?:&[^\s]*)?)',
        r'(https?://youtu\.be/[a-zA-Z0-9_-]+)',
        r'(https?://(?:www\.)?youtube\.com/embed/[a-zA-Z0-9_-]+)',
    ]

    for pattern in patterns:
        match = re.search(pattern, text)
        if match:
            return match.group(1)

    # If the whole text looks like a video ID, construct URL
    if re.match(r'^[a-zA-Z0-9_-]{11}$', text):
        return f"https://youtube.com/watch?v={text}"

    return None


if __name__ == "__main__":
    import uvicorn
    port = int(os.environ.get("PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=port)
