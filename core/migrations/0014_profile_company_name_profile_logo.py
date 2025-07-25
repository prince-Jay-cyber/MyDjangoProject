# Generated by Django 5.2.3 on 2025-07-08 09:41

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0013_alter_application_message'),
    ]

    operations = [
        migrations.AddField(
            model_name='profile',
            name='company_name',
            field=models.CharField(blank=True, max_length=255),
        ),
        migrations.AddField(
            model_name='profile',
            name='logo',
            field=models.ImageField(blank=True, null=True, upload_to='company_logos/'),
        ),
    ]
