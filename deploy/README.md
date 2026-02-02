# Deploying Podcast Summariser to Render

## Quick Deploy

### 1. Push to GitHub

Make sure the `agents/podcast_summariser` folder is in a GitHub repo.

### 2. Create Render Web Service

1. Go to [Render Dashboard](https://dashboard.render.com)
2. Click **New** → **Web Service**
3. Connect your GitHub repo
4. Configure:
   - **Name**: `friday-podcast-summariser`
   - **Root Directory**: `agents/podcast_summariser`
   - **Runtime**: Python 3
   - **Build Command**: `pip install -r deploy/requirements.txt`
   - **Start Command**: `uvicorn deploy.app:app --host 0.0.0.0 --port $PORT`

### 3. Set Environment Variables

In Render dashboard, add:
- `OPENROUTER_API_KEY` - Your OpenRouter API key

### 4. Deploy

Render will auto-deploy. You'll get a URL like:
```
https://friday-podcast-summariser.onrender.com
```

## Test the Endpoint

```bash
curl -X POST https://friday-podcast-summariser.onrender.com \
  -H "Content-Type: application/json" \
  -d '{"command": "https://www.youtube.com/watch?v=dQw4w9WgXcQ"}'
```

## Register in Supabase

Run this SQL in your Supabase SQL Editor:

```sql
INSERT INTO public.agents (
  name,
  slug,
  url,
  description,
  icon,
  use_cases,
  trigger_keywords,
  version,
  author
) VALUES (
  'Podcast Summariser',
  'podcast-summariser',
  'https://friday-podcast-summariser.onrender.com',  -- Replace with your actual URL
  'Summarize YouTube podcasts into key topics, takeaways, and insights',
  'Podcast',
  ARRAY['Summarize podcasts', 'Extract key insights', 'Get video highlights'],
  ARRAY['podcast', 'youtube', 'video', 'summarize', 'summarise', 'episode'],
  '1.0.0',
  'Friday'
);
```

## Trigger Detection

The orchestrator will trigger this agent when:
- User is watching a YouTube video (detected via screenshot)
- Keywords like "podcast", "youtube", "summarize" appear in context
- A YouTube URL is detected in artifacts

## Local Testing

```bash
cd agents/podcast_summariser
pip install -r deploy/requirements.txt
OPENROUTER_API_KEY=your-key uvicorn deploy.app:app --reload
```

Then test:
```bash
curl -X POST http://localhost:8000 \
  -H "Content-Type: application/json" \
  -d '{"command": "https://youtube.com/watch?v=..."}'
```
