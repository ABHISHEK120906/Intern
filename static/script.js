// ===== Global Variables =====
let currentUser = null;
let authToken = null;
let isDarkMode = false;

// ===== API Configuration =====
const API_BASE_URL = 'http://localhost:5000';

// ===== Initialize Application =====
document.addEventListener('DOMContentLoaded', function() {
    initializeApp();
    setupEventListeners();
    setupScrollAnimations();
    setupProgressBar();
    checkAuthStatus();
});

function initializeApp() {
    // Check for saved theme preference
    const savedTheme = localStorage.getItem('theme');
    if (savedTheme === 'dark') {
        document.documentElement.setAttribute('data-theme', 'dark');
        isDarkMode = true;
        updateThemeIcon();
    }
    
    // Initialize counters
    animateCounters();
    
    // Initialize charts
    initializeCharts();
}

// ===== Event Listeners =====
function setupEventListeners() {
    // Navigation
    document.querySelectorAll('.nav-link').forEach(link => {
        link.addEventListener('click', function(e) {
            e.preventDefault();
            const target = this.getAttribute('href').substring(1);
            scrollToSection(target);
        });
    });
    
    // Auth form
    document.getElementById('authForm').addEventListener('submit', handleAuth);
    
    // Profile form
    document.getElementById('profileForm').addEventListener('submit', handleProfileUpdate);
    
    // File upload
    const uploadArea = document.getElementById('uploadArea');
    const resumeInput = document.getElementById('resumeInput');
    
    uploadArea.addEventListener('click', () => resumeInput.click());
    uploadArea.addEventListener('dragover', handleDragOver);
    uploadArea.addEventListener('drop', handleFileDrop);
    resumeInput.addEventListener('change', handleFileSelect);
    
    // Search functionality
    document.getElementById('internshipSearch')?.addEventListener('input', handleInternshipSearch);
    
    // Window scroll
    window.addEventListener('scroll', handleScroll);
}

// ===== Theme Toggle =====
function toggleTheme() {
    isDarkMode = !isDarkMode;
    const theme = isDarkMode ? 'dark' : 'light';
    document.documentElement.setAttribute('data-theme', theme);
    localStorage.setItem('theme', theme);
    updateThemeIcon();
}

function updateThemeIcon() {
    const icon = document.getElementById('themeIcon');
    icon.className = isDarkMode ? 'fas fa-sun' : 'fas fa-moon';
}

// ===== Navigation =====
function toggleNav() {
    const navMenu = document.getElementById('navMenu');
    navMenu.classList.toggle('active');
}

function scrollToSection(sectionId) {
    const section = document.getElementById(sectionId);
    if (section) {
        section.scrollIntoView({ behavior: 'smooth' });
    }
}

// ===== Scroll Progress Bar =====
function setupProgressBar() {
    window.addEventListener('scroll', () => {
        const scrollTop = window.scrollY;
        const docHeight = document.documentElement.scrollHeight - window.innerHeight;
        const scrollPercent = (scrollTop / docHeight) * 100;
        document.getElementById('scrollProgress').style.width = scrollPercent + '%';
    });
}

// ===== Scroll Animations =====
function setupScrollAnimations() {
    const observerOptions = {
        threshold: 0.1,
        rootMargin: '0px 0px -50px 0px'
    };
    
    const observer = new IntersectionObserver((entries) => {
        entries.forEach(entry => {
            if (entry.isIntersecting) {
                entry.target.classList.add('active');
            }
        });
    }, observerOptions);
    
    document.querySelectorAll('.scroll-animate').forEach(el => {
        observer.observe(el);
    });
}

// ===== Counter Animation =====
function animateCounters() {
    const counters = document.querySelectorAll('.stat-number');
    
    counters.forEach(counter => {
        const target = parseInt(counter.getAttribute('data-target'));
        const increment = target / 100;
        let current = 0;
        
        const updateCounter = () => {
            current += increment;
            if (current < target) {
                counter.textContent = Math.ceil(current);
                requestAnimationFrame(updateCounter);
            } else {
                counter.textContent = target;
            }
        };
        
        // Start animation when element is in view
        const observer = new IntersectionObserver((entries) => {
            entries.forEach(entry => {
                if (entry.isIntersecting) {
                    updateCounter();
                    observer.unobserve(entry.target);
                }
            });
        });
        
        observer.observe(counter);
    });
}

// ===== Authentication =====
function showAuthModal(mode = 'login') {
    const modal = document.getElementById('authModal');
    const title = document.getElementById('authTitle');
    const submitBtn = document.getElementById('authSubmitBtn');
    const nameGroup = document.getElementById('nameGroup');
    const roleGroup = document.getElementById('roleGroup');
    const switchText = document.getElementById('authSwitchText');
    const switchBtn = document.getElementById('authSwitchBtn');
    
    if (mode === 'register') {
        title.textContent = 'Register';
        submitBtn.textContent = 'Register';
        nameGroup.style.display = 'block';
        roleGroup.style.display = 'block';
        switchText.textContent = 'Already have an account?';
        switchBtn.textContent = 'Login';
    } else {
        title.textContent = 'Login';
        submitBtn.textContent = 'Login';
        nameGroup.style.display = 'none';
        roleGroup.style.display = 'none';
        switchText.textContent = "Don't have an account?";
        switchBtn.textContent = 'Register';
    }
    
    modal.classList.add('active');
}

function closeAuthModal() {
    document.getElementById('authModal').classList.remove('active');
    document.getElementById('authForm').reset();
}

function switchAuthMode() {
    const isLogin = document.getElementById('authTitle').textContent === 'Login';
    showAuthModal(isLogin ? 'register' : 'login');
}

async function handleAuth(e) {
    e.preventDefault();
    
    const email = document.getElementById('authEmail').value;
    const password = document.getElementById('authPassword').value;
    const name = document.getElementById('authName').value;
    const role = document.getElementById('authRole').value;
    
    const isLogin = document.getElementById('authTitle').textContent === 'Login';
    
    showLoading();
    
    try {
        const endpoint = isLogin ? '/auth/login' : '/auth/register';
        const payload = isLogin ? 
            { email, password } : 
            { name, email, password, role, profile: {} };
        
        const response = await fetch(`${API_BASE_URL}${endpoint}`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify(payload)
        });
        
        const data = await response.json();
        
        if (response.ok) {
            if (isLogin) {
                authToken = data.access_token;
                currentUser = data.user;
                localStorage.setItem('authToken', authToken);
                localStorage.setItem('currentUser', JSON.stringify(currentUser));
                
                closeAuthModal();
                showDashboard();
                updateUIForAuthenticatedUser();
            } else {
                showNotification('Registration successful! Please login.', 'success');
                switchAuthMode();
            }
        } else {
            showNotification(data.error || 'Authentication failed', 'error');
        }
    } catch (error) {
        showNotification('Network error. Please try again.', 'error');
    } finally {
        hideLoading();
    }
}

