from django.urls import path, include
from MockInterviews.views import RegisterUserView, ProtectedView, UploadVideoView, AnalyzeVideoView, FeedbackViewSet, UserViewSet, VideosViewSet, get_user_details
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView
from rest_framework.routers import DefaultRouter
from MockInterviews import views

feedback_list = FeedbackViewSet.as_view({
    'get':'list',
    'post':'create'
})

feedback_detail = FeedbackViewSet.as_view({
    'get':'retrieve',
    'put':'update',
    'patch':'partial_update',
    'delete':'destroy'
})

users_list = UserViewSet.as_view({
    'get':'list',
    'post':'create'
})

users_detail = UserViewSet.as_view({
    'get':'retrieve',
    'put':'update',
    'patch':'partial_update',
    'delete':'destroy'
})

video_list = VideosViewSet.as_view({
    'get':'list',
    'post':'create'
})

video_detail = VideosViewSet.as_view({
    'get':'retrieve',
    'put':'update',
    'patch':'partial_update',
    'delete':'destroy'
})

router = DefaultRouter()
router.register(r'feedback', views.FeedbackViewSet, basename='feedback')
router.register(r'users', views.UserViewSet, basename='users')
router.register(r'videos', views.VideosViewSet, basename='videos')

urlpatterns = [
    path('', include(router.urls)),
    path('register/', RegisterUserView.as_view(), name='register'),
    path('login/', TokenObtainPairView.as_view(), name='token_obtain_pair'),  # Login endpoint
    path('token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),  # Refresh token endpoint
    path('protected/', ProtectedView.as_view(), name='protected'),
    path('upload_video/', UploadVideoView.as_view(), name='upload_video'),
    path('analyze/<int:video_id>/',AnalyzeVideoView.as_view(), name="analyze_video"),
    path('user-details/', get_user_details, name='user_details'),
]