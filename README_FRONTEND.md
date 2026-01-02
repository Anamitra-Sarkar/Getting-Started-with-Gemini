Frontend (Next.js) quick start

Install dependencies and run development server:

```bash
cd frontend
npm install
npm run dev
```

Set these env vars in your shell or .env.local:

- NEXT_PUBLIC_FIREBASE_API_KEY
- NEXT_PUBLIC_FIREBASE_AUTH_DOMAIN
- NEXT_PUBLIC_FIREBASE_PROJECT_ID
- NEXT_PUBLIC_BACKEND_URL (e.g. http://localhost:8000)

The frontend uses Firebase Auth for authentication and expects the backend to verify ID tokens.
