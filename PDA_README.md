# 🤖 Smart Data Categorizer & Automation Engine

An intelligent data categorization and automation system built on the Hushh Model Context Protocol (MCP) that processes and categorizes your emails and calendar events using AI-powered content analysis.

## 🌟 What This System Does

This Smart Data Categorizer provides intelligent content classification and automation for your personal data while maintaining complete privacy and user control. Built following Hushh MCP principles, it ensures your data never leaves your control.

### Core Features

- **🧠 AI-Powered Content Classification**: Advanced categorization using multi-LLM support
- **📧 Smart Email Analysis**: Intelligent email categorization with priority detection  
- **📅 Calendar Intelligence**: Advanced scheduling pattern recognition and optimization
- **🔄 Automated Processing**: Background task automation with real-time progress tracking
- **🛡️ Privacy-First Architecture**: Complete consent management and data control
- **� Encrypted Storage**: Secure vault storage that persists across sessions
- **🌐 Seamless Integration**: OAuth integration with Gmail and Google Calendar
- **📊 Real-time Dashboard**: Live processing updates with comprehensive insights

## 🏗️ System Architecture

### 1. Agent-Based Processing Architecture
```
Data Sources → Processing Agents → AI Analysis → Categorized Output
     ↓              ↓                 ↓              ↓
Gmail/Calendar → Email/Calendar → Multi-LLM AI → Smart Categories
                  Processors      Analysis      & Automation
```

### 2. Data Processing Flow
1. **Consent Validation**: User explicitly grants permissions for specific data types
2. **Secure Data Access**: OAuth-protected access to Gmail/Calendar APIs  
3. **AI-Powered Analysis**: Content categorization using multiple LLM providers
4. **Smart Classification**: Advanced priority detection and sentiment analysis
5. **Automated Actions**: Intelligent automation based on content patterns
4. **Encrypted Storage**: All processed data stored with AES-256 encryption in vault
5. **User Dashboard**: Interactive visualization of categorized data and insights

### 3. Hushh MCP Protocol Compliance
- ✅ **Consent Tokens**: Granular permission system for each data type and operation
- ✅ **Data Minimization**: Only processes data with explicit user consent
- ✅ **Multi-LLM Processing**: AI analysis using Ollama, OpenAI, Groq, Hugging Face
- ✅ **Audit Trails**: Complete logging of all data processing activities
- ✅ **Right to Delete**: Complete data deletion and consent revocation
- ✅ **Data Portability**: Export all processed data in standard formats

## 🛠️ Technical Architecture

### Core Components

```
hushh_mcp/
├── agents/                    # Processing agents for data analysis
│   ├── email_processor/       # Email categorization and analysis
│   ├── calendar_processor/    # Calendar event processing
│   └── audit_logger/          # Compliance and audit logging
├── operons/                   # AI-powered analysis modules
│   ├── categorize_content.py  # Multi-LLM categorization engine
│   ├── content_classification.py # Advanced content analysis
│   ├── privacy_audit.py       # Data sensitivity assessment
│   └── scheduling_intelligence.py # Smart calendar optimization
├── vault/                     # Encrypted storage system
│   ├── storage.py            # Core vault functionality
│   └── persistent_storage.py # Data persistence layer
├── consent/                   # Consent management system
└── integrations/             # External service integrations
    └── gmail_client.py       # Google OAuth and API integration
```

### Agent Architecture

1. **Email Processor Agent** (`agents/email_processor/`)
   - Fetches emails via Gmail API with pagination support
   - AI-powered categorization using multiple LLM providers
   - Priority detection and sentiment analysis
   - Encrypted storage of processed results

2. **Calendar Processor Agent** (`agents/calendar_processor/`)
   - Google Calendar integration for event analysis
   - Scheduling pattern recognition and optimization
   - Meeting intelligence and productivity insights
   - Smart automation suggestions

3. **Audit Logger Agent** (`agents/audit_logger/`)
   - Complete activity logging for compliance
   - Privacy audit trail generation
   - Consent validation and tracking
   - Transparency reporting for users

## 🚀 Quick Start

### Prerequisites
- Python 3.8+
- Node.js 16+ (for frontend dashboard)
- Google OAuth credentials (for Gmail/Calendar integration)
- Ollama (optional, for local AI processing)

### Installation

1. **Clone the repository**
```bash
git clone <repository-url>
cd hushh
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
