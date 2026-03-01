# Civic Issue Management System

A comprehensive web application for reporting and tracking civic issues, built with React, FastAPI, and MySQL.

## Features

- **Home Page**: Welcoming interface with easy navigation.
- **Authentication**: Login and Signup for citizens.
- **Report Issue**: Submit complaints with description, location (auto-capture), voice input, and image upload.
- **Tracking**: Monitor complaint status (Submitted, In Progress, Resolved).
- **Admin Dashboard**: Manage complaints, update status, and filter by priority.
- **Notifications**: See updates on complaint status.
- **About**: Learn more about the system.

## Tech Stack

- **Frontend**: React (Vite), CSS Modules (Glassmorphism), Lucide React (Icons), Axios.
- **Backend**: FastAPI, SQLAlchemy, Pydantic.
- **Database**: MySQL (configured in `backend/database.py`).

## Setup Instructions

### Backend

1. Navigate to the project root:
   ```bash
   cd e:\PROJECT\CIVIC-ISSUE-MANAGEMENT-SYSTEM
   ```
2. Create virtual environment and install dependencies:
   ```bash
   python -m venv venv
   .\venv\Scripts\activate
   pip install -r backend/requirements.txt
   ```
3. Update database credentials in `backend/database.py` if needed (Default: `root:password@localhost/civic_db`).
4. Run the server:
   ```bash
   uvicorn backend.main:app --reload
   ```
   The API will be available at `http://localhost:8000`.

### Frontend

1. Navigate to frontend directory:
   ```bash
   cd frontend
   ```
2. Install dependencies:
   ```bash
   npm install
   ```
3. Run the development server:
   ```bash
   npm run dev
   ```
   Access the app at `http://localhost:5173`.

## Usage

1. **Sign Up**: Create an account as a citizen.
2. **Report**: Use the "Report Issue" button to submit a complaint.
   - Click the microphone icon for voice input.
   - Click the location button to auto-detect your location.
   - Upload an image of the issue.
3. **Track**: View your submitted complaints in the "Track Status" page.
4. **Admin**: (For demo purposes, you can manually update user role to 'admin' in database) Access `/admin` dashboard to view all complaints and update their status.

## Future Enhancements

- Integration with real AI service (e.g., OpenAI/Google Vision) for accurate categorization.
- Real-time notifications using WebSockets.
- Mobile app version.
- Enhanced analytics dashboard.