function checkAuthStatus() {
    const savedToken = localStorage.getItem('authToken');
    const savedUser = localStorage.getItem('currentUser');
    
    if (savedToken && savedUser) {
        authToken = savedToken;
        currentUser = JSON.parse(savedUser);
        showDashboard();
        updateUIForAuthenticatedUser();
    }
}

function updateUIForAuthenticatedUser() {
    if (currentUser) {
        document.getElementById('userName').textContent = currentUser.name;
        document.getElementById('userRole').textContent = currentUser.role.charAt(0).toUpperCase() + currentUser.role.slice(1);
        
        // Update nav button
        const navBtn = document.querySelector('.nav-btn');
        navBtn.innerHTML = `<i class="fas fa-sign-out-alt"></i> Logout`;
        navBtn.onclick = logout;
        
        // Load dashboard data
        loadDashboardData();
    }
}

function logout() {
    authToken = null;
    currentUser = null;
    localStorage.removeItem('authToken');
    localStorage.removeItem('currentUser');
    
    // Hide dashboard
    document.getElementById('dashboard').style.display = 'none';
    document.querySelector('.hero').style.display = 'flex';
    
    // Update nav button
    const navBtn = document.querySelector('.nav-btn');
    navBtn.innerHTML = `<i class="fas fa-user"></i> Login`;
    navBtn.onclick = () => showAuthModal('login');
    
    // Scroll to top
    window.scrollTo({ top: 0, behavior: 'smooth' });
}

// ===== Dashboard Functions =====
function showDashboard() {
    document.querySelector('.hero').style.display = 'none';
    document.getElementById('dashboard').style.display = 'block';
}

function showDashboardSection(section) {
    // Hide all sections
    document.querySelectorAll('.content-section').forEach(sec => {
        sec.style.display = 'none';
    });
    
    // Show selected section
    document.getElementById(`${section}-section`).style.display = 'block';
    
    // Update nav items
    document.querySelectorAll('.nav-item').forEach(item => {
        item.classList.remove('active');
    });
    event.target.classList.add('active');
    
    // Load section-specific data
    switch(section) {
        case 'profile':
            loadProfileData();
            break;
        case 'internships':
            loadInternships();
            break;
        case 'applications':
            loadApplications();
            break;
        case 'notifications':
            loadNotifications();
            break;
        case 'security':
            loadSecurityFeatures();
            break;
        case 'enterprise-dashboard':
            loadEnterpriseDashboard();
            break;
        case 'student-dashboard-enhanced':
            loadStudentDashboardEnhanced();
            break;
    }
}

async function loadDashboardData() {
    if (!currentUser) return;
    
    try {
        // Load user stats
        const statsResponse = await fetch(`${API_BASE_URL}/analytics/dashboard`, {
            headers: {
                'Authorization': `Bearer ${authToken}`
            }
        });
        
        if (statsResponse.ok) {
            const stats = await statsResponse.json();
            updateDashboardStats(stats);
        }
        
        // Load readiness score
        const readinessResponse = await fetch(`${API_BASE_URL}/ai/placement-readiness-score`, {
            headers: {
                'Authorization': `Bearer ${authToken}`
            }
        });
        
        if (readinessResponse.ok) {
            const readiness = await readinessResponse.json();
            document.getElementById('readinessScore').textContent = readiness.total_score + '%';
        }
        
    } catch (error) {
        console.error('Error loading dashboard data:', error);
    }
}

function updateDashboardStats(stats) {
    document.getElementById('totalInternships').textContent = stats.overview.total_internships;
    document.getElementById('totalApplications').textContent = stats.overview.total_applications;
    document.getElementById('notifications').textContent = '0'; // Will be updated when notifications are loaded
}

// ===== Profile Management =====
async function loadProfileData() {
    if (!currentUser) return;
    
    try {
        const response = await fetch(`${API_BASE_URL}/auth/profile`, {
            headers: {
                'Authorization': `Bearer ${authToken}`
            }
        });
        
        if (response.ok) {
            const profile = await response.json();
            document.getElementById('profileName').value = profile.name;
            document.getElementById('profileEmail').value = profile.email;
            document.getElementById('profilePhone').value = profile.profile.phone || '';
            document.getElementById('profileBio').value = profile.profile.bio || '';
            document.getElementById('profileSkills').value = profile.profile.skills.join(', ') || '';
        }
    } catch (error) {
        console.error('Error loading profile:', error);
    }
}

async function handleProfileUpdate(e) {
    e.preventDefault();
    
    const name = document.getElementById('profileName').value;
    const phone = document.getElementById('profilePhone').value;
    const bio = document.getElementById('profileBio').value;
    const skills = document.getElementById('profileSkills').value.split(',').map(s => s.trim()).filter(s => s);
    
    showLoading();
    
    try {
        const response = await fetch(`${API_BASE_URL}/auth/profile`, {
            method: 'PUT',
            headers: {
                'Authorization': `Bearer ${authToken}`,
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                name,
                profile: {
                    phone,
                    bio,
                    skills,
                    education: [],
                    experience: []
                }
            })
        });
        
        if (response.ok) {
            showNotification('Profile updated successfully!', 'success');
            currentUser.name = name;
            localStorage.setItem('currentUser', JSON.stringify(currentUser));
            document.getElementById('userName').textContent = name;
        } else {
            const error = await response.json();
            showNotification(error.error || 'Update failed', 'error');
        }
    } catch (error) {
        showNotification('Network error. Please try again.', 'error');
    } finally {
        hideLoading();
    }
}

// ===== File Upload =====
function handleDragOver(e) {
    e.preventDefault();
    e.currentTarget.classList.add('dragover');
}

function handleFileDrop(e) {
    e.preventDefault();
    e.currentTarget.classList.remove('dragover');
    
    const files = e.dataTransfer.files;
    if (files.length > 0) {
        handleFileUpload(files[0]);
    }
}

function handleFileSelect(e) {
    const file = e.target.files[0];
    if (file) {
        handleFileUpload(file);
    }
}

async function handleFileUpload(file) {
    if (file.type !== 'application/pdf') {
        showNotification('Please upload a PDF file', 'error');
        return;
    }
    
    const formData = new FormData();
    formData.append('file', file);
    
    showLoading();
    
    try {
        const response = await fetch(`${API_BASE_URL}/upload/resume`, {
            method: 'POST',
            headers: {
                'Authorization': `Bearer ${authToken}`
            },
            body: formData
        });
        
        if (response.ok) {
            const result = await response.json();
            showNotification('Resume uploaded successfully!', 'success');
        } else {
            const error = await response.json();
            showNotification(error.error || 'Upload failed', 'error');
        }
    } catch (error) {
        showNotification('Network error. Please try again.', 'error');
    } finally {
        hideLoading();
    }
}

// ===== Resume Analysis =====
async function analyzeResume() {
    const resumeInput = document.getElementById('resumeInput');
    const file = resumeInput.files[0];
    
    if (!file) {
        showNotification('Please upload a resume first', 'error');
        return;
    }
    
    const formData = new FormData();
    formData.append('file', file);
    
    showLoading();
    
    try {
        const response = await fetch(`${API_BASE_URL}/ai/resume-analyze`, {
            method: 'POST',
            headers: {
                'Authorization': `Bearer ${authToken}`
            },
            body: formData
        });
        
        if (response.ok) {
            const analysis = await response.json();
            showResumeAnalysisResults(analysis.analysis);
        } else {
            const error = await response.json();
            showNotification(error.error || 'Analysis failed', 'error');
        }
    } catch (error) {
        showNotification('Network error. Please try again.', 'error');
    } finally {
        hideLoading();
    }
}

