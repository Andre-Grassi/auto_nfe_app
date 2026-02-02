import sys

# Força encoding UTF-8 no console do Windows para suportar caracteres Unicode
# Necessário para apps bundled (Flet build) onde o console não usa UTF-8 por padrão
if sys.stdout and hasattr(sys.stdout, "reconfigure"):
    try:
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    except Exception:
        pass
if sys.stderr and hasattr(sys.stderr, "reconfigure"):
    try:
        sys.stderr.reconfigure(encoding="utf-8", errors="replace")
    except Exception:
        pass

# Compatibilidade com Python 3.12+ (distutils foi removido do stdlib)
# Precisa vir ANTES de qualquer import que use undetected_chromedriver
import types

try:
    from distutils.version import LooseVersion  # noqa: F401
except ImportError:
    from packaging.version import Version as LooseVersion

    # Cria módulo fake distutils.version para bibliotecas que ainda usam
    distutils_version = types.ModuleType("distutils.version")
    distutils_version.LooseVersion = LooseVersion
    sys.modules["distutils"] = types.ModuleType("distutils")
    sys.modules["distutils.version"] = distutils_version

import flet as ft
import asyncio
import os
import logging
from datetime import datetime

# Configura logging para arquivo (útil para debug em PCs sem console)
LOG_DIR = os.path.join(os.environ.get("LOCALAPPDATA", "."), "AutoNfe", "logs")
os.makedirs(LOG_DIR, exist_ok=True)
LOG_FILE = os.path.join(LOG_DIR, f"app_{datetime.now().strftime('%Y%m%d_%H%M%S')}.log")

logging.basicConfig(
    level=logging.DEBUG,
    format="%(asctime)s - %(levelname)s - %(message)s",
    handlers=[
        logging.FileHandler(LOG_FILE, encoding="utf-8"),
        logging.StreamHandler(),  # Também mostra no console se disponível
    ],
)
logger = logging.getLogger(__name__)
logger.info(f"=== App iniciando - Log: {LOG_FILE} ===")

try:
    logger.info("Importando config.paths...")
    from config.paths import (
        APPDATA_DIR,
        PROFILE_PATH,
        EMPRESAS_NFSE_PATH,
        EMPRESAS_NFE_PATH,
    )

    logger.info("Importando config.template_utils...")
    from config.template_utils import ensure_config_file

    logger.info(f"APPDATA_DIR: {APPDATA_DIR}")

    logger.info("Importando views...")
    from views.home import HomeView
    from views.nfe import NfeView
    from views.nfse import NfseView

    logger.info("Views importadas com sucesso")

    logger.info("Importando auto_nfe...")
    from auto_nfe import ClientNfe

    logger.info("auto_nfe importado com sucesso")

except Exception as e:
    logger.exception(f"ERRO FATAL durante imports: {e}")
    raise


async def main(page: ft.Page):
    # --- Configurações ---
    # Garante que arquivos de configuração existam no AppData
    os.makedirs(APPDATA_DIR, exist_ok=True)

    # Cria configs a partir dos templates se não existirem
    if ensure_config_file(PROFILE_PATH, "profile_template.toml"):
        logger.info(f"Criado: {PROFILE_PATH}")
    if ensure_config_file(EMPRESAS_NFSE_PATH, "empresas_nfse_template.toml"):
        logger.info(f"Criado: {EMPRESAS_NFSE_PATH}")
    if ensure_config_file(EMPRESAS_NFE_PATH, "empresas_nfe_template.toml"):
        logger.info(f"Criado: {EMPRESAS_NFE_PATH}")

    # --- Janela ---
    page.title = "Auto Nfe"
    page.theme_mode = ft.ThemeMode.DARK
    page.padding = 40
    page.vertical_alignment = ft.MainAxisAlignment.START
    page.horizontal_alignment = ft.CrossAxisAlignment.CENTER

    # --- Roteamento ---
    async def go_back(e):
        # Option 1: Pop the view
        if len(page.views) > 1:
            page.views.pop()
            top_view = page.views[-1]
            if not top_view.route:
                return
            await page.push_route(top_view.route)

    def route_change():
        page.views.clear()

        logger.info(f"Rota alterada para: {page.route}")

        if page.route == "/":
            home_view = HomeView(page)
            logger.info("Entrou na HomeView")
            page.views.append(home_view)
        elif page.route == "/nfe":
            nfe_view = NfeView(page)
            logger.info("Entrou na NfeView")
            page.views.append(nfe_view)
        elif page.route == "/nfse":
            nfse_view = NfseView(page)
            logger.info("Entrou na NfseView")
            page.views.append(nfse_view)

        page.update()

    async def view_pop(view):
        page.views.pop()
        top_view = page.views[-1]

        if top_view.route:
            await page.push_route(top_view.route)

    page.on_route_change = route_change
    page.on_view_pop = view_pop

    # --- Inicializa App ---
    logger.info("Inicializando aplicação...")

    route_change()


try:
    logger.info("Iniciando ft.run()...")
    ft.run(main=main, assets_dir="assets")
except Exception as e:
    logger.exception(f"ERRO FATAL em ft.run(): {e}")
    raise
