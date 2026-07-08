import React from 'react';
import { Navigate } from 'react-router-dom';

function ProtectedRoute({ children }) {
  const isAuthenticated = false; // TODO: Replace with real auth check
  return isAuthenticated ? children : <Navigate to="/login" />;
}

export default ProtectedRoute; 