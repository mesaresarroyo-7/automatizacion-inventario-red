# -*- coding: utf-8 -*-
"""api_client.py - Cliente REST HTTPS con autenticacion (Bearer token) y manejo de errores."""
from __future__ import annotations
import logging
from typing import Any, Dict, Optional

import requests

log = logging.getLogger("api_client")


def construir_headers(config: Dict[str, Any], autenticado: bool = True) -> Dict[str, str]:
    """Construye las cabeceras HTTP; incluye el token Bearer si autenticado=True."""
    headers = {"Accept": "application/json", "User-Agent": "devops-inventario/1.0"}
    if autenticado:
        auth = config["api"]["auth"]
        headers["Authorization"] = f"{auth['tipo']} {auth['token']}"
    return headers


def _get(url: str, headers: Dict[str, str], timeout: int, verificar_ssl: bool) -> Optional[requests.Response]:
    """GET HTTPS controlando codigos de estado (incluida autenticacion) y excepciones."""
    try:
        resp = requests.get(url, headers=headers, timeout=timeout, verify=verificar_ssl)
        c = resp.status_code
        if c == 200:
            log.info("200 OK -> acceso autorizado: %s", url)
            return resp
        if c == 401:
            log.warning("401 Unauthorized -> autenticacion fallida (token ausente o invalido)")
        elif c == 403:
            log.warning("403 Forbidden -> el token no tiene permisos para el recurso")
        elif c == 404:
            log.warning("404 Not Found -> recurso no encontrado: %s", url)
        elif 400 <= c < 500:
            log.error("%s Client Error -> error del cliente", c)
        elif 500 <= c < 600:
            log.error("%s Server Error -> error del servidor", c)
        return None
    except requests.exceptions.SSLError:
        log.error("SSLError -> fallo de certificado SSL (alerta de seguridad)")
    except requests.exceptions.Timeout:
        log.error("Timeout -> el servicio no respondio en %ss", timeout)
    except requests.exceptions.ConnectionError:
        log.error("ConnectionError -> sin conectividad de red")
    return None


def consultar_servicio_seguro(config: Dict[str, Any]) -> Optional[Dict[str, Any]]:
    """Accede al endpoint protegido enviando el token Bearer en la cabecera Authorization."""
    api = config["api"]
    url = f"{api['base_url'].rstrip('/')}{api['endpoint_seguro']}"
    log.info("GET %s   [Authorization: %s <token>]", url, api["auth"]["tipo"])
    resp = _get(url, construir_headers(config, True), api["timeout"], api["verificar_ssl"])
    if resp is None:
        return None
    datos = resp.json()
    log.info("Autenticacion correcta -> authenticated=%s", datos.get("authenticated"))
    return datos


def probar_autenticacion_fallida(config: Dict[str, Any]) -> None:
    """Repite la solicitud SIN token para demostrar el manejo del error 401."""
    api = config["api"]
    url = f"{api['base_url'].rstrip('/')}{api['endpoint_seguro']}"
    log.info("Prueba de autenticacion fallida -> GET %s (sin token)", url)
    _get(url, construir_headers(config, False), api["timeout"], api["verificar_ssl"])


def probar_error_404(config: Dict[str, Any]) -> None:
    """Solicita un recurso inexistente para demostrar el manejo del error 404."""
    api = config["api"]
    url = f"{api['base_url'].rstrip('/')}{api['endpoint_invalido']}"
    log.info("Prueba de error 404 -> GET %s", url)
    _get(url, construir_headers(config, True), api["timeout"], api["verificar_ssl"])
