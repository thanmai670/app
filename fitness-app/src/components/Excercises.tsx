import React, { useEffect, useState } from 'react';
import { useParams } from 'react-router-dom';
import { fetchExerciseByMuscleGroup, Exercise } from '../services/excerciseService';

const Exercises: React.FC = () => {
  const { muscleGroup } = useParams<{ muscleGroup: string }>();
  const [exercise, setExercise] = useState<Exercise | null>(null);
  const [loading, setLoading] = useState<boolean>(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    setLoading(true);
    setError(null);
    fetchExerciseByMuscleGroup(muscleGroup!)
      .then(data => {
        if (data) {
          setExercise(data);
        } else {
          setError('No data found for this muscle group.');
        }
        setLoading(false);
      })
      .catch(err => {
        setError('Failed to fetch exercise data.');
        setLoading(false);
      });
  }, [muscleGroup]);

  if (loading) return <p>Loading...</p>;
  if (error) return <p>{error}</p>;

  const getEmbedUrl = (url: string) => {
    const urlObj = new URL(url);
    const videoId = urlObj.searchParams.get('v');
    return `https://www.youtube.com/embed/${videoId}`;
  };

  return (
    exercise ? (
      <div className="exercise-container p-4">
        <h1 className="text-2xl font-bold mb-4">{exercise.muscleName} Exercise</h1>
        <div className="video-container mb-4">
          <iframe
            width="560"
            height="315"
            src={getEmbedUrl(exercise.videoUrl)}
            title="YouTube video player"
            frameBorder="0"
            allow="accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture"
            allowFullScreen
          ></iframe>
        </div>
        <ul className="instructions-list list-decimal list-inside">
          {exercise.description.map((point, index) => (
            <li key={index} className="mb-2">{point}</li>
          ))}
        </ul>
      </div>
    ) : (
      <p>No exercise data available.</p>
    )
  );
};

export default Exercises;
