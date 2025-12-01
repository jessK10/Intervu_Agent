# InterVu Frontend

Modern Next.js 15 application providing voice-powered interview practice and career tools interface.

## Overview

The frontend offers:
- Voice-powered mock interview interface
- Real-time speech recognition and synthesis
- Interview history and performance tracking
- CV upload and profile management
- Job application workflow (analyze, tailor resume, generate letters)
- User dashboard with analytics

## Technology Stack

- **Framework**: Next.js 15 with App Router
- **Language**: TypeScript
- **Styling**: Tailwind CSS
- **Components**: ShadCN UI
- **Speech**: Web Speech API (synthesis and recognition)
- **State**: React hooks and local storage
- **API Client**: Fetch API with JWT authentication

## Project Structure

```
frontend/intervu/
├── app/                         # Next.js app directory
│   ├── api/                    # API routes
│   │   └── vapi/
│   │       └── generate/      # Question generation endpoint
│   │
│   ├── career/                 # Career tools pages
│   │   └── apply/             # Job application workflow
│   │
│   ├── dashboard/             # User dashboard
│   │   └── page.tsx
│   │
│   ├── interview/             # Interview pages
│   │   ├── start/            # Create new interview
│   │   └── [id]/             # Review interview details
│   │
│   ├── login/                # Authentication pages
│   ├── register/
│   ├── profile/              # User profile
│   │
│   ├── layout.tsx            # Root layout
│   ├── page.tsx              # Home page
│   └── globals.css           # Global styles
│
├── components/               # React components
│   ├── ui/                  # ShadCN UI components
│   │   ├── button.tsx
│   │   ├── input.tsx
│   │   ├── card.tsx
│   │   └── ...
│   │
│   └── VoiceInterviewUI.tsx  # Main interview component
│
├── lib/                     # Utilities
│   ├── utils.ts            # Helper functions
│   └── auth.ts             # Auth utilities
│
├── public/                  # Static assets
│   ├── logo.png
│   └── ...
│
├── next.config.ts
├── tailwind.config.ts
├── tsconfig.json
├── package.json
└── README.md               # This file
```

## Setup

### Prerequisites
- Node.js 18+ and npm
- Backend API running at http://localhost:8000

### Installation

1. Install dependencies:
```bash
npm install
```

2. Create `.env.local` file:
```env
NEXT_PUBLIC_API_URL=http://localhost:8000
GEMINI_API_KEY=your-gemini-api-key
```

3. Start development server:
```bash
npm run dev
```

Application runs at http://localhost:3000

### Build for Production

```bash
npm run build
npm start
```

## Key Features

### 1. Voice Interview System

**Component**: `VoiceInterviewUI.tsx`

Features:
- Text-to-speech AI interviewer
- Speech-to-text answer capture
- Real-time transcription display
- Automatic question progression
- Manual override controls

Browser Requirements:
- Google Chrome recommended
- Microphone permissions required
- HTTPS in production

Usage:
```typescript
const handleStartInterview = () => {
  // Speech synthesis
  const utterance = new SpeechSynthesisUtterance(question);
  window.speechSynthesis.speak(utterance);
  
  // Speech recognition
  const recognition = new webkitSpeechRecognition();
  recognition.start();
  recognition.onresult = (event) => {
    const transcript = event.results[0][0].transcript;
    // Process answer
  };
};
```

### 2. Interview Evaluation

**Page**: `app/interview/[id]/page.tsx`

Displays:
- Overall performance score
- Per-question breakdown with criteria scores
- Identified strengths and weaknesses
- Personalized coaching feedback
- Historical comparison

### 3. Career Application Workflow

**Page**: `app/career/apply/page.tsx`

Workflow:
1. Analyze job (URL or text)
2. Review extracted requirements
3. Generate tailored resume
4. Create cover letter
5. Generate recruiter messages
6. Save complete application

### 4. Dashboard

**Page**: `app/dashboard/page.tsx`

Shows:
- Interview history with scores
- Quick start interview button
- Performance trends
- Recent applications

## Components

### UI Components (ShadCN)

All components in `components/ui/` follow ShadCN patterns:

```typescript
import { Button } from "@/components/ui/button"
import { Input } from "@/components/ui/input"
import { Card } from "@/components/ui/card"
```

### Custom Components

**VoiceInterviewUI**:
Main interview interface with speech controls

**Navigation**:
Header with auth-aware menu

**InterviewCard**:
Reusable interview list item

## State Management

### Authentication

