from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('itineraries', '0003_merge_0002_narrative_and_statuses'),
    ]

    operations = [
        migrations.AddField(
            model_name='itinerary',
            name='origin_city',
            field=models.CharField(blank=True, default='', max_length=200),
        ),
        migrations.AddField(
            model_name='itinerary',
            name='origin_country',
            field=models.CharField(blank=True, default='', max_length=100),
        ),
        migrations.AddField(
            model_name='itinerary',
            name='destination_city',
            field=models.CharField(blank=True, default='', max_length=200),
        ),
        migrations.AddField(
            model_name='itinerary',
            name='destination_country',
            field=models.CharField(blank=True, default='', max_length=100),
        ),
    ]
