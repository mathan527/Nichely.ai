# Nichely - Hosting Documentation

## 🚀 Render.com Deployment Guide

This document outlines the changes made to deploy the Nichely application on Render's free hosting platform.

## 📋 Changes Made for Render Deployment

### 1. Configuration Updates (`config.py`)

**Before:**
- Hardcoded `.env` file path: `env_file = r"C:\Users\bruce\Downloads\New folder\nichely\app\.env"`
- Static configuration values

**After:**
- Removed hardcoded `.env` path
- All configuration values now use `os.getenv()` with fallback defaults
- Added server configuration for Render:
  - `PORT: int = int(os.getenv("PORT", "8000"))`
  - `HOST: str = os.getenv("HOST", "0.0.0.0")`

### 2. Render Configuration (`render.yaml`)

Created a complete Render deployment configuration with:
- **Service Type:** Web service on free plan
- **Runtime:** Python 3.11
- **Build Command:** `pip install --upgrade pip && pip install -r requirements.txt`
- **Start Command:** `python -m uvicorn main:app --host 0.0.0.0 --port $PORT`
- **Health Check:** Configured at root path `/`
- **Auto-deploy:** Enabled for code changes

### 3. Environment Variables

The following environment variables need to be set in Render dashboard:

#### Required for Full Functionality:
```
GROQ_API_KEY=your_groq_api_key_here
SUPABASE_URL=your_supabase_url_here  
SUPABASE_KEY=your_supabase_key_here
```

#### Optional (for Reddit integration):
```
REDDIT_CLIENT_ID=your_reddit_client_id_here
REDDIT_CLIENT_SECRET=your_reddit_client_secret_here
REDDIT_USERNAME=your_reddit_username_here
REDDIT_PASSWORD=your_reddit_password_here
```

#### Optional (with defaults):
```
REDDIT_USER_AGENT=NichelyApp/1.0
GROQ_PRIMARY_MODEL=meta-llama/llama-guard-4-12b
GROQ_BACKUP_MODEL=openai/gpt-oss-120b
GROQ_MAX_TOKENS=5000
HOST=0.0.0.0
PORT=8000
```

## 🛠️ Deployment Steps

### 1. Prepare Repository

1. Ensure all changes are committed to your Git repository
2. Push to GitHub/GitLab (Render supports both)

### 2. Create Render Service

1. Go to [Render.com](https://render.com) and sign up/login
2. Click "New +" → "Web Service"
3. Connect your Git repository
4. Render will automatically detect the `render.yaml` file

### 3. Configure Environment Variables

In the Render dashboard:

1. Go to your service → Environment tab
2. Add the required environment variables:

```bash
# Essential for AI functionality
GROQ_API_KEY=gsk_your_groq_api_key_here

# Essential for data storage  
SUPABASE_URL=https://your-project.supabase.co
SUPABASE_KEY=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...

# Optional: Reddit API (for enhanced data)
REDDIT_CLIENT_ID=your_client_id
REDDIT_CLIENT_SECRET=your_client_secret
REDDIT_USERNAME=your_username
REDDIT_PASSWORD=your_password
```

### 4. Deploy

1. Click "Create Web Service"
2. Render will automatically build and deploy your app
3. Access your live app at: `https://your-service-name.onrender.com`

## 🔧 Local Development vs Production

### Local Development
```bash
# Use .env file (create it locally)
cp .env.example .env
# Edit .env with your API keys
python -m uvicorn main:app --host 0.0.0.0 --port 8000 --reload
```

### Production (Render)
- Environment variables are set through Render dashboard
- No `.env` file needed
- Automatic deployment on Git push

## 📁 File Structure Changes

```
nichely/
├── app/
│   ├── config.py          # ✅ Updated for env vars
│   ├── main.py            # ✅ No changes needed
│   ├── render.yaml        # ✅ New deployment config
│   ├── requirements.txt   # ✅ Existing dependencies
│   ├── hosting.md         # ✅ This documentation
│   └── ...
```

## 🔐 API Keys Setup Guide

### 1. Groq API Key (Required)
1. Go to [Groq Console](https://console.groq.com)
2. Sign up and create an API key
3. Add as `GROQ_API_KEY` in Render

### 2. Supabase (Required)
1. Go to [Supabase](https://supabase.com)
2. Create a new project
3. Get URL and anon key from Settings → API
4. Add as `SUPABASE_URL` and `SUPABASE_KEY`

### 3. Reddit API (Optional)
1. Go to [Reddit Apps](https://www.reddit.com/prefs/apps)
2. Create a new app (script type)
3. Get client ID and secret
4. Add all Reddit credentials to Render

## 🚨 Important Notes

### Free Plan Limitations:
- **Sleep Mode:** Service sleeps after 15 minutes of inactivity
- **Cold Starts:** 30-60 second delay when waking up
- **Build Time:** Limited to 20 minutes
- **Bandwidth:** 100GB/month

### Production Considerations:
- **Database:** Use Supabase (included in free tier)
- **Static Files:** Served by FastAPI (works on free plan)
- **Background Tasks:** Limited on free plan

### Monitoring:
- Check logs in Render dashboard
- Set up health checks
- Monitor usage limits

## 🐛 Troubleshooting

### Common Issues:

**Build Fails:**
- Check `requirements.txt` for compatibility
- Verify Python version (3.11 recommended)

**App Won't Start:**
- Check environment variables are set
- Verify port configuration (`$PORT` is used)

**API Errors:**
- Confirm API keys are valid
- Check Supabase project is active

**Slow Response:**
- Expected on free plan (cold starts)
- Consider upgrading for production use

## 💡 Performance Tips

1. **Optimize Dependencies:** Keep `requirements.txt` lean
2. **Database Queries:** Use efficient Supabase queries
3. **Caching:** Implement Redis for production (paid plan)
4. **CDN:** Use Render's CDN for static files

## 🔄 Updating Your App

1. Make changes locally
2. Test locally: `python -m uvicorn main:app --reload`
3. Commit and push to Git
4. Render automatically redeploys (if auto-deploy enabled)

## 📞 Support

- **Render Docs:** [https://render.com/docs](https://render.com/docs)
- **Render Community:** [https://community.render.com](https://community.render.com)
- **FastAPI Docs:** [https://fastapi.tiangolo.com](https://fastapi.tiangolo.com)

---

**Last Updated:** September 25, 2025  
**Deployment Platform:** Render.com (Free Plan)  
**App Framework:** FastAPI + Python 3.11