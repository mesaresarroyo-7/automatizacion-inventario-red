# -*- coding: utf-8 -*-
"""main.py - Orquestador del sistema de automatizacion de inventario de red.

Uso:  python3 -m src.main
"""
from __future__ import annotations
import logging
from pathlib import Path

from src import utils, api_client, processor

logging.basicConfig(level=logging.INFO,
                    format="%(asctime)s [%(levelname)s] %(message)s",
                    datefmt="%H:%M:%S")

BASE = Path(__file__).resolve().parent.parent
DATA = BASE / "data"


def main() -> int:
    config = utils.cargar_config(DATA / "config.yaml")
    utils.mostrar_separador(f"{config['sistema']['nombre']} v{config['sistema']['version']}")

    locales = processor.consolidar(
        utils.cargar_json(DATA / "inventario.json"),
        utils.cargar_csv(DATA / "dispositivos.csv"),
        utils.cargar_xml(DATA / "inventario.xml"),
        utils.cargar_yaml(DATA / "inventario.yaml"),
    )
    print(f"Inventario local cargado: {len(locales)} dispositivos (JSON + CSV + XML + YAML)\n")
    processor.imprimir_tabla(locales)

    utils.mostrar_separador("Consumo de API REST HTTPS con autenticacion (Bearer token)")
    api_client.consultar_servicio_seguro(config)
    api_client.probar_autenticacion_fallida(config)
    api_client.probar_error_404(config)

    resumen = processor.generar_resumen(locales)
    utils.mostrar_separador("Resumen del inventario de red")
    print(f"Total de dispositivos : {resumen['total']}")
    print(f"Dispositivos activos  : {resumen['activos']}")
    print(f"Por tipo   : {resumen['por_tipo']}")
    print(f"Por estado : {resumen['por_estado']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
