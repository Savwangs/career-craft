import { auth } from '../firebase';
import { 
    signInWithEmailAndPassword,
    createUserWithEmailAndPassword,
    signOut,
    sendPasswordResetEmail,
    setPersistence,
    browserLocalPersistence
} from 'firebase/auth';

export const authService = {
  async login(email, password) {
    try {
        // Set persistence first
        await setPersistence(auth, browserLocalPersistence);
        
        const userCredential = await signInWithEmailAndPassword(auth, email, password);
        const token = await userCredential.user.getIdToken(true);
        localStorage.setItem('token', token);
        console.log("Login successful, token stored:", token);
        return userCredential.user;
    } catch (error) {
        console.error("Login error:", error);
        throw error;
    }
  },

  async register(email, password) {
    const userCredential = await createUserWithEmailAndPassword(auth, email, password);
    const token = await userCredential.user.getIdToken(true); // Force refresh
    localStorage.setItem('token', token);
    return userCredential.user;
  },

  async logout() {
    try {
      await signOut(auth);
      localStorage.removeItem('token');
    } catch (error) {
      console.error('Logout error:', error);
      throw error;
    }
  },

  async resetPassword(email) {
    await sendPasswordResetEmail(auth, email);
  },

  async getToken() {
    const currentUser = auth.currentUser;
    console.log("Getting token for user:", currentUser?.email);
    if (!currentUser) {
        console.log('No current user found');
        return null;
    }
    try {
      const newToken = await currentUser.getIdToken(true);
      console.log('New token generated:', newToken);
      localStorage.setItem('token', newToken);
      return newToken;
    } catch (error) {
      console.error('Error getting token:', error);
      return null;
    }
  }
};