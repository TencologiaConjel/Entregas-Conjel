# Generated by Django 5.1.7 on 2025-05-28 16:49

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0004_diacontabil_updated_at'),
    ]

    operations = [
        migrations.AlterField(
            model_name='operacao',
            name='tipo',
            field=models.CharField(choices=[('coleta', 'Coleta'), ('entrega', 'Entrega'), ('coleta e retirada', 'Coleta e Retirada')], max_length=20),
        ),
    ]
