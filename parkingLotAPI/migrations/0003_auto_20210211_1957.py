# Generated by Django 3.1.6 on 2021-02-11 19:57

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('parkingLotAPI', '0002_auto_20210210_1240'),
    ]

    operations = [
        migrations.AlterField(
            model_name='slot',
            name='carNo',
            field=models.CharField(db_index=True, max_length=24, null=True),
        ),
    ]