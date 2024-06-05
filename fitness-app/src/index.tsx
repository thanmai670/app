import React from 'react';
import { createRoot } from 'react-dom/client';
import './Assets/styles/tailwind.css'; // Ensure this path is correct
import AppRoutes from './routes';

const container = document.getElementById('root')!;
const root = createRoot(container);

root.render(
    <React.StrictMode>
        <AppRoutes />
    </React.StrictMode>
);
