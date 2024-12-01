import os
from django.test import TestCase
from django.core.files.uploadedfile import SimpleUploadedFile
from django.conf import settings
from .models import MockVideos, Users, Feedback
from django.urls import reverse
from .task import extract_audio
from .views import analyze_clarity
from rest_framework.test import APIClient
from rest_framework import status
from unittest.mock import patch, MagicMock

class VideoUploadTests(TestCase):

    # Test valid video file upload
    def test_valid_video_upload(self):
        with open('interview-cut.mp4', 'rb') as video_file:
            video = SimpleUploadedFile(
                name='interview-cut.mp4',
                content=video_file.read(),
                content_type='video/mp4'
            )
        
        # Upload the video using the POST request to the correct URL
        response = self.client.post(reverse('upload_video'), {'video': video})
        
        # Check if upload was successful (status code 200 or 201)
        self.assertEqual(response.status_code, 200)
        
        # Ensure the video is saved in the database
        uploaded_video = MockVideos.objects.get(name='valid_video.mp4')
        self.assertIsNotNone(uploaded_video)
        self.assertTrue(uploaded_video.file.name.endswith('.mp4'))  

    # Test invalid video file type (image instead of video)
    def test_invalid_video_type(self):
        invalid_file = SimpleUploadedFile(
            name='invalid_image.jpg',
            content=b'fake_image_data',
            content_type='image/jpeg'
        )
        
        response = self.client.post(reverse('upload_video'), {'video': invalid_file})
        
        # Check if the server rejects it with a 400 error or a custom error message
        self.assertEqual(response.status_code, 400)
        self.assertIn('Invalid file type', response.content.decode())

    # Test large video file upload (exceeds size limit)
    def test_large_video_file(self):
        large_file = SimpleUploadedFile(
            name='interview-cut.mp4',
            content=b'a' * (settings.MAX_UPLOAD_SIZE + 1),  
            content_type='video/mp4'
        )
        
        response = self.client.post(reverse('upload_video'), {'video': large_file})
        
        # Ensure the file is rejected due to size
        self.assertEqual(response.status_code, 400)
        self.assertIn('File size exceeds limit', response.content.decode())

    # Test that the video file is actually saved to disk
    def test_video_file_saved(self):
        with open('interview-cut', 'rb') as video_file:
            video = SimpleUploadedFile(
                name='interview-cut.mp4',
                content=video_file.read(),
                content_type='video/mp4'
            )

        response = self.client.post(reverse('upload_video'), {'video': video})
        
        # Ensure that the video was saved in the correct location
        uploaded_video = MockVideos.objects.get(name='valid_video.mp4')
        self.assertTrue(os.path.exists(uploaded_video.file.path))  # Check if file exists on disk

    # Test missing file (no video uploaded)
    def test_missing_video_file(self):
        response = self.client.post(reverse('upload_video'), {})
        self.assertEqual(response.status_code, 400)
        self.assertIn('No video file provided', response.content.decode())


class ClarityAnalysisTests(TestCase):

    # Test for valid text input with normal clarity
    def test_clarity_analysis_valid_response(self):
        response_text = "I believe communication is key in any team. I strive to be clear and concise."

        analysis_result = analyze_clarity(response_text)
        
        # Ensure the analysis contains the expected fields
        self.assertIn('avg_sentence_length', analysis_result)
        self.assertIn('filler_word_count', analysis_result)
        self.assertIn('grammar_issues', analysis_result)
        self.assertIn('clarity', analysis_result)

        # Ensure clarity score is within valid range (0-100)
        self.assertGreaterEqual(analysis_result['clarity'], 0)
        self.assertLessEqual(analysis_result['clarity'], 100)

        # Test for expected sentence length (average should be within normal range)
        self.assertGreaterEqual(analysis_result['avg_sentence_length'], 8)
        self.assertLessEqual(analysis_result['avg_sentence_length'], 20)

    # Test for text with many filler words
    def test_clarity_analysis_with_filler_words(self):
        response_text = "Um, I like technology, you know, and uh, solving problems is, um, important."

        analysis_result = analyze_clarity(response_text)
        
        # Ensure that filler words count is greater than 0
        self.assertGreater(analysis_result['filler_word_count'], 0)
        
        # Check that the clarity score is penalized for filler words
        self.assertLess(analysis_result['clarity'], 100)

    # Test for text with long sentences (sentence length outside optimal range)
    def test_clarity_analysis_long_sentences(self):
        response_text = "I believe that communication is one of the most important skills in any team, and in order to be effective, one must always strive for clarity and brevity when delivering their message to ensure understanding and avoid confusion."

        analysis_result = analyze_clarity(response_text)
        
        # Check if the average sentence length is too long
        self.assertGreater(analysis_result['avg_sentence_length'], 20)

        # Ensure clarity score is penalized for long sentences
        self.assertLess(analysis_result['clarity'], 100)

    # Test for text with grammar issues
    def test_clarity_analysis_with_grammar_issues(self):
        response_text = "Me and my team are working together to solving problems and to improve performance."

        analysis_result = analyze_clarity(response_text)
        
        # Check that there are grammar issues (e.g., "Me" should be "I")
        self.assertGreater(len(analysis_result['grammar_issues']), 0)

        # Ensure clarity score is penalized for grammar issues
        self.assertLess(analysis_result['clarity'], 100)

    # Test for very clear and concise text
    def test_clarity_analysis_perfect_response(self):
        response_text = "Communication is essential for teamwork. Clarity improves understanding."

        analysis_result = analyze_clarity(response_text)

        # Check that clarity score is 100 or very close to 100 for a perfect response
        self.assertEqual(analysis_result['clarity'], 100)

    # Test for empty response
    def test_clarity_analysis_empty_response(self):
        response_text = ""

        analysis_result = analyze_clarity(response_text)
        
        # Ensure that the clarity score is penalized (most likely 0 for empty response)
        self.assertEqual(analysis_result['clarity'], 0)


