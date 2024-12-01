from rest_framework import serializers
from MockInterviews.models import Users, MockVideos, Feedback
import json


class UsersSerializer(serializers.ModelSerializer):
    class Meta:
        model = Users
        fields = '__all__'
        extra_kwargs = {
            'password': {'write_only': True}
        }
        def create(self, validated_data):
        # Create user with hashed password
            user = Users.objects.create_user(
                email=validated_data['email'],
                password=validated_data['password'],
                first_name=validated_data.get('first_name', ''),
                last_name=validated_data.get('last_name', ''),
            )
            return user

class MockVideosSerializer(serializers.ModelSerializer):
    class Meta:
        model = MockVideos
        fields = '__all__'

class FeedbackSerializer(serializers.ModelSerializer):
    class Meta:
        model = Feedback
        fields = '__all__'

        def get_feedback(self, obj):
            return json.loads(obj.feedback) if obj.feedback else None