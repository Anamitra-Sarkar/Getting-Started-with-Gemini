import { initializeApp } from 'firebase/app';
import { getAuth } from 'firebase/auth';

// Firebase configuration from environment variables
// These are public configuration values and safe to expose in frontend code
const firebaseConfig = {
  apiKey: process.env.REACT_APP_FIREBASE_API_KEY,
  authDomain: process.env.REACT_APP_FIREBASE_AUTH_DOMAIN,
  projectId: process.env.REACT_APP_FIREBASE_PROJECT_ID,
};

// Initialize Firebase only if configuration is provided
let app = null;
let auth = null;

// Check if Firebase config is available
const isFirebaseConfigured = firebaseConfig.apiKey && 
                              firebaseConfig.authDomain && 
                              firebaseConfig.projectId;

if (isFirebaseConfigured) {
  try {
    app = initializeApp(firebaseConfig);
    auth = getAuth(app);
  } catch (error) {
    console.warn('Firebase initialization failed:', error.message);
  }
}

export { auth, isFirebaseConfigured };
