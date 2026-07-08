import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { signup, sendOtp, verifyOtp } from '../services/api';

function Signup() {
  const [form, setForm] = useState({ username: '', email: '', phone: '', password: '' });
  const [error, setError] = useState(null);
  const [otpSent, setOtpSent] = useState(false);
  const [otp, setOtp] = useState('');
  const [emailVerified, setEmailVerified] = useState(false);
  const [otpMessage, setOtpMessage] = useState('');
  const [userCreated, setUserCreated] = useState(false);
  const navigate = useNavigate();

  const handleChange = (e) => {
    setForm({ ...form, [e.target.name]: e.target.value });
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError(null);
    setOtpMessage('');
    // 1. Create user first
    try {
      const res = await signup(form);
      if (res.message && res.message.toLowerCase().includes('registered')) {
        setUserCreated(true);
        // 2. Send OTP after user is created
        const otpRes = await sendOtp(form.email);
        if (otpRes.message) {
          setOtpSent(true);
          setOtpMessage('OTP sent to your email.');
        } else {
          setError(otpRes.error || 'Failed to send OTP.');
        }
      } else {
        setError(res.error || 'Signup failed');
      }
    } catch (err) {
      setError('Signup failed');
    }
  };

  const handleVerifyOtp = async () => {
    setError(null);
    setOtpMessage('');
    if (!otp) {
      setError('Please enter the OTP.');
      return;
    }
    const res = await verifyOtp(form.email, otp);
    if (res.message) {
      setEmailVerified(true);
      setOtpMessage('Email verified! You can now login.');
      setTimeout(() => navigate('/login'), 1200);
    } else {
      setError(res.error || 'OTP verification failed.');
    }
  };

  return (
    <div className="max-w-md mx-auto bg-white p-6 rounded shadow">
      <h1 className="text-2xl font-bold mb-4">Signup</h1>
      {!userCreated ? (
        <form onSubmit={handleSubmit}>
          <label className="block mb-2">First Name</label>
          <input className="w-full border p-2 mb-4 rounded" name="firstName" onChange={handleChange} />
          <label className="block mb-2">Last Name</label>
          <input className="w-full border p-2 mb-4 rounded" name="lastName" onChange={handleChange} />
          <label className="block mb-2">Username</label>
          <input className="w-full border p-2 mb-4 rounded" name="username" required onChange={handleChange} />
          <label className="block mb-2">Email</label>
          <input className="w-full border p-2 mb-4 rounded" name="email" type="email" required onChange={handleChange} value={form.email} />
          <label className="block mb-2">Phone</label>
          <input className="w-full border p-2 mb-4 rounded" name="phone" type="tel" onChange={handleChange} />
          <label className="block mb-2">Password</label>
          <input className="w-full border p-2 mb-4 rounded" name="password" type="password" required onChange={handleChange} />
          <button className="w-full bg-green-600 text-white py-2 rounded" type="submit">Signup</button>
        </form>
      ) : (
        <div>
          <div className="mb-4">Please check your email for the OTP to verify your account.</div>
          {otpSent && !emailVerified && (
            <div className="mb-4">
              <label className="block mb-2">Enter OTP</label>
              <div className="flex">
                <input className="w-full border p-2 rounded-l" value={otp} onChange={e => setOtp(e.target.value)} />
                <button type="button" className="bg-green-600 text-white px-4 rounded-r" onClick={handleVerifyOtp}>Verify OTP</button>
              </div>
            </div>
          )}
          {otpMessage && <div className="text-green-600 mb-2 text-center">{otpMessage}</div>}
        </div>
      )}
      {error && <div className="text-red-600 mt-4 text-center">{error}</div>}
    </div>
  );
}

export default Signup; 