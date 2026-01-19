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

# Groq API (using GEMINI_API_KEY name for compatibility)
GEMINI_API_KEY=<your-groq-api-key>
GEMINI_API_URL=https://api.groq.com/openai/v1

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

# Groq API (using GEMINI_API_KEY name for compatibility)
GEMINI_API_KEY=<your-groq-api-key>
GEMINI_API_URL=https://api.groq.com/openai/v1

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

---

## MongoDB Atlas Integration

### Overview

The application now supports MongoDB Atlas for persistent storage using Motor (async MongoDB driver) and Beanie (async ODM). This is in addition to the existing SQLite/SQL database support.

### MongoDB Atlas Setup

#### 1. Create MongoDB Atlas Cluster

1. Go to [MongoDB Atlas](https://www.mongodb.com/cloud/atlas)
2. Create a free M0 cluster (sufficient for development/testing)
3. Choose cloud provider and region closest to your Render deployment
4. Wait for cluster provisioning

#### 2. Configure Network Access

1. Navigate to **Network Access** in Atlas dashboard
2. Click **Add IP Address**
3. Select **Allow Access from Anywhere** (0.0.0.0/0) for Render
   - Note: For production, consider restricting to specific IP ranges
4. Save changes

#### 3. Create Database User

1. Go to **Database Access** → **Add New Database User**
2. Select **Password** authentication method
3. Create username and strong password
4. Assign **Read and write to any database** role
5. Save user

#### 4. Get Connection String

1. Click **Connect** on your cluster
2. Choose **Connect your application**
3. Select **Driver: Python 3.12+**
4. Copy the connection string:
   ```
   mongodb+srv://username:<password>@cluster0.xxxxx.mongodb.net/?retryWrites=true&w=majority
   ```
5. Replace `<password>` with your actual database password
6. Optionally specify database name:
   ```
   mongodb+srv://username:password@cluster0.xxxxx.mongodb.net/vaelis?retryWrites=true&w=majority
   ```

#### 5. Production-Ready Connection String

For production deployments with multiple instances:
```
mongodb+srv://username:password@cluster.mongodb.net/vaelis?retryWrites=true&w=majority&maxPoolSize=50&serverSelectionTimeoutMS=5000
```

Parameters explained:
- `maxPoolSize=50`: Allows up to 50 concurrent connections per instance
- `serverSelectionTimeoutMS=5000`: 5 second timeout for server selection
- `retryWrites=true`: Automatically retry failed write operations
- `w=majority`: Ensures writes are acknowledged by majority of replica set

### Render Environment Variables for MongoDB

Add these environment variables in Render dashboard:

```bash
# MongoDB Atlas (Required for MongoDB features)
MONGODB_URI=mongodb+srv://username:password@cluster.mongodb.net/vaelis?retryWrites=true&w=majority&maxPoolSize=50

# Existing variables (keep these)
PYTHONPATH=.
FRONTEND_ORIGINS=https://your-frontend-url.vercel.app,http://localhost:3000
LOG_LEVEL=INFO
GEMINI_API_KEY=your_groq_api_key
GEMINI_API_URL=https://api.groq.com/openai/v1
JWT_SECRET_KEY=your_jwt_secret_here

# Optional: File upload size limit
MAX_UPLOAD_SIZE_MB=10
```

### MongoDB Features

#### Health Check Endpoint

The `/health` endpoint now checks MongoDB connectivity:

```bash
curl https://your-backend.onrender.com/health
```

Response when MongoDB is connected:
```json
{
  "status": "ok",
  "sql_db": "connected",
  "mongo_db": "connected"
}
```

Response when MongoDB is unavailable:
```json
{
  "status": "degraded",
  "sql_db": "connected",
  "mongo_db": "unreachable"
}
```

#### MongoDB-Based Agents Router

New endpoint: `/agents-mongo/`

This provides MongoDB-backed agent persistence with the following features:
- Async operations using Motor and Beanie
- MongoDB ObjectId support
- Compound indexes for efficient queries
- Owner-based access control

Endpoints:
- `GET /agents-mongo/stats` - Dashboard statistics
- `POST /agents-mongo/` - Create agent
- `GET /agents-mongo/` - List user's agents
- `GET /agents-mongo/{agent_id}` - Get agent by ID
- `PUT /agents-mongo/{agent_id}` - Update agent
- `PATCH /agents-mongo/{agent_id}` - Partial update agent
- `DELETE /agents-mongo/{agent_id}` - Delete agent

### Testing MongoDB Integration

#### 1. Verify MongoDB Connection

Check Render logs for startup message:
```
MongoDB / Beanie initialized
```

#### 2. Test Health Endpoint

```bash
curl https://your-backend.onrender.com/health
```

#### 3. Test Agent Creation

Using curl:
```bash
curl -X POST https://your-backend.onrender.com/agents-mongo/ \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"name": "Test Agent", "description": "Testing MongoDB"}'
```

#### 4. Verify Persistence

1. Create an agent via API or frontend
2. Restart the Render service
3. List agents - should still exist

### Troubleshooting MongoDB Issues

#### Issue: "MONGODB_URI not set"

**Solution**: Add `MONGODB_URI` environment variable in Render dashboard

#### Issue: "mongo_db: unreachable"

**Causes and solutions**:
1. **Network access**: Verify 0.0.0.0/0 is allowed in Atlas Network Access
2. **Credentials**: Check username/password in connection string
3. **Connection string format**: Ensure proper URL encoding of special characters
4. **Cluster status**: Verify cluster is running in Atlas dashboard

#### Issue: "Authentication failed"

**Solution**: 
1. Verify database user exists in Atlas
2. Check password in connection string (URL encode special characters)
3. Ensure user has correct permissions

#### Issue: Slow startup

**Solution**: Add `serverSelectionTimeoutMS=5000` to connection string

### MongoDB Atlas Monitoring

1. Go to Atlas cluster dashboard
2. Click **Metrics** tab
3. Monitor:
   - **Connections**: Should be < maxPoolSize per instance
   - **Operations**: Read/write operations per second
   - **Network**: Data transfer
   - **Storage**: Database size

### Data Migration (SQL to MongoDB)

If migrating existing data from SQL to MongoDB:

1. Create migration script in `tools/migrations/`
2. Set environment variables:
   ```bash
   MONGODB_URI=your_atlas_uri
   LEGACY_DATABASE_URL=sqlite:///./backend_data.db
   ```
3. Run migration:
   ```bash
   python tools/migrations/sql_to_mongo.py
   ```

Note: This is optional - the app supports both SQL and MongoDB concurrently.

### CORS Configuration Enhancement

The CORS middleware now properly handles comma-separated origins:

```python
# In Render, set:
FRONTEND_ORIGINS=https://app.example.com,https://admin.example.com,http://localhost:3000
```

This allows multiple frontend origins for:
- Production frontend
- Admin dashboard
- Local development

### Security Considerations for MongoDB

1. **Never commit connection strings** - Use environment variables only
2. **Use strong passwords** - Generate with password manager
3. **Restrict network access** - Use specific IP ranges when possible
4. **Monitor access logs** - Review in Atlas Security → Access Manager
5. **Enable encryption** - Atlas encrypts data at rest by default
6. **Rotate credentials periodically** - Update database user passwords
7. **Use Secret Files for sensitive data** - Firebase JSON via Render Secret Files

### Scaling with MongoDB

#### Horizontal Scaling

- Render auto-scaling on paid plans
- Increase `maxPoolSize` in connection string
- Monitor connection count in Atlas

#### Vertical Scaling

- Upgrade MongoDB Atlas cluster tier (M10, M20, M30, etc.)
- More RAM and CPU for complex queries
- Dedicated clusters for production

#### Read Replicas

- Available on M10+ clusters
- Distribute read load across replicas
- Specify in connection string for read preference

### MongoDB Best Practices

1. **Indexes**: Agent model has indexes on `owner_id` and compound `(owner_id, name)`
2. **Connection pooling**: `maxPoolSize` set appropriately for instance count
3. **Timeouts**: `serverSelectionTimeoutMS` prevents hanging on startup
4. **Error handling**: All MongoDB operations wrapped in try/except with logging
5. **Async operations**: Uses Motor for async I/O, no blocking operations
