# Generated manually to add applicable_types field

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('app', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='category',
            name='applicable_types',
            field=models.CharField(blank=True, default='', max_length=255, help_text='CSV of product types: book,laptop,mobile,cloth or empty for all'),
        ),
    ]