function showResumeAnalysisResults(analysis) {
    const modal = document.createElement('div');
    modal.className = 'modal active';
    modal.innerHTML = `
        <div class="modal-content glass-card">
            <div class="modal-header">
                <h3>Resume Analysis Results</h3>
                <button class="modal-close" onclick="this.closest('.modal').remove()">
                    <i class="fas fa-times"></i>
                </button>
            </div>
            <div class="modal-body">
                <div class="analysis-score">
                    <h4>Overall Score: ${analysis.score}/100</h4>
                    <div class="progress-bar" style="width: ${analysis.score}%"></div>
                </div>
                <div class="analysis-section">
                    <h4>Skills Found:</h4>
                    <div class="skills-list">
                        ${analysis.skills_found.map(skill => `<span class="skill-tag">${skill}</span>`).join('')}
                    </div>
                </div>
                <div class="analysis-section">
                    <h4>Suggestions:</h4>
                    <ul>
                        ${analysis.suggestions.map(suggestion => `<li>${suggestion}</li>`).join('')}
                    </ul>
                </div>
            </div>
        </div>
    `;
    document.body.appendChild(modal);
}

// ===== Internships =====
async function loadInternships() {
    if (!currentUser) return;
    
    showLoading();
    
    try {
        const response = await fetch(`${API_BASE_URL}/internships`, {
            headers: {
                'Authorization': `Bearer ${authToken}`
            }
        });
        
        if (response.ok) {
            const data = await response.json();
            displayInternships(data.internships);
        } else {
            const error = await response.json();
            showNotification(error.error || 'Failed to load internships', 'error');
        }
    } catch (error) {
        showNotification('Network error. Please try again.', 'error');
    } finally {
        hideLoading();
    }
}

function displayInternships(internships) {
    const grid = document.getElementById('internshipsGrid');
    
    if (internships.length === 0) {
        grid.innerHTML = '<p>No internships available at the moment.</p>';
        return;
    }
    
    grid.innerHTML = internships.map(internship => `
        <div class="internship-card glass-card">
            <h3>${internship.title}</h3>
            <div class="company">${internship.company_name}</div>
            <div class="location">
                <i class="fas fa-map-marker-alt"></i> ${internship.location}
            </div>
            <div class="duration">
                <i class="fas fa-clock"></i> ${internship.duration}
            </div>
            <div class="stipend">
                <i class="fas fa-money-bill"></i> ${internship.stipend}
            </div>
            <div class="skills">
                ${internship.skills_required.map(skill => `<span class="skill-tag">${skill}</span>`).join('')}
            </div>
            <div class="actions">
                <button class="btn btn-primary" onclick="applyToInternship('${internship._id}')">
                    Apply Now
                </button>
                <button class="btn btn-secondary" onclick="viewInternshipDetails('${internship._id}')">
                    View Details
                </button>
            </div>
        </div>
    `).join('');
}

async function applyToInternship(internshipId) {
    showLoading();
    
    try {
        const response = await fetch(`${API_BASE_URL}/applications`, {
            method: 'POST',
            headers: {
                'Authorization': `Bearer ${authToken}`,
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                internship_id: internshipId
            })
        });
        
        if (response.ok) {
            showNotification('Application submitted successfully!', 'success');
            loadApplications(); // Refresh applications list
        } else {
            const error = await response.json();
            showNotification(error.error || 'Application failed', 'error');
        }
    } catch (error) {
        showNotification('Network error. Please try again.', 'error');
    } finally {
        hideLoading();
    }
}

function handleInternshipSearch(e) {
    const searchTerm = e.target.value.toLowerCase();
    const cards = document.querySelectorAll('.internship-card');
    
    cards.forEach(card => {
        const text = card.textContent.toLowerCase();
        card.style.display = text.includes(searchTerm) ? 'block' : 'none';
    });
}

// ===== Applications =====
async function loadApplications() {
    if (!currentUser) return;
    
    showLoading();
    
    try {
        const response = await fetch(`${API_BASE_URL}/applications`, {
            headers: {
                'Authorization': `Bearer ${authToken}`
            }
        });
        
        if (response.ok) {
            const data = await response.json();
            displayApplications(data.applications);
        } else {
            const error = await response.json();
            showNotification(error.error || 'Failed to load applications', 'error');
        }
    } catch (error) {
        showNotification('Network error. Please try again.', 'error');
    } finally {
        hideLoading();
    }
}

function displayApplications(applications) {
    const list = document.getElementById('applicationsList');
    
    if (applications.length === 0) {
        list.innerHTML = '<p>No applications yet. Start applying to internships!</p>';
        return;
    }
    
    list.innerHTML = applications.map(app => `
        <div class="application-card glass-card">
            <div class="application-info">
                <h3>${app.internship_id || 'Internship Application'}</h3>
                <div class="company">Applied on: ${app.applied_date}</div>
                <div class="status-badge status-${app.status}">${app.status}</div>
            </div>
        </div>
    `).join('');
}

// ===== AI Tools =====
async function getJobRecommendations() {
    showLoading();
    
    try {
        const response = await fetch(`${API_BASE_URL}/ai/job-recommendations`, {
            headers: {
                'Authorization': `Bearer ${authToken}`
            }
        });
        
        if (response.ok) {
            const data = await response.json();
            showJobRecommendations(data.recommendations);
        } else {
            const error = await response.json();
            showNotification(error.error || 'Failed to get recommendations', 'error');
        }
    } catch (error) {
        showNotification('Network error. Please try again.', 'error');
    } finally {
        hideLoading();
    }
}

function showJobRecommendations(recommendations) {
    const modal = document.createElement('div');
    modal.className = 'modal active';
    modal.innerHTML = `
        <div class="modal-content glass-card" style="max-width: 800px;">
            <div class="modal-header">
                <h3>Job Recommendations</h3>
                <button class="modal-close" onclick="this.closest('.modal').remove()">
                    <i class="fas fa-times"></i>
                </button>
            </div>
            <div class="modal-body">
                ${recommendations.length === 0 ? 
                    '<p>No recommendations available. Update your profile to get better recommendations.</p>' :
                    recommendations.map(job => `
                        <div class="recommendation-card glass-card" style="margin-bottom: 1rem;">
                            <h4>${job.title} - ${job.company_name}</h4>
                            <div class="match-percentage">Match: ${job.match_percentage}%</div>
                            <div class="skills">
                                <strong>Matching skills:</strong> ${job.matching_skills.join(', ')}
                            </div>
                            <div class="missing-skills">
                                <strong>Missing skills:</strong> ${job.missing_skills.join(', ') || 'None'}
                            </div>
                        </div>
                    `).join('')
                }
            </div>
        </div>
    `;
    document.body.appendChild(modal);
}

