# Automatización de Inventario de Red

Proyecto práctico de la unidad didáctica **DevOps: Fundamentos** (IDAT). Sistema modular que automatiza la consulta y consolidación del inventario de dispositivos de red, procesando datos locales en cuatro formatos (JSON, CSV, XML y YAML) y consumiendo un servicio externo mediante una **REST API sobre HTTPS con autenticación por token Bearer**.

## Estructura

```
devops-inventario-red/
├── data/
│   ├── config.yaml        # Configuración (API, token, timeout, SSL)
│   ├── dispositivos.csv    # Inventario en formato CSV
│   ├── inventario.json     # Inventario en formato JSON
│   ├── inventario.xml      # Inventario en formato XML
│   └── inventario.yaml     # Inventario en formato YAML
└── src/
    ├── utils.py            # Carga de archivos JSON/CSV/XML/YAML
    ├── api_client.py       # Cliente REST HTTPS + autenticación Bearer
    ├── processor.py        # Consolidación, filtrado y resumen
    └── main.py             # Orquestador principal
```

## Requisitos

- Python 3.8+
- Dependencias: `pip install -r requirements.txt`

## Uso

```bash
python3 -m src.main
```

## Autenticación de la API REST

El módulo `api_client.py` accede a un endpoint protegido enviando un **token Bearer** en la cabecera `Authorization` sobre HTTPS (con verificación SSL). El cliente maneja de forma controlada:

| Código / Error   | Descripción                                        |
|------------------|----------------------------------------------------|
| 200 OK           | Acceso autorizado (token válido)                   |
| 401 Unauthorized | Autenticación fallida (token ausente o inválido)   |
| 403 Forbidden    | Token sin permisos                                 |
| 404 Not Found    | Recurso no encontrado                              |
| 5xx              | Error del servidor                                 |
| SSLError / Timeout / ConnectionError | Excepciones de red controladas |

## Ramas

- `main` / `master`: versión estable.
- `desarrollo`: rama de trabajo (incluye la autenticación de la API).

## Equipo

- Lopez Verdi, Cristina Veronica
- Bohorquez Patroni, Pedro Stefano
- Mesares Arroyo, Juan Eduardo
- Ramirez de la Cruz, Jorge Shairf
- Rojas Jara, Ahmed Alejandro

---
Instituto IDAT — Unidad Didáctica *DevOps: Fundamentos*
