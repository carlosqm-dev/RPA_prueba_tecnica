# Bot RPA - Verificación de Sanciones OFAC

Bot de automatización robótica de procesos (RPA) desarrollado en Python que consulta personas almacenadas en una base de datos PostgreSQL y verifica si se encuentran en la lista de sanciones de la OFAC (Office of Foreign Assets Control) del Departamento del Tesoro de Estados Unidos. El proceso incluye la captura de evidencias, almacenamiento de resultados y generación de reportes.

---

## Requisitos Previos

Antes de ejecutar el proyecto, asegúrese de tener instalado:

- **Python 3.8** o superior
- **Google Chrome** (última versión estable)
- **Git** (opcional, para clonar el repositorio)

---

## Estructura del Proyecto

```
prueba_tecnica/
├── src/
│   ├── main.py                        # Punto de entrada
│   ├── config/                        # Configuración y constantes
│   ├── base_datos/                    # Conexión y repositorios PostgreSQL
│   ├── scraping/                      # Navegador y buscador OFAC
│   ├── servicios/                     # Lógica de negocio
│   └── utilidades/                    # Logger y capturas de pantalla
├── tests/                             # Pruebas del proyecto
├── capturas/                          # Screenshots generados
├── reportes/                          # Reportes Excel exportados
├── logs/                              # Archivos de log y resúmenes
├── .env                               # Variables de entorno (no versionado)
├── .env.example                       # Plantilla de variables de entorno
├── requirements.txt                   # Dependencias Python
└── README.md
```

---

## Instalación

### 1. Crear entorno virtual

```bash
python -m venv .venv
```

### 2. Activar entorno virtual

**Windows:**
```bash
.venv\Scripts\activate
```

**Linux/Mac:**
```bash
source .venv/bin/activate
```

### 3. Instalar dependencias

```bash
pip install -r requirements.txt
```

---

## Configuración

### Variables de Entorno

1. Copiar el archivo de ejemplo:

   ```bash
   copy .env.example .env
   ```

2. Editar el archivo `.env` con las credenciales correspondientes:

   ```env
   # Base de Datos
   DB_HOST=tu_host
   DB_PORT=5432
   DB_NAME=tu_base_datos
   DB_USER=tu_usuario
   DB_PASSWORD=tu_contraseña

   # Selenium
   OFAC_URL=https://sanctionssearch.ofac.treas.gov/
   SELENIUM_IMPLICIT_WAIT=10
   SELENIUM_EXPLICIT_WAIT=20
   SELENIUM_HEADLESS=false

   # Directorios
   DIR_CAPTURAS=capturas
   DIR_REPORTES=reportes
   DIR_LOGS=logs
   ```

---

## Ejecución

Desde la raíz del proyecto, con el entorno virtual activado:

```bash
python -m src.main
```

El bot mostrará el progreso en consola y al finalizar generará:
- Un resumen en `logs/resumen_rpa_ofac_YYYYMMDD.log`
- Capturas de pantalla en `capturas/`
- Reporte Excel de registros incompletos en `reportes/`

---
