# Generated by Django 5.1.3 on 2024-12-04 00:35

import django.core.validators
import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):
    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name="Cliente",
            fields=[
                ("id", models.AutoField(primary_key=True, serialize=False)),
                (
                    "rut",
                    models.CharField(
                        max_length=10,
                        unique=True,
                        validators=[
                            django.core.validators.RegexValidator(
                                message="RUT inválido", regex="^\\d{7,8}-[0-9kK]$"
                            )
                        ],
                        verbose_name="RUT",
                    ),
                ),
                (
                    "nombres",
                    models.CharField(
                        max_length=12,
                        validators=[
                            django.core.validators.RegexValidator(
                                message="solo puede contener letras",
                                regex="^[a-zA-ZáéíóúÁÉÍÓÚñÑ\\s]+$",
                            )
                        ],
                    ),
                ),
                (
                    "apellidos",
                    models.CharField(
                        max_length=15,
                        validators=[
                            django.core.validators.RegexValidator(
                                message="solo puede contener letras",
                                regex="^[a-zA-ZáéíóúÁÉÍÓÚñÑ\\s]+$",
                            )
                        ],
                    ),
                ),
                (
                    "telefono",
                    models.CharField(
                        max_length=9,
                        validators=[
                            django.core.validators.RegexValidator(
                                message="Teléfono inválido", regex="^\\+?\\d{7,15}$"
                            )
                        ],
                    ),
                ),
                ("email", models.EmailField(max_length=40)),
                (
                    "direccion",
                    models.CharField(
                        max_length=200,
                        validators=[
                            django.core.validators.RegexValidator(
                                message="solo puede contener letras, números y los caracteres . , -",
                                regex="^[a-zA-Z0-9áéíóúÁÉÍÓÚñÑ\\s.,-]+$",
                            )
                        ],
                    ),
                ),
                (
                    "comuna",
                    models.CharField(
                        max_length=20,
                        validators=[
                            django.core.validators.RegexValidator(
                                message="La comuna solo puede contener letras",
                                regex="^[a-zA-ZáéíóúÁÉÍÓÚñÑ\\s]+$",
                            )
                        ],
                    ),
                ),
            ],
        ),
        migrations.CreateModel(
            name="Reparacion",
            fields=[
                ("id", models.AutoField(primary_key=True, serialize=False)),
                ("nombre", models.CharField(max_length=100)),
                ("precio", models.DecimalField(decimal_places=2, max_digits=10)),
                ("descripcion", models.TextField()),
            ],
        ),
        migrations.CreateModel(
            name="Vehiculo",
            fields=[
                ("id", models.AutoField(primary_key=True, serialize=False)),
                (
                    "patente",
                    models.CharField(
                        max_length=10,
                        unique=True,
                        validators=[
                            django.core.validators.RegexValidator(
                                message="solo puede contener letras mayúsculas y números",
                                regex="^[A-Z0-9]+$",
                            )
                        ],
                    ),
                ),
                (
                    "modelo",
                    models.CharField(
                        max_length=20,
                        validators=[
                            django.core.validators.RegexValidator(
                                message="El modelo solo puede contener letras y números",
                                regex="^[a-zA-Z0-9\\s]+$",
                            )
                        ],
                    ),
                ),
                (
                    "marca",
                    models.CharField(
                        max_length=20,
                        validators=[
                            django.core.validators.RegexValidator(
                                message="La marca solo puede contener letras",
                                regex="^[a-zA-Z\\s]+$",
                            )
                        ],
                    ),
                ),
                (
                    "año",
                    models.IntegerField(
                        validators=[
                            django.core.validators.MinValueValidator(
                                1900, message="El año debe ser mayor o igual a 1900"
                            ),
                            django.core.validators.MaxValueValidator(
                                2024, message="El año no puede ser mayor al actual"
                            ),
                        ]
                    ),
                ),
                (
                    "cliente",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="vehiculos",
                        to="secretaria.cliente",
                    ),
                ),
            ],
        ),
        migrations.CreateModel(
            name="OrdenTrabajo",
            fields=[
                ("id", models.AutoField(primary_key=True, serialize=False)),
                ("fecha_inicio", models.DateField()),
                ("fecha_entrega", models.DateField(blank=True, null=True)),
                ("estado", models.CharField(max_length=50)),
                ("observacion", models.TextField()),
                (
                    "cliente",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        to="secretaria.cliente",
                    ),
                ),
                (
                    "usuario",
                    models.ForeignKey(
                        blank=True,
                        null=True,
                        on_delete=django.db.models.deletion.SET_NULL,
                        to=settings.AUTH_USER_MODEL,
                    ),
                ),
                (
                    "reparacion",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        to="secretaria.reparacion",
                    ),
                ),
                (
                    "vehiculo",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        to="secretaria.vehiculo",
                    ),
                ),
            ],
        ),
    ]
