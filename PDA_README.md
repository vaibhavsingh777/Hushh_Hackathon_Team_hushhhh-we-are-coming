# 🔒 Hushh MCP Personal Digital Assistant (PDA)

A privacy-first Personal Digital Assistant built on the Model Context Protocol (MCP) that securely processes and categorizes your emails and calendar events using local AI.

## 🌟 What This PDA Does

This Personal Digital Assistant provides intelligent categorization and analysis of your personal data while maintaining complete privacy and user control. Built following Hushh principles, it ensures your data never leaves your control.

### Core Features

- **🔐 Privacy-First Email Processing**: Securely categorizes emails using local AI models
- **📅 Intelligent Calendar Analysis**: Analyzes scheduling patterns and optimizes your time
- **🤖 Local AI Categorization**: Uses Ollama and free LLM models for content analysis
- **🛡️ Complete Data Control**: Full consent management and data deletion rights
- **📊 Real-time Processing**: Live progress tracking with background processing
- **🔄 Persistent Storage**: Encrypted storage that persists across sessions
- **🌐 Google Integration**: Secure OAuth integration with Gmail and Google Calendar

## 🏗️ How It Works

### 1. Privacy-First Architecture
```
User Data → Local Processing → Encrypted Storage → User Dashboard
     ↓
No External AI APIs (Optional Local Models Only)
```

### 2. Data Processing Flow
1. **Consent Management**: User explicitly grants permissions for specific data types
2. **Secure Data Fetching**: OAuth-protected access to Gmail/Calendar APIs
3. **Local AI Analysis**: Content categorization using local Ollama models or free alternatives
4. **Encrypted Storage**: All processed data stored with AES-256 encryption
5. **User Dashboard**: Interactive visualization of categorized data

### 3. Hushh MCP Protocol Compliance
- ✅ **Consent Tokens**: Granular permission system for each data type
- ✅ **Data Minimization**: Only processes data with explicit consent
- ✅ **Local Processing**: AI analysis happens locally when possible
- ✅ **Audit Trails**: Complete logging of all data processing activities
- ✅ **Right to Delete**: Complete data deletion and consent revocation
- ✅ **Data Portability**: Export all processed data in standard formats

## 🚀 Quick Start

### Prerequisites
- Python 3.8+
- Node.js 16+ (for frontend)
- Google OAuth credentials (for Gmail/Calendar integration)
- Ollama (optional, for local AI processing)

### Installation

1. **Clone the repository**
```bash
git clone <repository-url>
cd hushh2
```

2. **Install Python dependencies**
```bash
pip install -r requirements.txt
```

3. **Set up environment variables**
```bash
cp .env.example .env
# Edit .env with your credentials
```

4. **Run the backend server**
```bash
python main.py
```

5. **Access the dashboard**
Open `http://localhost:8000/static/complete_dashboard.html`

## 🔧 Configuration

### Environment Variables (.env)
```env
# Security Keys (Generate with: python -c "import secrets; print(secrets.token_hex(32))")
SECRET_KEY=your_secret_key_here
VAULT_ENCRYPTION_KEY=your_encryption_key_here
JWT_SECRET=your_jwt_secret_here

# Google OAuth (Get from Google Cloud Console)
GOOGLE_OAUTH_CLIENT_ID=your_google_client_id
GOOGLE_OAUTH_CLIENT_SECRET=your_google_client_secret
GOOGLE_OAUTH_REDIRECT_URI=http://localhost:8000/auth/google/callback

# Optional: Local AI Configuration
OLLAMA_URL=http://localhost:11434
HUGGINGFACE_API_KEY=your_hf_token (optional)
GROQ_API_KEY=your_groq_key (optional)

# Hackathon Mode
HUSHH_HACKATHON=enabled
```

