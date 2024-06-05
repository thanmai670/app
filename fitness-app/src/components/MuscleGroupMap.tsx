import React, { useState, useCallback } from 'react';
import Model, { IExerciseData, IMuscleStats } from 'react-body-highlighter';
import { useNavigate } from 'react-router-dom';

const anteriorData: IExerciseData[] = [
    { name: 'Bench Press', muscles: ['chest', 'triceps', 'front-deltoids'] },
    { name: 'Push Ups', muscles: ['chest'] },
    // Add more exercises and associated muscles here
];

const posteriorData: IExerciseData[] = [
    { name: 'Deadlift', muscles: ['lower-back', 'hamstring', 'gluteal'] },
    { name: 'Pull Ups', muscles: ['upper-back', 'biceps'] },
    // Add more exercises and associated muscles here
];

const MuscleGroupMap: React.FC = () => {
    const [hoveredMuscle, setHoveredMuscle] = useState<string | null>(null);
    const [clickedMuscle, setClickedMuscle] = useState<string | null>(null);

    const navigate = useNavigate();

    const handleMouseEnter = (muscle: string) => {
        setHoveredMuscle(muscle);
    };

    const handleMouseLeave = () => {
        setHoveredMuscle(null);
    };

    const handleClick = useCallback(({ muscle }: IMuscleStats) => {
        setClickedMuscle(muscle);
        setTimeout(() => {
            setClickedMuscle(null);
        }, 5000); // Hides the message after 5 seconds
    }, []);

    return (
        <div className="relative z-10 flex flex-col items-center space-y-8 py-8">
            <div className="flex justify-center space-x-8">
                <div
                    className="flex-1 flex justify-center"
                    onMouseEnter={() => handleMouseEnter('anterior')}
                    onMouseLeave={handleMouseLeave}
                >
                    <Model
                        data={anteriorData}
                        style={{ width: '30rem', padding: '5rem', outline: '1px solid rgba(255, 255, 255, 0.5)' }}
                        onClick={handleClick}
                        highlightedColors={hoveredMuscle === 'anterior' ? ['rgba(255, 0, 0, 0.5)'] : []}
                    />
                </div>
                <div
                    className="flex-1 flex justify-center"
                    onMouseEnter={() => handleMouseEnter('posterior')}
                    onMouseLeave={handleMouseLeave}
                >
                    <Model
                        data={posteriorData}
                        style={{ width: '30rem', padding: '5rem', outline: '1px solid rgba(255, 255, 255, 0.5)' }}
                        onClick={handleClick}
                        highlightedColors={hoveredMuscle === 'posterior' ? ['rgba(255, 0, 0, 0.5)'] : []}
                    />
                </div>
            </div>
            <div className="p-2 m-4 max-w-sm bg-white rounded-lg shadow-md border border-gray-200 flex items-center">
                <div>
                    <h2 className="text-lg font-semibold mb-2 text-center">How to Use the Muscle Map</h2>
                    <ul className="list-disc list-inside text-sm text-center">
                        <li>Hover over a muscle to highlight it.</li>
                        <li>Click on a muscle to view exercises for that muscle.</li>
                    </ul>
                </div>
            </div>
            {clickedMuscle && (
                <div className="absolute bg-white p-2 border rounded shadow-md z-20">
                    {clickedMuscle} muscle was clicked.
                </div>
            )}
        </div>
    );
};

export default MuscleGroupMap;
