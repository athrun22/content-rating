# Generated by Django 2.0.3 on 2018-03-28 01:30

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('capstoneproject', '0002_remove_category_parent_set'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='wordcategory',
            name='strong',
        ),
        migrations.AddField(
            model_name='wordcategory',
            name='strength',
            field=models.BooleanField(choices=[(True, 'strong'), (False, 'weak')], default=False),
        ),
    ]
