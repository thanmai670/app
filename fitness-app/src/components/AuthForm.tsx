import React, { useState, ChangeEvent, FormEvent } from 'react';
import { authenticateUser } from '../services/authService';

interface LoginData {
  username: string;
  password: string;
}

interface RegistrationData extends LoginData {
  email: string;
  age: string;
}

const AuthForm: React.FC = () => {
  const [isLogin, setIsLogin] = useState<boolean>(true);
  const [formData, setFormData] = useState<RegistrationData>({
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
      const responseData = isLogin ? await authenticateUser(endpoint, formData) : await authenticateUser(endpoint, { username: formData.username, password: formData.password });
      const response = responseData as { message?: string, token?: string };

      setMessage(response.message || 'Success');
      if (isLogin && response.token) {
        localStorage.setItem('token', response.token);
      }
      setTimeout(() => {
        window.location.href = '/dashboard';
      }, 2000);
    } catch (error: any) {
      setMessage(error.message);
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="flex flex-col items-center justify-center min-h-screen bg-cover bg-no-repeat bg-fixed bg-center" style={{ backgroundImage: 'url(https://t3.ftcdn.net/jpg/04/29/35/62/360_F_429356296_CVQ5LkC6Pl55kUNLqLisVKgTw9vjyif1.jpg)' }}>
      <h2 className="text-white">{isLogin ? 'Login' : 'Sign Up'}</h2>
      <form onSubmit={handleSubmit} className="mt-5 p-5 bg-black bg-opacity-50 rounded-lg max-w-sm w-full">
        <input
          className="w-full p-2 mb-4 rounded-lg"
          type="text"
          name="username"
          placeholder="Username"
          value={formData.username}
          onChange={handleChange}
          required
        />
        <input
          className="w-full p-2 mb-4 rounded-lg"
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
              className="w-full p-2 mb-4 rounded-lg"
              type="email"
              name="email"
              placeholder="Email"
              value={formData.email}
              onChange={handleChange}
              required
            />
            <input
              className="w-full p-2 mb-4 rounded-lg"
              type="number"
              name="age"
              placeholder="Age"
              value={formData.age}
              onChange={handleChange}
              required
            />
          </>
        )}
        <button type="submit" className="w-full p-2 mt-4 rounded-lg bg-blue-400 text-gray-900" disabled={isLoading}>
          {isLoading ? 'Loading...' : isLogin ? 'Login' : 'Sign Up'}
        </button>
      </form>
      <p className="mt-4 cursor-pointer text-blue-400" onClick={() => setIsLogin(!isLogin)}>
        {isLogin ? 'Need an account? Sign up here.' : 'Already have an account? Log in here.'}
      </p>
      {message && <p className="mt-4 text-white">{message}</p>}
    </div>
  );
};

export default AuthForm;
