# Generated by Django 3.0.3 on 2020-03-20 16:59

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('certstreams', '0003_auto_20200320_1630'),
    ]

    operations = [
        migrations.AlterField(
            model_name='domain',
            name='score',
            field=models.IntegerField(null=True),
        ),
    ]
