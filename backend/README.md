# InterVu Backend

FastAPI-based backend server implementing multi-agent AI system for interview practice and career assistance.

## Overview

The backend provides RESTful APIs for:
- User authentication and profile management
- CV parsing and analysis
- Interview generation, execution, and evaluation
- Job application assistance (resume tailoring, cover letters, messaging)
- Historical data storage and retrieval

## Architecture

### Multi-Agent System

Eight specialized agents powered by Google Generative AI SDK:

**1. CV Parsing Agent** (`agents/cv_agent.py`)
- Parses raw CV text into structured JSON
- Extracts education, experience, projects, skills
- Uses schema enforcement for consistent output

**2. Job Analysis Agent** (`agents/job_agent.py`)
- Fetches job descriptions from URLs using BeautifulSoup
- Parses requirements, responsibilities, qualifications
- Identifies company culture and role context

**3. Resume Tailoring Agent** (`agents/resume_agent.py`)
- Matches user profile to job requirements
- Highlights relevant experience and skills
- Generates role-specific resume content

**4. Motivation Letter Agent** (`agents/letter_agent.py`)
- Creates personalized cover letters
- Supports professional and friendly tones
- Aligns with job requirements and company culture

**5. Messaging Agent** (`agents/messaging_agent.py`)
- Generates recruiter outreach emails
- Creates LinkedIn connection messages
- Personalizes based on job and company

**6. Evaluation Agent** (`agents/evaluation_agent.py`)
- Scores answers on clarity, structure, depth, examples
- Provides per-question feedback
- Calculates overall performance metrics

**7. Coaching Agent** (`agents/coaching_agent.py`)
- Generates personalized improvement strategies
- Leverages historical weaknesses
- Provides actionable tips

**8. Question Generation** (Frontend API route)
- Dynamically creates interview questions
- Customized by role, level, type, tech stack

### API Routes

**Authentication** (`routers/auth.py`)
- `POST /auth/register` - User registration
- `POST /auth/login` - JWT token generation
- `GET /auth/me` - Get current user

**Profile Management** (`routers/profile.py`)
- `POST /profile/upload-cv` - Parse and store CV
- `GET /profile/me` - Get user profile
- `PUT /profile/update` - Update profile data
- `GET /profile/strengths` - Aggregate interview insights

**Interview Management** (`routers/interview.py`)
- `POST /interview/save` - Save interview session
- `GET /interview/history` - List all interviews
- `GET /interview/{id}` - Get specific interview
- `POST /interview/{id}/evaluate` - Run evaluation agent
- `DELETE /interview/{id}` - Remove interview

**Career Tools** (`routers/career.py`)
- `POST /career/analyze-job` - Parse job posting
- `POST /career/tailor-resume` - Generate custom resume
- `POST /career/generate-letter` - Create cover letter
- `POST /career/generate-messages` - Create outreach
- `POST /career/save-application` - Store application
- `GET /career/applications` - List applications

### Database Schema

**users** collection:
```json
{
  "_id": "ObjectId",
  "email": "string",
  "username": "string",
  "hashed_password": "string",
  "created_at": "datetime"
}
```

**user_profiles** collection:
```json
{
  "_id": "ObjectId",
  "user_id": "string",
  "cv_text": "string",
  "headline": "string",
  "education": [{"degree": "...", "institution": "...", "year": "..."}],
  "experience": [{"title": "...", "company": "...", "duration": "...", "description": "..."}],
  "projects": [{"name": "...", "description": "...", "technologies": [...]}],
  "skills": {"technical": [...], "soft": [...]},
  "strengths": ["string"],
  "weaknesses": ["string"],
  "updated_at": "datetime"
}
```

**interviews** collection:
```json
{
  "_id": "ObjectId",
  "user_id": "string",
  "questions": ["string"],
  "answers": ["string"],
  "role": "string",
  "level": "string",
  "type": "string",
  "techstack": ["string"],
  "evaluations": [{
    "overall_score": "number",
    "criteria": {"clarity": "number", "structure": "number", ...},
    "strengths": ["string"],
    "weaknesses": ["string"],
    "feedback": "string"
  }],
  "overall_score": "number",
  "strengths": ["string"],
  "weaknesses": ["string"],
  "feedback": "string",
  "coaching_tips": ["string"],
  "created_at": "datetime"
}
```

**applications** collection:
```json
{
  "_id": "ObjectId",
  "user_id": "string",
  "job_data": {
    "job_title": "string",
    "company": "string",
    "url": "string",
    "requirements": ["string"],
    ...
  },
  "tailored_resume": {...},
  "cover_letter": "string",
  "messages": {
    "recruiter_email": "string",
    "linkedin_message": "string"
  },
  "created_at": "datetime"
}
```

## Setup

### Prerequisites
- Python 3.9 or higher
- MongoDB 4.4+
- Google Gemini API key

