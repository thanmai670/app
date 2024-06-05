import React, { useEffect, useState } from 'react';
import { useParams } from 'react-router-dom';
import { Bar } from 'react-chartjs-2';
import 'chart.js/auto';  // Automatically registers all necessary components for Chart.js
import { fetchProgress, Progress } from '../services/progressService';

const ProgressChart: React.FC = () => {
  const { id } = useParams<{ id: string }>();
  const [chartData, setChartData] = useState<any>(null);

  useEffect(() => {
    const fetchData = async () => {
      try {
        const progress: Progress = await fetchProgress(id || '60d21b4667d0d8992e610c85');  // Use mock ID for testing
        const labels = progress.logs.map(log => new Date(log.date).toLocaleDateString());
        const data = progress.logs.map(log => log.value);

        setChartData({
          labels,
          datasets: [
            {
              label: `${progress.activityType} Progress`,
              data,
              backgroundColor: 'green',
              borderColor: 'rgba(75, 192, 192, 1)',
              borderWidth: 1
            }
          ]
        });
      } catch (error: any) {
        console.error('Error fetching progress data', error);
      }
    };

    fetchData();
  }, [id]);

  if (!chartData) return <p>Loading...</p>;

  return (
    <div className="flex justify-center items-center min-h-screen bg-gray-100">
      <div className="bg-white shadow-lg rounded-lg p-4 w-full max-w-md">
        <h2 className="text-xl font-semibold mb-4">Progress Chart</h2>
        <div className="h-64">
          <Bar data={chartData} options={{
            maintainAspectRatio: false,
            scales: {
              y: {
                beginAtZero: true
              }
            }
          }} />
        </div>
      </div>
    </div>
  );
};

export default ProgressChart;
