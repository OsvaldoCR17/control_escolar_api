from django.contrib import admin
from django.utils.html import format_html
from control_escolar_api.models import *

@admin.register(Administradores)
class ProfilesAdmin(admin.ModelAdmin):
    list_display = ("id", "user", "creation", "update")
    search_fields = ("user__username", "user__email", "user__first_name", "user__last_name")

@admin.register(Alumnos)
class AlumnosAdmin(admin.ModelAdmin):
    list_display = ("id", "user", "creation", "update")
    search_fields = ("user__username", "user__email", "user__first_name", "user__last_name")

@admin.register(Maestros)
class MaestrosAdmin(admin.ModelAdmin):
    list_display = ("id", "user", "creation", "update")
    search_fields = ("user__username", "user__email", "user__first_name", "user__last_name")
    
@admin.register(Materias)
class MateriasAdmin(admin.ModelAdmin):
    list_display = ("id", "nrc", "creation", "update")
    search_fields = ("nrc", "nombre_materia", "seccion", "profesor_asignado__user__first_name", "profesor_asignado__user__last_name")
