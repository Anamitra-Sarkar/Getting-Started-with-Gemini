# Production Deployment Guide

## Backend Deployment (Render)

### Deployment Options

Render supports two deployment methods:
1. **Native Python Environment** (recommended for simplicity)
2. **Docker Container** (recommended for consistency and containerization)

---

### Option 1: Native Python Deployment (Current Setup)

#### Configuration Files

1. **runtime.txt** (Repository Root)
   - Locks Python version to 3.12.1
   - Prevents Render from defaulting to Python 3.13 which breaks Pillow and reportlab builds
   - Content: `python-3.12.1`

2. **render.yaml** (Repository Root)
   - Configured for native Python environment (not Docker)
   - Build command: `pip install -r requirements.txt`
   - Start command: `uvicorn backend.app:app --host 0.0.0.0 --port $PORT`
   - Environment variable: `PYTHONPATH=.`

3. **requirements.txt** (Repository Root)
   - All dependencies pinned to tested versions
   - Critical pins:
     - `Pillow==10.3.0` (incompatible with Python 3.13)
     - `reportlab==3.6.13` (incompatible with Python 3.13)

#### Environment Variables (Render Dashboard)

Required environment variables to set in Render dashboard:

```
PYTHONPATH=.
FRONTEND_ORIGINS=https://getting-started-with-gemini.vercel.app
LOG_LEVEL=info

# Firebase Admin
FIREBASE_PROJECT_ID=<your-firebase-project-id>
FIREBASE_PRIVATE_KEY=<your-firebase-private-key>
FIREBASE_CLIENT_EMAIL=<your-firebase-client-email>

# Google Gemini API
GOOGLE_API_KEY=<your-google-api-key>

# Optional: Tavily Search API
TAVILY_API_KEY=<your-tavily-api-key>

# Optional: Database URL (defaults to SQLite in local storage)
# DATABASE_URL=sqlite:///./backend_data.db
```

---

### Option 2: Docker Deployment

#### Configuration Files

1. **backend/Dockerfile**
   - Python 3.12-slim base image
   - Creates `/app/data` directory for SQLite database with write permissions
   - Sets `PYTHONPATH=/app` for proper module imports
   - Default `DATABASE_URL=sqlite:///./data/backend_data.db`
   - Uses repository root as build context

2. **.dockerignore** (Repository Root)
   - Excludes frontend, node_modules, tests, and media files from Docker build context
   - Reduces build time and image size

#### Building Docker Image Locally

```bash
# From repository root
docker build -f backend/Dockerfile -t vaelis-backend .
```

#### Running Docker Container Locally

```bash
# Run with default settings
docker run -p 8000:8000 -e PORT=8000 vaelis-backend

# Run with environment variables
docker run -p 8000:8000 \
  -e PORT=8000 \
  -e GOOGLE_API_KEY=your-key \
  -e FRONTEND_ORIGINS=https://getting-started-with-gemini.vercel.app \
  -e FIREBASE_PROJECT_ID=your-project-id \
  -e FIREBASE_PRIVATE_KEY="your-private-key" \
  -e FIREBASE_CLIENT_EMAIL=your-email@project.iam.gserviceaccount.com \
  vaelis-backend

# Test health endpoint
curl http://localhost:8000/health
# Expected: {"status":"ok"}
```

#### Docker Deployment on Render

1. Go to Render Dashboard
2. Create a new **Web Service**
3. Select **Docker** as the environment
4. Set **Dockerfile Path**: `backend/Dockerfile`
5. Set **Docker Build Context Directory**: `.` (repository root)
6. Configure environment variables (see below)

#### Environment Variables for Docker Deployment (Render)

