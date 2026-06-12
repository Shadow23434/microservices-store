from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('app', '0001_initial'),
    ]

    operations = [
        # Rename field and add new fields on Recommendation
        migrations.RenameField(
            model_name='recommendation',
            old_name='recommended_book_ids',
            new_name='recommended_product_ids',
        ),
        migrations.AddField(
            model_name='recommendation',
            name='algorithm',
            field=models.CharField(default='multi_signal', max_length=50),
        ),
        migrations.AddField(
            model_name='recommendation',
            name='reason',
            field=models.CharField(blank=True, max_length=255),
        ),
        # Create WishlistItem model
        migrations.CreateModel(
            name='WishlistItem',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('customer_id', models.IntegerField(db_index=True)),
                ('product_id', models.IntegerField()),
                ('added_at', models.DateTimeField(auto_now_add=True)),
            ],
            options={
                'ordering': ['-added_at'],
                'unique_together': {('customer_id', 'product_id')},
            },
        ),
        # Create Conversation model
        migrations.CreateModel(
            name='Conversation',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('customer_id', models.IntegerField(db_index=True)),
                ('session_id', models.CharField(blank=True, max_length=64)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
            ],
        ),
        # Create ChatMessage model
        migrations.CreateModel(
            name='ChatMessage',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('role', models.CharField(choices=[('user', 'User'), ('assistant', 'Assistant')], max_length=10)),
                ('content', models.TextField()),
                ('product_ids', models.TextField(blank=True)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('conversation', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='messages', to='app.conversation')),
            ],
            options={
                'ordering': ['created_at'],
            },
        ),
    ]
