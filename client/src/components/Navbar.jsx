import React from 'react';
import { useNavigate } from 'react-router-dom';
import logo from '../assets/logo.svg';

const categories = [
  'Government Schemes',
  'Private Companies',
  'Education',
  'Healthcare',
  'Sports',
  'Entertainment',
  'Finance & Markets',
];

const languages = [
  { code: 'en', label: 'English' },
  { code: 'hi', label: 'Hindi' },
  { code: 'ta', label: 'Tamil' },
  { code: 'te', label: 'Telugu' },
  { code: 'bn', label: 'Bengali' },
  { code: 'ml', label: 'Malayalam' },
  { code: 'mr', label: 'Marathi' },
  { code: 'gu', label: 'Gujarati' },
  { code: 'kn', label: 'Kannada' },
];

function Navbar({ onCategorySelect, onLanguageSelect, onHome }) {
  const [showCategories, setShowCategories] = React.useState(false);
  const [showLanguages, setShowLanguages] = React.useState(false);
  const [showProfileMenu, setShowProfileMenu] = React.useState(false);
  const [user, setUser] = React.useState(() => {
    // For demo, check localStorage for user
    try {
      return JSON.parse(localStorage.getItem('user'));
    } catch {
      return null;
    }
  });
  const navigate = useNavigate();
  const [categoryDropdownActive, setCategoryDropdownActive] = React.useState(false);
  const [languageDropdownActive, setLanguageDropdownActive] = React.useState(false);

  // Close dropdowns on outside click
  React.useEffect(() => {
    function handleClick(e) {
      if (!e.target.closest('.navbar-category') && showCategories) setShowCategories(false);
      if (!e.target.closest('.navbar-language') && showLanguages) setShowLanguages(false);
      if (!e.target.closest('.navbar-profile') && showProfileMenu) setShowProfileMenu(false);
    }
    document.addEventListener('mousedown', handleClick);
    return () => document.removeEventListener('mousedown', handleClick);
  }, [showCategories, showLanguages, showProfileMenu]);

  const handleCategoryMouseEnter = () => {
    setShowCategories(true);
    setCategoryDropdownActive(true);
  };
  const handleCategoryMouseLeave = () => {
    setCategoryDropdownActive(false);
    setTimeout(() => {
      if (!categoryDropdownActive) setShowCategories(false);
    }, 120);
  };
  const handleCategoryDropdownMouseEnter = () => setCategoryDropdownActive(true);
  const handleCategoryDropdownMouseLeave = () => {
    setCategoryDropdownActive(false);
    setShowCategories(false);
  };

  const handleLanguageMouseEnter = () => {
    setShowLanguages(true);
    setLanguageDropdownActive(true);
  };
  const handleLanguageMouseLeave = () => {
    setLanguageDropdownActive(false);
    setTimeout(() => {
      if (!languageDropdownActive) setShowLanguages(false);
    }, 120);
  };
  const handleLanguageDropdownMouseEnter = () => setLanguageDropdownActive(true);
  const handleLanguageDropdownMouseLeave = () => {
    setLanguageDropdownActive(false);
    setShowLanguages(false);
  };

  const handleCategoryClick = (cat) => {
    setShowCategories(false);
    if (onCategorySelect) onCategorySelect(cat);
  };

  const handleLanguageClick = (lang) => {
    setShowLanguages(false);
    if (onLanguageSelect) onLanguageSelect(lang);
  };

  const handleHomeClick = (e) => {
    if (onHome) onHome();
    navigate('/');
    window.location.reload(); // Force refresh
  };

  const handleProfileClick = () => {
    setShowProfileMenu((v) => !v);
  };

  const handleLogout = () => {
    localStorage.removeItem('user');
    setUser(null);
    setShowProfileMenu(false);
    navigate('/login');
  };

  const handleProfilePage = () => {
    setShowProfileMenu(false);
    navigate('/profile');
  };

  return (
    <nav className="bg-white shadow mb-6" style={{ minHeight: '96px' }}>
      <div className="container mx-auto px-4 py-4 flex items-center justify-between">
        {/* Logo */}
        <div className="flex items-center cursor-pointer" onClick={handleHomeClick} title="Go to Home">
          <img src={logo} alt="Public Pulse Logo" style={{ height: '72px', width: 'auto', marginRight: '18px' }} />
        </div>
        {/* Center: Home, Categories, Language */}
        <div className="flex items-center space-x-10 mx-auto">
          <button onClick={handleHomeClick} className="text-xl font-bold text-gray-800 hover:text-yellow-700 focus:outline-none">Home</button>
          <div
            className="relative navbar-category"
            onMouseEnter={handleCategoryMouseEnter}
            onMouseLeave={handleCategoryMouseLeave}
          >
            <button
              className="text-xl font-bold hover:text-yellow-700 focus:outline-none"
              onClick={() => setShowCategories((v) => !v)}
            >
              Categories
            </button>
            {showCategories && (
              <div
                className="absolute left-0 mt-2 w-56 bg-white border rounded shadow z-10"
                onMouseEnter={handleCategoryDropdownMouseEnter}
                onMouseLeave={handleCategoryDropdownMouseLeave}
              >
                {categories.map((cat) => (
                  <button
                    key={cat}
                    className="block w-full text-left px-4 py-2 hover:bg-blue-100"
                    onClick={() => handleCategoryClick(cat)}
                  >
                    {cat}
                  </button>
                ))}
              </div>
            )}
          </div>
          <div
            className="relative navbar-language"
            onMouseEnter={handleLanguageMouseEnter}
            onMouseLeave={handleLanguageMouseLeave}
          >
            <button
              className="text-xl font-bold hover:text-yellow-700 focus:outline-none"
              onClick={() => setShowLanguages((v) => !v)}
            >
              Language
            </button>
            {showLanguages && (
              <div
                className="absolute left-0 mt-2 w-48 bg-white border rounded shadow z-10"
                onMouseEnter={handleLanguageDropdownMouseEnter}
                onMouseLeave={handleLanguageDropdownMouseLeave}
              >
                {languages.map((lang) => (
                  <button
                    key={lang.code}
                    className="block w-full text-left px-4 py-2 hover:bg-blue-100"
                    onClick={() => handleLanguageClick(lang.code)}
                  >
                    {lang.label}
                  </button>
                ))}
              </div>
            )}
          </div>
        </div>
        {/* Right: Profile or Login */}
        <div className="relative navbar-profile">
          {user ? (
            <>
              <button
                className="flex items-center space-x-2 bg-gray-100 px-3 py-2 rounded hover:bg-gray-200 focus:outline-none"
                onClick={handleProfileClick}
              >
                <span className="font-semibold text-blue-700">{user.name || user.username || 'Profile'}</span>
                <svg className="w-4 h-4" fill="none" stroke="currentColor" strokeWidth="2" viewBox="0 0 24 24"><path strokeLinecap="round" strokeLinejoin="round" d="M19 9l-7 7-7-7" /></svg>
              </button>
              {showProfileMenu && (
                <div className="absolute right-0 mt-2 w-40 bg-white border rounded shadow z-20">
                  <button className="block w-full text-left px-4 py-2 hover:bg-blue-100" onClick={handleProfilePage}>Profile</button>
                  <button className="block w-full text-left px-4 py-2 hover:bg-blue-100" onClick={handleLogout}>Logout</button>
                </div>
              )}
            </>
          ) : (
            <button
              className="bg-blue-600 text-white px-4 py-2 rounded hover:bg-blue-700"
              onClick={() => navigate('/login')}
            >
              Login
            </button>
          )}
        </div>
      </div>
    </nav>
  );
}

export default Navbar; 