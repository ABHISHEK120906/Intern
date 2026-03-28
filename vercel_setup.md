# Vercel Deployment Configuration
# AI-Powered Internship & Placement Tracking System

## 🚀 Vercel Deployment Setup

### Required Files for Vercel:
1. `vercel.json` - Vercel configuration
2. `requirements.txt` - Python dependencies
3. `app.py` - Modified Flask app for serverless
4. `.env` - Environment variables

### Deployment Steps:
1. Install Vercel CLI: `npm i -g vercel`
2. Run: `vercel` in project directory
3. Follow prompts
4. Set environment variables in Vercel dashboard

### Environment Variables Needed:
- MONGODB_URI
- JWT_SECRET_KEY
- FLASK_ENV=production
- UPLOAD_FOLDER=uploads
- MAX_CONTENT_LENGTH=16777216

### Notes:
- Static files served from `/static/`
- Templates from `/templates/`
- MongoDB Atlas connection required
- Serverless function timeout: 10 seconds
