# Celery Setup for Testimony Transcription

This backend uses Celery for asynchronous transcription of audio testimonies using OpenAI's Whisper API.

## Requirements

- Redis server (as message broker)
- Environment variables configured (see `.env` file)
- Docker and Docker Compose (recommended)

## Production/Docker Setup (Recommended)

### 1. Environment Variables
Create a `.env` file in the root directory with:
```env
# Redis Configuration (use 'redis' as hostname for Docker)
REDIS_URL=redis://redis:6379/0

# OpenAI Configuration
OPENAI_API_KEY=your_openai_api_key

# Google Cloud Storage
GCS_BUCKET_NAME=your_gcs_bucket_name
GOOGLE_APPLICATION_CREDENTIALS=/run/secrets/gdrive-creds.json

# Supabase Configuration
SUPABASE_URL=https://your-project.supabase.co
SUPABASE_KEY=your_supabase_anon_key

# Optional Celery Configuration
CELERY_LOG_LEVEL=info
```

### 2. Start All Services
```bash
docker-compose up -d
```

This will start:
- **Redis server** (port 6379)
- **FastAPI backend** (port 8000)
- **Celery worker** (transcription queue)
- **Flower monitoring** (port 5555) - optional

### 3. Monitor Services
- **API**: http://localhost:8000
- **API Docs**: http://localhost:8000/docs
- **Celery Monitor**: http://localhost:5555 (Flower UI)
- **Worker Stats**: http://localhost:8000/worker/stats

## Development Setup (Local)

### 1. Start Redis
```bash
# Using Docker
docker run -d -p 6379:6379 redis:7-alpine

# Or using local Redis installation
redis-server
```

### 2. Environment Variables
Make sure these are set in your `.env` file:
```env
REDIS_URL=redis://localhost:6379/0
OPENAI_API_KEY=your_openai_api_key
GCS_BUCKET_NAME=your_gcs_bucket_name
GOOGLE_APPLICATION_CREDENTIALS=path_to_your_service_account.json
SUPABASE_URL=your_supabase_url
SUPABASE_KEY=your_supabase_key
```

### 3. Start the FastAPI Backend
```bash
cd backend
uvicorn src.app.main:app --reload --host 0.0.0.0 --port 8000
```

### 4. Start the Celery Worker
```bash
# Option 1: Using the development script
cd backend
python run_worker.py

# Option 2: Using celery command directly
cd backend
celery -A src.app.tasks worker --loglevel=info --queues=transcription
```

## API Endpoints

### Upload Testimony
```http
POST /testimonies
Content-Type: multipart/form-data

file: audio_file.mp3
church_id: optional_church_id
tags: optional,comma,separated,tags
```

Response includes `task_id` for tracking progress.

### Check Task Status
```http
GET /tasks/{task_id}
```

Returns:
```json
{
  "task_id": "uuid",
  "status": "PENDING|SUCCESS|FAILURE|RETRY",
  "result": "transcription_text_if_completed",
  "traceback": "error_details_if_failed"
}
```

### Worker Statistics
```http
GET /worker/stats
```

## Task Flow

1. Audio file uploaded to `/testimonies`
2. File uploaded to Google Cloud Storage
3. Testimony record created in Supabase with `transcript_status: "pending"`
4. Celery task `transcribe_testimony` queued with testimony ID and GCS URI
5. Worker picks up task:
   - Downloads audio from GCS
   - Sends to OpenAI Whisper API
   - Updates Supabase with transcript and status
6. Status updates: `pending` → `processing` → `completed`/`failed`

## Task Configuration

- **Queue**: `transcription`
- **Max Retries**: 3
- **Retry Delay**: 60 seconds (exponential backoff)
- **Worker Concurrency**: 2 (configurable in docker-compose.yml)
- **Retry Conditions**: Rate limits, timeouts

## Monitoring

### Flower UI (Recommended)
Visit http://localhost:5555 for a web-based monitoring interface showing:
- Active/completed/failed tasks
- Worker statistics
- Task details and results
- Real-time updates

### API Endpoints
- Check worker status: `GET /worker/stats`
- Check specific task: `GET /tasks/{task_id}`

### Command Line
- View logs: `docker-compose logs worker`
- Monitor Redis: `docker exec -it <redis-container> redis-cli monitor`

## Troubleshooting

### Worker not starting
```bash
# Check logs
docker-compose logs worker

# Restart worker
docker-compose restart worker
```

### Tasks stuck in PENDING
- Ensure worker container is running: `docker-compose ps`
- Check Redis connectivity: `docker-compose logs redis`
- Verify environment variables: `docker-compose config`

### Transcription failures
- Check OpenAI API key and credits
- Verify GCS permissions and bucket name
- Check audio file format compatibility
- Review worker logs: `docker-compose logs worker`

### Performance Issues
- Adjust worker concurrency in docker-compose.yml
- Monitor memory usage: `docker stats`
- Scale workers: `docker-compose up -d --scale worker=3`

### Flower Service Issues
If flower fails to start due to missing credentials:
- The flower service uses `SKIP_CLIENT_INIT=true` to avoid initializing heavy clients
- This allows monitoring without requiring GCS/OpenAI credentials
- If you still see issues, check: `docker-compose logs flower` 