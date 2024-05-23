# Generated by Django 5.0.4 on 2024-05-20 18:01

import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('plataforma', '0002_pessoa_status'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='Analise',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('data', models.DateTimeField(auto_now_add=True)),
                ('decisao', models.CharField(choices=[('A', 'Aprovado'), ('R', 'Reprovado')], max_length=1)),
                ('mensagem', models.TextField(blank=True, null=True)),
                ('analisador', models.ForeignKey(on_delete=django.db.models.deletion.DO_NOTHING, to=settings.AUTH_USER_MODEL, verbose_name='analisado por')),
                ('pessoa', models.ForeignKey(on_delete=django.db.models.deletion.DO_NOTHING, to='plataforma.pessoa')),
            ],
        ),
    ]
