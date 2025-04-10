# Multiple Choice Question Generation Tool - Frontend

This project is the frontend interface for the Multiple Choice Question Generation Tool, providing an interactive user experience for generating and managing multiple choice questions.

## Installation

### Prerequisites

- Node.js 22.0.7 or later
- npm (comes with Node.js)
- Internet connection

### Setup Instructions

1. **Install Node.js**

   Download and install Node.js version 22.0.7 from the [official Node.js website](https://nodejs.org/).
   
   To verify the installation, run:
   ```bash
   node --version
   ```
   
   This should display `v22.0.7` or higher.

2. **Clone the repository**

   ```bash
   git clone <repository-url>
   cd multiple-choice-question-tool
   ```

3. **Install dependencies**

   ```bash
   npm install
   ```

4. **Configure Environment Variables**

   Create a `.env` file in the root directory with the following content:
   
   ```
   VITE_BE_URL=your_backend_url_here
   ```
   
   Replace `your_backend_url_here` with the URL of your backend server (e.g., `http://localhost:5000`).

## Usage

Start the development server:

```bash
npm run dev
```

This will launch the application in development mode. Open your browser and navigate to the displayed URL (typically `http://localhost:5173`) to access the application.

## Features

- User-friendly interface for generating multiple choice questions
- Question customization options
- Preview and export functionality
- Integration with backend AI services

## Building for Production

To create a production build:

```bash
npm run build
```

## License

[MIT License](LICENSE)