class AnalyzeVideoViewTests(TestCase):
    def setUp(self):
        # Create mock video and user instances for the tests
        self.user = Users.objects.create(id=1, username="testuser", email="testuser@example.com")
        self.video = MockVideos.objects.create(id=1, user_id=self.user, video="interview-cut.mp4")
        self.client = APIClient()

    @patch('MockInterviews.task.extract_audio')
    @patch('MockInterviews.views.transcribe_audio')
    @patch('MockInterviews.views.analyze_clarity')
    @patch('MockInterviews.views.analyze_facial_features_upper_body')
    @patch('MockInterviews.views.generate_feedback_and_recommendations')
    def test_video_analysis_success(self, mock_generate_feedback, mock_analyze_facial, mock_analyze_clarity, mock_transcribe, mock_extract_audio):
        # Mock the function outputs
        mock_extract_audio.return_value = "mock_audio_path.wav"
        mock_transcribe.return_value = "This is a transcription of the video."
        mock_analyze_clarity.return_value = {
            "clarity": 85,
            "avg_sentence_length": 15,
            "filler_word_count": 3,
            "grammar_issues": []
        }
        mock_analyze_facial.return_value = {
            "confidence_score": 90,
            "eye_contact": 80,
            "posture_score": 75,
            "expression_analysis": "neutral"
        }
        mock_generate_feedback.return_value = {
            "feedback": "Good job!",
            "recommendations": "Try to reduce filler words."
        }

        # Make the API request
        response = self.client.post(
            f'http://127.0.0.1:8000/analyze/1',  
            format='json'
        )

        # Validate the response
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn("transcription", response.data)
        self.assertIn("clarity_analysis", response.data)
        self.assertIn("facial_analysis", response.data)
        self.assertIn("feedback", response.data)
        self.assertIn("recommendations", response.data)

    @patch('yourapp.views.extract_audio')
    @patch('yourapp.views.transcribe_audio')
    @patch('yourapp.views.analyze_clarity')
    @patch('yourapp.views.analyze_facial_features_upper_body')
    def test_video_not_found(self, mock_analyze_facial, mock_analyze_clarity, mock_transcribe, mock_extract_audio):
        # Simulate a video not found scenario by passing a non-existing video ID
        response = self.client.post('http://127.0.0.1:8000/analyze/1', format='json')

        # Check for 404 response
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        self.assertIn("error", response.data)

    @patch('MockInterviews.views.extract_audio')
    @patch('MockInterviews.task.transcribe_audio')
    @patch('MockInterviews.views.analyze_clarity')
    @patch('MockInterviews.views.analyze_facial_features_upper_body')
    def test_video_analysis_internal_error(self, mock_analyze_facial, mock_analyze_clarity, mock_transcribe, mock_extract_audio):
        # Simulate an internal error by raising an exception in the view
        mock_extract_audio.side_effect = Exception("Unexpected error")

        response = self.client.post(
            f'http://127.0.0.1:8000/analyze/1',  
            format='json'
        )

        # Check for 500 error
        self.assertEqual(response.status_code, status.HTTP_500_INTERNAL_SERVER_ERROR)
        self.assertIn("error", response.data)
        self.assertIn("details", response.data)

    @patch('MockInterviews.views.extract_audio')
    @patch('MockInterviews.task.transcribe_audio')
    @patch('MockInterviews.views.analyze_clarity')
    @patch('MockInterviews.views.analyze_facial_features_upper_body')
    def test_missing_video_id(self, mock_analyze_facial, mock_analyze_clarity, mock_transcribe, mock_extract_audio):
        # Simulate missing video ID in the URL
        response = self.client.post('http://127.0.0.1:8000/analyze/1', format='json')

        # Check for 404 response due to missing video ID
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    @patch('MockInterviews.views.extract_audio')
    @patch('MockInterviews.task.transcribe_audio')
    @patch('MockInterviews.views.analyze_clarity')
    @patch('MockInterviews.views.analyze_facial_features_upper_body')
    def test_feedback_saved_in_database(self, mock_analyze_facial, mock_analyze_clarity, mock_transcribe, mock_extract_audio):
        # Mock the function outputs
        mock_extract_audio.return_value = "mock_audio_path.wav"
        mock_transcribe.return_value = "This is a transcription of the video."
        mock_analyze_clarity.return_value = {
            "clarity": 85,
            "avg_sentence_length": 15,
            "filler_word_count": 3,
            "grammar_issues": []
        }
        mock_analyze_facial.return_value = {
            "confidence_score": 90,
            "eye_contact": 80,
            "posture_score": 75,
            "expression_analysis": "neutral"
        }
        mock_generate_feedback.return_value = {
            "feedback": "Good job!",
            "recommendations": "Try to reduce filler words."
        }

        # Make the API request
        response = self.client.post(
            f'http://127.0.0.1:8000/analyze/1',  
            format='json'
        )

        # Ensure that the feedback is saved in the database
        feedback_record = Feedback.objects.last()
        self.assertEqual(feedback_record.video_id, self.video)
        self.assertEqual(feedback_record.user_id, self.user)
        self.assertEqual(feedback_record.confidence_score, 90)
        self.assertEqual(feedback_record.clarity_score, 85)
        self.assertEqual(feedback_record.body_language_score, 75)