# Automatización de Inventario de Red

Proyecto práctico de la unidad didáctica **DevOps: Fundamentos** (IDAT).
Automatiza la consulta y consolidación del inventario de dispositivos de red de
la organización.

El script lee el inventario local en **cuatro formatos de datos**
(JSON, CSV, XML y YAML), consume un **servicio externo mediante una REST API
sobre HTTPS**, consolida ambos orígenes y genera un reporte unificado con
totales por tipo y por estado.

## Arquitectura

```
inventario_local.json ┐
inventario_local.csv  ├─► scripts/devops_inventario.py ─► reporte_inventario.json
inventario_local.xml  │            ▲
inventario_local.yaml ┘            │
                        REST API (HTTPS)  https://api.restful-api.dev/objects
```

## Requisitos

- Python 3.8+
- Dependencias: `pip install -r requirements.txt`

## Uso

```bash
# Ejecución completa (inventario local + REST API)
python3 scripts/devops_inventario.py

# Solo datos locales (sin consultar la API)
python3 scripts/devops_inventario.py --sin-api

# Parámetros disponibles
python3 scripts/devops_inventario.py --dir . --api-url https://api.restful-api.dev --salida reporte_inventario.json
```

## Buenas prácticas aplicadas

- Funciones con responsabilidad única y *type hints*.
- `docstrings` descriptivos en módulo y funciones.
- Registro de eventos con el módulo `logging`.
- Manejo de excepciones para E/S de archivos y para la REST API
  (errores 4xx/5xx, *timeouts* y fallos de conexión).
- Configuración por línea de comandos con `argparse`.

## Manejo de errores de la REST API

| Situación             | Código | Manejo en el script                |
|-----------------------|--------|------------------------------------|
| Petición correcta     | 200    | Procesa el JSON de respuesta       |
| Recurso inexistente   | 404    | `raise_for_status()` → `HTTPError` |
| Error del servidor    | 5xx    | `raise_for_status()` → `HTTPError` |
| Servicio sin respuesta| —      | `Timeout` controlado               |
| Sin conectividad      | —      | `ConnectionError` controlado       |

## Equipo

- Lopez Verdi, Cristina Veronica
- Bohorquez Patroni, Pedro Stefano
- Mesares Arroyo, Juan Eduardo
- Ramirez de la Cruz, Jorge Shairf
- Rojas Jara, Ahmed Alejandro

---
Instituto IDAT — Unidad Didáctica *DevOps: Fundamentos*
