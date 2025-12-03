# Control Escolar API

API en Django/DRF para gestionar usuarios (administradores, alumnos, maestros) y materias. Incluye autenticación por token, panel de administración y endpoints CRUD básicos.

## Características
- Autenticación de API con tokens (DRF TokenAuth y Bearer).
- Gestión de perfiles: `Administradores`, `Alumnos`, `Maestros`.
- Gestión de `Materias` con relación a `Maestros` y días en JSON.
- Panel de administración de Django para todos los modelos.
- Endpoints de listado y detalle por rol.

## Requisitos
- Python 3.10+ (probado con 3.13)
- MariaDB/MySQL (config vía `my.cnf`)
- Entorno virtual de Python

## Instalación
1) Crear entorno virtual y activar
```powershell
python -m venv env\control_escolar_api
env\control_escolar_api\Scripts\Activate.ps1
python -m pip install --upgrade pip
```

2) Instalar dependencias
```powershell
pip install -r requirements.txt
```

3) Configurar VS Code (opcional, ya incluido)
- `.vscode/settings.json` apunta al intérprete del venv y añade `python.analysis.extraPaths`.

## Configuración
- Base de datos: archivo `my.cnf` leído por Django en `DATABASES['default']['OPTIONS']['read_default_file']`.
- CORS: `CORS_ALLOWED_ORIGINS` ajustado en `settings.py`.
- DRF: `REST_FRAMEWORK` con `SessionAuthentication`, `BearerTokenAuthentication` y filtros.
- Tokens: `rest_framework.authtoken` incluido en `INSTALLED_APPS`.

## Migraciones
```powershell
python manage.py makemigrations
python manage.py migrate
```

## Usuarios y autenticación
### Crear token de usuario
Puedes usar el endpoint de login o crear tokens vía administración/gestión propia. El login devuelve:
- Admin: datos básicos + `token` + `roles`.
- Alumno: datos básicos + `token` + `rol` + perfil `alumno` (cuando está habilitado).

### Login API
```http
POST /login/
{
	"username": "usuario",
	"password": "clave"
}
```
Respuesta (ejemplo admin):
```json
{
	"id": 1,
	"first_name": "Ana",
	"last_name": "García",
	"email": "ana@example.com",
	"token": "<TOKEN>",
	"roles": ["administrador"]
}
```
Usa el token en peticiones posteriores:
```http
Authorization: Bearer <TOKEN>
```

## Endpoints
Las rutas están definidas en `control_escolar_api/urls.py`.

### Administradores
- `POST /admin/` Registrar administrador
- `GET /lista-admins/` Listar administradores
- `PUT /admin/` Actualizar administrador (requiere `id` en body)
- `DELETE /admin/?id=<ID>` Eliminar administrador

Body de registro (ejemplo):
```json
{
	"rol": "administrador",
	"first_name": "Ana",
	"last_name": "García",
	"email": "ana@example.com",
	"password": "Secreta123",
	"clave_admin": "ADM-001",
	"telefono": "555-123-4567",
	"rfc": "XAXX010101000",
	"edad": 33,
	"ocupacion": "Directora"
}
```

### Alumnos
- `POST /alumnos/` Registrar alumno
- `GET /lista-alumnos/` Listar alumnos
- `GET /alumnos/?id=<ID>` Obtener alumno por id
- `PUT /alumnos/` Actualizar alumno (requiere `id`)
- `DELETE /alumnos/?id=<ID>` Eliminar alumno

Campos relevantes del modelo `Alumnos`:
- `fecha_nacimiento` es `DateField` y acepta `YYYY-MM-DD`.

### Maestros
- `POST /maestros/` Registrar maestro
- `GET /lista-maestros/` Listar maestros
- `GET /maestros/?id=<ID>` Obtener maestro por id
- `PUT /maestros/` Actualizar maestro (requiere `id`)
- `DELETE /maestros/?id=<ID>` Eliminar maestro

Notas:
- `materias_json` se guarda como JSON-string y se devuelve parseado a lista en los endpoints.

### Materias
- `POST /materias/` Crear materia (solo administradores)
- `GET /lista-materias/` Listar materias
- `GET /materias/?id=<ID>` Obtener materia por id
- `PUT /materias/` Actualizar materia (requiere `id`)
- `DELETE /materias/?id=<ID>` Eliminar materia

Body de creación (ejemplo):
```json
{
	"nrc": "123123",
	"nombre_materia": "Sistemas Operativos II",
	"seccion": "123",
	"dias_json": ["Lunes","Martes","Jueves"],
	"hora_inicio": "07:00:00",
	"hora_fin": "09:00:00",
	"profesor_asignado": 2,
	"programa_educativo": "Licenciatura en Ciencias de la Computación",
	"salon": "CCO4014",
	"creditos": 5
}
```
Notas:
- `dias_json` se acepta como lista y se almacena como JSON-string, devolviéndose parseada como lista.
- `profesor_asignado` es id de `Maestros` (FK). En PUT/POST puedes enviar el entero; internamente se valida y asigna la instancia.

## Panel de Administración
- Ruta: `GET /admin/` (Django Admin)
- Modelos registrados: `Administradores`, `Alumnos`, `Maestros`, `Materias`.
- Búsqueda (`search_fields`) en `Materias` por: `nrc`, `nombre_materia`, `seccion`, `programa_educativo`, `salon`, y campos del profesor (`first_name`, `last_name`, `email`).

## Errores comunes y soluciones
- 405 Method Not Allowed en `GET /materias/`: esa ruta solo acepta `POST` y `PUT` si no se implementa `get()`. Usa `GET /materias/?id=<ID>` o `GET /lista-materias/` según tu vista.
- 500 al asignar `profesor_asignado`: asigna por instancia (`Maestros`) o usa el sufijo `_id` (p. ej. `profesor_asignado_id = 2`).
- CSRF 403 en `/admin/`: el admin requiere cookie/encabezado CSRF. Para API, usa token en `Authorization`.

## Desarrollo local
1) Iniciar servidor
```powershell
python manage.py runserver
```
2) Probar login
```http
POST http://127.0.0.1:8000/login/
```
3) Probar endpoints con token
```http
Authorization: Bearer <TOKEN>
```

## Estructura del proyecto
- `control_escolar_api/models.py`: Modelos (perfiles y materias)
- `control_escolar_api/serializers.py`: Serializadores DRF
- `control_escolar_api/views/`: Vistas por dominio (`users.py`, `alumnos.py`, `maestros.py`, `materias.py`, `auth.py`)
- `control_escolar_api/urls.py`: Rutas
- `static/`: Archivos estáticos (Django Admin y DRF UI)

## Estándares de datos
- Fechas (`DateField`): `YYYY-MM-DD`
- Horas (`TimeField`): `HH:MM:SS`
- JSON listas: `dias_json` y `materias_json` se manejan como arrays en la API y se almacenan como JSON-string.

## Consejos de producción
- Activa MariaDB Strict Mode (ver warning `mysql.W002`).
- Protege `SECRET_KEY` con variables de entorno.
- Configura `ALLOWED_HOSTS` y CORS para tu dominio.
- Considera `JSONField` para `dias_json` y `IntegerField` para `creditos` (requiere migraciones).

## Licencia
Proyecto interno/privado. No incluye encabezados de licencia.
