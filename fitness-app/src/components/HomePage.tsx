// src/components/HomePage.tsx
import React, { useContext } from 'react';
import { Link } from 'react-router-dom';
import Footer from './common/Footer';
import AuthContext from './AuthContext'; // Assume AuthContext is used to manage authentication state

const HomePage: React.FC = () => {
    const { isAuthenticated } = useContext(AuthContext);

    return (
        <div>
            <div className="home-page h-screen bg-cover bg-center" style={{ backgroundImage: 'url(https://media.istockphoto.com/id/1335253635/video/exercise-for-the-body-keeping-fit-for-health-young-women-fitness-and-exercise-training.jpg?s=640x640&k=20&c=e0C4zJ-x5_UfbbtxSnGQ-ZtNA7oF_XhUfoQCBODQXKM=)' }}>
                <div className="flex items-center justify-center h-full bg-black bg-opacity-60">
                    <div className="text-center text-white p-8 rounded-lg">
                        <h1 className="text-5xl mb-4">Welcome to the Fitness Tracker</h1>
                        <p className="text-xl mb-8">Your journey to a healthier life starts here. Track your workouts, monitor your progress, and stay motivated.</p>
                        {!isAuthenticated && (
                            <div>
                                <Link to="/login" className="bg-red-500 hover:bg-red-700 text-white font-bold py-2 px-4 rounded mr-4">
                                    Login
                                </Link>
                            </div>
                        )}
                    </div>
                </div>
            </div>
            <section className="bg-gray-100 py-20">
                <div className="container mx-auto text-center">
                    <h2 className="text-4xl font-bold mb-8">What We Offer</h2>
                    <div className="flex flex-wrap justify-center">
                        <div className="w-full md:w-1/3 p-4">
                            <div className="bg-white shadow-lg rounded-lg p-6">
                                <h3 className="text-2xl font-semibold mb-4">Track Workouts</h3>
                                <p>Log your exercises, sets, and reps with ease and monitor your progress over time.</p>
                            </div>
                        </div>
                        <div className="w-full md:w-1/3 p-4">
                            <div className="bg-white shadow-lg rounded-lg p-6">
                                <h3 className="text-2xl font-semibold mb-4">Monitor Progress</h3>
                                <p>Visualize your progress with detailed charts and graphs.</p>
                            </div>
                        </div>
                        <div className="w-full md:w-1/3 p-4">
                            <div className="bg-white shadow-lg rounded-lg p-6">
                                <h3 className="text-2xl font-semibold mb-4">Stay Motivated</h3>
                                <p>Set goals and receive motivational tips to keep you on track.</p>
                            </div>
                        </div>
                    </div>
                </div>
            </section>
            <section className="bg-white py-20">
                <div className="container mx-auto text-center">
                    <h2 className="text-4xl font-bold mb-8">Community Support</h2>
                    <p>Join a community of like-minded individuals who are also on their fitness journey. Share tips, ask for advice, and stay motivated together.</p>
                </div>
            </section>
            <Footer />
        </div>
    );
};

export default HomePage;
