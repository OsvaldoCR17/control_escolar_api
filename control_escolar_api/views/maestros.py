import json
from django.db.models import *
from django.db import transaction
from django.shortcuts import get_object_or_404
from control_escolar_api.serializers import UserSerializer
from control_escolar_api.serializers import *
from control_escolar_api.models import *
from rest_framework import permissions
from rest_framework import generics
from rest_framework import status
from rest_framework.response import Response
from django.contrib.auth.models import Group

class MaestrosAll(generics.CreateAPIView):
    #Esta función es esencial para todo donde se requiera autorización de inicio de sesión (token)
    permission_classes = (permissions.IsAuthenticated,)
    # Invocamos la petición GET para obtener todos los maestros
    def get(self, request, *args, **kwargs):
        maestros = Maestros.objects.filter(user__is_active=1).order_by("id")
        lista = MaestroSerializer(maestros, many=True).data
        for maestro in lista:
            if isinstance(maestro, dict) and "materias_json" in maestro:
                try:
                    maestro["materias_json"] = json.loads(maestro["materias_json"])
                except Exception:
                    maestro["materias_json"] = []
        return Response(lista, 200)

class MaestroView(generics.CreateAPIView):
    #Permisos por método (sobreescribe el coportamiento default)
    # Verifica que el usuario esté autenticado para las peticiones GET, PUT y DELETE
    def get_permissions(self):
        if self.request.method in ['GET', 'PUT', 'DELETE']:
            self.permission_classes = [permissions.IsAuthenticated]
        return [] # POST no requiere autenticación
    
    # Obtner usuario por ID
    permission_classes = (permissions.IsAuthenticated,)
    def get(self, request, *args, **kwargs):
        maestro = get_object_or_404(Maestros, id=request.GET.get("id"))
        maestro_data = MaestroSerializer(maestro).data
        if "materias_json" in maestro_data:
            try:
                maestro_data["materias_json"] = json.loads(maestro_data["materias_json"])
            except Exception:
                maestro_data["materias_json"] = []
        return Response(maestro_data, 200)
    #Registrar nuevo usuario
    @transaction.atomic
    def post(self, request, *args, **kwargs):
        # Serializamos los datos del maestro para volverlo de nuevo JSON
        user = UserSerializer(data=request.data)
        
        if user.is_valid():
            # Grabar datos del maestro
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

            #Almacenar los datos adicionales del maestro
            maestro = Maestros.objects.create(user=user,
                                            id_trabajador= request.data["id_trabajador"],
                                            fecha_nacimiento= request.data["fecha_nacimiento"],
                                            telefono= request.data["telefono"],
                                            rfc= request.data["rfc"].upper(),
                                            cubiculo= request.data["cubiculo"],
                                            area_investigacion= request.data["area_investigacion"],
                                            materias_json= json.dumps(request.data["materias_json"]))
            maestro.save()

            return Response({"Maestro creado con el ID: ": maestro.id }, 201)

        return Response(user.errors, status=status.HTTP_400_BAD_REQUEST)
    
    # Actualizar datos del maestro
    @transaction.atomic
    def put(self, request, *args, **kwargs):
        permission_classes = (permissions.IsAuthenticated,)
        maestro = get_object_or_404(Maestros, id=request.data["id"])
        user = maestro.user

        # Actualizar datos de User
        user.first_name = request.data['first_name']
        user.last_name = request.data['last_name']
        user.email = request.data['email']
        user.username = request.data['email']
        user.save()

        # Actualizar datos de Maestro
        maestro.id_trabajador= request.data["id_trabajador"]
        maestro.fecha_nacimiento= request.data["fecha_nacimiento"]
        maestro.telefono= request.data["telefono"]
        maestro.rfc= request.data["rfc"].upper()
        maestro.cubiculo= request.data["cubiculo"]
        maestro.area_investigacion= request.data["area_investigacion"]
        maestro.materias_json= json.dumps(request.data["materias_json"])
        maestro.save()

        return Response({"Maestro actualizado con el ID: ": maestro.id }, 200)
    
    #Eliminar maestro con delete (Borrar realmente)
    @transaction.atomic
    def delete(self, request, *args, **kwargs):
        maestro = get_object_or_404(Maestros, id=request.GET.get("id"))
        try:
            maestro.user.delete()
            return Response({"details": "Maestro eliminado correctamente"}, 200)
        except Exception as e:
            return Response({"details": "Algo pasó al eliminar " + str(e)}, 400)
    
    