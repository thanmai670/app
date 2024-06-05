import axios from 'axios';

const API_URL = 'http://localhost:5000/api'; // Adjust the URL to your backend API

export const getExercisesByBodyPart = async (bodyPart: string) => {
    try {
        const response = await axios.get(`${API_URL}/exercises/${bodyPart}`);
        return response.data;
    } catch (error) {
        console.error('Error fetching exercises', error);
        throw error;
    }
};
