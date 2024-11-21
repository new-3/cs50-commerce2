# Generated by Django 4.2.16 on 2024-11-21 01:09

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('auctions', '0005_ADD_STR_METHODS_MODELS'),
    ]

    operations = [
        migrations.AlterField(
            model_name='category',
            name='name',
            field=models.CharField(max_length=15),
        ),
        migrations.AlterField(
            model_name='listing',
            name='category',
            field=models.CharField(blank=True, choices=[('PNT', 'Paintings'), ('TOY', 'Toys')], help_text='Select the category of your item(optional).', max_length=3),
        ),
    ]
