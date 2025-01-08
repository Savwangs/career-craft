import { auth } from '../firebase';
import { 
  signInWithEmailAndPassword,
  createUserWithEmailAndPassword,
  signOut,
  sendPasswordResetEmail
} from 'firebase/auth';

export const authService = {
  async login(email, password) {
    const userCredential = await signInWithEmailAndPassword(auth, email, password);
    const token = await userCredential.user.getIdToken();
    localStorage.setItem('token', token);
    return userCredential.user;
  },

  async register(email, password) {
    const userCredential = await createUserWithEmailAndPassword(auth, email, password);
    const token = await userCredential.user.getIdToken();
    localStorage.setItem('token', token);
    return userCredential.user;
  },

  async logout() {
    try {
      await signOut(auth);
      localStorage.removeItem('token');
      window.location.href = '/login'; // Force redirect to login page
    } catch (error) {
      console.error('Logout error:', error);
      throw error;
    }
  },

  async resetPassword(email) {
    await sendPasswordResetEmail(auth, email);
  },

  getToken() {
    return localStorage.getItem('token');
  }
};