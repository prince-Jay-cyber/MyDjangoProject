# Generated by Django 5.2.3 on 2025-07-10 14:11

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0023_jobalert'),
    ]

    operations = [
        migrations.AlterField(
            model_name='jobalert',
            name='sent_at',
            field=models.DateTimeField(auto_now_add=True),
        ),
    ]
