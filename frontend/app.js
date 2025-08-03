// API Configuration
const API_BASE = 'http://localhost:8000';

// Application State
let authToken = null;
let userEmail = null;
let processingStates = {
    email: false,
    calendar: false
};

// Page Management
function showPage(pageId) {
    // Hide all pages
    document.querySelectorAll('.page').forEach(page => {
        page.classList.remove('active');
    });
    
    // Show target page
    const targetPage = document.getElementById(pageId);
    if (targetPage) {
        targetPage.classList.add('active');
        targetPage.classList.add('fade-in');
    }
}

// Authentication Functions
function handleGoogleSignIn() {
    console.log('🔐 Starting Google OAuth...');
    
    // Show loading state on button
    const btn = document.getElementById('google-signin-btn');
    const originalText = btn.innerHTML;
    btn.innerHTML = '<i class="fas fa-spinner fa-spin"></i> Connecting...';
    btn.disabled = true;
    
    // Redirect to OAuth endpoint
    window.location.href = `${API_BASE}/auth/google/redirect`;
}

function handleAuthSuccess() {
    const urlParams = new URLSearchParams(window.location.search);
    const token = urlParams.get('token');
    const email = urlParams.get('email');
    
    if (token) {
        console.log('✅ Authentication successful!', { email });
        
        // Store auth data
        authToken = token;
        userEmail = email;
        localStorage.setItem('jwt_token', token);
        localStorage.setItem('user_email', email);
        
        // Show success page briefly
        showPage('auth-success-page');
        
        // Redirect to dashboard after 2 seconds
        setTimeout(() => {
            showPage('dashboard-page');
            initializeDashboard();
            
            // Clean URL
            window.history.replaceState({}, document.title, window.location.pathname);
        }, 2000);
        
        return true;
    }
    
    return false;
}

function handleLogout() {
    console.log('🚪 Logging out...');
    
    // Clear auth data
    authToken = null;
    userEmail = null;
    localStorage.removeItem('jwt_token');
    localStorage.removeItem('user_email');
    
    // Reset processing states
    processingStates = { email: false, calendar: false };
    
    // Show landing page
    showPage('landing-page');
}

function initializeDashboard() {
    // Set user email in dashboard
    const userEmailElement = document.getElementById('user-email');
    if (userEmailElement && userEmail) {
        userEmailElement.textContent = userEmail;
    }
    
    // Reset all progress indicators
    hideProgress('email');
    hideProgress('calendar');
    
    console.log('📊 Dashboard initialized for:', userEmail);
}

// API Request Helper
async function makeAuthenticatedRequest(endpoint, options = {}) {
    if (!authToken) {
        throw new Error('No authentication token available');
    }
    
    const config = {
        headers: {
            'Authorization': `Bearer ${authToken}`,
            'Content-Type': 'application/json',
            ...options.headers
        },
        ...options
    };
    
    const response = await fetch(`${API_BASE}${endpoint}`, config);
    
    if (!response.ok) {
        if (response.status === 401) {
            // Token expired or invalid
            handleLogout();
            throw new Error('Authentication expired. Please sign in again.');
        }
        throw new Error(`API request failed: ${response.status} ${response.statusText}`);
    }
    
    return response.json();
}

// Email Processing Functions
async function processEmails() {
    if (processingStates.email) {
        console.log('Email processing already in progress');
        return;
    }
    
    const days = parseInt(document.getElementById('email-days').value) || 30;
    console.log(`📧 Starting email processing for ${days} days...`);
    
    try {
        processingStates.email = true;
        
        // Update UI
        const btn = document.getElementById('process-emails-btn');
        btn.disabled = true;
        btn.innerHTML = '<i class="fas fa-spinner fa-spin"></i> Processing...';
        
        showProgress('email', 'Initializing email analysis...');
        
        // Start processing
        const result = await makeAuthenticatedRequest(`/api/emails/process/${days}`, {
            method: 'POST'
        });
        
        console.log('✅ Email processing completed:', result);
        
        // Simulate progress updates (since we have enhanced logging in backend)
        await simulateProgressUpdates('email', result);
        
        // Show results
        showResults('email', result);
        
    } catch (error) {
        console.error('❌ Email processing failed:', error);
        showError('email', error.message);
    } finally {
        processingStates.email = false;
        
        // Reset button
        const btn = document.getElementById('process-emails-btn');
        btn.disabled = false;
        btn.innerHTML = '<i class="fas fa-play"></i> Process Emails';
    }
}

