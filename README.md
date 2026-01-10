# Bot RPA - Verificación de Sanciones OFAC

Bot de automatización robótica de procesos (RPA) que realiza verificaciones de sanciones OFAC para personas almacenadas en una base de datos PostgreSQL.

## Descripción

Este bot automatiza el proceso de verificación de sanciones de la OFAC (Office of Foreign Assets Control) mediante:

1. Consulta de personas en la base de datos
2. Validación de datos (cruce con tabla maestra)
3. Búsqueda automática en el sitio web de OFAC
4. Captura de resultados y screenshots
5. Almacenamiento de resultados en la base de datos
6. Exportación de reportes a Excel

## Estructura del Proyecto

```
prueba_tecnica/
├── src/
│   ├── main.py                      # Punto de entrada
│   ├── config/                      # Configuración
│   │   ├── configuracion.py         # Variables de configuración
│   │   └── constantes.py            # Constantes del proyecto
│   ├── base_datos/                  # Capa de datos
│   │   ├── conexion.py              # Pool de conexiones
│   │   ├── repositorio_personas.py  # CRUD de personas
│   │   └── repositorio_resultados.py # CRUD de resultados
│   ├── scraping/                    # Web scraping
│   │   ├── navegador.py             # Configuración Selenium
│   │   └── buscador_ofac.py         # Lógica de búsqueda OFAC
│   ├── servicios/                   # Lógica de negocio
│   │   ├── servicio_validacion.py   # Validación de datos
│   │   ├── servicio_procesamiento.py # Orquestador principal
│   │   └── servicio_exportacion.py  # Exportación a Excel
│   └── utilidades/                  # Utilidades
│       ├── logger.py                # Configuración de logging
│       └── captura_pantalla.py      # Manejo de screenshots
├── tests/                           # Pruebas unitarias
├── capturas/                        # Screenshots (generado)
├── reportes/                        # Archivos Excel (generado)
├── logs/                            # Archivos de log (generado)
├── .env                             # Variables de entorno
├── .gitignore
├── requirements.txt
└── README.md
```

## Requisitos

- Python 3.8+
- Google Chrome
- ChromeDriver (compatible con tu versión de Chrome)

## Instalación

1. Clonar o descargar el proyecto

2. Crear y activar el entorno virtual:
   ```bash
   python -m venv .venv
   .venv\Scripts\activate  # Windows
   source .venv/bin/activate  # Linux/Mac
   ```

3. Instalar dependencias:
   ```bash
   pip install -r requirements.txt
   ```

4. Configurar variables de entorno:
   - Copiar `.env.example` a `.env`
   - Ajustar los valores según tu entorno

## Uso

Ejecutar el bot:

```bash
python -m src.main
```

O desde la raíz del proyecto:

```bash
python src/main.py
```

## Configuración

Las variables de configuración se pueden ajustar en el archivo `.env`:

| Variable | Descripción | Valor por defecto |
|----------|-------------|-------------------|
| `DB_HOST` | Host de la base de datos | localhost |
| `DB_PORT` | Puerto de la base de datos | 5432 |
| `DB_NAME` | Nombre de la base de datos | prueba-tecnica |
| `DB_USER` | Usuario de la base de datos | - |
| `DB_PASSWORD` | Contraseña de la base de datos | - |
| `SELENIUM_HEADLESS` | Ejecutar sin interfaz gráfica | false |

## Estados de Transacción

| Estado | Descripción |
|--------|-------------|
| `OK` | Búsqueda completada exitosamente |
| `NOK` | Error en la búsqueda |
| `Información incompleta` | Falta dirección o país |
| `No cruza con maestra` | Persona no encontrada en tabla maestra |

## Pruebas

Ejecutar pruebas unitarias:

```bash
python -m pytest tests/
```

## Entregables

1. Código fuente del proyecto
2. Video de ejecución
3. Screenshots capturados (carpeta `capturas/`)
4. Tabla de resultados actualizada en la base de datos
5. Reporte Excel con registros incompletos

## Autor

Desarrollado como prueba técnica para PrevalentWare.
