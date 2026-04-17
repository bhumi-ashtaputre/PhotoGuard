# PhotoGuard - Render Deployment Guide

## ✅ Pre-Deployment Checklist

Your app has been prepared for Render! Here's what I did:
- ✅ Added `Procfile` (tells Render how to run your app)
- ✅ Added `runtime.txt` (specifies Python 3.11)
- ✅ Updated `requirements.txt` (added gunicorn for production)
- ✅ Modified `app.py` (removed hardcoded secrets, added proper port binding)
- ✅ Added `.gitignore` (excludes unnecessary files)

## 🚀 Steps to Deploy on Render

### Step 1: Create a GitHub Repository
1. Go to https://github.com/new
2. Create a new repository called `photoguard`
3. Do NOT initialize with README (we'll push our code)

### Step 2: Push Your Code to GitHub

Open terminal in your PhotoGuard folder and run:

```bash
git init
git add .
git commit -m "Initial commit: PhotoGuard app ready for Render"
git branch -M main
git remote add origin https://github.com/YOUR_USERNAME/photoguard.git
git push -u origin main
```

Replace `YOUR_USERNAME` with your actual GitHub username.

### Step 3: Deploy on Render
1. Go to https://render.com/
2. Sign up with GitHub (easiest option)
3. Click **"New +"** → **"Web Service"**
4. Select your `photoguard` repository
5. Fill in the details:
   - **Name**: `photoguard`
   - **Environment**: `Python 3`
   - **Build Command**: `pip install -r requirements.txt`
   - **Start Command**: `gunicorn app:app`
6. Click **"Create Web Service"**

### Step 4: Wait for Deployment
- Render will automatically build and deploy your app
- You'll see a live URL like: `https://photoguard-xxx.onrender.com`
- Check the deploy logs if there are any issues

### Step 5: (Optional) Add Environment Variables
If you want to use a custom secret key:
1. In Render dashboard, go to your service
2. Click **"Environment"**
3. Add variable: `SECRET_KEY` = `your-secure-key-here`
4. Click **"Save"** (app auto-redeploys)

## 📝 Important Notes

### Current Limitations (for free Render tier)
- **Data resets**: Your user accounts and uploaded photos disappear when the server restarts (free tier)
- **File storage**: Uploads are stored temporarily (not persistent)
- **In-memory data**: All user data, social links, trusted friends are lost on restart

### ⚠️ For Production, You'll Need:
1. **Persistent Database** - Add PostgreSQL to Render ($7/month)
2. **File Storage** - Use cloud storage (AWS S3, Azure Blob, etc.)
3. **Upgrade Render Plan** - Free plan spins down after 15 minutes of inactivity

### Upgrade Path (When Ready)
For a production-ready app:
```
Render Dashboard → Add PostgreSQL Database ($7/month)
Connect DATABASE_URL to your Flask app
Upgrade free plan to Starter ($7/month for always-on)
```

## 🔗 Your App URL
Once deployed, visit: `https://photoguard-[random-id].onrender.com`

## ❓ Troubleshooting
- **Build fails?** Check that all files are in the repo (Procfile, runtime.txt, requirements.txt)
- **App crashes?** Check Render logs for errors
- **Port issues?** The app now reads PORT from environment (already fixed!)

## 📚 Render Documentation
- https://render.com/docs/deploy-flask

Good luck! 🎉
