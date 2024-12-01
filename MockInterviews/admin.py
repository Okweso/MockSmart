from django.contrib import admin
from .models import Users, MockVideos, Feedback

# Register your models here.
class UsersAdmin(admin.ModelAdmin):
    pass
admin.site.register(Users, UsersAdmin)

class MockVideosAdmin(admin.ModelAdmin):
    pass
admin.site.register(MockVideos, MockVideosAdmin)

class FeedbackAdmin(admin.ModelAdmin):
    pass
admin.site.register(Feedback, FeedbackAdmin)