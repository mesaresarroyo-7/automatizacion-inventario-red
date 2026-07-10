# -*- coding: utf-8 -*-
"""utils.py - Utilidades de carga de archivos (JSON, CSV, XML, YAML)."""
from __future__ import annotations
import csv
import json
import xml.etree.ElementTree as ET
from pathlib import Path
from typing import Any, Dict, List

import yaml

CAMPOS = ("id", "hostname", "tipo", "ip", "ubicacion", "estado")


def mostrar_separador(titulo: str = "") -> None:
    """Imprime un separador visual con un titulo opcional."""
    print("=" * 64)
    if titulo:
        print(f"  {titulo}")
        print("=" * 64)


def cargar_config(ruta: Path) -> Dict[str, Any]:
    """Carga la configuracion del sistema desde un archivo YAML."""
    with Path(ruta).open(encoding="utf-8") as fh:
        return yaml.safe_load(fh)


def cargar_json(ruta: Path) -> List[Dict[str, Any]]:
    """Carga un inventario en formato JSON."""
    with Path(ruta).open(encoding="utf-8") as fh:
        return json.load(fh)


def cargar_csv(ruta: Path) -> List[Dict[str, Any]]:
    """Carga un inventario en formato CSV usando DictReader."""
    with Path(ruta).open(encoding="utf-8", newline="") as fh:
        return list(csv.DictReader(fh))


def cargar_xml(ruta: Path) -> List[Dict[str, Any]]:
    """Carga un inventario en formato XML normalizando cada <dispositivo>."""
    raiz = ET.parse(ruta).getroot()
    return [{c: (n.findtext(c) or "").strip() for c in CAMPOS}
            for n in raiz.findall("dispositivo")]


def cargar_yaml(ruta: Path) -> List[Dict[str, Any]]:
    """Carga un inventario en formato YAML."""
    with Path(ruta).open(encoding="utf-8") as fh:
        return yaml.safe_load(fh) or []
