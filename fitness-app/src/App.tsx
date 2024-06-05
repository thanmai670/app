import React from 'react';
import { Outlet, Link } from 'react-router-dom';

const App: React.FC = () => {
    return (
        <div className="App">
            <header className="App-header">
                <nav>
                    <ul className="flex space-x-4 p-4 bg-blue-500 text-white">
                        <li>
                            <Link to="/">Home</Link>
                        </li>
                        <li>
                            <Link to="/muscle-group-map">Muscle Group Map</Link>
                        </li>
                    </ul>
                </nav>
            </header>
            <main className="App-main">
                <Outlet />
            </main>
        </div>
    );
};


export default App;
