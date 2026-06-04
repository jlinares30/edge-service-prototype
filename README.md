# Edge Service Prototype

Servicio edge para integración IoT — estructura mínima y guía de inicio rápido.

## Requisitos
- Python 3.10+ (preferible)
- Git
- Opcional: Docker

## Instalación y ejecución local

1. Crear y activar un entorno virtual:

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
```

2. Instalar dependencias:

```powershell
pip install -r requirements.txt
```

3. Configurar variables de entorno

 - Crea un archivo `.env` en la raíz si usas `python-dotenv`, o exporta variables en tu entorno.

4. Ejecutar la aplicación:

```powershell
python app.py
```

## Estructura principal

- `app.py`: punto de entrada principal del servicio ([app.py](app.py)).
- `requirements.txt`: dependencias del proyecto ([requirements.txt](requirements.txt)).
- `shared/infrastructure/database.py`: inicialización de conexión a datos ([shared/infrastructure/database.py](shared/infrastructure/database.py)).
- Módulos principales: `iam/`, `monitoring/` y `shared/` (contienen capas `application`, `domain`, `infrastructure`, `interfaces`).

## Desarrollo

- Formato y linting: aplica tu formateador y linter preferido (Black, pylint, flake8).
- Ejecuta cambios desde la raíz del repo y prueba endpoints/locales según el diseño del servicio.

## Docker (opcional)

Si quieres dockerizar el servicio crea un `Dockerfile` y un `docker-compose.yml` con las variables necesarias. Ignora el fichero `docker-compose.override.yml` local si lo usas.