// Calendar Processing Functions
async function processCalendar() {
    if (processingStates.calendar) {
        console.log('Calendar processing already in progress');
        return;
    }
    
    const daysBack = parseInt(document.getElementById('calendar-days-back').value) || 30;
    const daysForward = parseInt(document.getElementById('calendar-days-forward').value) || 30;
    
    console.log(`📅 Starting calendar processing (${daysBack} days back, ${daysForward} days forward)...`);
    
    try {
        processingStates.calendar = true;
        
        // Update UI
        const btn = document.getElementById('process-calendar-btn');
        btn.disabled = true;
        btn.innerHTML = '<i class="fas fa-spinner fa-spin"></i> Processing...';
        
        showProgress('calendar', 'Initializing calendar analysis...');
        
        // Start processing
        const result = await makeAuthenticatedRequest(`/api/calendar/process/${daysBack}/${daysForward}`, {
            method: 'POST'
        });
        
        console.log('✅ Calendar processing completed:', result);
        
        // Simulate progress updates
        await simulateProgressUpdates('calendar', result);
        
        // Show results
        showResults('calendar', result);
        
    } catch (error) {
        console.error('❌ Calendar processing failed:', error);
        showError('calendar', error.message);
    } finally {
        processingStates.calendar = false;
        
        // Reset button
        const btn = document.getElementById('process-calendar-btn');
        btn.disabled = false;
        btn.innerHTML = '<i class="fas fa-play"></i> Process Calendar';
    }
}

// Progress UI Functions
function showProgress(type, status) {
    const progressSection = document.getElementById(`${type}-progress`);
    const statusElement = document.getElementById(`${type}-status`);
    
    if (progressSection) {
        progressSection.style.display = 'block';
        progressSection.classList.add('slide-up');
    }
    
    if (statusElement && status) {
        statusElement.textContent = status;
    }
}

function updateProgress(type, percentage, status) {
    const progressFill = document.getElementById(`${type}-progress-fill`);
    const statusElement = document.getElementById(`${type}-status`);
    
    if (progressFill) {
        progressFill.style.width = `${percentage}%`;
    }
    
    if (statusElement && status) {
        statusElement.textContent = status;
    }
}

function hideProgress(type) {
    const progressSection = document.getElementById(`${type}-progress`);
    const resultsSection = document.getElementById(`${type}-results`);
    
    if (progressSection) {
        progressSection.style.display = 'none';
    }
    
    if (resultsSection) {
        resultsSection.style.display = 'none';
    }
}

async function simulateProgressUpdates(type, finalResult) {
    const steps = [
        { percent: 10, text: 'Connecting to data sources...' },
        { percent: 25, text: 'Fetching data...' },
        { percent: 40, text: 'Processing with AI...' },
        { percent: 60, text: 'Categorizing content...' },
        { percent: 80, text: 'Generating insights...' },
        { percent: 95, text: 'Finalizing results...' },
        { percent: 100, text: 'Complete!' }
    ];
    
    for (const step of steps) {
        updateProgress(type, step.percent, step.text);
        await sleep(800); // Wait 800ms between updates
    }
}

function showResults(type, result) {
    const resultsSection = document.getElementById(`${type}-results`);
    
    if (!resultsSection) return;
    
    // Create results HTML
    let resultsHTML = '<h4>✅ Processing Complete!</h4>';
    
    if (result.processed_count !== undefined) {
        resultsHTML += `<p><strong>Items processed:</strong> ${result.processed_count}</p>`;
    }
    
    if (result.categories && Object.keys(result.categories).length > 0) {
        resultsHTML += '<p><strong>Categories found:</strong></p>';
        resultsHTML += '<ul>';
        for (const [category, count] of Object.entries(result.categories)) {
            resultsHTML += `<li>${category}: ${count} items</li>`;
        }
        resultsHTML += '</ul>';
    }
    
    if (result.insights && result.insights.length > 0) {
        resultsHTML += '<p><strong>Key insights:</strong></p>';
        resultsHTML += '<ul>';
        result.insights.slice(0, 3).forEach(insight => {
            resultsHTML += `<li>${insight}</li>`;
        });
        resultsHTML += '</ul>';
    }
    
    if (result.summary) {
        resultsHTML += `<p><strong>Summary:</strong> ${result.summary}</p>`;
    }
    
    resultsSection.innerHTML = resultsHTML;
    resultsSection.style.display = 'block';
    resultsSection.classList.add('slide-up');
    
    // Update insights card
    updateInsightsCard(type, result);
}

