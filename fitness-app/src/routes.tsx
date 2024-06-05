import React from 'react';
import { BrowserRouter as Router, Routes, Route } from 'react-router-dom';
import App from './App';
import MuscleGroupMap from './components/MuscleGroupMap';
import Exercises from './components/Excercises';

const AppRoutes: React.FC = () => (
    <Router>
        <Routes>
            <Route path="/" element={<App />}>
                <Route index element={<MuscleGroupMap />} />
                <Route path="exercises/:bodyPart" element={<Exercises />} />
            </Route>
        </Routes>
    </Router>
);

export default AppRoutes;
