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
import json

class MateriasAll(generics.CreateAPIView):
    #Esta función es esencial para todo donde se requiera autorización de inicio de sesión (token)
    permission_classes = (permissions.IsAuthenticated,)
    # Invocamos la petición GET para obtener todas las materias
    def get(self, request, *args, **kwargs):
        materias = Materias.objects.all().order_by("id")
        lista = MateriaSerializer(materias, many=True).data
        # Convertir dias_json de JSON-string a lista, igual que en maestros.py
        for materia in lista:
            if isinstance(materia, dict) and "dias_json" in materia:
                try:
                    materia["dias_json"] = json.loads(materia["dias_json"]) if materia["dias_json"] else []
                except Exception:
                    materia["dias_json"] = []

        return Response(lista, 200)

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
  
class MateriaView(generics.CreateAPIView):
    # Registrar nueva materia (solo administradores)
    permission_classes = (permissions.IsAuthenticated,)
    
    #Obtner materia por ID
    def get(self, request, *args, **kwargs):
        materia = get_object_or_404(Materias, id=request.GET.get("id"))
        materia_data = MateriaSerializer(materia).data
        # Convertir dias_json de JSON-string a lista
        if isinstance(materia_data, dict) and "dias_json" in materia_data:
            try:
                materia_data["dias_json"] = json.loads(materia_data["dias_json"]) if materia_data["dias_json"] else []
            except Exception:
                materia_data["dias_json"] = []
        return Response(materia_data, 200)
    
     #Registrar nueva materia

    @transaction.atomic
    def post(self, request, *args, **kwargs):
        # Comprobar permiso adicional: solo usuarios del grupo 'administrador'
        if not request.user.groups.filter(name='administrador').exists():
            return Response({'detail': 'Forbidden - only administrators can create materias'}, status=status.HTTP_403_FORBIDDEN)
        # Preparar datos (manejar dias_json si viene como lista)
        data = request.data.copy()
        try:
            if 'dias_json' in data and isinstance(data['dias_json'], list):
                data['dias_json'] = json.dumps(data['dias_json'])
        except Exception:
            pass

        # Serializamos los datos de la materia para validarlos
        materia_serializer = MateriaSerializer(data=data)

        if materia_serializer.is_valid():
            # Validar que el NRC no exista (similar a la validación de email en AdminView)
            nrc = data.get('nrc')
            if nrc:
                existing = Materias.objects.filter(nrc=nrc).first()
                if existing:
                    return Response({"message": "NRC "+nrc+", is already taken"}, 400)

            # Grabar datos de la materia
            materia = materia_serializer.save()
            materia_data = MateriaSerializer(materia).data
            # Devolver dias_json como lista (parsing JSON-string)
            if isinstance(materia_data, dict) and "dias_json" in materia_data:
                try:
                    materia_data["dias_json"] = json.loads(materia_data["dias_json"]) if materia_data["dias_json"] else []
                except Exception:
                    materia_data["dias_json"] = []

            return Response(materia_data, 201)

        return Response(materia_serializer.errors, 400)
    
    # Actualizar datos de la materia
    @transaction.atomic
    def put(self, request, *args, **kwargs):
        permission_classes = (permissions.IsAuthenticated,)
        materia = get_object_or_404(Materias, id=request.data["id"])
        maestro = get_object_or_404(Maestros, id=request.data["profesor_asignado"]) 
        materia.nrc = request.data["nrc"]
        materia.nombre_materia = request.data["nombre_materia"]
        materia.seccion = request.data["seccion"]
        materia.dias_json = json.dumps(request.data["dias_json"])
        materia.hora_inicio = request.data["hora_inicio"]
        materia.hora_fin = request.data["hora_fin"]
        materia.programa_educativo = request.data["programa_educativo"]
        materia.profesor_asignado = maestro
        materia.salon = request.data["salon"]
        materia.save()
        
        return Response({"Materia actualizada con el ID: ": materia.id }, 200)
    
    # Eliminar materia
    @transaction.atomic
    def delete(self, request, *args, **kwargs):
        materia = get_object_or_404(Materias, id=request.GET.get("id"))
        try:
            materia.delete()
            return Response({"Materia eliminada con el ID: ": materia.id }, 200)
        except Exception as e:
            return Response({"details": "Algo pasó al eliminar " +str(e)}, 400)