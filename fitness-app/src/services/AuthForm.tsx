import React, { useState, ChangeEvent, FormEvent } from 'react';
import axios from 'axios';

interface FormData {
  username: string;
  password: string;
  email: string;
  age: string;
}

const AuthForm: React.FC = () => {
  const [isLogin, setIsLogin] = useState<boolean>(true);
  const [formData, setFormData] = useState<FormData>({
    username: '',
    password: '',
    email: '',
    age: ''
  });
  const [message, setMessage] = useState<string>('');
  const [isLoading, setIsLoading] = useState<boolean>(false);

  const handleChange = (e: ChangeEvent<HTMLInputElement>) => {
    setFormData({
      ...formData,
      [e.target.name]: e.target.value
    });
  };

  const handleSubmit = async (e: FormEvent) => {
    e.preventDefault();
    const endpoint = isLogin ? '/login' : '/registration';

    if (!isLogin && Number(formData.age) < 18) {
      setMessage('Sorry, you must be at least 18 to register');
      return;
    }

    try {
      setIsLoading(true);
      const response = await axios.post(`http://127.0.0.1:5000${endpoint}`, formData);
      setMessage(response.data.message || 'Success');
      if (isLogin && response.data.token) {
        localStorage.setItem('token', response.data.token);
      }
      setTimeout(() => {
        window.location.href = '/home';
      }, 2000);
    } catch (error: any) {
      const errorMessage = error.response ? (error.response.data.error || 'Something went wrong') : 'Network error';
      setMessage(errorMessage);
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="auth-container">
      <h2 style={{ color: 'white' }}>{isLogin ? 'Login' : 'Sign Up'}</h2>
      <form onSubmit={handleSubmit} className="form-container">
        <input
          className="input-field"
          type="text"
          name="username"
          placeholder="Username"
          value={formData.username}
          onChange={handleChange}
          required
        />
        <input
          className="input-field"
          type="password"
          name="password"
          placeholder="Password"
          value={formData.password}
          onChange={handleChange}
          required
        />
        {!isLogin && (
          <>
            <input
              className="input-field"
              type="email"
              name="email"
              placeholder="Email"
              value={formData.email}
              onChange={handleChange}
              required
            />
            <input
              className="input-field"
              type="number"
              name="age"
              placeholder="Age"
              value={formData.age}
              onChange={handleChange}
              required
            />
          </>
        )}
        <button type="submit" className="submit-button" disabled={isLoading}>
          {isLoading ? 'Loading...' : isLogin ? 'Login' : 'Sign Up'}
        </button>
      </form>
      <p className="toggle-text" onClick={() => setIsLogin(!isLogin)}>
        {isLogin ? 'Need an account? Sign up here.' : 'Already have an account? Log in here.'}
      </p>
      {message && <p className="message">{message}</p>}
    </div>
  );
};

export default AuthForm;
