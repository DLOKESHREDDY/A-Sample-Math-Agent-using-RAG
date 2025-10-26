# 🚀 Cloud Deployment Guide - Pearson Math Tutor

## 📋 Deployment Overview

Your application has **2 components**:
1. **Backend API** (FastAPI/Python) - Needs a Python hosting service
2. **Frontend** (Static HTML) - Can use Netlify ✅

## 🎯 Recommended Deployment Strategy

### **Frontend → Netlify**
### **Backend → Render** (Free tier available)

---

## 🔧 Step 1: Deploy Backend to Render

### Option A: Render.com (Recommended - Free tier available)

1. **Go to**: https://render.com
2. **Sign up** (or log in with GitHub)
3. **Create New → Web Service**
4. **Connect your repository** (push code to GitHub first)
5. **Configure settings**:
   ```
   Build Command: pip install -r requirements.txt
   Start Command: python -m uvicorn main:app --host 0.0.0.0 --port $PORT
   Environment: Python 3
   ```

6. **Add Environment Variables** in Render dashboard:
   ```env
   OPENAI_API_KEY=your_openai_key
   GEMINI_API_KEY=your_gemini_key
   PINECONE_API_KEY=your_pinecone_key
   PINECONE_INDEX_NAME=math-textbooks-free
   PINECONE_ENVIRONMENT=us-west1-gcp-free
   PORT=10000
   ```

7. **Click Deploy**

✅ **Your backend will be live at**: `https://your-app-name.onrender.com`

---

## 🌐 Step 2: Deploy Frontend to Netlify

### Option A: Drag & Drop (Easiest)

1. **Go to**: https://app.netlify.com
2. **Drag and drop** your `frontend` folder
3. **Done!** Your site is live

### Option B: Connect GitHub Repo

1. **Go to**: https://app.netlify.com
2. **Click "Add new site" → Import from Git**
3. **Connect GitHub** and select your repo
4. **Build settings**:
   - Build command: (leave empty)
   - Publish directory: `frontend`

---

## 🔗 Step 3: Connect Frontend to Deployed Backend

After deploying both, update the frontend to use your Render backend URL.

### Update `frontend/index.html`:

Find this line (around line 2):
```javascript
const API_URL = 'http://127.0.0.1:8000';
```

Change to your Render backend URL:
```javascript
const API_URL = 'https://your-app-name.onrender.com';
```

**Redeploy** to Netlify (or drag & drop again).

---

## 📁 Alternative: Quick Deploy with Files

Since you have Netlify, here's the fastest way:

### Quick Method:

1. **Update API URL in frontend**:
   ```bash
   # Edit frontend/index.html
   # Change: const API_URL = 'http://127.0.0.1:8000';
   # To: const API_URL = 'YOUR_RENDER_BACKEND_URL';
   ```

2. **Prepare for deployment**:
   ```bash
   cd /Users/lokeshreddydarukumalli/Documents/Pearson
   
   # Create deployment package
   mkdir deploy_frontend
   cp -r frontend/* deploy_frontend/
   
   # Create _redirects file for SPA
   echo "/index.html 200" > deploy_frontend/_redirects
   ```

3. **Deploy to Netlify**:
   - Go to https://app.netlify.com
   - Drag & drop the `deploy_frontend` folder
   - Done!

---

## 🐳 Alternative: Docker Deployment (All-in-One)

For a complete deployment on a single platform:

### Option 1: Render.com (Full Stack)

1. **Create `Procfile`** in backend:
   ```
   web: uvicorn main:app --host 0.0.0.0 --port $PORT
   ```

2. **Add `static.txt`** to include frontend:
   ```
   include = frontend/*
   ```

3. **Deploy**: Use Render's full-stack deployment

### Option 2: Railway.app

1. Go to https://railway.app
2. New Project → Deploy from GitHub
3. Select your repo
4. Add environment variables
5. Deploy!

---

## 📝 Environment Variables Needed

Add these to your backend deployment platform:

