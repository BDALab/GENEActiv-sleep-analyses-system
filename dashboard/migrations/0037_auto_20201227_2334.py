# Generated by Django 3.1.1 on 2020-12-27 22:34

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ('dashboard', '0036_auto_20201227_2331'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='sleepnight',
            name='end',
        ),
        migrations.RemoveField(
            model_name='sleepnight',
            name='start',
        ),
        migrations.AlterField(
            model_name='sleepnight',
            name='sleep_end',
            field=models.DateTimeField(verbose_name='sleep end'),
        ),
        migrations.AlterField(
            model_name='sleepnight',
            name='sleep_onset',
            field=models.DateTimeField(verbose_name='sleep onset'),
        ),
    ]