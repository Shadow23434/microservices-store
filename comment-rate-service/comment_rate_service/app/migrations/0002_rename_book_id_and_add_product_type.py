# Generated manually to rename book_id to product_id and add product_type

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('app', '0001_initial'),
    ]

    operations = [
        migrations.RenameField(
            model_name='review',
            old_name='book_id',
            new_name='product_id',
        ),
        migrations.AddField(
            model_name='review',
            name='product_type',
            field=models.CharField(blank=True, default='book', max_length=50),
        ),
        migrations.AlterUniqueTogether(
            name='review',
            unique_together={('customer_id', 'product_id')},
        ),
    ]