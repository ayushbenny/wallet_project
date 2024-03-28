# Generated by Django 5.0.3 on 2024-03-26 18:16

import uuid
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('wallet_manager', '0002_wallet'),
    ]

    operations = [
        migrations.AddField(
            model_name='wallet',
            name='wallet_id',
            field=models.UUIDField(default=uuid.uuid4, editable=False, unique=True),
        ),
    ]
