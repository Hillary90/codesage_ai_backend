# Deploy CodeSage Backend to Render

## Step-by-Step Deployment Guide

### Step 1: Prepare Your Repository

1. Make sure all files are committed to GitHub:
```bash
cd codesage_ai_backend
git add .
git commit -m "chore: prepare for Render deployment"
git push origin main
```

### Step 2: Create Render Account

1. Go to [render.com](https://render.com)
2. Click "Get Started for Free"
3. Sign up with GitHub (recommended)
4. Authorize Render to access your repositories

### Step 3: Create PostgreSQL Database

1. From Render Dashboard, click "New +"
2. Select "PostgreSQL"
3. Configure:
   - **Name**: `codesage-db`
   - **Database**: `codesage`
   - **User**: `codesage`
   - **Region**: Choose closest to you
   - **Plan**: Free (or paid for production)
4. Click "Create Database"
5. Wait for database to be created
6. **IMPORTANT**: Copy the "Internal Database URL" (you'll need this)

### Step 4: Create Web Service

1. From Render Dashboard, click "New +"
2. Select "Web Service"
3. Connect your GitHub repository:
   - Click "Connect account" if not connected
   - Find and select your `codesage_ai_backend` repository
4. Configure the service:
   - **Name**: `codesage-backend`
   - **Region**: Same as database
   - **Branch**: `main`
   - **Root Directory**: Leave empty (or specify if in monorepo)
   - **Runtime**: `Python 3`
   - **Build Command**: `./build.sh`
   - **Start Command**: `gunicorn app:app`
   - **Plan**: Free (or paid for production)

### Step 5: Add Environment Variables

In the "Environment" section, add these variables:

| Key | Value |
|-----|-------|
| `FLASK_APP` | `app.py` |
| `FLASK_ENV` | `production` |
| `SECRET_KEY` | Click "Generate" or use your own |
| `JWT_SECRET_KEY` | Click "Generate" or use your own |
| `DATABASE_URL` | Paste the Internal Database URL from Step 3 |
| `REDIS_URL` | (Optional) Add if using Redis |
| `OPENAI_API_KEY` | Your OpenAI API key |
| `ANTHROPIC_API_KEY` | Your Anthropic API key (optional) |
| `GITHUB_TOKEN` | Your GitHub personal access token |
| `CORS_ORIGINS` | Your frontend URL (e.g., `https://your-frontend.vercel.app`) |

### Step 6: Deploy

1. Click "Create Web Service"
2. Render will automatically:
   - Clone your repository
   - Install dependencies
   - Run migrations
   - Start your application
3. Wait for deployment to complete (5-10 minutes)
4. You'll see "Live" status when ready

### Step 7: Get Your Backend URL

1. Your backend will be available at: `https://codesage-backend.onrender.com`
2. Test the health endpoint: `https://codesage-backend.onrender.com/health`
3. Copy this URL for your frontend configuration

### Step 8: Update Frontend

Update your frontend `.env` file:
```env
VITE_API_URL=https://codesage-backend.onrender.com/api
```

### Step 9: Configure Custom Domain (Optional)

1. Go to your web service settings
2. Click "Custom Domain"
3. Add your domain (e.g., `api.codesage.com`)
4. Follow DNS configuration instructions

## Important Notes

### Free Tier Limitations
- Service spins down after 15 minutes of inactivity
- First request after spin-down takes 30-60 seconds
- 750 hours/month free (enough for one service)

### Database Backups
- Free tier: No automatic backups
- Paid tier: Daily automatic backups

### Monitoring
- Check logs: Dashboard → Your Service → Logs
- Set up health checks: Dashboard → Your Service → Health & Alerts

### Troubleshooting

**Build fails:**
- Check `build.sh` has correct permissions
- Verify all dependencies in `requirements.txt`
- Check Python version in `runtime.txt`

**Database connection fails:**
- Verify DATABASE_URL is correct
- Check database is in same region
- Ensure migrations ran successfully

**App crashes:**
- Check logs in Render dashboard
- Verify all environment variables are set
- Test locally with production settings

**CORS errors:**
- Update CORS_ORIGINS with your frontend URL
- Check CORS configuration in `app.py`

## Useful Commands

### View Logs
```bash
# From Render dashboard or use Render CLI
render logs -s codesage-backend
```

### Run Migrations Manually
```bash
# From Render Shell (Dashboard → Shell)
flask db upgrade
```

### Restart Service
```bash
# From dashboard: Manual Deploy → Clear build cache & deploy
```

## Next Steps

1. ✅ Backend deployed on Render
2. 🔄 Deploy frontend on Vercel/Netlify
3. 🔐 Set up custom domain
4. 📊 Configure monitoring and alerts
5. 🚀 Set up CI/CD pipeline

## Support

- Render Docs: https://render.com/docs
- Render Community: https://community.render.com
- GitHub Issues: Create issue in your repository
