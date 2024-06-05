import React, { useState } from 'react';
import { Link } from 'react-router-dom';

const NavBar: React.FC = () => {
    const [isSidebarOpen, setIsSidebarOpen] = useState<boolean>(false);

    const toggleSidebar = () => {
        setIsSidebarOpen(!isSidebarOpen);
    };

    return (
        <div className="flex">
            <aside className={`bg-gray-800 text-white w-full md:w-1/4 min-h-screen p-4 ${isSidebarOpen ? 'block' : 'hidden'}`}>
                {/* Sidebar content goes here */}
                <h2 className="text-xl font-semibold mb-4">Menu</h2>
                <ul className="space-y-2">
                    <li>
                        <Link to="/calorie-tracker">Calorie Tracker</Link>
                    </li>
                    <li>
                        <Link to="/exercise-progress">Exercise Progress Tracker</Link>
                    </li>
                    <li>
                        <Link to="/muscle-wiki">Muscle Wiki</Link>
                    </li>
                </ul>
            </aside>
            <nav className="bg-blue-500 p-4 flex-grow">
                <button onClick={toggleSidebar} className="text-white">
                    {isSidebarOpen ? 'Close' : 'Open'} Menu
                </button>
            </nav>
        </div>
    );
};

export default NavBar;