function showSkillGapModal() {
    const modal = document.createElement('div');
    modal.className = 'modal active';
    modal.innerHTML = `
        <div class="modal-content glass-card">
            <div class="modal-header">
                <h3>Skill Gap Analysis</h3>
                <button class="modal-close" onclick="this.closest('.modal').remove()">
                    <i class="fas fa-times"></i>
                </button>
            </div>
            <div class="modal-body">
                <form id="skillGapForm">
                    <div class="form-group">
                        <label>Target Job Skills (comma separated)</label>
                        <input type="text" id="targetSkills" class="form-input" 
                               placeholder="Python, JavaScript, React, SQL" required>
                    </div>
                    <button type="submit" class="btn btn-primary">Analyze Skills</button>
                </form>
            </div>
        </div>
    `;
    document.body.appendChild(modal);
    
    document.getElementById('skillGapForm').addEventListener('submit', handleSkillGapAnalysis);
}

async function handleSkillGapAnalysis(e) {
    e.preventDefault();
    
    const targetSkills = document.getElementById('targetSkills').value
        .split(',')
        .map(s => s.trim())
        .filter(s => s);
    
    showLoading();
    
    try {
        const response = await fetch(`${API_BASE_URL}/ai/skill-gap-analysis`, {
            method: 'POST',
            headers: {
                'Authorization': `Bearer ${authToken}`,
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                target_job_skills: targetSkills
            })
        });
        
        if (response.ok) {
            const data = await response.json();
            showSkillGapResults(data.analysis);
        } else {
            const error = await response.json();
            showNotification(error.error || 'Analysis failed', 'error');
        }
    } catch (error) {
        showNotification('Network error. Please try again.', 'error');
    } finally {
        hideLoading();
    }
}

function showSkillGapResults(analysis) {
    const modal = document.createElement('div');
    modal.className = 'modal active';
    modal.innerHTML = `
        <div class="modal-content glass-card" style="max-width: 800px;">
            <div class="modal-header">
                <h3>Skill Gap Analysis Results</h3>
                <button class="modal-close" onclick="this.closest('.modal').remove()">
                    <i class="fas fa-times"></i>
                </button>
            </div>
            <div class="modal-body">
                <div class="readiness-score">
                    <h4>Readiness: ${analysis.readiness_percentage}%</h4>
                    <div class="progress-bar" style="width: ${analysis.readiness_percentage}%"></div>
                </div>
                <div class="analysis-section">
                    <h4>Current Skills:</h4>
                    <div class="skills-list">
                        ${analysis.existing_skills.map(skill => `<span class="skill-tag">${skill}</span>`).join('')}
                    </div>
                </div>
                <div class="analysis-section">
                    <h4>Missing Skills:</h4>
                    <div class="skills-list">
                        ${analysis.missing_skills.map(skill => `<span class="skill-tag" style="background: var(--error-color); color: white;">${skill}</span>`).join('')}
                    </div>
                </div>
                <div class="analysis-section">
                    <h4>Learning Recommendations:</h4>
                    ${analysis.learning_recommendations.map(rec => `
                        <div class="learning-rec">
                            <strong>${rec.skill} (${rec.priority}):</strong>
                            <ul>
                                ${rec.resources.map(resource => `<li>${resource}</li>`).join('')}
                            </ul>
                        </div>
                    `).join('')}
                </div>
                <div class="estimated-time">
                    <strong>Estimated Learning Time:</strong> ${analysis.estimated_learning_time}
                </div>
            </div>
        </div>
    `;
    document.body.appendChild(modal);
}

async function updateReadinessScore() {
    showLoading();
    
    try {
        const response = await fetch(`${API_BASE_URL}/ai/placement-readiness-score`, {
            headers: {
                'Authorization': `Bearer ${authToken}`
            }
        });
        
        if (response.ok) {
            const data = await response.json();
            showReadinessScoreResults(data);
        } else {
            const error = await response.json();
            showNotification(error.error || 'Failed to get readiness score', 'error');
        }
    } catch (error) {
        showNotification('Network error. Please try again.', 'error');
    } finally {
        hideLoading();
    }
}

function showReadinessScoreResults(data) {
    const modal = document.createElement('div');
    modal.className = 'modal active';
    modal.innerHTML = `
        <div class="modal-content glass-card">
            <div class="modal-header">
                <h3>Placement Readiness Score</h3>
                <button class="modal-close" onclick="this.closest('.modal').remove()">
                    <i class="fas fa-times"></i>
                </button>
            </div>
            <div class="modal-body">
                <div class="readiness-score">
                    <h4 style="color: ${data.color}">${data.readiness_level}: ${data.total_score}/100</h4>
                    <div class="progress-bar" style="width: ${data.total_score}%; background: ${data.color};"></div>
                </div>
                <div class="score-components">
                    <h4>Score Breakdown:</h4>
                    <div class="component">
                        <span>Skills:</span>
                        <div class="progress-bar" style="width: ${data.components.skills}%"></div>
                        <span>${data.components.skills}%</span>
                    </div>
                    <div class="component">
                        <span>Applications:</span>
                        <div class="progress-bar" style="width: ${data.components.applications}%"></div>
                        <span>${data.components.applications}%</span>
                    </div>
                    <div class="component">
                        <span>Profile:</span>
                        <div class="progress-bar" style="width: ${data.components.profile}%"></div>
                        <span>${data.components.profile}%</span>
                    </div>
                    <div class="component">
                        <span>Resume:</span>
                        <div class="progress-bar" style="width: ${data.components.resume}%"></div>
                        <span>${data.components.resume}%</span>
                    </div>
                </div>
                <div class="suggestions">
                    <h4>Improvement Suggestions:</h4>
                    <ul>
                        ${data.suggestions.map(suggestion => `<li>${suggestion}</li>`).join('')}
                    </ul>
                </div>
                <div class="next-milestone">
                    <strong>Next Milestone:</strong> ${data.next_milestone}
                </div>
            </div>
        </div>
    `;
    document.body.appendChild(modal);
}

// ===== Notifications =====
async function loadNotifications() {
    if (!currentUser) return;
    
    showLoading();
    
    try {
        const response = await fetch(`${API_BASE_URL}/notifications`, {
            headers: {
                'Authorization': `Bearer ${authToken}`
            }
        });
        
        if (response.ok) {
            const data = await response.json();
            displayNotifications(data.notifications);
        } else {
            const error = await response.json();
            showNotification(error.error || 'Failed to load notifications', 'error');
        }
    } catch (error) {
        showNotification('Network error. Please try again.', 'error');
    } finally {
        hideLoading();
    }
}

function displayNotifications(notifications) {
    const list = document.getElementById('notificationsList');
    
    if (notifications.length === 0) {
        list.innerHTML = '<p>No notifications yet.</p>';
        return;
    }
    
    list.innerHTML = notifications.map(notification => `
        <div class="notification-card glass-card">
            <div class="notification-icon">
                <i class="fas fa-${getNotificationIcon(notification.type)}"></i>
            </div>
            <div class="notification-content">
                <h4>${notification.title}</h4>
                <p>${notification.message}</p>
                <div class="notification-time">${notification.created_date}</div>
            </div>
        </div>
    `).join('');
}

