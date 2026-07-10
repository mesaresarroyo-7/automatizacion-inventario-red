#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Automatizacion de inventario de red.

Lee el inventario local en JSON, CSV, XML y YAML, consume un servicio externo
mediante una REST API sobre HTTPS y genera un reporte consolidado.
Buenas practicas: funciones con responsabilidad unica, type hints, docstrings,
logging y manejo de excepciones (errores 4xx/5xx, timeouts y conexion).
"""
from __future__ import annotations
import argparse, csv, json, logging, sys
import xml.etree.ElementTree as ET
from pathlib import Path
from typing import Any, Dict, List

try:
    import yaml
except ImportError:
    yaml = None
try:
    import requests
except ImportError:
    requests = None

logging.basicConfig(level=logging.INFO,
                    format="%(asctime)s [%(levelname)s] %(message)s",
                    datefmt="%H:%M:%S")
log = logging.getLogger("inventario")
CAMPOS = ("id", "hostname", "tipo", "ip", "ubicacion", "estado")


def cargar_json(ruta: Path) -> List[Dict[str, Any]]:
    """Lee un inventario en formato JSON."""
    with ruta.open(encoding="utf-8") as fh:
        datos = json.load(fh)
    log.info("JSON  -> %s registros de %s", len(datos), ruta.name)
    return datos


def cargar_csv(ruta: Path) -> List[Dict[str, Any]]:
    """Lee un inventario en formato CSV con DictReader."""
    with ruta.open(encoding="utf-8", newline="") as fh:
        datos = list(csv.DictReader(fh))
    log.info("CSV   -> %s registros de %s", len(datos), ruta.name)
    return datos


def cargar_xml(ruta: Path) -> List[Dict[str, Any]]:
    """Lee un inventario en formato XML normalizando cada <dispositivo>."""
    raiz = ET.parse(ruta).getroot()
    datos = [{c: (n.findtext(c) or "").strip() for c in CAMPOS}
             for n in raiz.findall("dispositivo")]
    log.info("XML   -> %s registros de %s", len(datos), ruta.name)
    return datos


def cargar_yaml(ruta: Path) -> List[Dict[str, Any]]:
    """Lee un inventario en formato YAML (requiere PyYAML)."""
    if yaml is None:
        log.warning("PyYAML no instalado; se omite %s", ruta.name)
        return []
    with ruta.open(encoding="utf-8") as fh:
        datos = yaml.safe_load(fh) or []
    log.info("YAML  -> %s registros de %s", len(datos), ruta.name)
    return datos


LECTORES = {".json": cargar_json, ".csv": cargar_csv,
            ".xml": cargar_xml, ".yaml": cargar_yaml, ".yml": cargar_yaml}


def cargar_local(carpeta: Path) -> List[Dict[str, Any]]:
    """Consolida todos los formatos locales soportados."""
    total: List[Dict[str, Any]] = []
    for ruta in sorted(carpeta.glob("inventario_local.*")):
        lector = LECTORES.get(ruta.suffix.lower())
        if not lector:
            continue
        try:
            total.extend(lector(ruta))
        except Exception as exc:
            log.error("No se pudo leer %s: %s", ruta.name, exc)
    return total


def consultar_api(base_url: str, timeout: int = 10) -> List[Dict[str, Any]]:
    """GET seguro (HTTPS) al endpoint /objects, con manejo de errores."""
    if requests is None:
        log.error("La libreria 'requests' no esta instalada.")
        return []
    url = f"{base_url.rstrip('/')}/objects"
    cab = {"Accept": "application/json", "User-Agent": "devops-inventario/1.0"}
    try:
        log.info("GET %s", url)
        resp = requests.get(url, headers=cab, timeout=timeout)
        resp.raise_for_status()
        datos = resp.json()
        log.info("API   -> %s activos externos (HTTP %s)", len(datos), resp.status_code)
        return datos
    except requests.exceptions.HTTPError as exc:
        log.error("Error HTTP %s: %s", exc.response.status_code, exc)
    except requests.exceptions.Timeout:
        log.error("Timeout: el servicio no respondio en %ss", timeout)
    except requests.exceptions.ConnectionError as exc:
        log.error("Error de conexion: %s", exc)
    except ValueError:
        log.error("La respuesta no es un JSON valido.")
    return []


def probar_error_api(base_url: str, timeout: int = 10) -> None:
    """Solicita un recurso inexistente para demostrar el manejo de un 404."""
    if requests is None:
        return
    url = f"{base_url.rstrip('/')}/objects/id-inexistente-999"
    try:
        log.info("Prueba de error -> GET %s", url)
        requests.get(url, timeout=timeout).raise_for_status()
    except requests.exceptions.HTTPError as exc:
        log.warning("Capturado HTTP %s (recurso inexistente)", exc.response.status_code)
    except requests.exceptions.RequestException as exc:
        log.warning("Excepcion de red controlada: %s", exc)


def normalizar_api(activos: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """Adapta los objetos externos al esquema del inventario."""
    return [{"id": f"EXT-{i.get('id')}", "hostname": i.get("name", "?"),
             "tipo": "activo_externo", "ip": "-", "ubicacion": "nube",
             "estado": "activo"} for i in activos]


def generar_reporte(disp: List[Dict[str, Any]]) -> Dict[str, Any]:
    """Resume totales por tipo y por estado."""
    por_tipo: Dict[str, int] = {}
    por_estado: Dict[str, int] = {}
    for d in disp:
        por_tipo[d.get("tipo", "?")] = por_tipo.get(d.get("tipo", "?"), 0) + 1
        por_estado[d.get("estado", "?")] = por_estado.get(d.get("estado", "?"), 0) + 1
    return {"total": len(disp), "por_tipo": por_tipo,
            "por_estado": por_estado, "dispositivos": disp}


def imprimir_tabla(disp: List[Dict[str, Any]]) -> None:
    """Muestra el inventario consolidado en una tabla."""
    print("\n{:<10} {:<22} {:<16} {:<14} {:<12}".format(
        "ID", "HOSTNAME", "TIPO", "IP", "ESTADO"))
    print("-" * 78)
    for d in disp:
        print("{:<10} {:<22} {:<16} {:<14} {:<12}".format(
            str(d.get("id", "")), str(d.get("hostname", "")),
            str(d.get("tipo", "")), str(d.get("ip", "")), str(d.get("estado", ""))))


def main(argv: List[str] | None = None) -> int:
    p = argparse.ArgumentParser(description="Inventario de red (local + REST API).")
    p.add_argument("--dir", default=".", help="Carpeta con inventario_local.*")
    p.add_argument("--api-url", default="https://api.restful-api.dev", help="URL base HTTPS")
    p.add_argument("--salida", default="reporte_inventario.json", help="Archivo de salida")
    p.add_argument("--sin-api", action="store_true", help="Omite la REST API")
    args = p.parse_args(argv)

    carpeta = Path(args.dir)
    if not carpeta.is_dir():
        log.error("La carpeta %s no existe.", carpeta)
        return 1

    log.info("== Inicio de la automatizacion de inventario ==")
    disp = cargar_local(carpeta)
    if not args.sin_api:
        disp.extend(normalizar_api(consultar_api(args.api_url)))
        probar_error_api(args.api_url)

    rep = generar_reporte(disp)
    imprimir_tabla(disp)
    print("\nResumen por tipo:  ", rep["por_tipo"])
    print("Resumen por estado:", rep["por_estado"])
    print("Total de dispositivos:", rep["total"])
    Path(args.salida).write_text(json.dumps(rep, indent=2, ensure_ascii=False), encoding="utf-8")
    log.info("Reporte guardado en %s", args.salida)
    log.info("== Fin de la automatizacion ==")
    return 0


if __name__ == "__main__":
    sys.exit(main())
