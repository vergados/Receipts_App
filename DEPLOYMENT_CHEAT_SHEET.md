# 📄 Receipts App Deployment Cheat Sheet

**Start to finish: ~45 minutes** | **Cost: $21/month**

---

## ☑️ PRE-FLIGHT (Local Setup)

```bash
cd /Users/jasonalaounis/Downloads/receipts-app

# Generate secret keys (save these!)
openssl rand -hex 32  # → SECRET_KEY
openssl rand -hex 32  # → JWT_SECRET_KEY

# Commit code
git add .
git commit -m "Ready for deployment"
git push origin main
```

---

## 1️⃣ DATABASE (Railway) - 5 min

**Setup:**
1. Go to https://railway.app → Sign in with GitHub
2. Click **New Project** → **Provision PostgreSQL**
3. Click PostgreSQL service → **Connect** tab
4. Copy **Postgres Connection URL**

```
postgresql://postgres:xxx@containers-us-west-xxx.railway.app:5432/railway
```

**Save this!** ☑️

---

## 2️⃣ MEDIA STORAGE (Backblaze B2) - 10 min

**Create Bucket:**
1. https://www.backblaze.com/b2 → Sign up
2. **Buckets** → **Create Bucket**
   - Name: `receipts-media`
   - Files: **Public**
3. Click **Create**

**Get Credentials:**
1. **App Keys** → **Add New Application Key**
   - Name: `receipts-app`
   - Access: `receipts-media` bucket
   - Permissions: **Read and Write**
2. **Save these immediately:**
   ```
   keyID: 000abc123...
   applicationKey: K000xxx...
   ```

**Get Endpoint:**
1. Go back to **Buckets** → click `receipts-media`
2. Note the **Endpoint**: `https://s3.us-west-002.backblazeb2.com`

**Save all three!** ☑️

---

## 3️⃣ BACKEND (Railway) - 15 min

**Deploy:**
1. Railway dashboard → Your project → **New Service** → **GitHub Repo**
2. Connect GitHub → Select `receipts-app` repo
3. Click the new service

**Configure:**
1. **Settings** → Set **Root Directory**: `backend`
2. **Settings** → Set **Start Command**:
   ```
   uvicorn app.main:app --host 0.0.0.0 --port $PORT
   ```

**Environment Variables:**
1. Click **Variables** → **Raw Editor** → Paste:

```bash
DATABASE_URL=${{Postgres.DATABASE_URL}}
SECRET_KEY=<your-first-hex-key>
JWT_SECRET_KEY=<your-second-hex-key>
FRONTEND_URL=https://receipts-app.vercel.app
S3_ENDPOINT=https://s3.us-west-002.backblazeb2.com
S3_ACCESS_KEY=<your-backblaze-keyID>
S3_SECRET_KEY=<your-backblaze-applicationKey>
S3_BUCKET=receipts-media
S3_REGION=us-west-002
NEWSROOM_ENABLED=true
NEWSROOM_BETA_USERS=[]
MAX_IMAGE_SIZE_MB=50
MAX_VIDEO_SIZE_MB=100
```

2. Click **Save** (auto-deploys)

**Get Backend URL:**
1. **Settings** → **Networking** → **Generate Domain**
2. Copy URL: `https://receipts-backend-production-xxx.up.railway.app`

**Save this!** ☑️

**Run Migrations:**
```bash
# Install Railway CLI
npm install -g @railway/cli

# Login and run migrations
railway login
railway link  # Select your project → backend service
railway run alembic upgrade head
```

**Test:** Visit `https://your-backend.railway.app/health` → Should see `{"status":"ok"}`

---

## 4️⃣ FRONTEND (Vercel) - 10 min

**Prepare:**
```bash
cd frontend

# Create production env file
echo "NEXT_PUBLIC_API_URL=https://your-backend.railway.app/api/v1" > .env.production
```

**Deploy:**
```bash
# Install Vercel CLI
npm install -g vercel

# Login
vercel login  # Opens browser

# Deploy
vercel

# Prompts:
# Set up and deploy? → Yes
# Which scope? → Your account
# Link existing? → No
# Project name? → receipts-app
# Directory? → ./
# Override settings? → No
```

**Configure Production:**
1. Go to https://vercel.com/dashboard
2. Select `receipts-app` → **Settings** → **Environment Variables**
3. Add:
   ```
   Key: NEXT_PUBLIC_API_URL
   Value: https://your-backend.railway.app/api/v1
   Environment: Production
   ```
4. **Deployments** → Click latest → **...** → **Redeploy**

**Get Frontend URL:** `https://receipts-app.vercel.app`

**Save this!** ☑️

---

## 5️⃣ CONNECT FRONTEND ↔ BACKEND - 2 min

**Update Backend CORS:**
1. Railway → Backend service → **Variables**
2. Edit `FRONTEND_URL`:
   ```
   FRONTEND_URL=https://receipts-app.vercel.app
   ```
3. Save (auto-redeploys)

---

## 6️⃣ VERIFICATION - 5 min

**Test Backend:**
- [ ] `https://your-backend.railway.app/health` → `{"status":"ok"}`
- [ ] `https://your-backend.railway.app/api/v1/health` → No error

**Test Frontend:**
- [ ] Homepage loads
- [ ] No console errors (F12 → Console)
- [ ] Register new user works
- [ ] Login works
- [ ] Create receipt works
- [ ] Image upload works

---

## 7️⃣ MONITORING (Optional) - 5 min

**Sentry (Error Tracking):**
```bash
# Frontend
cd frontend
npm install @sentry/nextjs
npx @sentry/wizard@latest -i nextjs

# Backend
cd backend
pip install sentry-sdk[fastapi]
# Add to main.py (see docs)
```

**UptimeRobot (Uptime Alerts):**
1. https://uptimerobot.com → Sign up
2. **Add New Monitor**
   - Type: HTTP(s)
   - URL: `https://your-backend.railway.app/health`
   - Interval: 5 minutes
3. Save

---

## 🚨 EMERGENCY ROLLBACK

**Frontend:**
1. Vercel dashboard → **Deployments**
2. Find last working deploy → **...** → **Promote to Production**

**Backend:**
1. Railway dashboard → **Deployments**
2. Click previous deployment → **Redeploy**

---

## 💰 MONTHLY COSTS

```
Railway Postgres:  $10
Railway Backend:   $5
Vercel:            $0 (free tier)
Backblaze B2:      $5
─────────────────────
TOTAL:             $20/month
```

---

## 📝 CREDENTIALS VAULT

**Fill this out as you go:**

```
DATABASE_URL:
postgresql://postgres:_______________@_______________.railway.app:5432/railway

SECRET_KEY:
_______________________________________________________________

JWT_SECRET_KEY:
_______________________________________________________________

BACKBLAZE_KEY_ID:
_______________________________________________________________

BACKBLAZE_APP_KEY:
_______________________________________________________________

BACKEND_URL:
https://_____________________________________.up.railway.app

FRONTEND_URL:
https://_____________________________________.vercel.app
```

---

## ✅ DONE!

**Your app is live at:** `https://receipts-app.vercel.app`

**Next steps:**
1. Create admin account (see main docs)
2. Create first verified newsroom
3. Monitor errors in Sentry
4. Check costs weekly in Railway/Vercel dashboards

---

**Questions? Check logs:**
- Railway: Service → Logs tab (real-time)
- Vercel: Project → Deployments → Click build → View logs

**Auto-deploy enabled:** Push to GitHub `main` branch = automatic deploy

---

*Print this page and check off each step as you complete it!*