```
# Render automatically sets PORT - do not override
# PORT=10000 (set by Render)

FRONTEND_ORIGINS=https://getting-started-with-gemini.vercel.app
LOG_LEVEL=info

# Firebase Admin
FIREBASE_PROJECT_ID=<your-firebase-project-id>
FIREBASE_PRIVATE_KEY=<your-firebase-private-key>
FIREBASE_CLIENT_EMAIL=<your-firebase-client-email>

# Google Gemini API
GOOGLE_API_KEY=<your-google-api-key>

# Optional: Tavily Search API
TAVILY_API_KEY=<your-tavily-api-key>

# Optional: Database URL (defaults to sqlite:///./data/backend_data.db)
# For persistent storage, consider using Render Disks or external DB
# DATABASE_URL=<your-database-url>
```

**Important Notes for Docker Deployment:**
- Render sets the `PORT` environment variable automatically (usually 10000)
- The Dockerfile is configured to use `$PORT` from environment
- SQLite database is stored in `/app/data/backend_data.db` inside container
- For persistent data across deployments, consider:
  - Using Render Persistent Disks mounted to `/app/data`
  - Using an external PostgreSQL database (set `DATABASE_URL`)

### Verification Steps

1. Verify build completes successfully
2. Check service starts without restart loop
3. Test health endpoint: `https://getting-started-with-gemini.onrender.com/health`
4. Expected response: `{"status": "ok"}`

---

## Frontend Deployment (Vercel)

### Configuration Files

1. **vercel.json** (frontend/)
   - Configures Vercel for Create React App deployment
   - Sets build output directory to `build`
   - Configures SPA routing with rewrites to index.html
   - Disables framework detection (this is CRA, not Next.js)

2. **tsconfig.json** (frontend/)
   - Added path alias: `"@/lib/*": ["lib/*"]`
   - Enables clean imports: `import { api } from '@/lib/api'`

3. **lib/api.ts** (frontend/lib/)
   - Centralized API client with all backend endpoints
   - Handles authentication via Firebase tokens
   - Uses `NEXT_PUBLIC_API_BASE_URL` environment variable

4. **lib/firebase.tsx** (frontend/lib/)
   - Firebase authentication setup
   - Context provider for user state

5. **package.json** (frontend/)
   - `packageManager` field removed to prevent lockfile mismatch
   - Allows Vercel to auto-detect npm from `package-lock.json`
   - Prevents yarn/npm conflicts during build

6. **craco.config.js** (frontend/)
   - Gracefully handles missing plugin modules with try/catch
   - Provides no-op fallbacks if plugins are not found
   - Prevents dev server crashes on optional plugins

### Vercel Project Settings

**IMPORTANT**: In the Vercel dashboard, configure the following project settings:

1. **Root Directory**: Set to `frontend` (not the repository root)
2. **Framework Preset**: Select "Create React App" or "Other"
3. **Build Command**: `npm run build` (auto-detected from vercel.json)
4. **Output Directory**: `build` (auto-detected from vercel.json)
5. **Install Command**: `npm install` or `npm ci`

### Environment Variables (Vercel Dashboard)

Required environment variables to set in Vercel dashboard:

```
# Backend API URL
NEXT_PUBLIC_API_BASE_URL=https://getting-started-with-gemini.onrender.com

# Firebase Configuration
NEXT_PUBLIC_FIREBASE_API_KEY=AIzaSyDEAOr3iqU6TJZ6uztMvC5mquZECPcBkkE
NEXT_PUBLIC_FIREBASE_AUTH_DOMAIN=fir-config-d3c36.firebaseapp.com
NEXT_PUBLIC_FIREBASE_PROJECT_ID=fir-config-d3c36
NEXT_PUBLIC_FIREBASE_STORAGE_BUCKET=fir-config-d3c36.firebasestorage.app
NEXT_PUBLIC_FIREBASE_MESSAGING_SENDER_ID=477435579926
NEXT_PUBLIC_FIREBASE_APP_ID=1:477435579926:web:d370e9fb5a3c5a05316f37
NEXT_PUBLIC_FIREBASE_MEASUREMENT_ID=G-PXZBD6HN1X
```

### Module Resolution

All components now use the `@/lib/api` path alias instead of relative imports:

- ✅ `import { getIdToken } from '@/lib/api'`
- ❌ `import { getIdToken } from '../lib/api'`
- ❌ `import { getIdToken } from '../../../lib/api'`

