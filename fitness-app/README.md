

## Project Structure

This project follows a structured directory layout to ensure easy management and scalability. Here's a breakdown of the key directories:

- **`/public`**:
  - Contains static assets like the main HTML file, which is the entry point for the application.

- **`/src/assets`**:
  - Holds all global styles and images. Utilizing Tailwind CSS, the configuration for styling is included here.

- **`/src/components`**:
  - This directory contains all the React components used across the application.
  - **`/common`**: Subdirectory for reusable UI elements like buttons, modals, and any other common components that appear throughout the app.

- **`/src/hooks`**:
  - Place for custom React hooks, which are used to manage state or side effects across multiple components. These hooks help keep the components clean and focused on the UI.

- **`/src/services`**:
  - Dedicated to functions or classes that handle API requests. By separating these from the UI components, the project maintains a clean separation of concerns, enhancing maintainability and scalability.

- **`/src/utils`**:
  - A directory for utility functions which are used across the application to perform common tasks like data formatting or validation.

Each part of this structure is designed to support the application's functionality in a clean and efficient manner, ensuring that the codebase is easy to understand and maintain.