```env
# Required API Keys
OPENAI_API_KEY=sk-proj-...
GEMINI_API_KEY=AIzaS...
PINECONE_API_KEY=pcsk_...

# Configuration
PINECONE_INDEX_NAME=math-textbooks-free
PINECONE_ENVIRONMENT=us-west1-gcp-free
GEMINI_MODEL=gemini-2.0-flash
GEMINI_TEMPERATURE=0.2
GEMINI_MAX_TOKENS=1200

# App Settings
APP_NAME=Pearson Math Tutor
DEBUG=false
LOG_LEVEL=INFO

# Rate Limiting
MAX_REQUESTS_PER_MINUTE=60
MAX_TOKENS_PER_REQUEST=2000

# CORS (Add your Netlify domain)
ALLOWED_ORIGINS=https://your-app-name.netlify.app
```

---

## 🎯 Recommended: Netlify Functions (Serverless)

Netlify can also host your backend with **Netlify Functions**!

### Convert to Serverless:

1. **Create `netlify/functions/api.py`**:
   ```python
   from mangum import Mangum
   from main import app
   
   handler = Mangum(app)
   ```

2. **Add to requirements.txt**:
   ```
   mangum
   ```

3. **Create `netlify.toml`**:
   ```toml
   [build]
     command = "pip install -r requirements.txt"
     functions = "netlify/functions"
   
   [[redirects]]
     from = "/api/*"
     to = "/.netlify/functions/api/:splat"
     status = 200
   
   [[redirects]]
     from = "/*"
     to = "/index.html"
     status = 200
   ```

4. **Deploy**: Everything on Netlify!

---

## 🚀 Quick Start Commands

### 1. Prepare for Deployment

```bash
cd /Users/lokeshreddydarukumalli/Documents/Pearson

# Option 1: Deploy frontend only (need backend separately)
# Update API_URL in frontend/index.html
# Then drag frontend folder to Netlify

# Option 2: Full deployment
git init  # if not already
git add .
git commit -m "Ready for deployment"
git push origin main
```

### 2. Deploy to Render (Backend)

```bash
# Create Procfile
echo "web: python -m uvicorn main:app --host 0.0.0.0 --port \$PORT" > backend/Procfile

# Push to GitHub
git push origin main

# Then go to render.com and deploy
```

### 3. Deploy to Netlify (Frontend)

```bash
# Just drag frontend folder to Netlify
# Or use Netlify CLI:
npm install -g netlify-cli
netlify deploy --prod --dir=frontend
```

---

## ✅ Post-Deployment Checklist

- [ ] Backend deployed and accessible
- [ ] Frontend deployed to Netlify
- [ ] API_URL updated in frontend
- [ ] Environment variables set
- [ ] CORS configured
- [ ] Test the deployed app

---

## 🔧 Troubleshooting

### CORS Errors
Update `config.py`:
```python
allowed_origins: list = [
    "https://your-app.netlify.app",  # Add your Netlify URL
    "https://*.netlify.app",  # Allow all Netlify subdomains
]
```

### Backend Not Starting
Check logs in Render dashboard. Common issues:
- Missing environment variables
- Wrong port configuration
- Pinecone connection issues

### Frontend Can't Connect to Backend
1. Check browser console for errors
2. Verify API_URL is correct
3. Check CORS settings

---

## 📊 Performance Tips

1. **Enable Caching** in Netlify
2. **Compress responses** with gzip
3. **Use CDN** for static assets
4. **Monitor** with Render/Railway dashboards

---

## 🎉 Quick Deploy Commands

```bash
# 1. Update API URL for production
cd /Users/lokeshreddydarukumalli/Documents/Pearson/frontend
# Edit index.html and change API_URL

# 2. Deploy frontend to Netlify (drag & drop frontend folder)

# 3. Create Render account and deploy backend
# Or use: netlify dev  # for local testing with Netlify functions
```

---

**Need Help?** Check the logs in Render/Netlify dashboards for errors.

