# Sample Data Script for Smart AI Internship Tracking System

from pymongo import MongoClient
import bcrypt
from datetime import datetime
import os
from dotenv import load_dotenv

load_dotenv()

# Connect to MongoDB
client = MongoClient(os.getenv('MONGODB_URI'))
db = client['placement_system']

# Clear existing data (optional - comment out if you want to keep existing data)
print("Clearing existing collections...")
db.users.delete_many({})
db.internships.delete_many({})
db.applications.delete_many({})
db.trainings.delete_many({})
db.notifications.delete_many({})

# Create Sample Users
print("Creating sample users...")

# Sample Students
students = [
    {
        'name': 'Alice Johnson',
        'email': 'alice@example.com',
        'password': bcrypt.hashpw('password123'.encode('utf-8'), bcrypt.gensalt()),
        'role': 'student',
        'created_at': datetime.now().isoformat(),
        'profile': {
            'phone': '1234567890',
            'address': '123 Main St, City, State',
            'bio': 'Computer Science student passionate about AI and machine learning',
            'skills': ['Python', 'JavaScript', 'React', 'SQL', 'Machine Learning'],
            'education': [
                {
                    'degree': 'B.Tech Computer Science',
                    'institution': 'Tech University',
                    'year': '2024'
                }
            ],
            'experience': [
                {
                    'title': 'Web Development Intern',
                    'company': 'StartUp Inc',
                    'duration': '3 months'
                }
            ]
        }
    },
    {
        'name': 'Bob Smith',
        'email': 'bob@example.com',
        'password': bcrypt.hashpw('password123'.encode('utf-8'), bcrypt.gensalt()),
        'role': 'student',
        'created_at': datetime.now().isoformat(),
        'profile': {
            'phone': '0987654321',
            'address': '456 Oak Ave, City, State',
            'bio': 'Information Technology student with focus on cybersecurity',
            'skills': ['Java', 'C++', 'Python', 'Network Security', 'Linux'],
            'education': [
                {
                    'degree': 'B.Sc Information Technology',
                    'institution': 'IT College',
                    'year': '2024'
                }
            ],
            'experience': []
        }
    },
    {
        'name': 'Carol Williams',
        'email': 'carol@example.com',
        'password': bcrypt.hashpw('password123'.encode('utf-8'), bcrypt.gensalt()),
        'role': 'student',
        'created_at': datetime.now().isoformat(),
        'profile': {
            'phone': '5551234567',
            'address': '789 Pine Rd, City, State',
            'bio': 'Electronics Engineering student interested in IoT and embedded systems',
            'skills': ['C', 'Arduino', 'Raspberry Pi', 'IoT', 'Circuit Design'],
            'education': [
                {
                    'degree': 'B.E Electronics',
                    'institution': 'Engineering College',
                    'year': '2024'
                }
            ],
            'experience': [
                {
                    'title': 'Hardware Intern',
                    'company': 'Electronics Corp',
                    'duration': '2 months'
                }
            ]
        }
    }
]

# Sample Companies
companies = [
    {
        'name': 'Tech Innovators Inc',
        'email': 'hr@techinnovators.com',
        'password': bcrypt.hashpw('password123'.encode('utf-8'), bcrypt.gensalt()),
        'role': 'company',
        'created_at': datetime.now().isoformat(),
        'profile': {
            'phone': '1112223333',
            'address': '100 Tech Park, Silicon Valley, CA',
            'bio': 'Leading technology company specializing in AI and cloud solutions',
            'website': 'https://techinnovators.com',
            'industry': 'Technology',
            'size': '1000+ employees'
        }
    },
    {
        'name': 'Digital Solutions Ltd',
        'email': 'careers@digitalsolutions.com',
        'password': bcrypt.hashpw('password123'.encode('utf-8'), bcrypt.gensalt()),
        'role': 'company',
        'created_at': datetime.now().isoformat(),
        'profile': {
            'phone': '4445556666',
            'address': '200 Business Hub, New York, NY',
            'bio': 'Digital transformation company helping businesses modernize',
            'website': 'https://digitalsolutions.com',
            'industry': 'IT Services',
            'size': '500-1000 employees'
        }
    }
]

# Sample Admin
admin = {
    'name': 'System Administrator',
    'email': 'admin@placementsystem.com',
    'password': bcrypt.hashpw('admin123'.encode('utf-8'), bcrypt.gensalt()),
    'role': 'admin',
    'created_at': datetime.now().isoformat(),
    'profile': {
        'phone': '0000000000',
        'address': 'System Office',
        'bio': 'System administrator'
    }
}

# Insert users
user_ids = {}
for student in students:
    result = db.users.insert_one(student)
    user_ids[student['email']] = result.inserted_id
    print(f"Created student: {student['name']}")

for company in companies:
    result = db.users.insert_one(company)
    user_ids[company['email']] = result.inserted_id
    print(f"Created company: {company['name']}")

