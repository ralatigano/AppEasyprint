# Generated by Django 5.0.6 on 2024-10-09 23:43

import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('presupuestos', '0001_initial'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='Categoria',
            fields=[
                ('id', models.AutoField(primary_key=True, serialize=False)),
                ('nombre', models.CharField(blank=True, default=None, max_length=50)),
                ('created', models.DateTimeField(auto_now_add=True)),
                ('updated', models.DateTimeField(auto_now_add=True)),
            ],
        ),
        migrations.CreateModel(
            name='Producto',
            fields=[
                ('codigo', models.IntegerField(primary_key=True, serialize=False)),
                ('nombre', models.CharField(max_length=50)),
                ('precio', models.DecimalField(blank=True, decimal_places=2, default=0, max_digits=10, null=True)),
                ('factor', models.FloatField(blank=True, default=1, null=True)),
                ('ancho', models.FloatField(blank=True, default=0, null=True)),
                ('alto', models.FloatField(blank=True, default=0, null=True)),
                ('created', models.DateTimeField(auto_now_add=True)),
                ('updated', models.DateTimeField(auto_now_add=True)),
                ('cliente', models.CharField(blank=True, default=None, max_length=200, null=True)),
                ('info_adic', models.CharField(blank=True, default=None, max_length=200, null=True)),
                ('cantidad', models.FloatField(blank=True, default=None, null=True)),
                ('cant_area', models.FloatField(blank=True, default=1, null=True)),
                ('desc_plata', models.DecimalField(blank=True, decimal_places=2, default=0, max_digits=10, null=True)),
                ('desc_porcentaje', models.IntegerField(blank=True, default=0, null=True)),
                ('resultado', models.DecimalField(blank=True, decimal_places=2, default=0, max_digits=10, null=True)),
                ('empaquetado', models.BooleanField(default=False)),
                ('t_produccion', models.FloatField(blank=True, default=0, null=True)),
                ('categoria', models.ForeignKey(blank=True, default=None, null=True, on_delete=django.db.models.deletion.SET_NULL, to='productos.categoria')),
                ('presupuesto', models.ForeignKey(blank=True, default=None, null=True, on_delete=django.db.models.deletion.CASCADE, to='presupuestos.presupuesto')),
                ('vendedor', models.ForeignKey(blank=True, default=None, null=True, on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
        ),
    ]