function getNotificationIcon(type) {
    const icons = {
        'info': 'info-circle',
        'success': 'check-circle',
        'warning': 'exclamation-triangle',
        'error': 'times-circle'
    };
    return icons[type] || 'info-circle';
}

// ===== Utility Functions =====
function showLoading() {
    document.getElementById('loadingOverlay').classList.add('active');
}

function hideLoading() {
    document.getElementById('loadingOverlay').classList.remove('active');
}

function showNotification(message, type = 'info') {
    const notification = document.createElement('div');
    notification.className = `notification ${type}`;
    notification.innerHTML = `
        <i class="fas fa-${getNotificationIcon(type)}"></i>
        <span>${message}</span>
        <button onclick="this.parentElement.remove()">
            <i class="fas fa-times"></i>
        </button>
    `;
    
    // Add styles for notification
    notification.style.cssText = `
        position: fixed;
        top: 20px;
        right: 20px;
        background: ${type === 'error' ? 'var(--error-color)' : type === 'success' ? 'var(--success-color)' : 'var(--primary-color)'};
        color: white;
        padding: 1rem 1.5rem;
        border-radius: 8px;
        display: flex;
        align-items: center;
        gap: 0.75rem;
        z-index: 4000;
        box-shadow: var(--shadow-lg);
        animation: slideInRight 0.3s ease-out;
    `;
    
    document.body.appendChild(notification);
    
    // Auto remove after 5 seconds
    setTimeout(() => {
        notification.remove();
    }, 5000);
}

function handleScroll() {
    const navbar = document.querySelector('.navbar');
    if (window.scrollY > 100) {
        navbar.style.background = isDarkMode ? 
            'rgba(15, 23, 42, 0.95)' : 
            'rgba(255, 255, 255, 0.95)';
    } else {
        navbar.style.background = isDarkMode ? 
            'rgba(15, 23, 42, 0.8)' : 
            'rgba(255, 255, 255, 0.8)';
    }
}

function refreshDashboard() {
    loadDashboardData();
    showNotification('Dashboard refreshed!', 'success');
}

