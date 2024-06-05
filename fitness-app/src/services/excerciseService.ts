import axios from 'axios';

const API_URL = 'http://localhost:5000/api'; // Adjust the URL to your backend API

// Function to fetch the JWT token from another system
const fetchToken = async (): Promise<string> => {
    try {
        const response = await axios.get('http://another-system.com/api/get-token'); // Adjust URL
        return response.data.token; // Assuming the response contains the token
    } catch (error) {
        console.error('Error fetching token', error);
        throw error;
    }
};

export const getExercisesByBodyPart = async (bodyPart: string) => {
    try {
        const token = await fetchToken();
        const response = await axios.get(`${API_URL}/exercises/${bodyPart}`, {
            headers: {
                'Authorization': `Bearer ${token}` // Include the token in the Authorization header
            }
        });
        return response.data;
    } catch (error) {
        console.error('Error fetching exercises', error);
        throw error;
    }
};
