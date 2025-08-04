# 🤖 Smart Data Categorizer & Automation Engine - Hushh MCP

A complete **Intelligent Data Categorization and Automation System** built following the **Hushh Model Context Protocol (MCP)** standards by **Team "We Are Coming"**. This system empowers users with AI-powered content analysis and smart automation while maintaining complete privacy control and consent management.

## 👥 Team "We Are Coming"

- **Aryan Tamboli** - Lead Developer & AI Integration Specialist
- **Vaibhav Singh** - Backend Architecture & Security Expert  
- **Rohit Gupta** - Frontend Development & UX Design
- **Udit** - Data Privacy & Compliance Specialist

## 🎯 Hackathon Project Overview

### What is this Smart Categorizer?
The Smart Data Categorizer & Automation Engine is a **privacy-by-design** system that intelligently processes and categorizes your personal data (emails, calendar events) using **multi-LLM AI integration** while ensuring you maintain complete control over your information. Unlike traditional cloud services, this system follows strict consent protocols and gives you the power to revoke access and delete data instantly.

### 🏆 Hushh MCP Protocol Compliance
This project fully implements the **Hushh Model Context Protocol (MCP)** with:
- ✅ **Agent-Based Architecture**: Specialized processing agents (Email, Calendar, Audit)
- ✅ **AI-Powered Classification**: Multi-LLM support (Ollama, OpenAI, Groq, Hugging Face)
- ✅ **Smart Automation**: Intelligent content analysis and automation suggestions
- ✅ **Consent Management**: Granular permission system with instant revocation
- ✅ **Privacy by Design**: Built-in privacy protection mechanisms
- ✅ **Audit Logging**: Complete activity tracking and compliance
- ✅ **Vault Storage**: Encrypted data storage with user-controlled keys
- ✅ **Trust Links**: Secure inter-agent communication
- ✅ **Data Minimization**: Only processes necessary data with explicit consent

### Core Philosophy
- **Intelligence First**: Advanced AI-powered content categorization and automation
- **Privacy-Preserving**: Your data never leaves your control
- **Consent-Based**: Explicit permission required for all processing
- **Multi-LLM Integration**: Flexible AI processing with multiple providers
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
- **🧠 Smart Content Classification**: AI-powered email and calendar categorization
- **🔄 Intelligent Automation**: Automated priority detection and sentiment analysis
- **📊 Advanced Analytics**: Scheduling intelligence and productivity insights
- **🛡️ Consent Management**: Demonstrate instant data deletion and consent revocation
- **🤖 Multi-LLM Support**: Show Ollama, OpenAI, Groq, and Hugging Face integration
- **⚡ Real-Time Processing**: Background processing with live status updates
- **📈 Unified Dashboard**: Combined email/calendar categorization view with insights

### Key Demo Points
🧠 **AI-Powered Intelligence**: Demonstrate advanced content classification across multiple LLMs  
🔄 **Smart Automation**: Show automated priority detection, sentiment analysis, and scheduling optimization  
📊 **Real-Time Dashboard**: Live processing status with comprehensive category analytics  
🛡️ **Privacy Controls**: One-click data deletion and granular consent management  
� **Security**: Encrypted vault storage with complete audit trails  
⚡ **Performance**: Efficient background processing with detailed progress tracking

## 🚀 Complete Setup Guide

### Prerequisites
- **Python 3.8+**
- **Google OAuth credentials** (optional, for real Gmail/Calendar integration)
- **Ollama** (optional, for local AI processing)



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

### 🛡️ Hushh MCP Protocol Implementation
This project demonstrates **complete compliance** with the Hushh Model Context Protocol:

#### ✅ Core MCP Components
- **Agent Framework**: Modular processing agents with clear responsibilities
- **Consent Management**: Granular permission system with instant revocation
- **Vault Storage**: AES-256 encrypted data storage with user-controlled keys
- **Operons**: Specialized content processing functions
- **Trust Links**: Secure inter-agent communication protocols
- **Audit Trails**: Comprehensive activity tracking for compliance

#### 🤖 Active MCP Agents
1. **EmailProcessorAgent** (`agent_email_processor`)
   - **Purpose**: AI-powered email categorization and intelligent content analysis
   - **Scope**: `VAULT_READ_EMAIL`
   - **Features**: Multi-LLM categorization, priority detection, sentiment analysis, automation suggestions
   - **Compliance**: Full consent validation, data revocation, comprehensive audit logging

2. **CalendarProcessorAgent** (`agent_calendar_processor`)  
   - **Purpose**: Smart calendar event processing and scheduling intelligence
   - **Scope**: `VAULT_READ_CALENDAR`
   - **Features**: Event categorization, productivity insights, scheduling optimization, pattern analysis
   - **Compliance**: Secure data access, consent-based processing, detailed audit trails

