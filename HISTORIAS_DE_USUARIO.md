# Historias de Usuario - Bot RPA OFAC

## Proyecto: Robot de Verificación de Antecedentes OFAC

---

## **HU-01: Conexión a Base de Datos**

**Como** desarrollador del bot RPA
**Quiero** establecer conexión con la base de datos PostgreSQL
**Para** poder acceder a las tablas de personas y almacenar resultados

### Criterios de Aceptación

```gherkin
Escenario: Conexión exitosa a la base de datos
  Dado que tengo las credenciales de conexión correctas
  Cuando el bot intenta conectarse a la base de datos
  Entonces la conexión debe establecerse exitosamente
  Y debe ser posible ejecutar consultas SQL

Escenario: Fallo en la conexión por credenciales incorrectas
  Dado que las credenciales de conexión son incorrectas
  Cuando el bot intenta conectarse a la base de datos
  Entonces debe mostrar un mensaje de error claro
  Y debe registrar el error en el log
  Y el proceso debe detenerse de manera controlada

Escenario: Manejo de pool de conexiones
  Dado que se establece una conexión a la base de datos
  Cuando se realizan múltiples operaciones
  Entonces el pool de conexiones debe reutilizarse eficientemente
  Y al finalizar el proceso, todas las conexiones deben cerrarse
```

---

## **HU-02: Obtener Personas a Consultar**

**Como** bot RPA
**Quiero** obtener el listado de personas desde la tabla "Personas"
**Para** identificar cuáles deben ser consultadas en OFAC

### Criterios de Aceptación

```gherkin
Escenario: Obtener personas con flag de consulta en "Si"
  Dado que la tabla "Personas" contiene registros
  Cuando el bot ejecuta la consulta para obtener personas
  Entonces debe retornar solo las personas donde aConsultar = "Si"
  Y cada persona debe incluir: id, idPersona, nombrePersona, aConsultar

Escenario: No hay personas para consultar
  Dado que no existen personas con aConsultar = "Si"
  Cuando el bot ejecuta la consulta
  Entonces debe retornar una lista vacía
  Y debe registrar en el log que no hay personas para procesar
  Y el proceso debe finalizar correctamente sin errores

Escenario: Unión con tabla maestra
  Dado que una persona existe en "Personas" con aConsultar = "Si"
  Cuando se obtiene el listado de personas
  Entonces debe hacer LEFT JOIN con "MaestraDetallePersonas"
  Y debe incluir direccion y pais si existen en la maestra
```

---

## **HU-03: Validar Información Completa de Personas**

**Como** bot RPA
**Quiero** validar que cada persona tenga dirección y país
**Para** determinar si puede ser consultada en OFAC o debe marcarse como información incompleta

### Criterios de Aceptación

```gherkin
Escenario: Persona con información completa
  Dado que una persona tiene direccion Y pais válidos (no NULL ni "None")
  Cuando se valida la información de la persona
  Entonces debe clasificarse como "persona válida para OFAC"
  Y debe continuar con el proceso de búsqueda

Escenario: Persona sin dirección o país
  Dado que una persona no tiene direccion O no tiene pais
  Cuando se valida la información de la persona
  Entonces debe clasificarse como "Información incompleta"
  Y debe insertarse en la tabla Resultados con estadoTransaccion = "Información incompleta"
  Y NO debe consultarse en OFAC

Escenario: Persona con campos en NULL o "None"
  Dado que una persona tiene direccion = NULL O pais = "None"
  Cuando se valida la información de la persona
  Entonces debe considerarse como información incompleta
  Y debe registrarse con estado "Información incompleta"

Escenario: Persona no existe en tabla maestra
  Dado que una persona con aConsultar = "Si" no tiene registro en "MaestraDetallePersonas"
  Cuando se valida la información de la persona
  Entonces debe clasificarse como "No cruza con maestra"
  Y debe insertarse en Resultados con estadoTransaccion = "No cruza con maestra"
  Y NO debe consultarse en OFAC
```

---

## **HU-04: Inserción Masiva de Registros No Consultables**

**Como** bot RPA
**Quiero** insertar masivamente los registros que no serán consultados en OFAC
**Para** optimizar el rendimiento y cumplir con el requisito de inserciones masivas

