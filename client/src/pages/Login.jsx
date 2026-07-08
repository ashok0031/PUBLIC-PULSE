import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { login } from '../services/api';

function Login() {
  const [identifier, setIdentifier] = useState('');
  const [password, setPassword] = useState('');
  const [error, setError] = useState(null);
  const navigate = useNavigate();

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError(null);
    try {
      const res = await login(identifier, password);
      if (res.message && res.message.toLowerCase().includes('successful')) {
        // Save user info to localStorage for profile menu
        const user = {
          name: res.user?.username || identifier,
          email: res.user?.email || identifier,
          username: res.user?.username || identifier,
        };
        localStorage.setItem('user', JSON.stringify(user));
        navigate('/');
      } else {
        setError(res.error || 'Login failed');
      }
    } catch (err) {
      setError('Login failed');
    }
  };

  return (
    <div className="max-w-md mx-auto bg-white p-6 rounded shadow">
      <h1 className="text-2xl font-bold mb-4">Login</h1>
      <form onSubmit={handleSubmit}>
        <label className="block mb-2">Username / Email / Phone</label>
        <input
          className="w-full border p-2 mb-4 rounded"
          value={identifier}
          onChange={e => setIdentifier(e.target.value)}
          required
        />
        <label className="block mb-2">Password</label>
        <input
          className="w-full border p-2 mb-4 rounded"
          type="password"
          value={password}
          onChange={e => setPassword(e.target.value)}
          required
        />
        <button className="w-full bg-blue-600 text-white py-2 rounded" type="submit">Login</button>
      </form>
      <div className="text-center mt-4">
        <span className="text-gray-600">Not registered?</span>
        <button
          className="ml-2 text-green-700 hover:underline"
          onClick={() => navigate('/signup')}
        >
          Signup
        </button>
      </div>
      {error && <div className="text-red-600 mt-4 text-center">{error}</div>}
    </div>
  );
}

export default Login; 