3. **AuditLoggerAgent** (`agent_audit_logger`)
   - **Purpose**: Privacy compliance tracking and transparency reporting
   - **Scope**: System-wide audit logging and compliance monitoring
   - **Features**: Consent tracking, processing activity logs, privacy audit reports, transparency dashboard
   - **Compliance**: Immutable logs, user data isolation, comprehensive activity tracking

### 🔧 System Architecture

#### Backend Core (`main.py`)
- **FastAPI REST API** with 15+ endpoints
- **Google OAuth 2.0** integration for secure authentication
- **JWT Token Management** with proper expiration handling
- **Background Task Processing** with real-time progress tracking
- **Comprehensive Error Handling** and detailed logging
- **Multi-LLM Integration** (Ollama, OpenAI, Groq, Hugging Face)

#### Frontend Dashboard (`frontend/`)
- **Responsive Web Interface** with modern CSS3/HTML5
- **Real-Time Processing Updates** via async API calls
- **Interactive Category Management** with drill-down capabilities
- **Privacy Control Panel** for consent and data management
- **Live Status Monitoring** with progress indicators

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

## 🧪 Testing & Verification

### 🎯 Comprehensive Test Coverage
Our project includes **65+ automated tests** ensuring Hushh MCP protocol compliance:

#### Agent Test Suites (`tests/`)
- **`test_email_processor_agent.py`**: 15+ tests for email processing compliance
- **`test_calendar_processor_agent.py`**: 20+ tests for calendar agent functionality  
- **`test_audit_logger_agent.py`**: 15+ tests for audit logging compliance
- **`test_schedule_event_operon.py`**: Tests for event creation operon
- **`test_token.py`**: Consent token validation and security tests
- **`test_vault.py`**: Encrypted storage and data protection tests
- **`test_trust.py`**: Inter-agent communication security tests

#### Test Categories
🔐 **Privacy & Consent Tests**
- Consent token validation and expiration
- Data revocation and complete deletion
- User data isolation and access controls
- Privacy assessment and data sensitivity

🤖 **AI Processing Tests**  
- Multi-LLM categorization accuracy
- Confidence scoring validation
- Fallback mechanism testing
- Content analysis verification

⚡ **Performance & Reliability Tests**
- Concurrent processing safety
- High-volume data handling
- Error recovery and resilience
- Background task management

🛡️ **Security & Compliance Tests**
- Audit trail integrity and immutability
- Encryption/decryption verification
- Authentication and authorization
- GDPR compliance validation

### Running Tests
```bash
# Run all tests with detailed output
pytest tests/ -v

# Run specific agent tests
pytest tests/test_email_processor_agent.py -v
pytest tests/test_calendar_processor_agent.py -v  
pytest tests/test_audit_logger_agent.py -v

# Run Hushh MCP compliance tests
pytest tests/ -k "hushh_protocol" -v

# Run privacy and consent tests
pytest tests/ -k "consent" -v
```

### Test Results Summary
- ✅ **Agent Framework**: All agents pass MCP compliance tests
- ✅ **Consent Management**: Granular permissions with instant revocation
- ✅ **Data Privacy**: Encrypted storage with user-controlled deletion  
- ✅ **AI Processing**: Multi-LLM integration with confidence scoring
- ✅ **Security**: Audit trails and access control validation
- ✅ **Performance**: Concurrent processing and error handling

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

## 🔮 Smart Categorization & Automation Features

### 🧠 AI-Powered Content Intelligence
- **Multi-LLM Classification**: Advanced categorization using Ollama, OpenAI, Groq, Hugging Face
- **Confidence Scoring**: AI confidence levels for each categorization decision
- **Context Understanding**: Deep content analysis beyond keyword matching
- **Adaptive Learning**: Improving accuracy through processing patterns
- **Fallback Mechanisms**: Rule-based classification when AI models unavailable

### 🔄 Intelligent Automation
- **Priority Detection**: Automatic importance and urgency classification
- **Sentiment Analysis**: Emotional tone detection in emails and events
- **Pattern Recognition**: Trend analysis across time periods and content types
- **Smart Suggestions**: Automated recommendations based on content analysis
- **Workflow Optimization**: Intelligent process improvements and efficiency gains

### 📊 Advanced Analytics & Insights  
- **Scheduling Intelligence**: Meeting optimization and calendar conflict detection
- **Productivity Analysis**: Comprehensive insights into time usage patterns
- **Content Metrics**: Detailed statistics on categorized data and trends
- **Processing Performance**: Real-time analytics on AI classification accuracy
- **User Behavior Insights**: Understanding of personal productivity patterns

### 🛡️ Privacy-First Security
- **Encrypted Vault Storage**: AES-256 encryption for all processed data
- **Granular Consent Management**: Fine-grained permissions for each data type
- **Complete Audit Trails**: Full transparency in all processing activities
- **Data Portability**: Export all categorized data in standard formats
- **Instant Data Deletion**: One-click removal of all user data and processing history

---

**🤖 Experience the future of intelligent data categorization with complete privacy control!**

For detailed technical documentation, troubleshooting, and advanced configuration, see the `/docs` directory.
