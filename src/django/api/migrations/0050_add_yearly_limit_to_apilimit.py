# Generated by Django 2.2.11 on 2021-01-05 18:54

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0049_add_contributornotifications'),
    ]

    operations = [
        migrations.AddField(
            model_name='apilimit',
            name='yearly_limit',
            field=models.PositiveIntegerField(blank=True, help_text='The number of requests a contributor can make per year.', null=True),
        ),
        migrations.AddField(
            model_name='historicalapilimit',
            name='yearly_limit',
            field=models.PositiveIntegerField(blank=True, help_text='The number of requests a contributor can make per year.', null=True),
        ),
    ]
