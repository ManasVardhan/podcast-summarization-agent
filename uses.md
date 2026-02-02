# Podcast Summariser

A Python agent that takes a podcast URL and generates a concise, well-structured summary using GPT-5.1-mini via OpenRouter.

## Use Cases

- **Quick podcast previews** - Get the gist of a podcast before committing to listen
- **Note-taking** - Generate summaries for podcasts you've listened to
- **Research** - Extract key insights from multiple podcasts quickly
- **Accessibility** - Convert audio content to readable text summaries
- **Content curation** - Summarize podcasts for newsletters or content aggregation

## Input

- `podcast_url`: URL to a podcast episode (supports YouTube)

## Output

A structured summary containing:
- Episode title and metadata
- Key topics discussed
- Main takeaways and insights
- Notable quotes (if any)

## Requirements

- Python 3.10+
- OpenRouter API key (set as `OPENROUTER_API_KEY` environment variable)
- Dependencies: `openai`, `youtube-transcript-api`

## Usage

```python
from agent import PodcastSummariser

summariser = PodcastSummariser()
summary = summariser.run("https://youtube.com/watch?v=example")
print(summary)
```

Or via CLI:

```bash
python agent.py "https://youtube.com/watch?v=example"
```

## Model

Uses `openai/gpt-5.1-mini` via OpenRouter for cost-effective, high-quality summarization.