Stored in localStorage:
```typescript
// Save token
localStorage.setItem('token', jwtToken);

// Get token
const token = localStorage.getItem('token');

// Clear on logout
localStorage.removeItem('token');
```

### API Calls

Standard pattern with JWT:
```typescript
const response = await fetch(`${API_URL}/endpoint`, {
  method: 'POST',
  headers: {
    'Content-Type': 'application/json',
    'Authorization': `Bearer ${token}`
  },
  body: JSON.stringify(data)
});

if (response.status === 401) {
  // Redirect to login
  router.push('/login');
  return;
}

const result = await response.json();
```

## Styling

### Tailwind Configuration

Custom theme in `tailwind.config.ts`:
```typescript
export default {
  theme: {
    extend: {
      colors: {
        primary: '#8b5cf6', // Purple
        // ... custom colors
      }
    }
  }
}
```

### Global Styles

Base styles in `app/globals.css`:
- CSS variables for theming
- Dark mode support
- Animation utilities

### Component Styling

Example:
```tsx
<div className="min-h-screen bg-black text-white p-10">
  <Card className="bg-gray-900 border-gray-700">
    <Button className="bg-purple-600 hover:bg-purple-700">
      Click me
    </Button>
  </Card>
</div>
```

## Routing

Next.js App Router patterns:

**Dynamic Routes**:
```
app/interview/[id]/page.tsx → /interview/123
```

**Route Groups**:
```
app/(auth)/login/page.tsx → /login
```

**API Routes**:
```
app/api/vapi/generate/route.ts → /api/vapi/generate
```

## API Integration

### Backend Endpoints

```typescript
// Base URL
const API_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';

// Auth
POST /auth/register
POST /auth/login
GET /auth/me

// Profile
POST /profile/upload-cv
GET /profile/me

// Interviews
POST /interview/save
GET /interview/history
GET /interview/{id}
POST /interview/{id}/evaluate

// Career
POST /career/analyze-job
POST /career/tailor-resume
POST /career/generate-letter
```

### Error Handling

```typescript
try {
  const res = await fetch(url, options);
  
  if (!res.ok) {
    throw new Error(`HTTP ${res.status}`);
  }
  
  return await res.json();
} catch (error) {
  console.error(error);
  // Show user-friendly message
  setError('Operation failed. Please try again.');
}
```

## Development

### Running Dev Server

```bash
npm run dev
```

Hot-reload enabled for all changes.

### Linting

```bash
npm run lint
```

Fix automatically:
```bash
npm run lint --fix
```

### Type Checking

```bash
npx tsc --noEmit
```

### Building

```bash
npm run build
```

Output in `.next/` directory.

## Browser Compatibility

**Fully Supported**:
- Chrome 90+
- Edge 90+
- Safari 14+
- Firefox 88+

**Voice Features Require**:
- Chrome or Edge (best support)
- Microphone access
- HTTPS in production

## Performance

### Optimizations

- Next.js Image component for optimized images
- Route-based code splitting
- Lazy loading for heavy components
- CSS purging via Tailwind

### Lighthouse Scores

Target metrics:
- Performance: 90+
- Accessibility: 95+
- Best Practices: 95+
- SEO: 90+

## Deployment

### Vercel (Recommended)

```bash
npm install -g vercel
vercel
```

Set environment variables in Vercel dashboard.

### Docker

```bash
docker build -t intervu-frontend .
docker run -p 3000:3000 intervu-frontend
```

### Static Export

```bash
npm run build
npm run export
```

Outputs to `out/` directory.

## Environment Variables

| Variable | Description | Default |
|----------|-------------|---------|
| NEXT_PUBLIC_API_URL | Backend API base URL | http://localhost:8000 |
| GEMINI_API_KEY | Google Gemini API key (frontend routes) | (required) |

## Troubleshooting

**Speech Recognition Not Working:**
- Use Chrome browser
- Grant microphone permissions
- Check console for errors
- Ensure HTTPS in production

**API Connection Failed:**
- Verify backend is running
- Check NEXT_PUBLIC_API_URL
- Inspect network tab for CORS issues

**Build Errors:**
```
Module not found
```
- Run `npm install`
- Delete `.next` and rebuild

**Type Errors:**
- Run `npm run lint`
- Check TypeScript version

## Testing

### Component Testing

```bash
npm run test
```

### E2E Testing

```bash
npm run test:e2e
```

## Contributing

1. Create feature branch
2. Follow TypeScript strict mode
3. Use Tailwind for styling
4. Add proper error handling
5. Test voice features in Chrome
6. Submit PR with description

## License

MIT License
