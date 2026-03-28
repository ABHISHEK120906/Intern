# Smart AI-Based Internship and Placement Tracking System

A comprehensive full-stack web application that helps students track internships and placements with AI-powered career guidance and analytics.

## 🚀 Features

### Core Modules
- **Admin Module**: Manage students, companies, training sessions, and placements
- **Student Module**: Profile management, internship applications, placement tracking
- **Company Module**: Post jobs, view applicants, manage hiring process
- **Training Module**: Schedule and track training sessions
- **Application Module**: Track application status and manage submissions

### AI Features
- **AI Resume Analyzer**: Upload PDF resumes for instant skill extraction and scoring
- **Smart Job Recommendations**: Personalized internship suggestions based on skills
- **Skill Gap Analysis**: Compare your skills with job requirements
- **Placement Readiness Score**: Comprehensive scoring system for placement readiness

### UI/UX Features
- **Glassmorphism Design**: Modern blur effects and transparency
- **Dark/Light Mode**: Toggle between themes
- **Responsive Design**: Mobile-friendly interface
- **Smooth Animations**: Scroll animations and transitions
- **Interactive Dashboard**: Real-time analytics and charts

## �️ Cybersecurity Training & Labs
- **Security Labs**: Hands-on labs with Nmap, Wireshark, Metasploit, Burp Suite
- **CTF Challenges**: Capture The Flag challenges (SQL Injection, XSS, Cryptography, Network Recon)
- **Kali Linux Integration**: Complete toolset for penetration testing and security auditing
- **Security Assessments**: Vulnerability scanning, penetration testing, network security audits
- **Digital Forensics**: Evidence collection, malware analysis, incident response
- **Security Certifications**: Track CEH, OSCP, CISSP, Security+ progress
- **Threat Intelligence**: Real-time threat monitoring and vulnerability tracking (Admin)

## �🛠 Technology Stack

### Backend
- **Python 3.8+**
- **Flask** - Web framework
- **MongoDB** - Database
- **JWT** - Authentication
- **PyPDF2** - PDF processing
- **bcrypt** - Password hashing

### Frontend
- **HTML5, CSS3, JavaScript**
- **Chart.js** - Data visualization
- **Font Awesome** - Icons
- **Google Fonts** - Typography

### Security Tools Integration
- **Nmap** - Network scanning and discovery
- **Wireshark** - Network traffic analysis
- **Metasploit** - Penetration testing framework
- **Burp Suite** - Web application security testing
- **John the Ripper** - Password cracking
- **SQLMap** - SQL injection testing
- **Aircrack-ng** - Wireless security testing
- **Autopsy** - Digital forensics platform
- **Volatility** - Memory forensics