admin_result = db.users.insert_one(admin)
user_ids[admin['email']] = admin_result.inserted_id
print(f"Created admin: {admin['name']}")

# Create Sample Internships
print("\nCreating sample internships...")

internships = [
    {
        'title': 'Frontend Developer Intern',
        'description': 'Join our team to build amazing web applications using React and modern JavaScript frameworks. You will work on real projects and learn from experienced developers.',
        'company_id': user_ids['hr@techinnovators.com'],
        'company_name': 'Tech Innovators Inc',
        'location': 'Remote',
        'duration': '3 months',
        'stipend': '$1000/month',
        'skills_required': ['React', 'JavaScript', 'CSS', 'HTML', 'Git'],
        'type': 'internship',
        'remote': True,
        'status': 'active',
        'created_at': datetime.now().isoformat(),
        'deadline': '2024-12-31',
        'requirements': ['Basic React knowledge', 'Good communication skills', 'Problem-solving attitude'],
        'benefits': ['Flexible working hours', 'Learning opportunities', 'Certificate of completion', 'Potential full-time offer'],
        'hiring_capacity': 5,
        'selected_count': 0
    },
    {
        'title': 'Machine Learning Intern',
        'description': 'Work on cutting-edge ML projects including natural language processing and computer vision. Strong foundation in Python and ML algorithms required.',
        'company_id': user_ids['hr@techinnovators.com'],
        'company_name': 'Tech Innovators Inc',
        'location': 'San Francisco, CA',
        'duration': '6 months',
        'stipend': '$1500/month',
        'skills_required': ['Python', 'Machine Learning', 'TensorFlow', 'Data Analysis', 'Statistics'],
        'type': 'internship',
        'remote': False,
        'status': 'active',
        'created_at': datetime.now().isoformat(),
        'deadline': '2024-12-15',
        'requirements': ['Strong Python skills', 'ML coursework', 'Mathematics background'],
        'benefits': ['Mentorship from senior engineers', 'Research opportunities', 'Conference attendance'],
        'hiring_capacity': 3,
        'selected_count': 0
    },
    {
        'title': 'Cybersecurity Analyst Intern',
        'description': 'Help protect our digital infrastructure and learn about security best practices. Monitor systems and analyze potential threats.',
        'company_id': user_ids['careers@digitalsolutions.com'],
        'company_name': 'Digital Solutions Ltd',
        'location': 'New York, NY',
        'duration': '4 months',
        'stipend': '$1200/month',
        'skills_required': ['Network Security', 'Linux', 'Python', 'Penetration Testing', 'Risk Assessment'],
        'type': 'internship',
        'remote': False,
        'status': 'active',
        'created_at': datetime.now().isoformat(),
        'deadline': '2024-12-20',
        'requirements': ['Network fundamentals', 'Security concepts', 'Analytical thinking'],
        'benefits': ['Security certifications', 'Hands-on experience', 'Industry exposure'],
        'hiring_capacity': 4,
        'selected_count': 0
    },
    {
        'title': 'IoT Developer Intern',
        'description': 'Design and develop IoT solutions for smart home and industrial applications. Work with embedded systems and cloud platforms.',
        'company_id': user_ids['careers@digitalsolutions.com'],
        'company_name': 'Digital Solutions Ltd',
        'location': 'Hybrid',
        'duration': '5 months',
        'stipend': '$1100/month',
        'skills_required': ['C', 'Arduino', 'Raspberry Pi', 'IoT', 'Cloud Computing'],
        'type': 'internship',
        'remote': True,
        'status': 'active',
        'created_at': datetime.now().isoformat(),
        'deadline': '2024-12-25',
        'requirements': ['Embedded systems knowledge', 'Basic electronics', 'Programming skills'],
        'benefits': ['Hardware provided', 'Innovation labs access', 'Patent opportunities'],
        'hiring_capacity': 6,
        'selected_count': 0
    }
]

internship_ids = {}
for internship in internships:
    result = db.internships.insert_one(internship)
    internship_ids[internship['title']] = result.inserted_id
    print(f"Created internship: {internship['title']}")

# Create Sample Applications
print("\nCreating sample applications...")

