# Generated by Django 2.0 on 2018-01-24 08:00

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('Photo', '0004_auto_20180124_1558'),
    ]

    operations = [
        migrations.AlterField(
            model_name='photo',
            name='photoFlikerId',
            field=models.CharField(max_length=20, null=True),
        ),
    ]
