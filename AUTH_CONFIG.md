# Authentication Configuration

## Development Authentication

This application uses a simple JWT-based authentication system for development and testing.

### Default Credentials

For development, the default password is: `devpass123`

You can customize this by setting the `DEV_AUTH_PASSWORD` environment variable:

```bash
export DEV_AUTH_PASSWORD=your_custom_password
```

### Usage

1. **Register a new user:**
   ```bash
   POST /api/auth/register
   {
     "email": "user@example.com",
     "password": "devpass123",
     "name": "User Name"
   }
   ```

2. **Login:**
   ```bash
   POST /api/auth/login
   {
     "email": "user@example.com",
     "password": "devpass123"
   }
   ```

### Production

In production, this simple authentication should be replaced with:
- Firebase Authentication (already supported via the `firebase_auth_required` dependency)
- Or a proper password hashing system using bcrypt/passlib

### Environment Variables

- `JWT_SECRET_KEY`: Secret key for JWT token signing (default: "dev-secret-key-change-in-production")
- `DEV_AUTH_PASSWORD`: Password for development authentication (default: "devpass123")
- `FIREBASE_CREDENTIALS_JSON`: Path to Firebase credentials file (for production)
