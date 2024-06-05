import React, { useState } from 'react';
import { useParams } from 'react-router-dom';
import { logWorkout, Log } from '../services/progressService';

const LogWorkout: React.FC = () => {
  const { id } = useParams<{ id: string }>();
  const [formData, setFormData] = useState<Log>({
    date: '',
    value: 0
  });
  const [message, setMessage] = useState<string>('');

  const handleChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    setFormData({
      ...formData,
      [e.target.name]: e.target.value
    });
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    try {
      await logWorkout(id || '60d21b4667d0d8992e610c85', formData);  // Use mock ID for testing
      setMessage('Workout logged successfully!');
    } catch (error: any) {
      setMessage(error.message);
    }
  };

  return (
    <div className="log-workout-container">
      <h2>Log Workout</h2>
      <form onSubmit={handleSubmit} className="form-container">
        <input
          type="date"
          name="date"
          value={formData.date}
          onChange={handleChange}
          required
        />
        <input
          type="number"
          name="value"
          placeholder="Value (e.g., distance)"
          value={formData.value}
          onChange={handleChange}
          required
        />
        <button type="submit">Log Workout</button>
      </form>
      {message && <p>{message}</p>}
    </div>
  );
};

export default LogWorkout;