// ===== Charts =====
function initializeCharts() {
    // Application Status Chart
    const appCtx = document.getElementById('applicationChart');
    if (appCtx) {
        new Chart(appCtx, {
            type: 'doughnut',
            data: {
                labels: ['Pending', 'Shortlisted', 'Selected', 'Rejected'],
                datasets: [{
                    data: [0, 0, 0, 0],
                    backgroundColor: [
                        '#f59e0b',
                        '#3b82f6',
                        '#10b981',
                        '#ef4444'
                    ]
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                plugins: {
                    legend: {
                        position: 'bottom'
                    }
                }
            }
        });
    }
    
    // Skills Overview Chart
    const skillsCtx = document.getElementById('skillsChart');
    if (skillsCtx) {
        new Chart(skillsCtx, {
            type: 'bar',
            data: {
                labels: ['Technical', 'Communication', 'Leadership', 'Problem Solving'],
                datasets: [{
                    label: 'Skill Level',
                    data: [0, 0, 0, 0],
                    backgroundColor: 'rgba(102, 126, 234, 0.5)',
                    borderColor: 'rgba(102, 126, 234, 1)',
                    borderWidth: 1
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                scales: {
                    y: {
                        beginAtZero: true,
                        max: 100
                    }
                }
            }
        });
    }
}

// ===== Cybersecurity Functions =====
async function loadSecurityFeatures() {
    if (!currentUser) return;
    
    showLoading();
    
    try {
        // Load security labs
        await loadSecurityLabs();
        
        // Load security challenges
        await loadSecurityChallenges();
        
        // Load Kali tools
        await loadKaliTools();
        
        // Load certifications
        await loadSecurityCertifications();
        
        // Load threat intelligence (admin only)
        if (currentUser.role === 'admin') {
            await loadThreatIntelligence();
        }
        
    } catch (error) {
        showNotification('Error loading security features', 'error');
    } finally {
        hideLoading();
    }
}

async function loadSecurityLabs() {
    try {
        const response = await fetch(`${API_BASE_URL}/security/labs`, {
            headers: { 'Authorization': `Bearer ${authToken}` }
        });
        
        if (response.ok) {
            const data = await response.json();
            displaySecurityLabs(data.labs);
        }
    } catch (error) {
        console.error('Error loading security labs:', error);
    }
}

function displaySecurityLabs(labs) {
    const container = document.getElementById('securityLabs');
    
    if (labs.length === 0) {
        container.innerHTML = '<p>No security labs available at the moment.</p>';
        return;
    }
    
    container.innerHTML = labs.map(lab => `
        <div class="lab-card glass-card">
            <div class="points">${lab.points || '0'} pts</div>
            <h4>${lab.title}</h4>
            <div class="difficulty difficulty-${lab.difficulty}">${lab.difficulty}</div>
            <p>${lab.description}</p>
            <div class="tools">
                ${lab.tools.map(tool => `<span class="tool-tag">${tool}</span>`).join('')}
            </div>
            <div class="lab-details">
                <div><strong>Duration:</strong> ${lab.duration}</div>
                <div><strong>Category:</strong> ${lab.category}</div>
            </div>
            <button class="btn btn-primary" onclick="startSecurityLab('${lab._id}')">
                <i class="fas fa-play"></i> Start Lab
            </button>
        </div>
    `).join('');
}

async function loadSecurityChallenges() {
    try {
        const response = await fetch(`${API_BASE_URL}/security/challenges`, {
            headers: { 'Authorization': `Bearer ${authToken}` }
        });
        
        if (response.ok) {
            const data = await response.json();
            displaySecurityChallenges(data.challenges);
        }
    } catch (error) {
        console.error('Error loading security challenges:', error);
    }
}

function displaySecurityChallenges(challenges) {
    const container = document.getElementById('securityChallenges');
    
    if (challenges.length === 0) {
        container.innerHTML = '<p>No security challenges available at the moment.</p>';
        return;
    }
    
    container.innerHTML = challenges.map(challenge => `
        <div class="challenge-card glass-card">
            <div class="points">${challenge.points} pts</div>
            <h4>${challenge.title}</h4>
            <div class="category">${challenge.category}</div>
            <p>${challenge.description}</p>
            <div class="challenge-details">
                <div><strong>Difficulty:</strong> Level ${challenge.difficulty_level}</div>
                <div><strong>Type:</strong> ${challenge.type}</div>
            </div>
            <button class="btn btn-primary" onclick="attemptChallenge('${challenge._id}')">
                <i class="fas fa-flag"></i> Attempt Challenge
            </button>
        </div>
    `).join('');
}

async function attemptChallenge(challengeId) {
    const modal = document.createElement('div');
    modal.className = 'modal active';
    modal.innerHTML = `
        <div class="modal-content glass-card">
            <div class="modal-header">
                <h3>Submit Challenge Solution</h3>
                <button class="modal-close" onclick="this.closest('.modal').remove()">
                    <i class="fas fa-times"></i>
                </button>
            </div>
            <div class="modal-body">
                <form id="challengeForm">
                    <div class="form-group">
                        <label>Your Solution</label>
                        <textarea id="challengeSolution" class="form-input" rows="4" 
                                  placeholder="Enter your solution or command here..." required></textarea>
                    </div>
                    <button type="submit" class="btn btn-primary">Submit Solution</button>
                </form>
            </div>
        </div>
    `;
    document.body.appendChild(modal);
    
    document.getElementById('challengeForm').addEventListener('submit', (e) => {
        e.preventDefault();
        submitChallengeSolution(challengeId);
    });
}

async function submitChallengeSolution(challengeId) {
    const solution = document.getElementById('challengeSolution').value;
    
    showLoading();
    
    try {
        const response = await fetch(`${API_BASE_URL}/security/challenges/${challengeId}/submit`, {
            method: 'POST',
            headers: {
                'Authorization': `Bearer ${authToken}`,
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({ solution })
        });
        
        const result = await response.json();
        
        if (response.ok) {
            showChallengeResult(result);
            // Reload challenges to update progress
            await loadSecurityChallenges();
        } else {
            showNotification(result.error || 'Submission failed', 'error');
        }
    } catch (error) {
        showNotification('Network error. Please try again.', 'error');
    } finally {
        hideLoading();
    }
}

function showChallengeResult(result) {
    const modal = document.createElement('div');
    modal.className = 'modal active';
    modal.innerHTML = `
        <div class="modal-content glass-card">
            <div class="modal-header">
                <h3>${result.is_correct ? '🎉 Challenge Completed!' : '❌ Try Again'}</h3>
                <button class="modal-close" onclick="this.closest('.modal').remove()">
                    <i class="fas fa-times"></i>
                </button>
            </div>
            <div class="modal-body">
                <div class="challenge-result">
                    <div class="result-status ${result.is_correct ? 'success' : 'error'}">
                        ${result.is_correct ? 'Correct Solution!' : 'Incorrect Solution'}
                    </div>
                    <div class="points-earned">
                        <strong>Points Earned:</strong> ${result.points_earned}
                    </div>
                    ${result.new_skills ? `
                        <div class="new-skills">
                            <strong>New Skills Earned:</strong>
                            <div class="skills-list">
                                ${result.new_skills.map(skill => `<span class="skill-tag">${skill}</span>`).join('')}
                            </div>
                        </div>
                    ` : ''}
                </div>
            </div>
        </div>
    `;
    document.body.appendChild(modal);
}

async function loadKaliTools() {
    try {
        const response = await fetch(`${API_BASE_URL}/security/kali-tools`, {
            headers: { 'Authorization': `Bearer ${authToken}` }
        });
        
        if (response.ok) {
            const data = await response.json();
            displayKaliTools(data);
        }
    } catch (error) {
        console.error('Error loading Kali tools:', error);
    }
}

function displayKaliTools(tools) {
    const container = document.getElementById('kaliTools');
    
    let html = '';
    for (const [category, toolList] of Object.entries(tools)) {
        html += `
            <div class="kali-tool-category">
                <h4><i class="fas fa-tools"></i> ${category.replace('_', ' ').toUpperCase()}</h4>
                <div class="kali-tool-list">
                    ${toolList.map(tool => `
                        <div class="kali-tool-item">
                            <div class="tool-info">
                                <div class="tool-name">${tool.name}</div>
                                <div class="tool-description">${tool.description}</div>
                            </div>
                        </div>
                    `).join('')}
                </div>
            </div>
        `;
    }
    
    container.innerHTML = html;
}

async function loadSecurityCertifications() {
    try {
        const response = await fetch(`${API_BASE_URL}/security/certifications`, {
            headers: { 'Authorization': `Bearer ${authToken}` }
        });
        
        if (response.ok) {
            const data = await response.json();
            displayCertifications(data);
        }
    } catch (error) {
        console.error('Error loading certifications:', error);
    }
}

function displayCertifications(data) {
    const tracker = document.getElementById('certTracker');
    const available = document.getElementById('availableCerts');
    
    // Display user certifications
    if (data.user_certifications && data.user_certifications.length > 0) {
        tracker.innerHTML = data.user_certifications.map(cert => `
            <div class="cert-item completed">
                <div class="cert-icon">
                    <i class="fas fa-certificate"></i>
                </div>
                <div class="cert-info">
                    <h5>${cert.name}</h5>
                    <p>${cert.provider} - ${cert.status}</p>
                </div>
            </div>
        `).join('');
    } else {
        tracker.innerHTML = '<p>No certifications earned yet. Start with Security+!</p>';
    }
    
    // Display available certifications
    available.innerHTML = data.available_certifications.map(cert => `
        <div class="cert-card glass-card">
            <h5>${cert.name}</h5>
            <div class="cert-provider">${cert.provider}</div>
            <div class="cert-details">
                <div class="cert-detail">
                    <i class="fas fa-signal"></i> ${cert.level}
                </div>
                <div class="cert-detail">
                    <i class="fas fa-clock"></i> ${cert.estimated_hours}h
                </div>
                <div class="cert-detail">
                    <i class="fas fa-barcode"></i> ${cert.exam_code}
                </div>
            </div>
            <div class="cert-domains">
                <h6>Domains:</h6>
                <div class="domain-list">
                    ${cert.domains.map(domain => `<span class="domain-tag">${domain}</span>`).join('')}
                </div>
            </div>
            <button class="btn btn-primary" onclick="startCertification('${cert.name}')">
                <i class="fas fa-graduation-cap"></i> Start Learning
            </button>
        </div>
    `).join('');
}

async function loadThreatIntelligence() {
    try {
        const response = await fetch(`${API_BASE_URL}/security/threat-intel`, {
            headers: { 'Authorization': `Bearer ${authToken}` }
        });
        
        if (response.ok) {
            const data = await response.json();
            displayThreatIntelligence(data);
            
            // Show threat intelligence section
            document.getElementById('threatIntelSection').style.display = 'block';
        }
    } catch (error) {
        console.error('Error loading threat intelligence:', error);
    }
}

function displayThreatIntelligence(data) {
    // Update metrics
    document.getElementById('activeThreats').textContent = data.security_metrics.active_threats;
    document.getElementById('securityScore').textContent = data.security_metrics.security_score + '%';
    
    // Display threats
    const threatList = document.getElementById('threatList');
    threatList.innerHTML = data.current_threats.map(threat => `
        <div class="threat-item glass-card">
            <h4>
                <i class="fas fa-exclamation-triangle"></i>
                ${threat.type}
                <span class="threat-severity severity-${threat.severity}">${threat.severity}</span>
            </h4>
            <p>${threat.description}</p>
            <div class="threat-meta">
                <span><i class="fas fa-laptop"></i> ${threat.affected_systems} systems</span>
                <span><i class="fas fa-calendar"></i> ${threat.first_seen}</span>
            </div>
        </div>
    `).join('');
}

async function runSecurityAssessment(type) {
    const modal = document.createElement('div');
    modal.className = 'modal active';
    modal.innerHTML = `
        <div class="modal-content glass-card">
            <div class="modal-header">
                <h3>Security Assessment</h3>
                <button class="modal-close" onclick="this.closest('.modal').remove()">
                    <i class="fas fa-times"></i>
                </button>
            </div>
            <div class="modal-body">
                <form id="assessmentForm">
                    <div class="form-group">
                        <label>Target URL (optional)</label>
                        <input type="url" id="targetUrl" class="form-input" 
                               placeholder="https://example.com">
                    </div>
                    <button type="submit" class="btn btn-primary">
                        <i class="fas fa-shield-alt"></i> Run Assessment
                    </button>
                </form>
            </div>
        </div>
    `;
    document.body.appendChild(modal);
    
    document.getElementById('assessmentForm').addEventListener('submit', (e) => {
        e.preventDefault();
        performAssessment(type);
    });
}

async function performAssessment(type) {
    const targetUrl = document.getElementById('targetUrl').value;
    
    showLoading();
    
    try {
        const response = await fetch(`${API_BASE_URL}/security/assessment`, {
            method: 'POST',
            headers: {
                'Authorization': `Bearer ${authToken}`,
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                type: type,
                target_url: targetUrl
            })
        });
        
        const result = await response.json();
        
        if (response.ok) {
            showAssessmentResults(result.assessment);
        } else {
            showNotification(result.error || 'Assessment failed', 'error');
        }
    } catch (error) {
        showNotification('Network error. Please try again.', 'error');
    } finally {
        hideLoading();
    }
}

function showAssessmentResults(assessment) {
    const modal = document.createElement('div');
    modal.className = 'modal active';
    modal.innerHTML = `
        <div class="modal-content glass-card" style="max-width: 800px;">
            <div class="modal-header">
                <h3>🔍 Security Assessment Results</h3>
                <button class="modal-close" onclick="this.closest('.modal').remove()">
                    <i class="fas fa-times"></i>
                </button>
            </div>
            <div class="modal-body">
                <div class="assessment-results">
                    <h4>Security Score: ${assessment.score}/100</h4>
                    <div class="assessment-score">
                        <div class="score-circle score-${assessment.score >= 80 ? 'high' : assessment.score >= 60 ? 'medium' : 'low'}">
                            ${assessment.score}
                        </div>
                        <div class="score-details">
                            <div>Overall security rating</div>
                            <div>${assessment.score >= 80 ? 'Good' : assessment.score >= 60 ? 'Fair' : 'Needs Improvement'}</div>
                        </div>
                    </div>
                    
                    <h4>Vulnerabilities Found:</h4>
                    <div class="findings-list">
                        ${assessment.results.findings.map(finding => `
                            <div class="finding-item">
                                <span class="finding-severity severity-${finding.severity}">${finding.severity}</span>
                                <div class="finding-details">
                                    <strong>${finding.issue}</strong>
                                    ${finding.cve ? `<div>CVE: ${finding.cve}</div>` : ''}
                                    ${finding.endpoint ? `<div>Endpoint: ${finding.endpoint}</div>` : ''}
                                    ${finding.recommendation ? `<div>Recommendation: ${finding.recommendation}</div>` : ''}
                                </div>
                            </div>
                        `).join('')}
                    </div>
                    
                    <h4>Recommendations:</h4>
                    <div class="recommendations-list">
                        ${assessment.results.recommendations.map(rec => `<li>${rec}</li>`).join('')}
                    </div>
                </div>
            </div>
        </div>
    `;
    document.body.appendChild(modal);
}

function startSecurityLab(labId) {
    showNotification('Security lab feature coming soon!', 'info');
}

function startCertification(certName) {
    showNotification(`Starting ${certName} learning path...`, 'info');
}

// ===== Add CSS for security results =====
const securityStyles = document.createElement('style');
securityStyles.textContent = `
    .challenge-result {
        text-align: center;
        padding: 2rem;
    }
    
    .result-status {
        font-size: 1.5rem;
        font-weight: 700;
        margin-bottom: 1rem;
        padding: 1rem;
        border-radius: 8px;
    }
    
    .result-status.success {
        background: var(--success-color);
        color: white;
    }
    
    .result-status.error {
        background: var(--error-color);
        color: white;
    }
    
    .points-earned {
        font-size: 1.25rem;
        margin-bottom: 1rem;
    }
    
    .new-skills {
        margin-top: 1rem;
    }
    
    .skills-list {
        display: flex;
        flex-wrap: wrap;
        gap: 0.5rem;
        margin-top: 0.5rem;
    }
`;
document.head.appendChild(securityStyles);

// ===== Enterprise Dashboard Functions =====
async function loadEnterpriseDashboard() {
    if (!currentUser || currentUser.role !== 'admin') {
        showNotification('Admin access required', 'error');
        return;
    }
    
    showLoading();
    
    try {
        const response = await fetch(`${API_BASE_URL}/analytics/enterprise-dashboard`, {
            headers: { 'Authorization': `Bearer ${authToken}` }
        });
        
        if (response.ok) {
            const data = await response.json();
            displayEnterpriseDashboard(data);
        } else {
            showNotification('Failed to load enterprise dashboard', 'error');
        }
    } catch (error) {
        showNotification('Error loading enterprise dashboard', 'error');
    } finally {
        hideLoading();
    }
}

function displayEnterpriseDashboard(data) {
    // Update overview cards
    document.getElementById('totalStudents').textContent = data.overview.total_students;
    document.getElementById('totalCompanies').textContent = data.overview.total_companies;
    document.getElementById('totalInternships').textContent = data.overview.total_internships;
    document.getElementById('placementRate').textContent = data.overview.placement_rate + '%';
    
    // Create charts
    createPlacementsPerCompanyChart(data.charts.placements_per_company);
    createApplicationStatusChart(data.charts.selected_vs_rejected);
    createInternshipGrowthChart(data.charts.internship_growth);
    createDepartmentPlacementsChart(data.charts.department_wise_placements);
    
    // Display top companies
    displayTopCompanies(data.top_companies);
    
    // Display recent activities
    displayRecentActivities(data.recent_activities);
}

function createPlacementsPerCompanyChart(data) {
    const ctx = document.getElementById('placementsPerCompanyChart').getContext('2d');
    new Chart(ctx, {
        type: 'bar',
        data: {
            labels: Object.keys(data),
            datasets: [{
                label: 'Placements',
                data: Object.values(data),
                backgroundColor: '#2563EB',
                borderColor: '#1D4ED8',
                borderWidth: 1
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            scales: {
                y: {
                    beginAtZero: true,
                    ticks: {
                        stepSize: 1
                    }
                }
            }
        }
    });
}

function createApplicationStatusChart(data) {
    const ctx = document.getElementById('applicationStatusChart').getContext('2d');
    new Chart(ctx, {
        type: 'pie',
        data: {
            labels: ['Selected', 'Rejected', 'Pending'],
            datasets: [{
                data: [data.selected, data.rejected, data.pending],
                backgroundColor: ['#22C55E', '#EF4444', '#F59E0B'],
                borderColor: ['#16A34A', '#DC2626', '#D97706'],
                borderWidth: 1
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false
        }
    });
}

function createInternshipGrowthChart(data) {
    const ctx = document.getElementById('internshipGrowthChart').getContext('2d');
    new Chart(ctx, {
        type: 'line',
        data: {
            labels: Object.keys(data),
            datasets: [{
                label: 'Internships Posted',
                data: Object.values(data),
                borderColor: '#2563EB',
                backgroundColor: 'rgba(37, 99, 235, 0.1)',
                tension: 0.4,
                fill: true
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            scales: {
                y: {
                    beginAtZero: true
                }
            }
        }
    });
}

function createDepartmentPlacementsChart(data) {
    const ctx = document.getElementById('departmentPlacementsChart').getContext('2d');
    new Chart(ctx, {
        type: 'doughnut',
        data: {
            labels: Object.keys(data),
            datasets: [{
                data: Object.values(data),
                backgroundColor: [
                    '#2563EB',
                    '#22C55E',
                    '#F59E0B',
                    '#EF4444',
                    '#8B5CF6',
                    '#64748B'
                ],
                borderColor: '#FFFFFF',
                borderWidth: 2
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false
        }
    });
}

function displayTopCompanies(companies) {
    const container = document.getElementById('topCompaniesTable');
    
    if (companies.length === 0) {
        container.innerHTML = '<p>No placement data available</p>';
        return;
    }
    
    container.innerHTML = companies.map(([name, placements]) => `
        <div class="company-row">
            <span class="company-name">${name}</span>
            <span class="company-placements">${placements} placements</span>
        </div>
    `).join('');
}

function displayRecentActivities(activities) {
    const container = document.getElementById('recentActivities');
    
    container.innerHTML = activities.map(activity => `
        <div class="activity-item">
            <div class="activity-icon">
                <i class="fas fa-${getActivityIcon(activity.type)}"></i>
            </div>
            <div class="activity-message">${activity.message}</div>
        </div>
    `).join('');
}

function getActivityIcon(type) {
    const icons = {
        'placement': 'trophy',
        'internship': 'briefcase',
        'application': 'paper-plane'
    };
    return icons[type] || 'info-circle';
}

// ===== Enhanced Student Dashboard Functions =====
async function loadStudentDashboardEnhanced() {
    if (!currentUser || currentUser.role !== 'student') {
        showNotification('Student access required', 'error');
        return;
    }
    
    showLoading();
    
    try {
        const response = await fetch(`${API_BASE_URL}/analytics/student-dashboard`, {
            headers: { 'Authorization': `Bearer ${authToken}` }
        });
        
        if (response.ok) {
            const data = await response.json();
            displayStudentDashboardEnhanced(data);
        } else {
            showNotification('Failed to load student dashboard', 'error');
        }
    } catch (error) {
        showNotification('Error loading student dashboard', 'error');
    } finally {
        hideLoading();
    }
}

function displayStudentDashboardEnhanced(data) {
    // Update overview cards
    document.getElementById('studentApplications').textContent = data.overview.total_applications;
    document.getElementById('studentPlaced').textContent = data.overview.placed_count;
    document.getElementById('studentSuccessRate').textContent = data.overview.success_rate + '%';
    document.getElementById('studentSkills').textContent = data.skills.total_skills;
    
    // Display skills
    displayUserSkills(data.skills.user_skills);
    
    // Create skill match chart
    createSkillMatchChart(data.skills.skill_matches);
    
    // Create application timeline chart
    createApplicationTimelineChart(data.timeline);
    
    // Display recommendations
    displayStudentRecommendations(data.recommendations);
}

function displayUserSkills(skills) {
    const container = document.getElementById('userSkillsTags');
    
    if (skills.length === 0) {
        container.innerHTML = '<p>No skills added yet</p>';
        return;
    }
    
    container.innerHTML = skills.map(skill => `
        <span class="skill-tag">${skill}</span>
    `).join('');
}

function createSkillMatchChart(data) {
    const ctx = document.getElementById('skillMatchChart').getContext('2d');
    
    new Chart(ctx, {
        type: 'bar',
        data: {
            labels: Object.keys(data),
            datasets: [{
                label: 'Skill Match %',
                data: Object.values(data),
                backgroundColor: '#22C55E',
                borderColor: '#16A34A',
                borderWidth: 1
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            scales: {
                y: {
                    beginAtZero: true,
                    max: 100,
                    ticks: {
                        callback: function(value) {
                            return value + '%';
                        }
                    }
                }
            }
        }
    });
}

function createApplicationTimelineChart(data) {
    const ctx = document.getElementById('applicationTimelineChart').getContext('2d');
    
    new Chart(ctx, {
        type: 'line',
        data: {
            labels: Object.keys(data),
            datasets: [{
                label: 'Applications',
                data: Object.values(data),
                borderColor: '#2563EB',
                backgroundColor: 'rgba(37, 99, 235, 0.1)',
                tension: 0.4,
                fill: true
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            scales: {
                y: {
                    beginAtZero: true,
                    ticks: {
                        stepSize: 1
                    }
                }
            }
        }
    });
}

function displayStudentRecommendations(recommendations) {
    const container = document.getElementById('studentRecommendations');
    
    container.innerHTML = recommendations.map(rec => `
        <li>${rec}</li>
    `).join('');
}

// ===== Add CSS for enterprise dashboard =====
const notificationStyles = document.createElement('style');
notificationStyles.textContent = `
    @keyframes slideInRight {
        from {
            transform: translateX(100%);
            opacity: 0;
        }
        to {
            transform: translateX(0);
            opacity: 1;
        }
    }
    
    .notification {
        animation: slideInRight 0.3s ease-out;
    }
    
    .notification button {
        background: none;
        border: none;
        color: white;
        cursor: pointer;
        padding: 0.25rem;
        border-radius: 50%;
        transition: background 0.3s ease;
    }
    
    .notification button:hover {
        background: rgba(255, 255, 255, 0.2);
    }
    
    .dragover {
        border-color: var(--primary-color) !important;
        background: var(--bg-tertiary) !important;
    }
    
    .analysis-score, .readiness-score {
        margin-bottom: 1.5rem;
    }
    
    .analysis-section, .score-components {
        margin-bottom: 1.5rem;
    }
    
    .skills-list {
        display: flex;
        flex-wrap: wrap;
        gap: 0.5rem;
        margin: 0.5rem 0;
    }
    
    .component {
        display: grid;
        grid-template-columns: 100px 1fr 50px;
        align-items: center;
        gap: 0.5rem;
        margin-bottom: 0.5rem;
    }
    
    .learning-rec {
        margin-bottom: 1rem;
        padding: 1rem;
        background: var(--bg-tertiary);
        border-radius: 8px;
    }
    
    .learning-rec ul {
        margin: 0.5rem 0 0 1rem;
    }
`;
document.head.appendChild(notificationStyles);
