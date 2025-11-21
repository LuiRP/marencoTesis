from django.db import models
from django.contrib.auth import get_user_model

CustomUser = get_user_model()


# Create your models here.
class Tutorship(models.Model):
    COURSE_CHOICES = [
        ("calculo_i", "Cálculo I"),
        ("logica", "Lógica"),
        ("calculo_ii", "Cálculo II"),
        ("introduccion_a_la_informatica", "Introducción a la Informática"),
        ("estadistica_descriptiva", "Estadística Descriptiva"),
        ("ingles_instrumental", "Inglés Instrumental"),
        ("calculo_iii", "Cálculo III"),
        ("fisica", "Física"),
        ("algoritmos_y_programacion_i", "Algoritmos y Programación I"),
        ("algebra", "Álgebra"),
        ("inferencia_y_probabilidades", "Inferencia y Probabilidades"),
        ("calculo_iv", "Cálculo IV"),
        ("estructuras_discretas", "Estructuras Discretas"),
        ("algoritmos_y_programacion_ii", "Algoritmos y Programación II"),
        ("electronica", "Electrónica"),
        ("bases_de_datos_i", "Bases de Datos I"),
        ("algoritmos_y_programacion_iii", "Algoritmos y Programación III"),
        ("bases_de_datos_ii", "Bases de Datos II"),
        ("metodos_numericos", "Métodos Numéricos"),
        (
            "principios_de_ingenieria_del_software",
            "Principios de Ingeniería del Software",
        ),
        ("arquitecturas_software", "Arquitecturas Software"),
        (
            "metodologias_de_desarrollo_de_software",
            "Metodologías de Desarrollo de Software",
        ),
        ("redes_y_comunicaciones_i", "Redes y Comunicaciones I"),
        ("desarrollo_de_aplicaciones_i", "Desarrollo de Aplicaciones I"),
        ("redes_y_comunicaciones_ii", "Redes y Comunicaciones II"),
        ("desarrollo_de_aplicaciones_ii", "Desarrollo de Aplicaciones II"),
    ]
    name = models.CharField("Nombre de la tutoria", choices=COURSE_CHOICES)
    tutor = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    description = models.TextField("Descripcion de la tutoria")
    created_at = models.DateTimeField(auto_now_add=True)


class TimePeriod(models.Model):
    WEEK_DAYS = [
        ("lunes", "Lunes"),
        ("martes", "Martes"),
        ("miercoles", "Miercoles"),
        ("jueves", "Jueves"),
        ("viernes", "Viernes"),
        ("sabado", "Sabado"),
        ("domingo", "Domingo"),
    ]
    tutor = models.ForeignKey(
        CustomUser, on_delete=models.CASCADE, related_name="tutor"
    )
    student = models.ForeignKey(
        CustomUser,
        on_delete=models.CASCADE,
        blank=True,
        null=True,
        related_name="student",
    )
    week_day = models.CharField("Dia de la semana", choices=WEEK_DAYS)
    start_time = models.TimeField()
    end_time = models.TimeField(null=True, blank=True)
