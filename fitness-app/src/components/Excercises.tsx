import React from 'react';
import { useParams } from 'react-router-dom';
import useFetch from '../hooks/useFetch';

interface Exercise {
    id: number;
    name: string;
    description: string;
}

const Exercises: React.FC = () => {
    const { bodyPart } = useParams<{ bodyPart: string }>();
    const { data, loading, error } = useFetch(`http://localhost:5000/api/exercises/${bodyPart}`);

    if (loading) return <p>Loading...</p>;
    if (error) return <p>Error loading exercises</p>;

    return (
        <div>
            <h1>Exercises for {bodyPart}</h1>
            <ul>
                {data.map((exercise: Exercise) => (
                    <li key={exercise.id}>
                        <h2>{exercise.name}</h2>
                        <p>{exercise.description}</p>
                    </li>
                ))}
            </ul>
        </div>
    );
};

export default Exercises;
