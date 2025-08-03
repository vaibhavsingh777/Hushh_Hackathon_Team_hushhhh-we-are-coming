# 🚀 Hushh MCP Personal Digital Assistant - Privacy-First PDA

A complete **Privacy-First Personal Digital Assistant** built following the **Hushh Model Context Protocol (MCP)** standards by **Team "We Are Coming"**. This PDA empowers users with intelligent data processing while maintaining complete privacy control and consent management.

## 👥 Team "We Are Coming"

- **Aryan Tamboli** - Lead Developer & AI Integration Specialist
- **Vaibhav Singh** - Backend Architecture & Security Expert  
- **Rohit Gupta** - Frontend Development & UX Design
- **Udit** - Data Privacy & Compliance Specialist

## 🎯 Hackathon Project Overview

### What is this PDA?
The Hushh MCP Personal Digital Assistant is a **privacy-by-design** system that processes your personal data (emails, calendar events) using **local AI** while ensuring you maintain complete control over your information. Unlike traditional cloud services, this PDA follows strict consent protocols and gives you the power to revoke access and delete data instantly.

### 🏆 Hushh MCP Protocol Compliance
This project fully implements the **Hushh Model Context Protocol (MCP)** with:
- ✅ **Agent-Based Architecture**: Modular processing agents with clear responsibilities
- ✅ **Consent Management**: Granular permission system with instant revocation
- ✅ **Privacy by Design**: Built-in privacy protection mechanisms
- ✅ **Audit Logging**: Complete activity tracking and compliance
- ✅ **Vault Storage**: Encrypted data storage with user-controlled keys
- ✅ **Trust Links**: Secure inter-agent communication
- ✅ **Data Minimization**: Only processes necessary data with explicit consent

### Core Philosophy
- **Privacy First**: Your data never leaves your control
- **Consent-Based**: Explicit permission required for all processing
- **AI-Powered**: Intelligent categorization using local LLM models
- **Transparent**: Complete audit trails of all operations
- **User-Controlled**: Instant data deletion and consent revocation

## 🎬 Demo Instructions (Hackathon Submission)

### Quick Demo Setup (5 Minutes)

1. **Clone and Install**
```bash
git clone https://github.com/vaibhavsingh777/Hushh_Hackathon_Team_hushhhh-we-are-coming.git
cd Hushh_Hackathon_Team_hushhhh-we-are-coming
pip install -r requirements.txt
```

2. **Start Backend**
```bash
python main.py
# Backend available at: http://localhost:8000
```

3. **Start Frontend**
```bash
cd frontend
python -m http.server 3000
# Frontend available at: http://localhost:3000
```

4. **Demo Features**
- **Privacy-First Email Processing**: Upload/connect Gmail for AI categorization
- **Intelligent Calendar Analysis**: Process calendar events with scheduling insights  
- **Consent Management**: Demonstrate instant data deletion and consent revocation
- **Multi-LLM Support**: Show local Ollama, OpenAI, and rule-based fallbacks
- **Real-Time Processing**: Background processing with live status updates
- **Unified Categories**: Combined email/calendar categorization view

### Key Demo Points
🔐 **Privacy Controls**: Show one-click data deletion and consent revocation  
🤖 **AI Processing**: Demonstrate multi-LLM categorization with confidence scores  
📊 **Real-Time UI**: Live processing status and category updates  
🛡️ **Security**: Encrypted storage and audit trails  
⚡ **Performance**: Background processing with progress tracking

## 🚀 Complete Setup Guide

### Prerequisites
- **Python 3.8+**
- **Google OAuth credentials** (optional, for real Gmail/Calendar integration)
- **Ollama** (optional, for local AI processing)

### Installation & Configuration

```bash
# Install Python dependencies
pip install -r requirements.txt

# Set up environment variables (optional)
cp .env.example .env
# Edit .env with your settings (Google OAuth, encryption keys, etc.)
```

### System Access Points

- **Frontend Dashboard**: http://localhost:3000
- **Backend API**: http://localhost:8000
- **API Documentation**: http://localhost:8000/docs
- **Health Check**: http://localhost:8000/health

## 🌟 Core Functionality

### 🔐 Privacy-First Email Processing
- **AI-Powered Categorization**: Uses local LLM models (Ollama, Groq, OpenAI) to categorize emails
- **Sentiment Analysis**: Analyzes email sentiment and priority levels
- **Secure Gmail Integration**: OAuth-based access with granular permissions
- **Privacy Protection**: All processing happens locally with encrypted storage

### 📅 Intelligent Calendar Analysis
- **Event Categorization**: Automatically categorizes meetings and appointments
- **Scheduling Optimization**: Analyzes patterns and suggests improvements
- **Productivity Insights**: Provides analytics on time usage and meeting efficiency
- **Google Calendar Integration**: Secure OAuth access to calendar data

