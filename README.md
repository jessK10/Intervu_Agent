# InterVu - AI-Powered Interview & Career Platform

InterVu is an intelligent platform that combines AI-powered interview practice with comprehensive career assistance. Built on a multi-agent architecture using Google's Generative AI, it provides personalized interview coaching, resume tailoring, and job application support.

## Features

### Voice-Powered Mock Interviews
- AI interviewer speaks questions using natural voicee
- Speech recognition captures verbal responses
- Automatic transcription and storage
- Support for technical and behavioral interviews
- Customizable by role, level, and technology stack

### Intelligent Interview Evaluation
- Multi-criteria scoring (clarity, structure, technical depth, examples)
- Per-question detailed feedback
- Overall performance metrics
- Personalized coaching based on performance
- Historical tracking of strengths and weaknesses

### Career Application Suite
- CV parsing with structured data extraction
- Job description analysis from URL or text
- Resume tailoring for specific roles
- Automated cover letter generation
- Professional recruiter outreach messages

### User Management
- Secure authentication with JWT tokens
- Personal dashboard with interview history
- Application tracking
- Profile management

## Architecture

### Multi-Agent System

InterVu implements 8 specialized AI agents powered by Google Generative AI SDK:

1. **CV Parsing Agent** - Extracts structured data from resume text
2. **Job Analysis Agent** - Processes and analyzes job descriptions
3. **Resume Tailoring Agent** - Creates customized resumes for specific roles
4. **Motivation Letter Agent** - Generates personalized cover letters
5. **Messaging Agent** - Creates recruiter emails and LinkedIn messages
6. **Evaluation Agent** - Scores interview answers with detailed feedback
7. **Coaching Agent** - Provides personalized improvement strategies
8. **Question Generation** - Creates dynamic interview questions

### Technology Stack

**Frontend:**
- Next.js 15 with TypeScript
- Tailwind CSS + ShadCN UI components
- Web Speech API (synthesis and recognition)
- React hooks for state management

**Backend:**
- FastAPI (Python async framework)
- MongoDB with Motor async driver
- JWT authentication
- Google Generative AI SDK
- Pydantic for data validation

## Project Structure

```
InterVu/
├── backend/
│   ├── app/
│   │   ├── agents/           # 8 AI agents
│   │   ├── core/             # Config and security
│   │   ├── db/               # MongoDB connection
│   │   ├── models/           # Pydantic models
│   │   ├── routers/          # API endpoints
│   │   ├── schemas/          # Request/response schemas
│   │   └── main.py           # FastAPI entry point
│   ├── requirements.txt
│   └── Dockerfile
│
├── frontend/
│   └── intervu/
│       ├── app/              # Next.js pages
│       ├── components/       # React components
│       ├── lib/              # Utilities
│       └── public/           # Static assets
│
├── docker-compose.yml
├── README.md                 # This file
├── PROJECT_WRITEUP.md        # Detailed project description
└── .env                      # Environment variables
```

## Getting Started

### Prerequisites
- Python 3.9+
- Node.js 18+
- MongoDB 4.4+
- Google Gemini API key

### Backend Setup

1. Navigate to backend directory:
```bash
cd backend
```

2. Create virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

4. Create `.env` file in project root:
```env
MONGO_URI=mongodb://localhost:27017
MONGO_DB=intervu
SECRET_KEY=your-secret-key-here
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=60
GEMINI_API_KEY=your-gemini-api-key
```

5. Start the server:
```bash
uvicorn app.main:app --reload --port 8000
```

Backend runs at http://localhost:8000
API docs available at http://localhost:8000/docs

### Frontend Setup

1. Navigate to frontend directory:
```bash
cd frontend/intervu
```

2. Install dependencies:
```bash
npm install
```

3. Start development server:
```bash
npm run dev
```

Frontend runs at http://localhost:3000

### Docker Deployment (Optional)

Start all services with Docker Compose:
```bash
docker-compose up -d
```

## API Endpoints

### Authentication
- `POST /auth/register` - Create new account
- `POST /auth/login` - Login and get JWT token
- `GET /auth/me` - Get current user

### Profile Management
- `POST /profile/upload-cv` - Parse and save CV
- `GET /profile/me` - Get user profile
- `PUT /profile/update` - Update profile
- `GET /profile/strengths` - Get aggregated strengths/weaknesses

### Interviews
- `POST /interview/save` - Save completed interview
- `GET /interview/history` - Get interview history
- `GET /interview/{id}` - Get specific interview
- `POST /interview/{id}/evaluate` - Evaluate interview answers
- `DELETE /interview/{id}` - Delete interview

### Career Tools
- `POST /career/analyze-job` - Analyze job description
- `POST /career/tailor-resume` - Generate tailored resume
- `POST /career/generate-letter` - Create cover letter
- `POST /career/generate-messages` - Create outreach messages
- `POST /career/save-application` - Save complete application
- `GET /career/applications` - Get application history

## Usage Guide

### 1. Create Account
Register at http://localhost:3000/register and login

### 2. Upload CV (Optional)
Navigate to Profile > Upload CV to enable career tools

### 3. Start Mock Interview
1. Go to Dashboard > Start Interview
2. Select role, level, type, and tech stack
3. Choose number of questions
4. Click Generate Questions & Start Interview
5. Answer questions using voice or text
6. Click Evaluate Interview for detailed feedback

### 4. Job Application (Requires CV)
1. Navigate to Career Tools > Apply
2. Paste job URL or description
3. Click Analyze Job
4. Generate tailored resume
5. Create cover letter
6. Generate outreach messages
7. Save complete application

## Google SDK Usage

All backend agents use Google's Generative AI SDK (`google-generativeai`):

```python
import google.generativeai as genai

genai.configure(api_key=GEMINI_API_KEY)
model = genai.GenerativeModel('gemini-pro')
response = model.generate_content(prompt)
```

Each agent employs specialized prompts optimized for its specific task (evaluation, parsing, generation, etc.).

## Development

### Running Tests
```bash
cd backend
pytest
```

### Code Quality
```bash
# Backend
cd backend
black app/
flake8 app/

# Frontend
cd frontend/intervu
npm run lint
```

## Troubleshooting

**MongoDB Connection Error:**
- Ensure MongoDB is running: `mongod --dbpath /path/to/data`
- Check MONGO_URI in .env file

**Speech Recognition Not Working:**
- Use Google Chrome browser
- Grant microphone permissions
- Check for HTTPS in production

**API Key Error:**
- Verify GEMINI_API_KEY is set in .env
- Check API key has proper permissions

## License

MIT License - See LICENSE file for details

## Contributing

1. Fork the repository
2. Create feature branch (`git checkout -b feature/amazing-feature`)
3. Commit changes (`git commit -m 'Add amazing feature'`)
4. Push to branch (`git push origin feature/amazing-feature`)
5. Open Pull Request

## Support

For issues, questions, or contributions, please open an issue on GitHub.

## Acknowledgments

- Google Generative AI for powering all agents
- FastAPI for the excellent Python web framework
- Next.js team for the modern React framework
- ShadCN for beautiful UI components
