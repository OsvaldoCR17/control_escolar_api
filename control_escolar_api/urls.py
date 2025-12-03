from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from .views.bootstrap import VersionView
from control_escolar_api.views import users
from control_escolar_api.views import auth
from control_escolar_api.views import bootstrap
from control_escolar_api.views import alumnos
from control_escolar_api.views import maestros
from control_escolar_api.views import materias

urlpatterns = [
    #Crear Admin
        path('admin/', users.AdminView.as_view()),
    #Admin Data
        path('lista-admins/', users.AdminAll.as_view()),
    #Edit Admin
        #path('admins-edit/', users.AdminsViewEdit.as_view())
    
    #Crear Alumnos
        path('alumnos/', alumnos.AlumnoView.as_view()),
    #Alumno Data
        path('lista-alumnos/', alumnos.AlumnosAll.as_view()),
    #Edit Alumno
        #path('alumnos-edit/', alumnos.AlumnoViewEdit.as_view())

    #Crear Maestros
        path('maestros/', maestros.MaestroView.as_view()),
    #Maestro Data
        path('lista-maestros/', maestros.MaestrosAll.as_view()),
    #Edit Maestro
        #path('maestros-edit/', maestros.MaestroViewEdit.as_view())
        
    #Crear Materias
        path('materias/', materias.MateriaView.as_view()),
    #Materias Data
        path('lista-materias/', materias.MateriasAll.as_view()),
        
    #Total users
        path('total-usuarios/', users.TotalUsers.as_view()),
        
    #Login
        path('login/', auth.CustomAuthToken.as_view()),
    #Logout
        path('logout/', auth.Logout.as_view()),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)