This prevents module resolution errors in Vercel's strict build environment.

### Verification Steps

1. Verify build completes successfully
2. Check deployment at: `https://getting-started-with-gemini.vercel.app`
3. Test frontend loads without errors
4. Test API calls to backend work correctly

---

## Important Notes

### Backend

- **DO NOT** remove or modify `runtime.txt` - it's critical for Python version control
- **DO NOT** upgrade Pillow or reportlab without testing on Python 3.12 first
- **DO NOT** use `--reload` flag in production start command
- Render will automatically use `runtime.txt` when `env: python` is set

### Frontend

- **DO NOT** use relative imports for `lib/api` - always use `@/lib/api`
- **DO NOT** hardcode backend URLs - use `NEXT_PUBLIC_API_BASE_URL`
- **DO NOT** commit `.env.local` to repository
- Path alias `@/lib/*` requires `baseUrl: "."` in tsconfig.json

### Security

- Never commit Firebase private keys or API keys to the repository
- All sensitive configuration must be set via platform environment variables
- Frontend environment variables must be prefixed with `NEXT_PUBLIC_` to be accessible in browser
- Backend environment variables should NOT be prefixed and remain server-side only

---

## Troubleshooting

### Backend Build Failures

**Issue**: `Pillow` or `reportlab` build fails with `KeyError: '__version__'`

**Solution**: 
- Verify `runtime.txt` exists at repository root
- Verify `runtime.txt` contains exactly: `python-3.12.1`
- Check Render build logs confirm Python 3.12.1 is being used

**Issue**: Import errors like `ModuleNotFoundError: No module named 'backend'`

**Solution**:
- Verify `PYTHONPATH=.` is set in environment variables
- Check start command uses `backend.app:app` not `app:app`

### Frontend Build Failures

**Issue**: `Module not found: Can't resolve '../lib/api'`

**Solution**:
- Search codebase for any remaining relative imports
- Replace with `@/lib/api` path alias
- Verify `tsconfig.json` has `baseUrl: "."` and paths configured

**Issue**: `Cannot find module '@/lib/api'`

**Solution**:
- Verify `frontend/lib/api.ts` file exists and is committed
- Check `.gitignore` doesn't block `frontend/lib/` directory
- Rebuild to clear Next.js cache

---

## Testing Locally

### Backend

```bash
# Install dependencies
cd /path/to/repo
python3.12 -m pip install -r requirements.txt

# Set environment variables (create .env file)
export PYTHONPATH=.
export GOOGLE_API_KEY=your-key

# Run server
uvicorn backend.app:app --host 0.0.0.0 --port 8000

# Test health endpoint
curl http://localhost:8000/health
```

### Frontend

```bash
# Install dependencies
cd frontend
npm install

# Build for production
npm run build

# Run production build locally
npm start

# Or run development server
npm run dev
```

---

## Deployment Checklist

### Before Deploying Backend

- [ ] `runtime.txt` exists at repository root with `python-3.12.1`
- [ ] `requirements.txt` has pinned versions for Pillow and reportlab
- [ ] `render.yaml` specifies `env: python` and correct start command
- [ ] All environment variables are set in Render dashboard
- [ ] No `.env` files committed to repository

### Before Deploying Frontend

- [ ] `frontend/lib/api.ts` exists and is committed
- [ ] `frontend/lib/firebase.tsx` exists and is committed
- [ ] `tsconfig.json` has path alias configuration
- [ ] All imports use `@/lib/api` (no relative imports)
- [ ] All environment variables are set in Vercel dashboard with `NEXT_PUBLIC_` prefix
- [ ] Build succeeds locally: `npm run build`

### After Deployment

- [ ] Backend health endpoint returns 200 OK
- [ ] Backend service is running (no restart loops)
- [ ] Frontend site loads without errors
- [ ] Frontend can communicate with backend API
- [ ] Authentication flow works (if applicable)
- [ ] No console errors in browser developer tools
