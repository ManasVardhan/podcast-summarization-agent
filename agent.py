#!/usr/bin/env python3
"""
Podcast Summariser Agent
Takes a podcast URL and generates a structured summary using GPT-5.1-mini via OpenRouter.
"""

import os
import sys
import re
from urllib.parse import urlparse, parse_qs

from youtube_transcript_api import YouTubeTranscriptApi
from openai import OpenAI


class PodcastSummariser:
    """Core agent loop for podcast summarization."""

    def __init__(self):
        self.api_key = os.environ.get("OPENROUTER_API_KEY")
        if not self.api_key:
            raise ValueError("OPENROUTER_API_KEY environment variable not set")

        self.client = OpenAI(
            base_url="https://openrouter.ai/api/v1",
            api_key=self.api_key,
        )
        self.model = "openai/gpt-5.1-mini"

    def run(self, podcast_url: str) -> str:
        """
        Main agent loop: extract transcript and generate summary.

        Args:
            podcast_url: URL to podcast (YouTube)

        Returns:
            Formatted summary string
        """
        print(f"Processing: {podcast_url}")

        # Step 1: Extract video ID from URL
        video_id = self._extract_video_id(podcast_url)
        if not video_id:
            return "Error: Could not extract video ID from URL"

        print(f"Video ID: {video_id}")

        # Step 2: Get transcript
        transcript = self._get_transcript(video_id)
        if not transcript:
            return "Error: Could not fetch transcript for this video"

        print(f"Extracted transcript ({len(transcript)} chars)")

        # Step 3: Generate summary using LLM
        summary = self._generate_summary(transcript, podcast_url)

        return summary

    def _extract_video_id(self, url: str) -> str | None:
        """Extract YouTube video ID from various URL formats."""
        # Handle different YouTube URL formats
        patterns = [
            r'(?:v=|/v/|youtu\.be/)([a-zA-Z0-9_-]{11})',
            r'(?:embed/)([a-zA-Z0-9_-]{11})',
            r'^([a-zA-Z0-9_-]{11})$',  # Just the ID
        ]

        for pattern in patterns:
            match = re.search(pattern, url)
            if match:
                return match.group(1)

        # Try parsing as URL with query params
        try:
            parsed = urlparse(url)
            if parsed.query:
                params = parse_qs(parsed.query)
                if 'v' in params:
                    return params['v'][0]
        except Exception:
            pass

        return None

    def _get_transcript(self, video_id: str) -> str | None:
        """Fetch transcript using youtube-transcript-api."""
        try:
            # Try to get transcript, preferring manual captions over auto-generated
            transcript_list = YouTubeTranscriptApi.list_transcripts(video_id)

            # Try manual transcripts first (usually higher quality)
            try:
                transcript = transcript_list.find_manually_created_transcript(['en'])
            except Exception:
                # Fall back to auto-generated
                try:
                    transcript = transcript_list.find_generated_transcript(['en'])
                except Exception:
                    # Try any available transcript
                    transcript = transcript_list.find_transcript(['en', 'en-US', 'en-GB'])

            # Fetch and combine transcript text
            transcript_data = transcript.fetch()
            text_parts = [entry['text'] for entry in transcript_data]
            return ' '.join(text_parts)

        except Exception as e:
            print(f"Error fetching transcript: {e}")
            # Fallback: try direct fetch without language preference
            try:
                transcript_data = YouTubeTranscriptApi.get_transcript(video_id)
                text_parts = [entry['text'] for entry in transcript_data]
                return ' '.join(text_parts)
            except Exception as e2:
                print(f"Fallback also failed: {e2}")
                return None

    def _generate_summary(self, transcript: str, url: str) -> str:
        """Generate structured summary using GPT-5.1-mini."""
        # Truncate transcript if too long (context window management)
        max_chars = 100000
        if len(transcript) > max_chars:
            transcript = transcript[:max_chars] + "\n\n[Transcript truncated...]"

        system_prompt = """You are a podcast summarization expert. Given a podcast transcript, create a well-structured summary that captures the key information.

Your summary should include:
1. **Title & Overview** - A brief description of what the podcast is about
2. **Key Topics** - Main subjects discussed (bulleted list)
3. **Main Takeaways** - The most important insights and conclusions
4. **Notable Quotes** - Any memorable or impactful statements (if present)
5. **Summary** - A 2-3 paragraph executive summary

Be concise but comprehensive. Focus on actionable insights and key information."""

        user_prompt = f"""Please summarize the following podcast transcript:

Source URL: {url}

Transcript:
{transcript}"""

        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt},
                ],
                temperature=0.3,
                max_tokens=2000,
            )
            return response.choices[0].message.content

        except Exception as e:
            return f"Error generating summary: {e}"


def main():
    """CLI entrypoint."""
    if len(sys.argv) < 2:
        print("Usage: python agent.py <podcast_url>")
        print("Example: python agent.py 'https://youtube.com/watch?v=example'")
        sys.exit(1)

    podcast_url = sys.argv[1]

    try:
        agent = PodcastSummariser()
        summary = agent.run(podcast_url)
        print("\n" + "=" * 60)
        print("PODCAST SUMMARY")
        print("=" * 60 + "\n")
        print(summary)
    except ValueError as e:
        print(f"Error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
