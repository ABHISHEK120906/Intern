# Vercel Deployment Checklist

## ✅ Fixed Issues
1. **vercel.json configuration** - Updated to use `vercel_app.py` instead of `app.py`
2. **Vercel handler** - Added proper vercel-wsgi import with fallback
3. **Dependencies** - Added vercel-wsgi to requirements
4. **Error handling** - Added MongoDB connection failure handling

## 🚀 Deployment Steps

### 1. Environment Variables
Make sure these are set in your Vercel project:
- `MONGODB_URI` - Your MongoDB connection string
- `JWT_SECRET_KEY` - Your JWT secret
- `PYTHON_VERSION` - Set to 3.12 (already in vercel.json)

### 2. Files to Deploy
- `vercel_app.py` - Main application file
- `vercel.json` - Vercel configuration
- `vercel_requirements.txt` - Python dependencies
- `templates/` - HTML templates
- `static/` - CSS/JS files

### 3. Deploy Command
```bash
vercel --prod
```

## 🔍 Testing After Deployment
Test these endpoints:
- `/health` - Should return status: healthy
- `/` - Should serve your homepage
- `/api/current-ip` - Should return IP information
- `/test-db` - Should test MongoDB connection

## 🐛 Common Issues & Solutions

### MongoDB Connection Issues
- Ensure MONGODB_URI is correct in Vercel env vars
- Check IP whitelist in MongoDB Atlas
- Verify network access settings

### Function Timeout
- Vercel functions have 10-second timeout for Hobby plan
- Optimize database queries
- Consider Vercel Pro plan for longer timeouts

### Import Errors
- All dependencies must be in vercel_requirements.txt
- Check package versions are compatible
- Ensure no local file dependencies

## 📊 Monitoring
- Check Vercel logs for errors
- Monitor function execution time
- Set up uptime monitoring for critical endpoints

## 🔧 Debug Mode
Add `?debug=true` to any URL to see detailed error information during development.
