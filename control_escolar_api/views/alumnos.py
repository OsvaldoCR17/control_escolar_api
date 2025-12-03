from django.db.models import *
from django.db import transaction
from control_escolar_api.serializers import UserSerializer
from control_escolar_api.serializers import *
from control_escolar_api.models import *
from rest_framework import permissions
from rest_framework import generics
from rest_framework import status
from rest_framework.response import Response
from django.contrib.auth.models import Group
from django.shortcuts import get_object_or_404

class AlumnosAll(generics.CreateAPIView):
    #Esta función es esencial para todo donde se requiera autorización de inicio de sesión (token)
    permission_classes = (permissions.IsAuthenticated,)
    # Invocamos la petición GET para obtener todos los administradores
    def get(self, request, *args, **kwargs):
        admin = Alumnos.objects.filter(user__is_active = 1).order_by("id")
        lista = AlumnoSerializer(admin, many=True).data
        return Response(lista, 200)

class AlumnoView(generics.CreateAPIView):
    # Permisos por método (sobreescribe el coportamiento default)
    # Verifica que el usuario esté autenticado para las peticiones GET, PUT y DELETE
    def get_permissions(self):
        if self.request.method in ['GET', 'PUT', 'DELETE']:
            self.permission_classes = [permissions.IsAuthenticated]
        return [] # POST no requiere autenticación
    
    #Obtner usuario por ID
    permission_classes = (permissions.IsAuthenticated,)
    def get(self, request, *args, **kwargs):
        alumno = get_object_or_404(Alumnos, id = request.GET.get("id"))
        alumno = AlumnoSerializer(alumno).data
        return Response(alumno, 200)
    #Registrar nuevo usuario
    @transaction.atomic
    def post(self, request, *args, **kwargs):
        # Serializamos los datos del alumno para volverlo de nuevo JSON
        user = UserSerializer(data=request.data)
        
        if user.is_valid():
            #Grabar datos del alumno
            role = request.data['rol']
            first_name = request.data['first_name']
            last_name = request.data['last_name']
            email = request.data['email']
            password = request.data['password']
            #Valida si existe el usuario o bien el email registrado
            existing_user = User.objects.filter(email=email).first()

            if existing_user:
                return Response({"message":"Username "+email+", is already taken"},400)

            user = User.objects.create( username = email,
                                        email = email,
                                        first_name = first_name,
                                        last_name = last_name,
                                        is_active = 1)


            user.save()
            user.set_password(password)
            user.save()

            group, created = Group.objects.get_or_create(name=role)
            group.user_set.add(user)
            group.save()

            #Almacenar los datos adicionales del alumno
            alumno = Alumnos.objects.create(user=user,
                                            matricula= request.data["matricula"],
                                            curp= request.data["curp"].upper(),
                                            rfc= request.data["rfc"].upper(),
                                            fecha_nacimiento= request.data["fecha_nacimiento"],
                                            edad= request.data["edad"],
                                            telefono= request.data["telefono"],
                                            ocupacion= request.data["ocupacion"])
            alumno.save()

            return Response({"Alumno creado con el ID: ": alumno.id }, 201)

        return Response(user.errors, status=status.HTTP_400_BAD_REQUEST)
    
        #Actualizar datos del alumno
    @transaction.atomic
    def put(self, request, *args, **kwargs):
        alumno = get_object_or_404(Alumnos, id=request.data["id"])
        user = alumno.user

        #Actualizar datos de User
        user.first_name = request.data['first_name']
        user.last_name = request.data['last_name']
        user.email = request.data['email']
        user.username = request.data['email']
        if 'password' in request.data and request.data['password']:
            user.set_password(request.data['password'])
        user.save()

        #Actualizar datos de Alumno
        alumno.matricula= request.data["matricula"]
        alumno.curp= request.data["curp"].upper()
        alumno.rfc= request.data["rfc"].upper()
        alumno.fecha_nacimiento= request.data["fecha_nacimiento"]
        alumno.edad= request.data["edad"]
        alumno.telefono= request.data["telefono"]
        alumno.ocupacion= request.data["ocupacion"]
        alumno.save()

        return Response({"Alumno actualizado con el ID: ": alumno.id }, 200)
    
        #Eliminar alumno con delete (Borrar realmente)
    @transaction.atomic
    def delete(self, request, *args, **kwargs):
        alumno = get_object_or_404(Alumnos, id=request.GET.get("id"))
        try:
            alumno.user.delete()
            return Response({"details": "Alumno eliminado correctamente"}, 200)
        except Exception as e:
            return Response({"details": "Algo pasó al eliminar " + str(e)}, 400)