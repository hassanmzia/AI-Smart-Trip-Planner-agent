import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('itineraries', '0004_itinerary_origin_destination_fields'),
    ]

    operations = [
        migrations.CreateModel(
            name='TripFeedback',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('overall_rating', models.IntegerField(help_text='Overall trip satisfaction 1-5')),
                ('flight_rating', models.IntegerField(blank=True, null=True)),
                ('hotel_rating', models.IntegerField(blank=True, null=True)),
                ('activities_rating', models.IntegerField(blank=True, null=True)),
                ('food_rating', models.IntegerField(blank=True, null=True)),
                ('value_for_money_rating', models.IntegerField(blank=True, null=True)),
                ('loved_most', models.TextField(blank=True, help_text='What did you love most?')),
                ('would_change', models.TextField(blank=True, help_text='What would you change?')),
                ('additional_comments', models.TextField(blank=True)),
                ('would_visit_again', models.BooleanField(blank=True, null=True)),
                ('would_recommend', models.BooleanField(blank=True, null=True)),
                ('tags', models.JSONField(blank=True, default=list, help_text='Tags like: great_location, too_expensive, loved_culture, etc.')),
                ('sentiment', models.CharField(blank=True, choices=[('very_positive', 'Very Positive'), ('positive', 'Positive'), ('neutral', 'Neutral'), ('negative', 'Negative'), ('very_negative', 'Very Negative')], default='', max_length=20, help_text='Overall sentiment derived from NLP analysis')),
                ('sentiment_score', models.FloatField(blank=True, help_text='Sentiment polarity score (-1.0 to 1.0)', null=True)),
                ('emotions', models.JSONField(blank=True, default=dict, help_text='Detected emotions: {joy: 0.8, surprise: 0.3, ...}')),
                ('is_toxic', models.BooleanField(default=False)),
                ('toxicity_score', models.FloatField(blank=True, help_text='Toxicity score 0.0-1.0', null=True)),
                ('extracted_topics', models.JSONField(blank=True, default=list, help_text='Key topics extracted from comments: [beach, museum, food, ...]')),
                ('learned_preferences', models.JSONField(blank=True, default=dict, help_text='Preference signals: {hotel_priority: location, budget_sensitivity: 0.8}')),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('itinerary', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, related_name='feedback', to='itineraries.itinerary')),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='trip_feedbacks', to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'verbose_name': 'Trip Feedback',
                'verbose_name_plural': 'Trip Feedbacks',
                'db_table': 'trip_feedback',
                'ordering': ['-created_at'],
                'indexes': [
                    models.Index(fields=['user', '-created_at'], name='trip_feedba_user_id_idx'),
                    models.Index(fields=['sentiment'], name='trip_feedba_sentime_idx'),
                ],
            },
        ),
    ]
