# -*- coding: utf-8 -*-
"""processor.py - Procesamiento, normalizacion y resumen del inventario."""
from __future__ import annotations
from typing import Any, Dict, List


def normalizar_api(activos: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """Adapta los objetos del servicio externo al esquema del inventario."""
    return [{"id": f"EXT-{i.get('id')}", "hostname": i.get("name", "desconocido"),
             "tipo": "activo_externo", "ip": "-", "ubicacion": "nube",
             "estado": "activo"} for i in activos]


def consolidar(*origenes: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """Une varios origenes de datos en una sola lista de dispositivos."""
    total: List[Dict[str, Any]] = []
    for origen in origenes:
        total.extend(origen)
    return total


def filtrar_activos(dispositivos: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """Devuelve solo los dispositivos cuyo estado es 'activo'."""
    return [d for d in dispositivos if d.get("estado") == "activo"]


def generar_resumen(dispositivos: List[Dict[str, Any]]) -> Dict[str, Any]:
    """Calcula totales por tipo y por estado."""
    por_tipo: Dict[str, int] = {}
    por_estado: Dict[str, int] = {}
    for d in dispositivos:
        por_tipo[d.get("tipo", "?")] = por_tipo.get(d.get("tipo", "?"), 0) + 1
        por_estado[d.get("estado", "?")] = por_estado.get(d.get("estado", "?"), 0) + 1
    return {"total": len(dispositivos), "activos": len(filtrar_activos(dispositivos)),
            "por_tipo": por_tipo, "por_estado": por_estado}


def imprimir_tabla(dispositivos: List[Dict[str, Any]]) -> None:
    """Muestra el inventario consolidado en una tabla legible."""
    print("{:<10} {:<22} {:<16} {:<14} {:<12}".format(
        "ID", "HOSTNAME", "TIPO", "IP", "ESTADO"))
    print("-" * 76)
    for d in dispositivos:
        print("{:<10} {:<22} {:<16} {:<14} {:<12}".format(
            str(d.get("id", "")), str(d.get("hostname", "")),
            str(d.get("tipo", "")), str(d.get("ip", "")), str(d.get("estado", ""))))
