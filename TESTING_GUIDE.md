# Testing Guide: Optional Login & Offline Mode

## Quick Test Scenarios

### Scenario 1: Offline Mode (No Backend)
**Goal**: Verify app works without backend connection

1. **Stop the backend server** (if running)
2. Open the frontend at `http://localhost:3000`
3. Navigate to `/intelligence` directly
4. **Expected**:
   - Page loads successfully
   - Chat interface is visible
   - Sidebar shows "Login" button (not "Logout")
   - No user information displayed

5. Try to send a message in the chat
6. **Expected**:
   - Message appears in chat
   - Loading indicator shows
   - Toast notification appears: "Server down"
   - Error message appears in chat

7. Click other navigation items (Dashboard, Agents, Tools)
8. **Expected**:
   - All pages load successfully
   - No forced redirects to login
   - "Server down" toasts appear when data is needed

### Scenario 2: Login Without Backend
**Goal**: Verify login gracefully fails when backend is down

1. With backend **stopped**, click "Login" button in sidebar
2. **Expected**:
   - Auth dialog opens (modal overlay)
   - Form is visible with email/password fields
   - Google Sign-In button is visible
   - Close button (X) is present

3. Fill in email/password and click "ENTER SYSTEM"
4. **Expected**:
   - Button shows "PROCESSING..."
   - Toast appears: "Server down"
   - Dialog remains open
   - No redirect occurs

5. Click the X button to close dialog
6. **Expected**:
   - Dialog closes
   - Returns to previous page
   - Still shows "Login" in sidebar

### Scenario 3: With Backend - Email/Password Auth
**Goal**: Verify normal authentication flow works

1. **Start the backend server**
2. Navigate to any page (e.g., `/intelligence`)
3. Click "Login" in sidebar
4. **Register new account**:
   - Click "Need an account? Sign up"
   - Fill in name, email, password
   - Click "CREATE ACCOUNT"
5. **Expected**:
   - Toast: "Welcome to Vaelis!"
   - Dialog closes
   - Sidebar shows user name and email
   - "Logout" button appears

6. Send a message in Intelligence chat
7. **Expected**:
   - Message sends successfully
   - AI response appears
   - No "Server down" errors

8. Click "Logout"
9. **Expected**:
   - Returns to logged-out state
   - Sidebar shows "Login" button again
   - Can still browse pages

### Scenario 4: With Backend - Login Existing User
**Goal**: Verify login flow

1. With backend running, open app
2. Click "Login" in sidebar
3. Enter existing email/password (use dev password: `devpass123`)
4. Click "ENTER SYSTEM"
5. **Expected**:
   - Toast: "Welcome back!"
   - Dialog closes
   - User info in sidebar
   - Can use authenticated features

### Scenario 5: Google Sign-In Button
**Goal**: Verify Google button presence and behavior

1. Click "Login" in sidebar
2. **Expected**:
   - Auth form appears
   - "Or continue with" separator visible
   - White "GOOGLE" button with Google icon visible

3. Click "GOOGLE" button
4. **Expected** (without Google Client ID configured):
   - Toast: "Google Sign-In is currently unavailable..."
   - OR Google popup opens (if configured)

### Scenario 6: Navigation Without Auth
**Goal**: Verify all pages accessible without login

Pages to test:
- `/` (Landing)
- `/dashboard` (Dashboard)
- `/agents` (Agents)
- `/tools` (Tools)
- `/intelligence` (Intelligence)

For each page:
1. Navigate directly (paste URL)
2. **Expected**:
   - Page loads successfully
   - No redirect to `/auth`
   - UI is functional
   - Sidebar shows "Login" option

### Scenario 7: Auth Dialog vs Page
**Goal**: Verify both auth modes work

**Dialog Mode** (from sidebar):
- Click "Login" in sidebar
- Auth appears as modal overlay
- Has close button (X)
- Dark backdrop behind
- Click X or backdrop to close

**Page Mode** (direct navigation):
- Navigate to `/auth` directly
- Auth appears as full page
- No close button
- Background image visible
- Can only leave via navigation

### Scenario 8: Session Persistence
**Goal**: Verify login persists across refreshes

1. Login with email/password
2. Verify user info in sidebar
3. Refresh the page (F5)
4. **Expected**:
   - Still logged in
   - User info still displayed
   - Token persisted in localStorage

5. Open DevTools → Application → Local Storage
6. **Expected**:
   - `vaelis_token` key present
   - JWT token value visible

## Environment Variables Testing

### Test Without Google Client ID
1. Ensure `.env` has no `REACT_APP_GOOGLE_CLIENT_ID`
2. Start app
3. Click "Login" → "GOOGLE" button
4. **Expected**:
   - Generic error message about Google being unavailable

### Test With Google Client ID
1. Get Client ID from Google Cloud Console
2. Add to `.env`: `REACT_APP_GOOGLE_CLIENT_ID=your-id.apps.googleusercontent.com`
3. Restart frontend server
4. Click "Login" → "GOOGLE" button
5. **Expected**:
   - Google account picker popup opens
   - Can select account
   - Backend receives token (check network tab)

## Browser Console Testing

### Check for Errors
Open DevTools Console and verify:

1. **No unexpected errors** during normal navigation
2. **Expected errors only**:
   - "API Error" logs when backend is down (expected)
   - Console.error for failed fetch (expected when offline)

3. **Network tab**:
   - Failed requests show as red (expected when offline)
   - Successful requests show as green (with backend)

## Automated Test Commands

```bash
# Build frontend (must succeed)
cd frontend
npm run build

# Check Python syntax
python -m py_compile backend/routes/auth.py

# Run security checker (if available)
# No vulnerabilities should be found
```

## Known Behaviors (Not Bugs)

1. **"Server down" toasts are expected** when backend is unavailable
2. **Google OAuth uses placeholder** in development (documented in code)
3. **Some API calls will fail** without backend - this is normal for offline mode
4. **User data not persisted** without login - this is by design
5. **Chat messages disappear on refresh** when not logged in - expected behavior

## Success Criteria

All tests pass if:
- ✅ App loads without backend
- ✅ All pages accessible without login
- ✅ "Server down" toasts appear appropriately
- ✅ Login dialog opens from sidebar
- ✅ Email/password auth works with backend
- ✅ Google button is visible and clickable
- ✅ Logout works correctly
- ✅ Session persists across refreshes
- ✅ No unexpected console errors
- ✅ Build succeeds
- ✅ No security vulnerabilities found

## Troubleshooting

### Issue: Build fails
- Check Node version (should be 18+)
- Delete `node_modules` and `package-lock.json`
- Run `npm install` again
- Try `npm run build` again

### Issue: "Module not found" errors
- Verify all imports are correct
- Check file paths are absolute
- Restart development server

### Issue: Google Sign-In doesn't work
- Check if script loaded: `window.google` in console
- Verify Client ID in `.env`
- Check browser blocks third-party cookies
- Try in incognito mode

### Issue: Token not persisting
- Check browser's local storage
- Verify no browser extensions clearing storage
- Check if app is in private/incognito mode