applications = [
    {
        'student_id': user_ids['alice@example.com'],
        'internship_id': internship_ids['Frontend Developer Intern'],
        'company_id': user_ids['hr@techinnovators.com'],
        'status': 'selected',
        'applied_date': datetime.now().isoformat(),
        'resume_url': '/uploads/alice_resume.pdf',
        'cover_letter': 'I am excited to apply for the Frontend Developer Intern position. My experience with React and JavaScript makes me a strong candidate.',
        'notes': 'Strong portfolio, good communication skills'
    },
    {
        'student_id': user_ids['alice@example.com'],
        'internship_id': internship_ids['Machine Learning Intern'],
        'company_id': user_ids['hr@techinnovators.com'],
        'status': 'pending',
        'applied_date': datetime.now().isoformat(),
        'resume_url': '/uploads/alice_resume.pdf',
        'cover_letter': 'As a ML enthusiast, I would love to contribute to your cutting-edge projects.',
        'notes': 'Good academic background, relevant coursework'
    },
    {
        'student_id': user_ids['bob@example.com'],
        'internship_id': internship_ids['Cybersecurity Analyst Intern'],
        'company_id': user_ids['careers@digitalsolutions.com'],
        'status': 'shortlisted',
        'applied_date': datetime.now().isoformat(),
        'resume_url': '/uploads/bob_resume.pdf',
        'cover_letter': 'My background in network security and Linux makes me ideal for this role.',
        'notes': 'Strong technical skills, security certifications'
    },
    {
        'student_id': user_ids['carol@example.com'],
        'internship_id': internship_ids['IoT Developer Intern'],
        'company_id': user_ids['careers@digitalsolutions.com'],
        'status': 'pending',
        'applied_date': datetime.now().isoformat(),
        'resume_url': '/uploads/carol_resume.pdf',
        'cover_letter': 'I am passionate about IoT and have hands-on experience with Arduino and Raspberry Pi.',
        'notes': 'Hardware experience, innovative projects'
    }
]

for app in applications:
    db.applications.insert_one(app)
    print(f"Created application for student {app['student_id']}")

# Create Sample Training Sessions
print("\nCreating sample training sessions...")

trainings = [
    {
        'title': 'React Development Bootcamp',
        'description': 'Intensive 4-week bootcamp covering React, Redux, and modern frontend development',
        'instructor': 'John React Expert',
        'type': 'technical',
        'duration': '4 weeks',
        'schedule': 'Weekends, 9 AM - 5 PM',
        'status': 'active',
        'created_at': datetime.now().isoformat(),
        'materials': ['React Documentation', 'Course Videos', 'Practice Projects'],
        'max_participants': 30,
        'current_participants': 15
    },
    {
        'title': 'Machine Learning Fundamentals',
        'description': 'Comprehensive introduction to ML algorithms and practical applications',
        'instructor': 'Dr. AI Specialist',
        'type': 'technical',
        'duration': '6 weeks',
        'schedule': 'Tue/Thu, 6 PM - 8 PM',
        'status': 'active',
        'created_at': datetime.now().isoformat(),
        'materials': ['Python Notebooks', 'Dataset Collection', 'ML Algorithms Guide'],
        'max_participants': 25,
        'current_participants': 20
    },
    {
        'title': 'Soft Skills Workshop',
        'description': 'Develop essential soft skills for career success including communication and teamwork',
        'instructor': 'Sarah Soft Skills Coach',
        'type': 'soft skills',
        'duration': '2 weeks',
        'schedule': 'Weekdays, 4 PM - 6 PM',
        'status': 'active',
        'created_at': datetime.now().isoformat(),
        'materials': ['Communication Guide', 'Team Activities', 'Interview Tips'],
        'max_participants': 40,
        'current_participants': 35
    }
]

for training in trainings:
    db.trainings.insert_one(training)
    print(f"Created training: {training['title']}")

# Create Sample Notifications
print("\nCreating sample notifications...")

notifications = [
    {
        'user_id': user_ids['alice@example.com'],
        'title': 'Application Selected!',
        'message': 'Congratulations! Your application for Frontend Developer Intern has been selected.',
        'type': 'success',
        'created_date': datetime.now().isoformat(),
        'read': False
    },
    {
        'user_id': user_ids['bob@example.com'],
        'title': 'Interview Scheduled',
        'message': 'Your interview for Cybersecurity Analyst Intern has been scheduled for next week.',
        'type': 'info',
        'created_date': datetime.now().isoformat(),
        'read': False
    },
    {
        'user_id': user_ids['carol@example.com'],
        'title': 'New Internship Posted',
        'message': 'A new IoT Developer Intern position matching your skills has been posted.',
        'type': 'info',
        'created_date': datetime.now().isoformat(),
        'read': True
    },
    {
        'user_id': None,  # Broadcast notification
        'title': 'Training Registration Open',
        'message': 'Registration for React Development Bootcamp is now open. Limited seats available!',
        'type': 'info',
        'created_date': datetime.now().isoformat(),
        'read': False
    }
]

for notification in notifications:
    db.notifications.insert_one(notification)
    print(f"Created notification: {notification['title']}")

# Update internship selected counts
print("\nUpdating internship statistics...")
db.internships.update_one(
    {'_id': internship_ids['Frontend Developer Intern']},
    {'$set': {'selected_count': 1}}
)

print("\n=== Sample Data Creation Complete ===")
print("\nLogin Credentials:")
print("Students:")
print("  alice@example.com - password123")
print("  bob@example.com - password123")
print("  carol@example.com - password123")
print("\nCompanies:")
print("  hr@techinnovators.com - password123")
print("  careers@digitalsolutions.com - password123")
print("\nAdmin:")
print("  admin@placementsystem.com - admin123")
print("\nAccess the application at: http://localhost:5000")