### 🤖 Local AI & Machine Learning
- **Multi-LLM Support**: Works with Ollama, OpenAI, Groq, and Hugging Face models
- **Offline Capability**: Functions without internet when using local models
- **Confidence Scoring**: Provides AI confidence levels for all categorizations
- **Fallback Systems**: Multiple AI providers ensure reliable processing

### 🛡️ Advanced Privacy Controls
- **Granular Consent Management**: Permission system for each data type
- **Instant Data Deletion**: Complete data removal with one click
- **Audit Trails**: Full logging of all data processing activities
- **Data Portability**: Export all your data in standard formats
- **Right to be Forgotten**: GDPR-compliant data deletion

### 📊 Real-Time Processing & Analytics
- **Background Processing**: Non-blocking data analysis with progress tracking
- **Live Updates**: Real-time status updates during processing
- **Unified Categories**: Combined view of email and calendar categorizations
- **Performance Metrics**: Detailed insights into productivity and patterns

## 🏗️ Technical Architecture

### Hushh MCP Protocol Compliance
- ✅ **Consent Tokens**: Granular permission system following MCP standards
- ✅ **Agent Framework**: Modular processing agents (Email, Calendar, Audit)
- ✅ **Vault Storage**: Encrypted data storage with AES-256 encryption
- ✅ **Operons**: Specialized functions for content processing
- ✅ **Trust Links**: Secure agent-to-agent communication
- ✅ **Privacy Controls**: User-controlled data management

### System Components

#### 🔧 Backend Architecture (`main.py`)
- **FastAPI REST API** with comprehensive endpoints
- **Google OAuth 2.0** integration for secure authentication
- **JWT Token Management** for session handling
- **Background Task Processing** with real-time status tracking
- **Comprehensive Error Handling** and logging

#### 🎨 Frontend Dashboard (`frontend/`)
- **Responsive Web Interface** built with HTML5/CSS3/JavaScript
- **Real-Time Updates** using async API calls
- **Interactive Categories** with drill-down capabilities
- **Privacy Controls** for consent management
- **Processing Status** with live progress indicators

#### 🧠 AI Processing Agents (`hushh_mcp/agents/`)
- **EmailProcessorAgent**: AI-powered email analysis and categorization
- **CalendarProcessorAgent**: Event processing and scheduling intelligence
- **AuditLoggerAgent**: Activity tracking and compliance logging

#### ⚙️ Specialized Operons (`hushh_mcp/operons/`)
- **categorize_content**: Multi-LLM content categorization
- **schedule_event**: Event creation and management
- **privacy_audit**: Data sensitivity assessment
- **data_validation**: Data integrity checking

## 📋 Feature Showcase

### � Email Management
- **Smart Categorization**: Work, Personal, Finance, Newsletter, etc.
- **Priority Detection**: High, Medium, Low priority classification
- **Sender Analysis**: Relationship mapping and importance scoring
- **Content Extraction**: Key information identification and summarization

### 📅 Calendar Intelligence
- **Meeting Pattern Analysis**: Identifies productive vs. non-productive meetings
- **Time Optimization**: Suggests schedule improvements
- **Event Classification**: Categorizes different types of appointments
- **Conflict Detection**: Identifies scheduling conflicts and overlaps

### 🔒 Privacy & Security
- **End-to-End Encryption**: All data encrypted with user-controlled keys
- **Zero-Trust Architecture**: No data processing without explicit consent
- **Local Processing**: AI analysis happens on your machine when possible
- **Secure Storage**: Encrypted vault system for persistent data

### 📊 Analytics & Insights
- **Productivity Metrics**: Email response times, meeting efficiency
- **Pattern Recognition**: Identifies trends in communication and scheduling
- **Categorization Statistics**: Breakdown of email and calendar categories
- **AI Confidence Tracking**: Transparency in automated categorization

## 🔌 API Documentation

### Authentication Endpoints
- `GET /auth/google/redirect` - Initiate Google OAuth flow
- `GET /auth/google/callback` - Handle OAuth callback
- `GET /api/user/info` - Get authenticated user information

### Data Processing Endpoints
- `POST /api/emails/process/{days}` - Process emails with AI categorization
- `POST /api/calendar/process/{days_back}/{days_forward}` - Process calendar events
- `GET /api/processing/status/{task_id}` - Real-time processing status
- `GET /api/processing/results/{task_id}` - Get final processing results

### Data Access Endpoints
- `GET /api/categories/unified` - Get combined email/calendar categories
- `GET /api/emails/categories/{category}` - Filter emails by category
- `GET /api/calendar/categories/{category}` - Filter events by category
- `GET /api/emails/categorized` - Get all categorized emails
- `GET /api/calendar/categorized` - Get all categorized events

