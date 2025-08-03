# Smart Data Categorizer Frontend Dashboard

Interactive dashboard for the Smart Data Categorizer & Automation Engine with real-time processing updates.

## Setup

1. Start the backend:
```bash
cd ../
python main.py
```

2. Serve the frontend:
```bash
# Option 1: Using Python
python -m http.server 3000

# Option 2: Using Node.js (if available)
npx serve -p 3000

# Option 3: Open index.html directly in browser
```

## Features

- 🔐 Google OAuth authentication with secure session management
- 🧠 AI-powered email categorization with multi-LLM support
- � Smart calendar processing with scheduling intelligence
- � Real-time processing dashboard with live progress updates
- 📈 Comprehensive categorization analytics and insights
- 🛡️ Privacy controls with instant data deletion
- ⚡ Fast, responsive design with clean UX

## API Integration

The frontend communicates with the backend API at `http://localhost:8000`:

- `GET /auth/google/redirect` - OAuth initiation
- `POST /api/emails/process/{days}` - Email processing
- `POST /api/calendar/process/{days_back}/{days_forward}` - Calendar processing

## Architecture

- **Single HTML file** with embedded CSS and JavaScript
- **Modular design** following Hushh principles
- **Clean separation** between frontend and backend
- **No complex build process** - just open and run

## Usage

1. Open `index.html` in your browser
2. Click "Sign in with Google"
3. Complete OAuth flow
4. Use the dashboard to process your data

Backend must be running on port 8000 for full functionality.