### Criterios de Aceptación

```gherkin
Escenario: Insertar lote de personas con información incompleta
  Dado que existen N personas con información incompleta
  Cuando se ejecuta la inserción masiva
  Entonces todos los registros deben insertarse en una sola operación (executemany)
  Y cada registro debe tener estadoTransaccion = "Información incompleta"
  Y cantidadDeResultados debe ser 0 o NULL
  Y debe registrarse en el log la cantidad de registros insertados

Escenario: Insertar lote de personas que no cruzan con maestra
  Dado que existen N personas que no cruzan con maestra
  Cuando se ejecuta la inserción masiva
  Entonces todos los registros deben insertarse en una sola operación
  Y cada registro debe tener estadoTransaccion = "No cruza con maestra"
  Y cantidadDeResultados debe ser 0 o NULL

Escenario: No hay registros para insertar masivamente
  Dado que no hay personas con información incompleta o que no cruzan
  Cuando se intenta la inserción masiva
  Entonces no debe ejecutarse ninguna operación SQL
  Y debe continuar con el siguiente paso del proceso
```

---

## **HU-05: Navegar al Sitio Web de OFAC**

**Como** bot RPA
**Quiero** navegar al sitio web de OFAC (https://sanctionssearch.ofac.treas.gov/)
**Para** poder realizar búsquedas de personas

### Criterios de Aceptación

```gherkin
Escenario: Navegación exitosa a OFAC
  Dado que el navegador Chrome está iniciado
  Cuando el bot navega a la URL de OFAC
  Entonces la página debe cargarse completamente
  Y el formulario de búsqueda debe ser visible
  Y todos los elementos (Name, Address, Country, Search, Reset) deben estar presentes

Escenario: Timeout al cargar la página
  Dado que la página de OFAC no responde en 20 segundos
  Cuando el bot intenta navegar
  Entonces debe registrar un error de timeout
  Y debe reintentar hasta 3 veces
  Y si falla, debe detener el proceso con error

Escenario: Error de red
  Dado que no hay conexión a internet
  Cuando el bot intenta navegar a OFAC
  Entonces debe capturar el error de red
  Y debe registrarlo en el log
  Y debe finalizar el proceso con código de error
```

---

## **HU-06: Llenar Formulario de Búsqueda OFAC**

**Como** bot RPA
**Quiero** llenar los campos del formulario de OFAC con los datos de la persona
**Para** poder ejecutar la búsqueda de sanciones

### Criterios de Aceptación

```gherkin
Escenario: Llenar formulario con datos completos
  Dado que tengo una persona con nombre, direccion y pais
  Cuando lleno el formulario de OFAC
  Entonces el campo "Name" debe contener el nombrePersona
  Y el campo "Address" debe contener la direccion
  Y el dropdown "Country" debe seleccionar el pais
  Y todos los campos deben estar visibles y habilitados

Escenario: Seleccionar país en el dropdown
  Dado que el país de la persona es "All" o "United States"
  Cuando se selecciona el país en el dropdown
  Entonces debe seleccionarse por texto exacto primero
  Y si no existe exacto, debe buscar coincidencia parcial
  Y si no se encuentra, debe registrar una advertencia en el log

Escenario: Limpiar formulario antes de nueva búsqueda
  Dado que ya se realizó una búsqueda previa
  Cuando se va a buscar una nueva persona
  Entonces debe hacer clic en el botón "Reset"
  Y todos los campos deben quedar vacíos
  Y debe esperar 1 segundo para asegurar la limpieza
```

---

## **HU-07: Ejecutar Búsqueda en OFAC**

**Como** bot RPA
**Quiero** hacer clic en el botón "Search" y esperar los resultados
**Para** obtener el número de coincidencias encontradas

### Criterios de Aceptación

```gherkin
Escenario: Búsqueda exitosa con resultados
  Dado que el formulario está lleno correctamente
  Cuando hago clic en el botón "Search"
  Entonces debe aparecer el texto "Lookup Results"
  Y debe mostrarse "X Found" donde X >= 0
  Y debe extraerse el número de resultados correctamente

Escenario: Búsqueda sin resultados
  Dado que la persona no está en las listas de OFAC
  Cuando se ejecuta la búsqueda
  Entonces debe mostrarse "0 Found"
  Y debe registrarse cantidad = 0
  Y NO debe tomarse screenshot

Escenario: Error durante la búsqueda
  Dado que ocurre un error al hacer clic en Search
  Cuando se ejecuta la búsqueda
  Entonces debe registrarse el error en el log
  Y debe reintentarse hasta 3 veces con 2 segundos de espera
  Y si falla después de 3 intentos, debe marcarse como "NOK"

Escenario: Timeout esperando resultados
  Dado que los resultados no aparecen en 20 segundos
  Cuando se espera la respuesta de OFAC
  Entonces debe registrarse un timeout
  Y debe reintentarse la búsqueda
```

---

## **HU-08: Capturar Screenshot de Resultados**

**Como** bot RPA
**Quiero** capturar una screenshot cuando hay resultados > 0
**Para** tener evidencia visual de las coincidencias encontradas

### Criterios de Aceptación

```gherkin
Escenario: Capturar screenshot cuando hay resultados
  Dado que la búsqueda retorna cantidad > 0
  Cuando se detectan resultados
  Entonces debe capturarse una screenshot de la página
  Y el nombre debe ser "AAAAMMDD_idPersona.png"
  Y debe guardarse en la carpeta "capturas/"
  Y debe registrarse en el log la ruta del archivo

Escenario: No capturar screenshot cuando no hay resultados
  Dado que la búsqueda retorna cantidad = 0
  Cuando se completa la búsqueda
  Entonces NO debe capturarse ninguna screenshot
  Y debe continuar con el siguiente registro

Escenario: Error al capturar screenshot
  Dado que la screenshot falla por permisos o espacio en disco
  Cuando se intenta capturar
  Entonces debe registrarse el error en el log
  Y debe continuar con el proceso (no debe detenerlo)
  Y el resultado debe guardarse en BD con estado "OK" igualmente

Escenario: Formato del nombre de archivo
  Dado que la fecha es 28/07/2022 y el idPersona es 34
  Cuando se captura la screenshot
  Entonces el nombre debe ser "20220728_34.png"
  Y debe crearse el directorio "capturas/" si no existe
```

---

## **HU-09: Guardar Resultado en Base de Datos**

**Como** bot RPA
**Quiero** guardar el resultado de cada búsqueda en la tabla "Resultadosuser9145"
**Para** tener registro de todas las consultas realizadas

### Criterios de Aceptación

```gherkin
Escenario: Guardar resultado exitoso
  Dado que la búsqueda en OFAC fue exitosa
  Cuando se guarda el resultado
  Entonces debe insertarse un registro con:
    | Campo                 | Valor                    |
    | idPersona             | ID de la persona         |
    | nombrePersona         | Nombre de la persona     |
    | pais                  | País de la persona       |
    | cantidadDeResultados  | Número encontrado        |
    | estadoTransaccion     | "OK"                     |
  Y debe registrarse en el log el ID del registro insertado

Escenario: Guardar resultado con error
  Dado que la búsqueda en OFAC falló después de 3 reintentos
  Cuando se guarda el resultado
  Entonces estadoTransaccion debe ser "NOK"
  Y cantidadDeResultados debe ser 0
  Y debe registrarse el error en el log

Escenario: Validar campos obligatorios
  Dado que se va a insertar un resultado
  Cuando se ejecuta el INSERT
  Entonces idPersona, nombrePersona y estadoTransaccion deben ser NOT NULL
  Y si falta algún campo, debe lanzarse una excepción
  Y debe registrarse en el log

Escenario: Evitar duplicados
  Dado que ya existe un resultado para un idPersona
  Cuando se intenta insertar otro resultado para el mismo idPersona
  Entonces debe permitirse (no hay constraint UNIQUE)
  Pero debe registrarse una advertencia en el log
```

---

## **HU-10: Exportar Reporte Excel de Información Incompleta**

**Como** usuario del sistema
**Quiero** obtener un reporte Excel con todas las personas que tienen información incompleta
**Para** poder corregir los datos faltantes

### Criterios de Aceptación

```gherkin
Escenario: Exportar registros con información incompleta
  Dado que existen N registros con estadoTransaccion = "Información incompleta"
  Cuando se genera el reporte Excel
  Entonces debe crearse un archivo .xlsx en la carpeta "reportes/"
  Y el nombre debe ser "reporte_incompletos_AAAAMMDD.xlsx"
  Y debe contener todas las columnas de la tabla Resultados
  Y debe incluir solo registros con estadoTransaccion = "Información incompleta"

Escenario: No hay registros incompletos
  Dado que no existen registros con información incompleta
  Cuando se intenta generar el reporte
  Entonces debe crear un archivo vacío o con solo encabezados
  Y debe registrarse en el log que no hay registros

Escenario: Error al crear el archivo Excel
  Dado que no hay permisos de escritura en la carpeta "reportes/"
  Cuando se intenta generar el reporte
  Entonces debe capturarse el error
  Y debe registrarse en el log
  Y el proceso principal debe continuar (no debe detenerse)
```

---

## **HU-11: Procesamiento Completo de Múltiples Personas**

**Como** usuario del sistema
**Quiero** que el bot procese automáticamente todas las personas marcadas para consulta
**Para** verificar antecedentes de forma masiva y eficiente

### Criterios de Aceptación

```gherkin
Escenario: Procesar todas las personas correctamente
  Dado que hay 35 personas con aConsultar = "Si"
  Cuando se ejecuta el bot completo
  Entonces debe procesar las 35 personas
  Y debe clasificarlas en:
    - Personas válidas (a buscar en OFAC)
    - Información incompleta
    - No cruza con maestra
  Y debe insertar masivamente las no consultables
  Y debe buscar en OFAC solo las válidas
  Y debe generar el reporte Excel al final

Escenario: Manejo de errores sin detener el proceso
  Dado que una persona falla durante la búsqueda OFAC
  Cuando ocurre el error
  Entonces debe registrarse el error para esa persona
  Y debe continuar con la siguiente persona
  Y el proceso NO debe detenerse completamente

Escenario: Mostrar estadísticas finales
  Dado que el proceso completo ha finalizado
  Cuando termina la ejecución
  Entonces debe mostrar un resumen con:
    | Métrica                    | Descripción                |
    | Total personas             | Total procesadas           |
    | Búsquedas exitosas (OK)    | Consultadas en OFAC OK     |
    | Búsquedas fallidas (NOK)   | Consultadas en OFAC NOK    |
    | No cruzan con maestra      | Sin datos en maestra       |
    | Información incompleta     | Sin dirección o país       |
    | Errores                    | Errores no controlados     |
```

---

## **HU-12: Logging y Trazabilidad**

**Como** desarrollador/usuario del sistema
**Quiero** que todas las operaciones se registren en logs
**Para** poder depurar errores y auditar el proceso

### Criterios de Aceptación

```gherkin
Escenario: Registro de eventos importantes
  Dado que el bot está en ejecución
  Cuando ocurre cualquier evento importante
  Entonces debe registrarse en el log con:
    - Timestamp
    - Nivel (INFO, WARNING, ERROR)
    - Mensaje descriptivo
    - Contexto (idPersona si aplica)

Escenario: Registro de errores con stack trace
  Dado que ocurre una excepción
  Cuando se captura el error
  Entonces debe registrarse con nivel ERROR
  Y debe incluir el stack trace completo
  Y debe indicar en qué paso del proceso ocurrió

Escenario: Logs en archivo y consola
  Dado que el bot se está ejecutando
  Cuando se genera un log
  Entonces debe aparecer en la consola
  Y debe guardarse en un archivo "logs/rpa_ofac_AAAAMMDD.log"
  Y el archivo debe rotarse diariamente
```

---

## **HU-13: Manejo de Reintentos**

**Como** bot RPA
**Quiero** reintentar operaciones fallidas hasta 3 veces
**Para** mejorar la robustez ante errores transitorios de red o carga del sitio

### Criterios de Aceptación

```gherkin
Escenario: Reintento exitoso después de fallo temporal
  Dado que la primera búsqueda en OFAC falla por timeout
  Cuando el bot reintenta la operación
  Entonces debe esperar 2 segundos
  Y debe volver a navegar a OFAC
  Y debe reintentar la búsqueda
  Y si funciona en el segundo intento, debe marcarse como "OK"

Escenario: Fallo después de 3 reintentos
  Dado que la búsqueda falla 3 veces consecutivas
  Cuando se agota el número de reintentos
  Entonces debe marcarse como "NOK"
  Y debe registrarse en el log que falló después de 3 intentos
  Y debe continuar con la siguiente persona

Escenario: No reintentar operaciones de base de datos
  Dado que una inserción a BD falla
  Cuando ocurre el error
  Entonces NO debe reintentarse automáticamente
  Y debe lanzarse la excepción
  Y debe detener el procesamiento de esa persona
```

---

## **HU-14: Configuración del Sistema**

**Como** desarrollador del sistema
**Quiero** tener toda la configuración centralizada
**Para** poder modificar parámetros sin cambiar código

### Criterios de Aceptación

```gherkin
Escenario: Cargar configuración desde variables de entorno
  Dado que existen variables de entorno definidas
  Cuando el bot se inicializa
  Entonces debe cargar:
    - Credenciales de BD (host, puerto, usuario, contraseña)
    - URL de OFAC
    - Tiempos de espera
    - Modo headless
    - Directorios de capturas, reportes, logs

Escenario: Usar valores por defecto si no hay variables de entorno
  Dado que no existen variables de entorno definidas
  Cuando el bot se inicializa
  Entonces debe usar los valores por defecto configurados
  Y debe poder ejecutarse correctamente

Escenario: Validar configuración al inicio
  Dado que el bot se está iniciando
  Cuando se carga la configuración
  Entonces debe validar que:
    - Las credenciales de BD son válidas
    - La URL de OFAC es accesible
    - Los directorios de salida se pueden crear
  Y si algo falla, debe mostrar error claro y detener
```

---

## Resumen de Historias de Usuario

| ID | Historia de Usuario | Prioridad | Complejidad | Estado |
|----|---------------------|-----------|-------------|--------|
| HU-01 | Conexión a Base de Datos | Alta | Media | ✅ COMPLETADA |
| HU-02 | Obtener Personas a Consultar | Alta | Baja | ✅ COMPLETADA |
| HU-03 | Validar Información Completa | Alta | Media | ✅ COMPLETADA |
| HU-04 | Inserción Masiva de Registros | Alta | Media | ❌ PENDIENTE |
| HU-05 | Navegar al Sitio OFAC | Alta | Baja | ✅ COMPLETADA |
| HU-06 | Llenar Formulario OFAC | Alta | Media | ✅ COMPLETADA |
| HU-07 | Ejecutar Búsqueda en OFAC | Alta | Alta | ✅ COMPLETADA |
| HU-08 | Capturar Screenshot | Media | Baja | ❌ PENDIENTE |
| HU-09 | Guardar Resultado en BD | Alta | Media | ❌ PENDIENTE |
| HU-10 | Exportar Reporte Excel | Media | Baja | ❌ PENDIENTE |
| HU-11 | Procesamiento Completo | Alta | Alta | ❌ PENDIENTE |
| HU-12 | Logging y Trazabilidad | Media | Baja | ❌ PENDIENTE |
| HU-13 | Manejo de Reintentos | Media | Media | ❌ PENDIENTE |
| HU-14 | Configuración del Sistema | Alta | Baja | ✅ COMPLETADA |

---

## Definición de Done (DoD)

Para considerar una Historia de Usuario como **terminada**, debe cumplir:

1. ✅ Código implementado y funcionando
2. ✅ Todos los criterios de aceptación pasando
3. ✅ Pruebas unitarias creadas y pasando
4. ✅ Pruebas de integración ejecutadas exitosamente
5. ✅ Logging implementado para la funcionalidad
6. ✅ Manejo de errores implementado
7. ✅ Documentación actualizada (si aplica)
8. ✅ Code review realizado
9. ✅ Sin errores críticos en el análisis de código
10. ✅ Demostración exitosa al Product Owner
