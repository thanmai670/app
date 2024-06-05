import React, { useState, useCallback } from 'react';
import Model, { IExerciseData, IMuscleStats } from 'react-body-highlighter';

const data: IExerciseData[] = [
    { name: 'Bench Press', muscles: ['chest', 'triceps', 'front-deltoids'] },
    { name: 'Push Ups', muscles: ['chest'] },
    // Add more exercises and associated muscles here
];

const MuscleGroupMap: React.FC = () => {
    const [hoveredMuscle, setHoveredMuscle] = useState<string | null>(null);
    const [clickedMuscle, setClickedMuscle] = useState<string | null>(null);

    const handleMouseEnter = (muscle: string) => {
        setHoveredMuscle(muscle);
    };

    const handleMouseLeave = () => {
        setHoveredMuscle(null);
    };

    const handleClick = useCallback(({ muscle }: IMuscleStats) => {
        setClickedMuscle(muscle);
        alert(`${muscle} muscle was clicked.`);
    }, []);

    return (
        <div className="relative flex justify-center items-center ">
            <div className="flex-1 flex justify-start">
            <Model
                data={data}
                style={{ width: '30rem', padding: '5rem' }}
                onClick={handleClick}
                highlightedColors={hoveredMuscle ? ['#ffcccc'] : ['#b6bdc3']} // Default to gray if not hovered
            />
            </div>
            {clickedMuscle && (
                <div className="absolute bg-white p-2 border rounded shadow-md">
                    {clickedMuscle} muscle was clicked.
                </div>
            )}
        </div>
    );
};

export default MuscleGroupMap;
