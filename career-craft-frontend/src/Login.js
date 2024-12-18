import React, { useState } from 'react';
import { sendSignInLinkToEmail, createUserWithEmailAndPassword, updateProfile, sendPasswordResetEmail, signInWithEmailAndPassword } from 'firebase/auth';
import { useNavigate } from 'react-router-dom';
import { auth } from './firebase'; // Import the auth object from firebase-config.js

const Login = () => {
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [confirmPassword, setConfirmPassword] = useState('');
  const [error, setError] = useState('');
  const [message, setMessage] = useState('');
  const [isRegister, setIsRegister] = useState(false);
  const [isForgotPassword, setIsForgotPassword] = useState(false);
  const navigate = useNavigate();

  const handleEmailChange = (e) => setEmail(e.target.value);
  const handlePasswordChange = (e) => setPassword(e.target.value);
  const handleConfirmPasswordChange = (e) => setConfirmPassword(e.target.value);

  // Handle the form submission (login or register or forgot password)
  const handleSubmit = async (e) => {
    e.preventDefault();

    if (isForgotPassword) {
      // Handle the password reset link sending (when in forgot password mode)
      if (!email) {
        setError('Please enter your email');
        return;
      }

      try {
        await sendPasswordResetEmail(auth, email);
        setMessage('Password reset link sent! Check your email to continue.');
      } catch (err) {
        setError('Error: ' + err.message);
      }
    } else {
      // For Login or Register, check if email and password are filled
      if (!email || !password) {
        setError('Please fill in both fields');
        return;
      }

      if (isRegister) {
        // Handle Registration
        try {
          const userCredential = await createUserWithEmailAndPassword(auth, email, password);
          const actionCodeSettings = {
            url: window.location.href,
            handleCodeInApp: true,
          };
          await sendSignInLinkToEmail(auth, email, actionCodeSettings);
          setMessage('Registration successful! Check your email to continue.');
        } catch (err) {
          if (err.code === 'auth/email-already-in-use') {
            setError('Email already in use');
          } else {
            setError('Error: ' + err.message);
          }
        }
      } else {
        // Handle Login
        try {
          const userCredential = await signInWithEmailAndPassword(auth, email, password);
          setMessage('Login successful! Redirecting to your dashboard...');
          navigate('/dashboard'); // Redirect to dashboard (implement later)
        } catch (err) {
          setError('Invalid email or password');
        }
      }
    }
  };

  // Handle confirm password submission for registration
  const handleConfirmPasswordSubmit = async (e) => {
    e.preventDefault();

    if (password !== confirmPassword) {
      setError('Passwords do not match');
      return;
    }

    try {
      await updateProfile(auth.currentUser, {
        displayName: email,
      });
      setMessage('Account created successfully!');
      navigate('/dashboard'); // Redirect to dashboard (implement later)
    } catch (err) {
      setError('Error during account creation: ' + err.message);
    }
  };

  return (
    <div className="flex items-center justify-center min-h-screen bg-gray-100">
      <div className="bg-white p-8 rounded-lg shadow-lg w-full max-w-sm">
        <h2 className="text-2xl font-semibold text-center mb-6">{isRegister ? 'Register' : isForgotPassword ? 'Forgot Password' : 'Login'}</h2>
        <form onSubmit={handleSubmit} className="space-y-4">
          <div className="form-group">
            <label htmlFor="email" className="block text-sm font-medium text-gray-700">Email:</label>
            <input
              type="email"
              id="email"
              value={email}
              onChange={handleEmailChange}
              required
              className="mt-1 p-2 w-full border rounded-lg border-gray-300 focus:ring-indigo-500 focus:border-indigo-500"
            />
          </div>

          {!isForgotPassword && (
            <>
              <div className="form-group">
                <label htmlFor="password" className="block text-sm font-medium text-gray-700">Password:</label>
                <input
                  type="password"
                  id="password"
                  value={password}
                  onChange={handlePasswordChange}
                  required
                  className="mt-1 p-2 w-full border rounded-lg border-gray-300 focus:ring-indigo-500 focus:border-indigo-500"
                />
              </div>

              {isRegister && (
                <div className="form-group">
                  <label htmlFor="confirmPassword" className="block text-sm font-medium text-gray-700">Confirm Password:</label>
                  <input
                    type="password"
                    id="confirmPassword"
                    value={confirmPassword}
                    onChange={handleConfirmPasswordChange}
                    required
                    className="mt-1 p-2 w-full border rounded-lg border-gray-300 focus:ring-indigo-500 focus:border-indigo-500"
                  />
                </div>
              )}
            </>
          )}

          <div className="flex flex-col items-center space-y-4">
            <button type="submit" className="w-full py-2 px-4 bg-blue-500 text-white rounded-lg hover:bg-blue-600">
              {isRegister ? 'Register' : isForgotPassword ? 'Submit' : 'Login'}
            </button>

            <div className="text-center">
              {isRegister ? (
                <p className="text-sm">
                  Already have an account?{' '}
                  <span onClick={() => setIsRegister(false)} className="text-green-500 cursor-pointer hover:underline">Login</span>
                </p>
              ) : isForgotPassword ? (
                <p className="text-sm">
                  Remembered your password?{' '}
                  <span onClick={() => setIsForgotPassword(false)} className="text-green-500 cursor-pointer hover:underline">Login</span>
                </p>
              ) : (
                <p className="text-sm">
                  Don't have an account?{' '}
                  <span onClick={() => setIsRegister(true)} className="text-green-500 cursor-pointer hover:underline">Register</span>
                </p>
              )}
            </div>

            {!isForgotPassword && (
              <p className="text-sm text-center">
                <span onClick={() => setIsForgotPassword(true)} className="text-blue-500 cursor-pointer hover:underline">Forgot Password?</span>
              </p>
            )}
          </div>
        </form>

        {error && <p className="mt-4 text-red-500 text-center">{error}</p>}
        {message && <p className="mt-4 text-green-500 text-center">{message}</p>}
      </div>
    </div>
  );
};

export default Login;
