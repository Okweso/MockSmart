# Generated by Django 5.1.3 on 2024-11-29 09:47

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('MockInterviews', '0004_feedback_avd_sentence_length_feedback_eye_contact_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='feedback',
            name='recommendations',
            field=models.TextField(blank=True, null=True),
        ),
    ]
