from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('app', '0001_initial'),
    ]

    operations = [
        migrations.RenameField(
            model_name='orderitem',
            old_name='book_id',
            new_name='product_id',
        ),
        migrations.AddField(
            model_name='orderitem',
            name='product_name',
            field=models.CharField(default='', max_length=255),
        ),
        migrations.AddField(
            model_name='orderitem',
            name='product_type',
            field=models.CharField(default='book', max_length=50),
        ),
    ]