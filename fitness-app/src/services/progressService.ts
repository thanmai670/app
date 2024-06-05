import axios from 'axios';

const API_URL = 'http://localhost:5000/api';

export interface Goal {
  activityType: string;
  goal: number;
  endDate: string;
}

export interface Log {
  date: string;
  value: number;
}

export interface Progress {
  _id: string;  // Add an ID field
  activityType: string;
  goal: number;
  endDate: string;
  logs: Log[];
}

// Mock Data for Testing
const mockProgressData: Progress = {
  _id: '60d21b4667d0d8992e610c85',  // Mock MongoDB ObjectId
  activityType: 'running',
  goal: 50,
  endDate: '2023-12-31',
  logs: [
    { date: '2023-05-01', value: 5 },
    { date: '2023-05-02', value: 7 },
    { date: '2023-05-03', value: 10 },
    { date: '2023-05-04', value: 12 },
    { date: '2023-05-05', value: 0 },
    { date: '2023-05-06', value: 3 },
  ]
};

export const setGoal = async (goal: Goal) => {
  // Mock Response for Testing
  return new Promise<Goal>((resolve) => {
    setTimeout(() => {
      console.log('Goal set:', goal);
      resolve(goal);
    }, 500);
  });
};

export const logWorkout = async (progressId: string, log: Log) => {
  // Mock Response for Testing
  return new Promise<Log>((resolve) => {
    setTimeout(() => {
      console.log('Workout logged:', log);
      resolve(log);
    }, 500);
  });
};

export const fetchProgress = async (progressId: string): Promise<Progress> => {
  // Mock Response for Testing
  return new Promise<Progress>((resolve) => {
    setTimeout(() => {
      console.log('Fetching progress for id:', progressId);
      resolve(mockProgressData);
    }, 500);
  });
};