### Google OAuth Setup
1. Go to [Google Cloud Console](https://console.cloud.google.com/)
2. Create a new project or select existing
3. Enable Gmail API and Google Calendar API
4. Create OAuth 2.0 credentials
5. Add authorized redirect URI: `http://localhost:8000/auth/google/callback`

## 📱 Using the PDA

### 1. Authentication
- Click "Connect with Google" to authenticate
- Grant permissions for Gmail and Calendar access
- Your OAuth tokens are securely stored locally

### 2. Email Processing
- Navigate to "Email Processing" tab
- Select number of days to process
- Watch real-time progress as AI categorizes emails
- View categorized results and insights

### 3. Calendar Analysis
- Go to "Calendar Processing" tab
- Choose date range (past and future)
- AI analyzes scheduling patterns and meeting types
- Get productivity insights and optimization suggestions

### 4. Unified Dashboard
- "Dashboard" tab shows combined insights
- Filter by categories across email and calendar
- View detailed analytics and trends
- Export data or manage consent settings

### 5. Privacy Controls
- "Privacy Settings" tab for consent management
- Revoke specific permissions anytime
- Delete all processed data instantly
- Export your data in portable formats

## 🔒 Privacy & Security

### Data Protection
- **End-to-End Encryption**: All stored data encrypted with AES-256
- **Local Processing**: AI analysis happens locally when possible
- **No Data Sharing**: Your data never leaves your environment
- **Granular Consent**: Permission system for each data type
- **Audit Logging**: Complete trail of all data access

### Hushh Principles Compliance
- ✅ **User Agency**: Complete control over data processing
- ✅ **Transparency**: Clear indication of what data is processed and how
- ✅ **Minimization**: Only processes data with explicit consent
- ✅ **Purpose Limitation**: Data used only for stated purposes
- ✅ **Storage Limitation**: Data deleted when consent is revoked
- ✅ **Security**: Industry-standard encryption and security practices

## 🛠️ Technical Architecture

### Backend (FastAPI)
- **Agents**: Modular processing agents for different data types
- **Operons**: Specialized functions for specific tasks
- **Vault**: Secure encrypted storage system
- **Consent Management**: Granular permission system
- **Audit Logger**: Complete activity tracking

### Frontend (Vanilla JS)
- **Progressive Enhancement**: Works without JavaScript
- **Real-time Updates**: WebSocket-like progress tracking
- **Responsive Design**: Mobile-friendly interface
- **Privacy-First UX**: Clear consent and data management

### AI Processing
- **Local Models**: Ollama integration for offline processing
- **Free Alternatives**: Hugging Face, Groq for cloud processing
- **Fallback System**: Multiple AI providers for reliability
- **Privacy-Preserving**: Content analysis without data retention

## 🔬 Development

### Project Structure
```
hushh2/
├── main.py                 # FastAPI backend server
├── frontend/              # Web dashboard
├── hushh_mcp/            # Core MCP implementation
│   ├── agents/           # Processing agents
│   ├── operons/          # Specialized functions
│   ├── vault/            # Secure storage
│   ├── consent/          # Permission management
│   └── integrations/     # External API clients
├── tests/                # Comprehensive test suite
└── docs/                 # Documentation
```

### Testing
```bash
# Run all tests
pytest tests/ -v

# Test specific agent
pytest tests/test_email_processor_agent.py -v

# Test Hushh MCP compliance
pytest tests/ -k "hushh_mcp_protocol" -v
```

### Local AI Setup (Optional)
```bash
# Install Ollama
curl -fsSL https://ollama.ai/install.sh | sh

# Pull a model for categorization
ollama pull llama2:7b

# The PDA will automatically use local models when available
```

## 🌍 Hackathon Compliance

This project fully complies with Hushh Hackathon requirements:

### ✅ Hushh MCP Protocol Implementation
- Complete Model Context Protocol integration
- Proper agent and operon structure
- Consent management system
- Audit logging and privacy controls

### ✅ Privacy-First Design
- No unnecessary data collection
- Local AI processing when possible
- Granular consent management
- Complete data deletion capabilities

### ✅ User Agency
- Full control over data processing
- Transparent permission system
- Easy consent revocation
- Data export capabilities

### ✅ Technical Excellence
- Comprehensive test coverage
- Proper error handling
- Scalable architecture
- Documentation and code quality

## 📋 API Endpoints

### Authentication
- `GET /auth/google/redirect` - Google OAuth initiation
- `GET /auth/google/callback` - OAuth callback handler
- `GET /api/user/info` - Get authenticated user info

### Data Processing
- `POST /api/emails/process/{days}` - Process emails with AI
- `POST /api/calendar/process/{days_back}/{days_forward}` - Process calendar
- `GET /api/processing/status/{task_id}` - Real-time progress tracking

### Data Access
- `GET /api/categories/unified` - Get all categories
- `GET /api/emails/categories/{category}` - Filter emails by category
- `GET /api/calendar/categories/{category}` - Filter events by category

### Privacy Controls
- `GET /api/consent/active` - View active permissions
- `POST /api/consent/revoke` - Revoke specific consent
- `DELETE /api/data/delete` - Delete user data
- `GET /api/data/export` - Export all data

## 🤝 Contributing

This project follows Hushh principles for privacy-preserving development:

1. **Privacy by Design**: All features must respect user privacy
2. **Consent First**: No data processing without explicit permission
3. **Transparency**: Clear documentation of all data handling
4. **User Control**: Users must have full control over their data

## 📄 License

This project is developed for the Hushh Hackathon and follows Hushh's privacy-first principles.

## 🔗 Links

- [Hushh Platform](https://hushh.ai)
- [Model Context Protocol](https://modelcontextprotocol.io)
- [FastAPI Documentation](https://fastapi.tiangolo.com)
- [Ollama](https://ollama.ai)

---

**Built with 🔒 Privacy, 🤖 AI, and ❤️ for the Hushh Hackathon**
