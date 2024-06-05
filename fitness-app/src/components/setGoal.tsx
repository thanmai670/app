import React, { useState } from 'react';
import { setGoal, Goal } from '../services/progressService';

const SetGoal: React.FC = () => {
  const [formData, setFormData] = useState<Goal>({
    activityType: '',
    goal: 0,
    endDate: ''
  });
  const [message, setMessage] = useState<string>('');

  const handleChange = (e: React.ChangeEvent<HTMLInputElement | HTMLSelectElement>) => {
    setFormData({
      ...formData,
      [e.target.name]: e.target.value
    });
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    try {
      await setGoal(formData);
      setMessage('Goal set successfully!');
    } catch (error: any) {
      setMessage(error.message);
    }
  };

  return (
    <div className="set-goal-container">
      <h2>Set Your Goal</h2>
      <form onSubmit={handleSubmit} className="form-container">
        <select name="activityType" value={formData.activityType} onChange={handleChange} required>
          <option value="">Select Activity</option>
          <option value="walking">Walking</option>
          <option value="running">Running</option>
          <option value="cycling">Cycling</option>
          <option value="swimming">Swimming</option>
        </select>
        <input
          type="number"
          name="goal"
          placeholder="Goal (e.g., distance)"
          value={formData.goal}
          onChange={handleChange}
          required
        />
        <input
          type="date"
          name="endDate"
          value={formData.endDate}
          onChange={handleChange}
          required
        />
        <button type="submit">Set Goal</button>
      </form>
      {message && <p>{message}</p>}
    </div>
  );
};

export default SetGoal;
