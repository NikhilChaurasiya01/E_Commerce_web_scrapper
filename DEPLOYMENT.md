# Deployment Guide for Render

## Step-by-Step Instructions

### 1. ✅ Code is Already Pushed to GitHub
Your repository is live at: https://github.com/NikhilChaurasiya01/E_Commerce_web_scrapper

### 2. Deploy on Render

#### A. Sign Up / Log In to Render
1. Go to https://render.com
2. Sign up or log in with your GitHub account

#### B. Create New Web Service
1. Click **"New +"** button in the top right
2. Select **"Web Service"**

#### C. Connect Your Repository
1. Click **"Connect a repository"** 
2. If prompted, authorize Render to access your GitHub
3. Search for and select: **E_Commerce_web_scrapper**

#### D. Configure the Service

Fill in these settings:

**Basic Settings:**
- **Name**: `smartcompare` (or any name you prefer)
- **Region**: Choose closest to your users
- **Branch**: `main`
- **Root Directory**: Leave blank
- **Runtime**: `Python 3`

**Build & Deploy:**
- **Build Command**: `pip install -r requirements.txt`
- **Start Command**: `gunicorn app:app`

**Instance Type:**
- Select **"Free"** tier (for testing)
- Or **"Starter"** ($7/month) for better performance

**Advanced Settings (Optional):**
- **Auto-Deploy**: Yes (automatically deploy on git push)

#### E. Environment Variables (if needed)
No environment variables are required for basic setup.

#### F. Create Web Service
1. Click **"Create Web Service"** button
2. Wait 2-5 minutes for deployment to complete
3. You'll see build logs in real-time

### 3. Access Your Deployed Application

Once deployment succeeds:
- Your app URL will be: `https://smartcompare.onrender.com` (or your chosen name)
- Click the URL to open your live application!

### 4. Verify Deployment

Test these endpoints:
- Homepage: `https://your-app.onrender.com/`
- API Products: `https://your-app.onrender.com/api/products`
- API Stats: `https://your-app.onrender.com/api/stats`

## Important Notes

### Free Tier Limitations
- **Spin down after 15 minutes** of inactivity
- First request after spin-down takes 30-60 seconds
- 750 hours/month free usage

### Upgrading Performance
For production use, consider:
- **Starter Plan** ($7/month) - No spin down, better resources
- **Standard Plan** ($25/month) - More memory and CPU

### Custom Domain (Optional)
1. Go to your service settings
2. Click "Custom Domain"
3. Add your domain and follow DNS instructions

### Monitoring
- View logs in Render dashboard
- Monitor metrics (CPU, Memory, Bandwidth)
- Set up alerts for downtime

## Troubleshooting

### Build Fails
- Check `requirements.txt` is correct
- Verify Python version in `runtime.txt`
- Review build logs for errors

### App Not Loading
- Check start command: `gunicorn app:app`
- Verify port configuration (PORT environment variable)
- Check application logs

### 500 Errors
- Ensure CSV files are in repository
- Check file paths are correct
- Review error logs in Render dashboard

## Files Configured for Deployment

✅ **requirements.txt** - Python dependencies
✅ **runtime.txt** - Python version (3.12.4)
✅ **app.py** - Updated with PORT environment variable
✅ **.gitignore** - Excludes unnecessary files
✅ **README.md** - Project documentation

## Next Steps After Deployment

1. **Test all features** on live URL
2. **Share the link** with users
3. **Monitor performance** in Render dashboard
4. **Update code** by pushing to GitHub (auto-deploys if enabled)

## Updating Your App

To update the deployed application:

```bash
cd "d:\project\sem2\project product comprasion"
git add .
git commit -m "Your update message"
git push origin main
```

Render will automatically rebuild and deploy (if auto-deploy is enabled).

## Support

- Render Docs: https://render.com/docs
- GitHub Repo: https://github.com/NikhilChaurasiya01/E_Commerce_web_scrapper
- Render Community: https://community.render.com/

---

🎉 **Congratulations!** Your SmartCompare app is ready to deploy!