### Privacy & Consent Management
- `GET /api/consent/active` - View all active consent tokens
- `POST /api/consent/revoke` - Revoke consent and delete data
- `POST /api/consent/grant` - Grant new consent permissions
- `DELETE /api/data/delete` - Delete user data (right to be forgotten)
- `GET /api/data/export` - Export all user data

### Agent Actions
- `POST /api/agents/schedule_event` - Create new calendar events
- `POST /api/agents/create_note` - Generate structured notes

## 🔧 Configuration

### Environment Variables (`.env`)
```env
# Google OAuth (required for real Gmail/Calendar access)
GOOGLE_OAUTH_CLIENT_ID=your_google_client_id
GOOGLE_OAUTH_CLIENT_SECRET=your_google_client_secret
GOOGLE_OAUTH_REDIRECT_URI=http://localhost:8000/auth/google/callback

# Security & Encryption
JWT_SECRET=your_jwt_secret_key
VAULT_ENCRYPTION_KEY=your_32_byte_encryption_key

# AI/LLM Configuration
OPENAI_API_KEY=your_openai_api_key
GROQ_API_KEY=your_groq_api_key
HUGGINGFACE_API_KEY=your_huggingface_api_key
OLLAMA_BASE_URL=http://localhost:11434

# Database & Storage
DATABASE_URL=sqlite:///vault_data/hushh_pda.db
STORAGE_DIRECTORY=vault_data
```

### AI Model Configuration
The PDA supports multiple AI providers with automatic fallback:
1. **Ollama** (local, privacy-first)
2. **Groq** (fast cloud inference)
3. **OpenAI** (GPT models)
4. **Hugging Face** (open source models)

## 🧪 Testing & Development

### Run the Test Suite
```bash
# Run all tests
pytest tests/ -v

# Test specific components
pytest tests/test_email_processor_agent.py -v
pytest tests/test_calendar_processor_agent.py -v
pytest tests/test_consent_management.py -v

# Test Hushh MCP compliance
pytest tests/ -k "hushh_protocol" -v
```

### Development Server
```bash
# Start backend with auto-reload
python main.py

# Start frontend development server
cd frontend
python -m http.server 3000
```

## 🌍 Hackathon & Compliance

### ✅ Hushh MCP Protocol Implementation
- **Complete Agent Architecture**: Follows MCP agent design patterns
- **Proper Consent Management**: Token-based permission system
- **Audit Logging**: Comprehensive activity tracking
- **Privacy by Design**: Built-in privacy protection mechanisms
- **Data Minimization**: Only processes necessary data with consent

### ✅ Privacy Regulations Compliance
- **GDPR Ready**: Right to deletion, data portability, consent management
- **SOC2 Compatible**: Audit trails and security controls
- **Privacy by Design**: Built-in privacy protection from ground up

### ✅ Technical Excellence
- **Comprehensive Test Coverage**: 58+ automated tests
- **Error Handling & Validation**: Robust error management
- **Scalable Architecture**: Clean, maintainable codebase
- **Complete Documentation**: Extensive API and usage documentation

## 📱 User Interface Features

### Dashboard Overview
- **Unified Categories View**: Combined email and calendar categorization
- **Real-Time Processing Status**: Live updates during data processing
- **Interactive Category Cards**: Click to drill down into specific categories
- **Privacy Control Panel**: Manage consent and data deletion

### Processing Interface
- **Background Processing**: Non-blocking operations with progress bars
- **Status Notifications**: Real-time feedback on all operations
- **Error Handling**: Clear error messages and recovery suggestions
- **Results Display**: Comprehensive results with insights and statistics

### Privacy Management
- **Consent Dashboard**: View and manage all active permissions
- **Data Deletion**: One-click complete data removal
- **Export Functionality**: Download all your data in standard formats
- **Audit Trail Viewer**: See complete history of data processing

## 🔮 Advanced Features

### AI-Powered Insights
- **Content Classification**: Automatic categorization with confidence scores
- **Sentiment Analysis**: Emotional tone detection in communications
- **Priority Detection**: Importance and urgency classification
- **Pattern Recognition**: Trend analysis across time periods

### Scheduling Intelligence
- **Meeting Optimization**: Suggestions for better meeting efficiency
- **Calendar Conflicts**: Automatic detection of scheduling issues
- **Productivity Analysis**: Insights into time usage patterns
- **Event Clustering**: Group related events and activities

### Security & Privacy
- **Zero-Knowledge Architecture**: No server-side data retention
- **Client-Side Encryption**: Data encrypted before transmission
- **Consent Versioning**: Track changes in permission levels
- **Data Anonymization**: Optional anonymization for analytics

---

**🚀 Ready to revolutionize your personal data management with complete privacy control!**

For detailed technical documentation, troubleshooting, and advanced configuration, see the `/docs` directory.
