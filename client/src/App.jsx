import React, { useState, useRef } from 'react';
import { BrowserRouter as Router, Routes, Route } from 'react-router-dom';
import Navbar from './components/Navbar';
import Home from './pages/Home';
import Login from './pages/Login';
import Signup from './pages/Signup';
import Entity from './pages/Entity';
import NotFound from './pages/NotFound';
import Profile from './pages/Profile';

function GlobalLoader({ loading }) {
  if (!loading) return null;
  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center bg-black bg-opacity-30">
      <div className="w-16 h-16 border-4 border-blue-500 border-t-transparent rounded-full animate-spin" />
    </div>
  );
}

function App() {
  const [selectedCategory, setSelectedCategory] = useState(null);
  const [selectedLanguage, setSelectedLanguage] = useState(null);
  // Ref to trigger refresh in Home
  const homeRefreshRef = useRef(null);

  // Helper to reset filters when navigating Home
  const handleHome = () => {
    setSelectedCategory(null);
    setSelectedLanguage(null);
  };

  return (
    <>
      <GlobalLoader loading={false} />
      <Router>
        <div className="min-h-screen bg-gray-50">
          <Navbar
            onCategorySelect={setSelectedCategory}
            onLanguageSelect={setSelectedLanguage}
            onHome={handleHome}
          />
          <div className="container mx-auto py-6">
            <Routes>
              <Route path="/" element={
                <Home
                  selectedCategory={selectedCategory}
                  selectedLanguage={selectedLanguage}
                  setRefreshHandler={fn => { homeRefreshRef.current = fn; }}
                  setGlobalLoading={() => {}}
                />
              } />
              <Route path="/login" element={<Login />} />
              <Route path="/signup" element={<Signup />} />
              <Route path="/entity/:id" element={<Entity setGlobalLoading={() => {}} />} />
              <Route path="/profile" element={<Profile />} />
              <Route path="*" element={<NotFound />} />
            </Routes>
          </div>
        </div>
      </Router>
    </>
  );
}

export default App; 