### Installation

1. Create virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Create `.env` file in project root:
```env
MONGO_URI=mongodb://localhost:27017
MONGO_DB=intervu
SECRET_KEY=your-secret-key-minimum-32-characters
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=60
GEMINI_API_KEY=your-google-gemini-api-key
```

### Running the Server

Development mode:
```bash
uvicorn app.main:app --reload --port 8000
```

Production mode:
```bash
uvicorn app.main:app --host 0.0.0.0 --port 8000
```

Server runs at http://localhost:8000
Interactive API docs at http://localhost:8000/docs

### Docker Deployment

Build image:
```bash
docker build -t intervu-backend .
```

Run container:
```bash
docker run -p 8000:8000 --env-file .env intervu-backend
```

Or use docker-compose from project root:
```bash
docker-compose up -d
```

## Development

### Project Structure

```
backend/
├── app/
│   ├── agents/              # AI agent implementations
│   │   ├── __init__.py
│   │   ├── cv_agent.py
│   │   ├── job_agent.py
│   │   ├── resume_agent.py
│   │   ├── letter_agent.py
│   │   ├── messaging_agent.py
│   │   ├── evaluation_agent.py
│   │   └── coaching_agent.py
│   │
│   ├── core/                # Core configuration
│   │   ├── config.py        # Settings management
│   │   └── security.py      # Password hashing, JWT
│   │
│   ├── db/                  # Database connections
│   │   └── mongo.py         # MongoDB async client
│   │
│   ├── models/              # Pydantic models
│   │   ├── user.py
│   │   ├── profile.py
│   │   ├── interview.py
│   │   ├── application.py
│   │   └── models.py
│   │
│   ├── routers/             # API route handlers
│   │   ├── auth.py
│   │   ├── profile.py
│   │   ├── interview.py
│   │   ├── career.py
│   │   └── health.py
│   │
│   ├── schemas/             # Request/response schemas
│   │   ├── auth.py
│   │   └── user.py
│   │
│   └── main.py             # FastAPI application
│
├── Dockerfile
├── requirements.txt
└── README.md               # This file
```

### Adding New Agents

1. Create agent file in `app/agents/`:
```python
import google.generativeai as genai
import os

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
if GEMINI_API_KEY:
    genai.configure(api_key=GEMINI_API_KEY)

async def your_agent_function(input_data):
    prompt = f"Your specialized prompt with {input_data}"
    
    model = genai.GenerativeModel('gemini-pro')
    response = model.generate_content(prompt)
    
    return process_response(response.text)
```

2. Export in `app/agents/__init__.py`

3. Create router in `app/routers/` if needed

4. Register router in `app/main.py`

### Testing

Run tests:
```bash
pytest
```

Run with coverage:
```bash
pytest --cov=app tests/
```

### Code Quality

Format code:
```bash
black app/
```

Lint code:
```bash
flake8 app/
```

## API Authentication

All protected endpoints require JWT token in Authorization header:

```bash
curl -X GET http://localhost:8000/auth/me \
  -H "Authorization: Bearer YOUR_JWT_TOKEN"
```

Get token via login:
```bash
curl -X POST http://localhost:8000/auth/login \
  -H "Content-Type: application/json" \
  -d '{"username": "user@example.com", "password": "password"}'
```

## Environment Variables

| Variable | Description | Default |
|----------|-------------|---------|
| APP_NAME | Application name | InterVu API |
| APP_ENV | Environment (dev/prod) | dev |
| MONGO_URI | MongoDB connection string | mongodb://localhost:27017 |
| MONGO_DB | Database name | intervu |
| SECRET_KEY | JWT secret key | changeme |
| ALGORITHM | JWT algorithm | HS256 |
| ACCESS_TOKEN_EXPIRE_MINUTES | Token lifetime | 60 |
| GEMINI_API_KEY | Google Gemini API key | (required) |

## Troubleshooting

**MongoDB Connection Error:**
```
Failed to connect to MongoDB
```
Solution: Ensure MongoDB is running and URI is correct

**Import Error:**
```
ModuleNotFoundError: No module named 'XXX'
```
Solution: Activate virtual environment and install requirements

**Authentication Error:**
```
401 Unauthorized
```
Solution: Check JWT token is valid and not expired

**Gemini API Error:**
```
Failed to generate content
```
Solution: Verify GEMINI_API_KEY is set and valid

## Performance Notes

- All database operations use async/await for non-blocking I/O
- Agent calls are sequential within workflows but can be parallelized per request
- MongoDB indexes recommended for user_id fields
- Consider caching for frequently accessed data

## Security

- Passwords hashed with bcrypt
- JWT tokens with configurable expiration
- CORS configured for frontend origin
- Input validation via Pydantic
- MongoDB injection prevention through parameterized queries

## License

MIT License
