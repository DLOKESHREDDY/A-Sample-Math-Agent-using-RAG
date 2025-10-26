# 🚀 Quick Deployment Guide

## Step 1: Deploy Backend to Render (5 minutes)

1. Go to: https://render.com
2. Sign up (use GitHub)
3. Click **"New +"** → **Web Service**
4. **Connect your GitHub** and select this repo
5. Configure:
   - **Name**: pearson-math-tutor (or your choice)
   - **Region**: United States
   - **Branch**: main
   - **Build Command**: `cd backend && pip install -r requirements.txt`
   - **Start Command**: `cd backend && python -m uvicorn main:app --host 0.0.0.0 --port $PORT`

6. Click **"Advanced"** and add **Environment Variables**:

   ```env
   OPENAI_API_KEY=your_openai_api_key_here
   PINECONE_API_KEY=your_pinecone_api_key_here
   GEMINI_API_KEY=your_gemini_api_key_here
   PINECONE_INDEX_NAME=math-textbooks-free
   PINECONE_ENVIRONMENT=us-west1-gcp-free
   PORT=10000
   APP_NAME=Pearson Math Tutor
   DEBUG=false
   LOG_LEVEL=INFO
   MAX_REQUESTS_PER_MINUTE=60
   ```

7. Click **"Create Web Service"**
8. Wait ~5 minutes for deployment
9. **Copy your backend URL**: `https://pearson-math-tutor.onrender.com`

---

## Step 2: Deploy Frontend to Netlify (2 minutes)

### Option A: Drag & Drop (Easiest)

1. Update the backend URL in `frontend/index.html` (line 74):
   ```javascript
   : 'https://YOUR_RENDER_URL.onrender.com/chat';
   ```
   Replace `YOUR_RENDER_URL` with your actual Render URL

2. Go to: https://app.netlify.com
3. **Drag and drop** the `frontend` folder
4. Done! Your site is live at: `https://random-name.netlify.app`

### Option B: Git Push (Recommended)

1. Push to GitHub first:
   ```bash
   cd /Users/lokeshreddydarukumalli/Documents/Pearson
   git init  # if not already
   git add .
   git commit -m "Ready for deployment"
   git branch -M main  # if needed
   git remote add origin YOUR_GITHUB_REPO_URL
   git push -u origin main
   ```

2. Go to: https://app.netlify.com
3. Click **"Add new site"** → **"Import from Git"**
4. Connect GitHub and select your repo
5. **Build settings**:
   - **Base directory**: `frontend`
   - **Publish directory**: `frontend`
6. **Add environment variable** (optional):
   ```
   VITE_API_URL=https://pearson-math-tutor.onrender.com
   ```
7. Click **"Deploy site"**

---

## Step 3: Update CORS (Backend)

After getting your Netlify URL, update `backend/config.py`:

```python
allowed_origins: list = [
    "https://YOUR_NETLIFY_APP.netlify.app",  # Add your Netlify URL
    "https://*.netlify.app",  # Allow all Netlify subdomains
]
```

Then **redeploy** the backend on Render.

---

## ✅ You're Done!

- **Frontend**: `https://your-app.netlify.app`
- **Backend**: `https://your-app.onrender.com`

---

## 🔧 Troubleshooting

### CORS Error
1. Update `backend/config.py` with your Netlify URL
2. Redeploy backend on Render

### Backend Not Starting
Check logs in Render dashboard for errors

### Frontend Can't Connect
1. Check browser console (F12)
2. Verify API_URL is correct
3. Check CORS settings

---

## 📞 Need Help?

Check the logs:
- **Render**: Dashboard → Your Service → Logs
- **Netlify**: Site Settings → Build & Deploy → Deploys

