# MockSmart - AI-driven Mock Interview System

MockSmart is an AI-powered mock interview application designed to help users prepare for interviews by providing detailed feedback on their performance. It offers a comprehensive analysis of user responses through natural language processing (NLP), facial recognition, and body language assessment. The system analyzes video recordings of user responses, providing actionable feedback on key interview skills such as confidence, clarity, and body language.

## Features

- **AI-powered feedback**: Analyze video responses using NLP and facial recognition technologies.
- **Natural Language Processing (NLP)**: Evaluates the user's verbal communication, focusing on clarity, coherence, and confidence.
- **Facial Recognition**: Assesses body language, facial expressions, and eye contact to provide insights into the user's demeanor.
- **Detailed Reports**: Generates reports with suggestions for improvement in communication, body language, and overall presentation.
- **User-friendly Interface**: Easy-to-use interface for recording and uploading videos, along with the feedback reports.

## Technologies Used

- **Frontend**: 
  - React.js for the user interface.
  - Tailwind CSS for styling.
  
- **Backend**:
  - Django for the backend API.
  - DRF (Django Rest Framework) for building APIs.
  
- **AI & Machine Learning**:
  - NLP for analyzing the text from video responses.
  - Facial recognition and emotion detection for analyzing body language and facial expressions.
  - OpenCV for video analysis.
  - TensorFlow/PyTorch for implementing machine learning models.
  
- **Database**:
  - MySQL for storing user data, videos, and feedback.

  
  
## Setup & Installation

### Prerequisites

Make sure you have the following installed:

- Python 3.8 or higher
- Node.js and npm
- MySQL
- TensorFlow/PyTorch (depending on your system and configuration)

### Backend Setup

1. Clone the repository:
    ```bash
    git clone https://github.com/Okweso/mocksmart.git
    cd MockSmart
    ```

2. Create a virtual environment and activate it:
    ```bash
    python -m venv venv
    source venv/bin/activate  # On Windows, use venv\Scripts\activate
    ```

3. Install the required dependencies:
    ```bash
    pip install -r requirements.txt
    ```

4. Configure your PostgreSQL database:
    - Create a new database and configure your database settings in the `settings.py` file of the Django project.
  
5. Run migrations to set up the database:
    ```bash
    python manage.py makemigrations
    python manage.py migrate
    ```

6. Create a superuser to access the Django admin:
    ```bash
    python manage.py createsuperuser
    ```

7. Start the Django development server:
    ```bash
    python manage.py runserver
    ```

### Frontend Setup

1. Navigate to the frontend directory:
    ```bash
    cd MockSmart/frontend
    ```

2. Install the required dependencies:
    ```bash
    npm install
    ```

3. Start the React development server:
    ```bash
    npm start
    ```

### Running the App

Once both the frontend and backend are running, you can access the application at:

- Frontend: [http://localhost:3000](http://localhost:3000)
- Backend API: [http://localhost:8000/api/](http://localhost:8000/api/)

## Usage

1. **Create an Account**: Sign up to create an account.
2. **Record a Video**: Record yourself answering interview questions.
3. **Upload the video**: Upload the recorded video for analysis.
4. **Wait for feedback**: Receive detailed feedback based on your video response, including NLP analysis and facial recognition insights.
5. **Review & Improve**: Take actionable steps from the feedback to improve your interview performance.

## API Documentation

### Endpoints

#### 1. `GET /feedback/`
- **Description**: Retrieve feedback for a specific video or user.
- **Response**: Returns feedback data, including analysis on body language, NLP score, and suggestions for improvement.
- **Example Response**:
  ```json
  {
    "video_id": 1,
    "nlp_score": 75,
    "body_language_score": 80,
    "suggestions": {
      "nlp": "Improve your clarity and confidence.",
      "body_language": "Maintain eye contact throughout the response."
    }
  }

  #### 1. `GET /videos/`
- **Description**: Retrieve a list of all uploaded videos.
- **Response**: Returns metadata about each video, such as the video ID, user ID, and upload date.
- **Example Response**:
  ```json
  {
    "id": 1,
    "title": "Interview preparation for Agakhan",
    "video": "http://127.0.0.1:8000/media/videos/interview-cut.mp4",
    "date": "2024-11-29T07:30:31.774122Z",
    "user_id": null
    }
  }

  #### 1. `GET /analyze/<int:video_id>/`
- **Description**: Analyze a specific video and generate feedback using AI (NLP and facial recognition).

### 1. `GET /upload_video/`
- **Description**: Upload a video for analysis. The video will be processed and stored in the system.

# Running Tests

To ensure the stability and correctness of the MockSmart application, we have written comprehensive tests for both the frontend and backend.

### Backend Tests

1. **Setup**: Before running the tests, make sure you have followed the setup steps for the backend (as outlined in the "Backend Setup" section). Ensure your environment is correctly set up and the database is migrated.

2. **Running the Tests**: 
    To run the backend tests, navigate to the backend directory and use Django's testing framework:
    ```bash
    cd MockStart
    python manage.py test
    ```
    This will automatically discover and run all the tests in your project.

3. **Test Coverage**: The backend tests cover the following areas:
    - **API Endpoints**: Tests for the `GET /videos/`, `GET /feedback/`, `POST /analyze/<int:video_id>/`, and `POST /upload_video/` endpoints to ensure that they return the expected responses.
    - **Database Models**: Tests to verify the correct creation, retrieval, and deletion of data in models such as `Video` and `Feedback`.
    - **Business Logic**: Tests for the core application logic, including video analysis and feedback generation.
    - **Edge Cases**: Tests for handling edge cases, such as invalid input or failed video uploads.

4. **Test Results**: Once the tests are completed, Django will provide a summary of the tests that passed, failed, or were skipped.
### Frontend Tests
For frontend testing, ensure that all visualizations and user interactions work as expected.

## Contributing

We welcome contributions to improve MockSmart! If you'd like to contribute, please fork the repository and submit a pull request. Before submitting a pull request, ensure that the following steps have been completed:

- Fork the repository.
- Clone your fork and create a new branch for your feature.
- Implement your changes and write tests if applicable.
- Ensure all tests pass by running the test suite (`python manage.py test`).
- Submit a pull request with a clear description of your changes.



## Contact

For any questions, feel free to reach out to us via [paulokweso7@gmail.com].

---

Thank you for using MockSmart! We hope it helps you prepare for your next interview with confidence.
