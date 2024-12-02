from django.shortcuts import render
from rest_framework.views import APIView
from rest_framework import viewsets
from rest_framework.response import Response
from rest_framework import status
from rest_framework.decorators import permission_classes, api_view
from django.contrib.auth.hashers import make_password
from MockInterviews.models import Users, MockVideos, Feedback
from MockInterviews.serializers import UsersSerializer, MockVideosSerializer, FeedbackSerializer
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework.permissions import IsAuthenticated
from MockInterviews.task import extract_audio, transcribe_audio
import spacy
import cv2
import mediapipe as mp
#import openai
from transformers import pipeline
import json
import environ


nlp = spacy.load("en_core_web_sm")

# Create your views here.

class RegisterUserView(APIView):
    def post(self, request):
        data = request.data
        data['password'] = make_password(data['password'])
        serializer = UsersSerializer(data=data)
        if serializer.is_valid():
            user = serializer.save()

            #generate jwt token for the registered user
            refresh = RefreshToken.for_user(user)

            return Response({
                "message": "User registered successfully!",
                "user": {
                    "id": user.id,
                    "email": user.email,
                    "first_name": user.first_name,
                    "last_name": user.last_name,
                    "profession": user.profession,
                },
                "token": {
                    "refresh": str(refresh),
                    "access": str(refresh.access_token),
                }
            }, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_user_details(request):
    user = request.user
    return Response({
        "id": user.id,
        "email": user.email,
        "first_name": user.first_name,
        "last_name": user.last_name,
        "profession": getattr(user, 'profession', '')
    })

    

class ProtectedView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        return Response({"message": "This is a protected view."})
    

class UploadVideoView(APIView):
    def post(self, request):
        # Deserialize the incoming data
        serializer = MockVideosSerializer(data=request.data)
        
        if serializer.is_valid():
            # Validate file size and format
            video_file = request.FILES.get('video')
            if video_file:
                # File size validation (50MB max)
                max_size_mb = 50
                if video_file.size > max_size_mb * 1024 * 1024:
                    return Response(
                        {"error": f"File size exceeds {max_size_mb}MB limit"},
                        status=status.HTTP_400_BAD_REQUEST
                    )

                # File format validation
                allowed_formats = ['mp4', 'avi', 'mov', 'mkv']
                file_extension = video_file.name.split('.')[-1].lower()
                if file_extension not in allowed_formats:
                    return Response(
                        {"error": f"Unsupported file format '{file_extension}'"},
                        status=status.HTTP_400_BAD_REQUEST
                    )

            # Save the video record
            serializer.save()
            return Response(
                {"success": True, "message": "Video uploaded successfully", "video_id": serializer.data['id']},
                status=status.HTTP_201_CREATED
            )

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

#function to analyze body language
def analyze_facial_features_upper_body(video_path):
    """
    Analyze facial features and upper body posture for chest-up videos.
    """
    mp_face_detection = mp.solutions.face_detection
    mp_pose = mp.solutions.pose
    results_summary = {
        "expression_analysis": {},
        "eye_contact": 0,
        "confidence_score": 0,
        "posture_score": 0,
    }

    # Load video
    cap = cv2.VideoCapture(video_path)
    frame_count = 0
    eye_contact_count = 0
    stable_posture_count = 0

    with mp_face_detection.FaceDetection(min_detection_confidence=0.5) as face_detection, \
         mp_pose.Pose(min_detection_confidence=0.5) as pose_detection:
        while cap.isOpened():
            ret, frame = cap.read()
            if not ret:
                break

            frame_count += 1

            # Convert the frame to RGB
            frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

            # Analyze facial features
            face_results = face_detection.process(frame_rgb)
            if face_results.detections:
                for detection in face_results.detections:
                    # Analyze confidence from bounding box scores
                    confidence = detection.score[0]
                    results_summary["confidence_score"] += confidence

                    # Assume eye contact if a face is detected
                    eye_contact_count += 1

            # Analyze upper body posture
            pose_results = pose_detection.process(frame_rgb)
            if pose_results.pose_landmarks:
                landmarks = pose_results.pose_landmarks.landmark
                left_shoulder = landmarks[mp_pose.PoseLandmark.LEFT_SHOULDER]
                right_shoulder = landmarks[mp_pose.PoseLandmark.RIGHT_SHOULDER]

                # Calculate shoulder alignment
                shoulder_alignment = abs(left_shoulder.y - right_shoulder.y)
                if shoulder_alignment < 0.1:  # Threshold for alignment
                    stable_posture_count += 1

            # Stop processing after analyzing 100 frames for performance
            if frame_count >= 100:
                break

    # Calculate averages
    if frame_count > 0:
        avg_confidence = results_summary["confidence_score"] = frame_count
        results_summary["confidence_score"] = min(avg_confidence * 100, 100)
        results_summary["eye_contact"] = min((eye_contact_count / frame_count) * 100, 100)  # Cap at 100%
        results_summary["posture_score"] = min((stable_posture_count / frame_count) * 100, 100)  

    cap.release()
    return results_summary

# Clarity analysis function
def analyze_clarity(text):
    import spacy

    # Load Spacy model
    nlp = spacy.load("en_core_web_sm")
    doc = nlp(text)

    # Step 1: Count sentences and average sentence length
    sentences = list(doc.sents)
    avg_sentence_length = (
        sum(len(sent.text.split()) for sent in sentences) / len(sentences) if sentences else 0
    )

    # Step 2: Detect filler words
    filler_words = ["uh", "um", "like", "you know"]
    filler_count = sum(text.lower().count(word) for word in filler_words)

    # Step 3: Grammar check 
    grammar_issues = [token.text for token in doc if token.pos_ == "X"]

    # Step 4: Determine overall clarity score (I'm starting with a perfect score)
    clarity = 100  

    # Penalize for long average sentence lengths (optimal range: 8-20 words)
    if avg_sentence_length < 8 or avg_sentence_length > 20:
        clarity -= 10

    # Penalize based on filler word count (Max penalty: 20 points)
    clarity -= min(filler_count * 2, 20)  

    # Penalize for grammar issues (Max penalty: 30 points)
    clarity -= min(len(grammar_issues) * 5, 30)  

    # Ensuring clarity score is within bounds (0-100)
    clarity = max(0, min(clarity, 100))

    return {
        "avg_sentence_length": avg_sentence_length,
        "filler_word_count": filler_count,
        "grammar_issues": grammar_issues,
        "clarity": clarity,
    }

def extract_output(response_text, keyword):
    """
    Extracts the text following the specified keyword in the generated response.
    Args:
        response_text (str): The generated text from the model.
        keyword (str): The keyword (e.g., "Feedback:" or "Recommendation:").
    Returns:
        str: The extracted output after the keyword.
    """
    if keyword in response_text:
        return response_text.split(keyword, 1)[1].strip()
    return "No valid output found."

from transformers import AutoTokenizer, pipeline
#function for generating feedback and recommendations
def generate_feedback_and_recommendations(analysis_results):
    # confidence_score_feedback = ""
    # clarity_score_feedback = ""
    # body_language_feedback = ""
    # avg_sentence_length_feedback = ""
    # filler_word_count_feedback = ""
    # eye_contact_feedback = ""

    # if analysis_results.get('confidence_score', 0) <=25:
    #     confidence_score_feedback = "Your confidence was very low. You need to improve on it. You can practice more with relatives and friends to gain more confidence, then come back and give it another try."
    # elif analysis_results.get('confidence_score', 0) >25 and analysis_results.get('confidence_score', 0) <=50:
    #     confidence_score_feedback = "Keep working on your confidence. The low confidence score might impact your interview performance. Try relaxation techniques before interviews."
    # elif analysis_results.get('confidence_score', 0) >50 and analysis_results.get('confidence_score', 0) <=75:
    #     confidence_score_feedback = "Good confidence score. However, you can improve by practising more to improve on areas that you might be weak in."
    # elif analysis_results.get('confidence_score', 0) >75 and analysis_results.get('confidence_score', 0) <=100:
    #     confidence_score_feedback = "Great confidence levels. Please keep it up and ensure you are good on other areas to ensure a good impression."
    # else:
    #     confidence_score_feedback = "Something happened and we could not generate feedback for your confidence score"
    
    # if analysis_results.get('clarity', 0) <=25:
    #     clarity_score_feedback = "Your clarity is poor. Focus on articulating your thoughts clearly."
    # elif analysis_results.get('clarity', 0) >25 and analysis_results.get('clarity', 0) <=50:
    #     clarity_score_feedback = "Your clarity is below average. Avoid filler words and structure your responses."
    # elif analysis_results.get('clarity', 0) >50 and analysis_results.get('clarity', 0) <=75:
    #     clarity_score_feedback = "Good clarity. Keep responses concise and focused to improve further."
    # elif analysis_results.get('clarity', 0) >75 and analysis_results.get('clarity', 0) <=100:
    #     clarity_score_feedback = "Excellent clarity. Maintain this to make a great impression."
    # else:
    #     clarity_score_feedback = "Unable to generate feedback for clarity."

    # if analysis_results.get('posture_score', 0) <=25:
    #     body_language_feedback = "Poor posture detected. Sit upright and avoid slouching to appear more confident."
    # elif analysis_results.get('posture_score', 0) >25 and analysis_results.get('posture_score', 0) <=50:
    #     body_language_feedback = "Body posture needs improvement. Focus on keeping shoulders aligned."
    # elif analysis_results.get('posture_score', 0) >50 and analysis_results.get('posture_score', 0) <=75:
    #     body_language_feedback = "Decent posture. Small adjustments can enhance your professional presence."
    # elif analysis_results.get('posture_score', 0) >75 and analysis_results.get('posture_score', 0) <=100:
    #     body_language_feedback = "Excellent posture. This conveys confidence and professionalism."
    # else:
    #     body_language_feedback = "Something happened and we could not generate feedback for your clarity score"

    # if analysis_results.get('avg_sentence_length', 0) <=10:
    #     avg_sentence_length_feedback = "Your sentences are too short. Add more detail to provide clear responses."
    # elif analysis_results.get('avg_sentence_length', 0) >10 and analysis_results.get('avg_sentence_length', 0) <=25:
    #     avg_sentence_length_feedback = "Great sentence length. Keep responses concise yet informative."
    # elif analysis_results.get('avg_sentence_length', 0) >25 and analysis_results.get('avg_sentence_length', 0) <=35:
    #     avg_sentence_length_feedback = "Sentences are slightly long. Pause to ensure the message is clear."
    # else:
    #     avg_sentence_length_feedback = "Sentences are too long. Break ideas into shorter, clear sentences."
    
    # if analysis_results.get('eye_contact', 0) <=25:
    #     eye_contact_feedback = "Eye contact is minimal. Practice maintaining eye contact to build trust."
    # elif analysis_results.get('eye_contact', 0) >25 and analysis_results.get('eye_contact', 0) <=50:
    #     eye_contact_feedback = "Eye contact is low. Focus on the interviewer's face to stay engaged."
    # elif analysis_results.get('eye_contact', 0) >50 and analysis_results.get('eye_contact', 0) <=75:
    #     eye_contact_feedback = "Good eye contact. Stay consistent to convey confidence."
    # elif analysis_results.get('eye_contact', 0) >75 and analysis_results.get('eye_contact', 0) <=100:
    #     eye_contact_feedback = "Excellent eye contact. This helps in building strong connections."
    # else:
    #     eye_contact_feedback = "Unable to generate feedback for eye contact."
    
    # if analysis_results.get('filler_word_count', 0) <=7:
    #     filler_word_count_feedback = "Great job! Minimal filler words indicate strong verbal clarity."
    # elif analysis_results.get('filler_word_count', 0) >7 and analysis_results.get('filler_word_count', 0) <=14:
    #     filler_word_count_feedback = "Try reducing filler words for clearer communication."
    # else:
    #     filler_word_count_feedback = "Excessive filler words detected. Practice speaking slowly and clearly."
    
    # feedback = [
    #     {"Confidence Score": confidence_score_feedback},
    #     {"Eye Contact Score": eye_contact_feedback},
    #     {"Clarity Score": clarity_score_feedback},
    #     {"Body Language/Posture Score": body_language_feedback},
    #     {"Average Sentence Length": avg_sentence_length_feedback},
    #     {"Filler Words": filler_word_count_feedback}
    # ]

    # return feedback



    """
    Generate detailed feedback and recommendations using Hugging Face Transformers (GPT-2 or GPT-Neo)
    based on analysis results.
    
    Args:
        analysis_results (dict): A dictionary containing metrics like 'confidence_score',
                                 'eye_contact', 'posture_score', and 'expression_analysis'.
    
    Returns:
        tuple: A tuple containing two strings: feedback and recommendations.
    """
    
    # Initializing the text generation pipeline with GPT-2
    env = environ.Env()
    environ.Env.read_env()
    tokenizer = AutoTokenizer.from_pretrained("gpt2")
    generator = pipeline("text-generation", model="gpt2", tokenizer=tokenizer) #model="EleutherAI/gpt-neo-1.3B")
    generator = pipeline("text-generation", 
    model="EleutherAI/gpt-neo-1.3B", 
    use_auth_token=env('AUTH_TOKEN'))

    # Construct the prompt for feedback
    feedback_prompt = (
        f"""Here are examples of interview feedback based on performance metrics:

        Example 1:
        Confidence Score: 0.75
        Eye Contact: 70%
        Posture Score: 60%
        Facial Expressions: Neutral

        feedback: Your confidence was adequate, but try to speak more assertively. Work on maintaining consistent eye contact. Your posture needs improvement—sit up straight and avoid fidgeting. Try to smile more during responses to appear more engaging.

        Example 2:
        Confidence Score: 0.85
        Eye Contact: 90%
        Posture Score: 80%
        Facial Expressions: Positive

        feedback: Excellent confidence and eye contact! Your posture is good, but you can relax a little to seem more natural. Continue to use positive facial expressions—they help convey enthusiasm and interest.
        Now evaluate:
        Confidence Score: {analysis_results.get('confidence_score', 0):.2f}
        Eye Contact: {analysis_results.get('eye_contact', 0):.2f}%
        Posture Score: {analysis_results.get('posture_score', 0):.2f}%
        Facial Expressions: {analysis_results.get('expression_analysis', {})}

        Feedback:
        """
    )
    
    # Construct the prompt for recommendations
    recommendations_prompt = (
        f"""Here are examples of interview feedback based on performance metrics:
        Example 1:
        Confidence Score: 0.70
        Eye Contact: 65%
        Posture Score: 50%
        Facial Expressions: Neutral
        
        recommendation: Your confidence level needs improvement. Practice speaking with more assertiveness and clarity to build a strong impression. Your eye contact was intermittent—try to focus more on maintaining consistent eye contact with the interviewer. Your posture showed a lack of engagement; sit upright and avoid slouching to appear more professional. Facial expressions were neutral; smiling occasionally and showing enthusiasm will enhance your overall impact.
        
        Example 2:
        Confidence Score: 0.85
        Eye Contact: 80%
        Posture Score: 75%
        Facial Expressions: Positive
        
        recommendation: Experiment with slight posture adjustments to find the balance between professional and relaxed.

        Example 3:
        Confidence Score: 0.60
        Eye Contact: 50%
        Posture Score: 65%
        Facial Expressions: Stif

        recommendation: Practice with friends or mentors to get used to maintaining eye contact. Engage in relaxation exercises to reduce tension in your facial expressions. Work on projecting confidence through body language, such as hand gestures and posture.
        Now Evaluate:
        Confidence Score: {analysis_results.get('confidence_score', 0):.2f}
        Eye Contact: {analysis_results.get('eye_contact', 0):.2f}%
        Posture Score: {analysis_results.get('posture_score', 0):.2f}%
        Facial Expressions: {analysis_results.get('expression_analysis', {})}
        Recommendation:
        """
       
    )

    # Generate feedback using the Hugging Face model
    feedback_response = generator(feedback_prompt, max_new_tokens=50, num_return_sequences=1, temperature=0.7, top_p=0.9, top_k=50, eos_token_id=tokenizer.encode("Feedback:")[0])
    feedback = extract_output(feedback_response[0]['generated_text'], "Feedback: ")
    #feedback = feedback_response[0]['generated_text'].strip()

    # Generate recommendations using the Hugging Face model
    recommendations_response = generator(recommendations_prompt, max_new_tokens=50, num_return_sequences=1, temperature=0.7, top_p=0.9, top_k=50)
    recommendations = extract_output(recommendations_response[0]["generated_text"], "Recommendation: ")
    #recommendations = recommendations_response[0]['generated_text'].strip()
    print("Feedback:", feedback)
    print("Recommendations:", recommendations)
    
    return feedback, recommendations

import traceback
class AnalyzeVideoView(APIView):
    def post(self, request, video_id):
        try:
            # Fetch video record by ID
            video = MockVideos.objects.get(id=video_id)

            # data = json.loads(request.body)
            # user_id = data.get('id')
            user_instance = Users.objects.get(id=video.user_id.id)

            # Step 1: Extract audio from the video
            audio_path = extract_audio(video.video.path)

            # Step 2: Transcribe the audio
            transcription = transcribe_audio(audio_path)

            # Step 3: Analyze transcription clarity
            clarity_results = analyze_clarity(transcription)

            # Step 4: Analyze facial features
            facial_analysis = analyze_facial_features_upper_body(video.video.path)

            analysis_results = {
                "confidence_score": facial_analysis["confidence_score"],
                "eye_contact": facial_analysis["eye_contact"],
                "posture_score": facial_analysis["posture_score"],
                "expression_analysis": facial_analysis["expression_analysis"],
                "clarity": clarity_results["clarity"],
                "avg_sentence_length": clarity_results["avg_sentence_length"],
                "filler_word_count": clarity_results["filler_word_count"],
            }
            feedback, recommendations = generate_feedback_and_recommendations(analysis_results)
            #recommendations = generate_feedback_and_recommendations(analysis_results)
            feedback_json = json.dumps(feedback)
            # Step 5: Save results to the database
            # Create feedback record
            feedback_record = Feedback.objects.create(
                feedback=feedback,
                recommendations=recommendations,
                video_id=video,
                confidence_score=facial_analysis["confidence_score"],
                clarity_score=clarity_results["clarity"],
                body_language_score=facial_analysis["posture_score"],
                avd_sentence_length=clarity_results["avg_sentence_length"],
                filler_word_count=clarity_results["filler_word_count"],
                grammar_issues=", ".join(clarity_results["grammar_issues"]),
                eye_contact=facial_analysis["eye_contact"],
                user_id=user_instance
            )

            # Step 6: Save transcription or return as response
            # Example: Add transcription to video record (optional)
            video.transcription = transcription
            video.analysis_results = {
                "facial_analysis": facial_analysis,
                "transcription": transcription,
                "clarity_analysis": clarity_results,
                "feedback": feedback,
                "recommendations": recommendations,
            }
            video.save()

            return Response(
                {
                    "success": True, 
                    "transcription": transcription, 
                    "clarity_analysis": clarity_results,
                    "facial_analysis": facial_analysis,
                    "feedback": feedback,
                    "recommendations": recommendations,
                    "confidence_score": facial_analysis["confidence_score"],
                    "eye_contact": facial_analysis["eye_contact"],
                    "posture_score": facial_analysis["posture_score"],
                    "expression_analysis": facial_analysis["expression_analysis"],
                    "clarity": clarity_results["clarity"],
                    "avg_sentence_length": clarity_results["avg_sentence_length"],
                    "filler_word_count": clarity_results["filler_word_count"],
                    },
                status=status.HTTP_200_OK
            )
        except MockVideos.DoesNotExist:
            return Response(
                {"error": "Video not found"},
                status=status.HTTP_404_NOT_FOUND
            )
        
        except Exception as e:  
            stack_trace = traceback.format_exc()
            print(stack_trace)
            return Response(
                {
                    "error": f"An error occurred: {str(e)}",
                    "details": stack_trace  
                },
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
    
class FeedbackViewSet(viewsets.ModelViewSet):
    queryset = Feedback.objects.all()
    serializer_class = FeedbackSerializer

class UserViewSet(viewsets.ModelViewSet):
    queryset = Users.objects.all()
    serializer_class = UsersSerializer

class VideosViewSet(viewsets.ModelViewSet):
    queryset = MockVideos.objects.all()
    serializer_class = MockVideosSerializer