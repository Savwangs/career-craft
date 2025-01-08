import React from 'react';
import { BrowserRouter as Router, Routes, Route, Navigate } from 'react-router-dom';
import { AuthProvider, useAuth } from './contexts/AuthContext';
import Login from './components/Login';
import Dashboard from './components/Dashboard';
import Navigation from './components/Navigation';
import ResumeBuilder from './components/ResumeBuilder';

const PrivateRoute = ({ children }) => {
  const { user, loading } = useAuth();
  
  if (loading) {
    return <div>Loading...</div>;
  }
  
  return user ? children : <Navigate to="/login" replace />; // Changed from /signin to /login
};

function App() {
  const { user } = useAuth();

  return (
    <AuthProvider>
      <Router>
        <Routes>
          <Route path="/login" element={!user ? <Login /> : <Navigate to="/" replace />} />
          <Route path="/" element={
            <PrivateRoute>
              <>
                <Navigation />
                <Dashboard />
              </>
            </PrivateRoute>
          } />
          <Route path="/create-resume" element={
            <PrivateRoute>
              <>
                <Navigation />
                <ResumeBuilder />
              </>
            </PrivateRoute>
          } />
          <Route path="*" element={<Navigate to="/" replace />} />
        </Routes>
      </Router>
    </AuthProvider>
  );
}

export default App;