## 📦 Installation

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd Intern
   ```

2. **Install Python dependencies**
   ```bash
   pip install -r requirements.txt
   ```

3. **Set up environment variables**
   ```bash
   cp .env.example .env
   # Edit .env with your MongoDB URI and other settings
   ```

4. **Create uploads directory**
   ```bash
   mkdir uploads
   ```

5. **Run the application**
   ```bash
   python app.py
   ```

6. **Access the application**
   - Frontend: http://localhost:5000
   - API Base URL: http://localhost:5000

## 📚 API Documentation

### Authentication
- `POST /auth/register` - Register new user
- `POST /auth/login` - User login
- `GET /auth/profile` - Get user profile
- `PUT /auth/profile` - Update profile

### Internships
- `GET /internships` - Get all internships
- `POST /internships` - Create new internship (Company/Admin)
- `GET /internships/<id>` - Get internship details
- `PUT /internships/<id>` - Update internship
- `DELETE /internships/<id>` - Delete internship

### Applications
- `GET /applications` - Get user applications
- `POST /applications` - Apply for internship
- `PUT /applications/<id>/status` - Update application status

### AI Features
- `POST /ai/resume-analyze` - Analyze uploaded resume
- `GET /ai/job-recommendations` - Get job recommendations
- `POST /ai/skill-gap-analysis` - Analyze skill gaps
- `GET /ai/placement-readiness-score` - Get readiness score

### File Upload
- `POST /upload/resume` - Upload resume file

### 🔒 Cybersecurity Endpoints

#### Security Labs
- `GET /security/labs` - Get available security labs
- `POST /security/labs` - Create security lab (Admin/Company)

#### Security Challenges
- `GET /security/challenges` - Get CTF challenges
- `POST /security/challenges/<id>/submit` - Submit challenge solution

#### Security Assessment
- `POST /security/assessment` - Run security assessment
  - Types: `vulnerability_scan`, `penetration_test`, `network_security`

#### Kali Linux Tools
- `GET /security/kali-tools` - Get Kali Linux tools catalog

#### Security Certifications
- `GET /security/certifications` - Get certifications and recommendations
- `POST /security/certifications` - Add earned certification

#### Threat Intelligence (Admin Only)
- `GET /security/threat-intel` - Get threat intelligence dashboard

## 🎯 Usage Guide

### For Students
1. **Register**: Create account with student role
2. **Complete Profile**: Add skills, education, experience
3. **Upload Resume**: Upload PDF for AI analysis
4. **Browse Internships**: View and apply to opportunities
5. **Track Applications**: Monitor application status
6. **🛡️ Use Security Labs**: Practice hands-on cybersecurity skills
7. **🏆 Solve CTF Challenges**: Earn points and security skills
8. **🔍 Run Security Assessments**: Test system security
9. **🎓 Track Certifications**: Monitor CEH, OSCP, CISSP progress

### For Companies
1. **Register**: Create account with company role
2. **Post Internships**: Create job postings with requirements
3. **Review Applications**: View and manage applications
4. **Update Status**: Shortlist, reject, or select candidates
5. **🛡️ Create Security Labs**: Design hands-on training scenarios

### For Admins
1. **Register**: Create account with admin role
2. **View Dashboard**: Monitor system analytics
3. **Manage Users**: Oversee all user activities
4. **Create Training**: Schedule training sessions
5. **Send Notifications**: Broadcast system messages
6. **🚨 Monitor Threats**: Access threat intelligence dashboard

## 🔧 Configuration

### Environment Variables
- `MONGODB_URI`: MongoDB connection string
- `JWT_SECRET_KEY`: Secret key for JWT tokens
- `FLASK_ENV`: Environment (development/production)
- `FLASK_DEBUG`: Debug mode
- `UPLOAD_FOLDER`: File upload directory
- `MAX_CONTENT_LENGTH`: Maximum file size

### MongoDB Collections
- `users`: User accounts and profiles
- `internships`: Job postings and internships
- `applications`: Student applications
- `trainings`: Training sessions
- `notifications`: System notifications
- `security_labs`: Security training labs
- `security_challenges`: CTF challenges
- `certifications`: Security certifications tracking

## 🎨 UI Components

### Glassmorphism Cards
```css
.glass-card {
    background: rgba(255, 255, 255, 0.7);
    backdrop-filter: blur(8px);
    border-radius: 16px;
    border: 1px solid rgba(255, 255, 255, 0.2);
}
```

### Color Scheme
- **Primary**: #667eea
- **Secondary**: #764ba2
- **Accent**: #f093fb
- **Success**: #10b981
- **Warning**: #f59e0b
- **Error**: #ef4444
- **Security**: #dc2626 (for cybersecurity elements)

## 📊 Analytics Dashboard

### Key Metrics
- Total students and companies
- Active internships and applications
- Placement rates and trends
- Skill distribution analysis
- **NEW**: Security lab completion rates
- **NEW**: CTF challenge statistics
- **NEW**: Certification progress tracking

### Charts
- Application status distribution
- Skills overview
- Company hiring trends
- Placement progress
- **NEW**: Security skills radar chart
- **NEW**: Challenge completion heatmap

## 🔒 Security Features

### Authentication & Authorization
- JWT-based authentication
- Role-based access control (Student, Company, Admin)
- Password hashing with bcrypt
- Input validation and sanitization

### Security Training
- **Labs**: Network security, Web security, Penetration testing
- **Challenges**: SQL Injection, XSS, Cryptography, Network Recon
- **Tools**: Full Kali Linux integration
- **Assessments**: Automated vulnerability scanning and reporting

### Threat Intelligence
- Real-time threat monitoring
- CVE vulnerability tracking
- Security incident reporting
- Risk assessment dashboard

## 🚀 Deployment

### Production Setup
1. Set environment variables
2. Configure production database
3. Set up reverse proxy (nginx)
4. Enable HTTPS
5. Configure domain and SSL
6. **Security**: Set up WAF and rate limiting

### Docker Support
```dockerfile
FROM python:3.9-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt
COPY . .
EXPOSE 5000
CMD ["python", "app.py"]
```

## 🤝 Contributing

1. Fork the repository
2. Create feature branch
3. Make changes
4. Test thoroughly
5. Submit pull request

## 📄 License

This project is licensed under the MIT License.

## 🆘 Support

For issues and questions:
- Check the documentation
- Review API endpoints
- Test with sample data
- Contact development team

## 🎯 Future Enhancements

- Real-time chat system
- Interview scheduling
- Video conferencing integration
- Advanced analytics
- Mobile app development
- AI-powered interview preparation
- **🔒 Advanced security features**:
  - Live hacking labs
  - SIEM integration
  - Threat hunting platform
  - Security orchestration

---

**Built with ❤️ and 🔒 for students and cybersecurity professionals**
