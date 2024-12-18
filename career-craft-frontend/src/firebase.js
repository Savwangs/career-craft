// Import the functions you need from the SDKs you need
import { initializeApp } from "firebase/app";  // Firebase initialization
import { getAuth } from "firebase/auth";  // Firebase Auth
import { getFirestore } from "firebase/firestore";
// TODO: Add SDKs for Firebase products that you want to use
// https://firebase.google.com/docs/web/setup#available-libraries

// Your web app's Firebase configuration
// For Firebase JS SDK v7.20.0 and later, measurementId is optional
const firebaseConfig = {
  apiKey: "AIzaSyCQiwujHgUl0w4gtuQQzW_Og_-DxPFOI_c",
  authDomain: "career-craft-98538.firebaseapp.com",
  projectId: "career-craft-98538",
  storageBucket: "career-craft-98538.firebasestorage.app",
  messagingSenderId: "956492797583",
  appId: "1:956492797583:web:d7aa8521a0872a5e2842fa",
  measurementId: "G-QVZ8Z3MV8R"
};

const app = initializeApp(firebaseConfig);

// Initialize Firebase Authentication
const auth = getAuth(app);

// Export the services
export { auth };