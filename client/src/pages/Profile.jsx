import React, { useEffect, useState } from 'react';
import { useNavigate } from 'react-router-dom';

function Profile() {
  const [user, setUser] = useState(null);
  const navigate = useNavigate();

  useEffect(() => {
    try {
      const u = JSON.parse(localStorage.getItem('user'));
      if (!u) navigate('/login');
      setUser(u);
    } catch {
      navigate('/login');
    }
  }, [navigate]);

  const handleLogout = () => {
    localStorage.removeItem('user');
    navigate('/login');
  };

  if (!user) return null;

  return (
    <div className="max-w-md mx-auto bg-white p-6 rounded shadow mt-10">
      <h1 className="text-2xl font-bold mb-4">Profile</h1>
      <div className="mb-4">
        <div className="font-semibold">Username:</div>
        <div>{user.username}</div>
      </div>
      {user.name && user.name !== user.username && (
        <div className="mb-4">
          <div className="font-semibold">Name:</div>
          <div>{user.name}</div>
        </div>
      )}
      <div className="mb-4">
        <div className="font-semibold">Email:</div>
        <div>{user.email}</div>
      </div>
      <button className="bg-red-600 text-white px-4 py-2 rounded" onClick={handleLogout}>Logout</button>
    </div>
  );
}

export default Profile; 