function showError(type, message) {
    const resultsSection = document.getElementById(`${type}-results`);
    
    if (!resultsSection) return;
    
    resultsSection.innerHTML = `
        <h4>❌ Processing Failed</h4>
        <p style="color: #ff4757;"><strong>Error:</strong> ${message}</p>
        <p>Please try again or contact support if the issue persists.</p>
    `;
    resultsSection.style.display = 'block';
    resultsSection.classList.add('slide-up');
}

function updateInsightsCard(type, result) {
    const insightsContent = document.getElementById('insights-content');
    if (!insightsContent) return;
    
    const currentContent = insightsContent.innerHTML;
    let newInsight = '';
    
    if (type === 'email') {
        newInsight = `
            <div class="insight-item">
                <h4>📧 Email Insights</h4>
                <p>Processed ${result.processed_count || 0} emails with AI categorization</p>
                ${result.insights ? `<p><em>"${result.insights[0]}"</em></p>` : ''}
            </div>
        `;
    } else if (type === 'calendar') {
        newInsight = `
            <div class="insight-item">
                <h4>📅 Calendar Insights</h4>
                <p>Analyzed ${result.processed_count || 0} calendar events</p>
                ${result.insights ? `<p><em>"${result.insights[0]}"</em></p>` : ''}
            </div>
        `;
    }
    
    if (currentContent.includes('Run email or calendar analysis')) {
        insightsContent.innerHTML = newInsight;
    } else {
        insightsContent.innerHTML = currentContent + newInsight;
    }
}

// Utility Functions
function sleep(ms) {
    return new Promise(resolve => setTimeout(resolve, ms));
}

function checkAuthStatus() {
    const storedToken = localStorage.getItem('jwt_token');
    const storedEmail = localStorage.getItem('user_email');
    
    if (storedToken && storedEmail) {
        authToken = storedToken;
        userEmail = storedEmail;
        showPage('dashboard-page');
        initializeDashboard();
        return true;
    }
    
    return false;
}

// Event Listeners
document.addEventListener('DOMContentLoaded', function() {
    console.log('🚀 Hushh PDA Frontend loaded');
    
    // Check if user is returning from OAuth or already authenticated
    if (!handleAuthSuccess() && !checkAuthStatus()) {
        showPage('landing-page');
    }
    
    // Google Sign-in button
    const googleSignInBtn = document.getElementById('google-signin-btn');
    if (googleSignInBtn) {
        googleSignInBtn.addEventListener('click', handleGoogleSignIn);
    }
    
    // Logout button
    const logoutBtn = document.getElementById('logout-btn');
    if (logoutBtn) {
        logoutBtn.addEventListener('click', handleLogout);
    }
    
    // Process buttons
    const processEmailsBtn = document.getElementById('process-emails-btn');
    if (processEmailsBtn) {
        processEmailsBtn.addEventListener('click', processEmails);
    }
    
    const processCalendarBtn = document.getElementById('process-calendar-btn');
    if (processCalendarBtn) {
        processCalendarBtn.addEventListener('click', processCalendar);
    }
    
    // Input validation
    const numberInputs = document.querySelectorAll('input[type="number"]');
    numberInputs.forEach(input => {
        input.addEventListener('input', function() {
            if (this.value < 1) this.value = 1;
            if (this.value > 365) this.value = 365;
        });
    });
});

// Error handling for unhandled promise rejections
window.addEventListener('unhandledrejection', function(event) {
    console.error('Unhandled promise rejection:', event.reason);
    
    // Show user-friendly error
    const errorMessage = event.reason?.message || 'An unexpected error occurred';
    
    // Find any visible progress sections and show error
    ['email', 'calendar'].forEach(type => {
        const progressSection = document.getElementById(`${type}-progress`);
        if (progressSection && progressSection.style.display !== 'none') {
            showError(type, errorMessage);
        }
    });
});

console.log('✨ Hushh PDA Frontend ready!');
