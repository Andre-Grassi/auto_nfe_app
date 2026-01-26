# Compatibilidade com Python 3.12+ (distutils foi removido do stdlib)
# Precisa vir ANTES de qualquer import que use undetected_chromedriver
import sys
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

from shutil import copyfile

from config.paths import (
    APPDATA_DIR,
    PROFILE_PATH,
    PROFILE_TEMPLATE_PATH,
    EMPRESAS_NFSE_PATH,
    EMPRESAS_NFSE_TEMPLATE_PATH,
    EMPRESAS_NFE_PATH,
    EMPRESAS_NFE_TEMPLATE_PATH,
)

# --- Views ---
from views.home import HomeView
from views.nfe import NfeView
from views.nfse import NfseView

# --- Client Nfe ---
from auto_nfe import ClientNfe


async def main(page: ft.Page):
    # --- Configurações ---
    # Garante que dados no AppData existam
    os.makedirs(APPDATA_DIR, exist_ok=True)
    if not os.path.exists(PROFILE_PATH):
        copyfile(PROFILE_TEMPLATE_PATH, PROFILE_PATH)
    if not os.path.exists(EMPRESAS_NFSE_PATH):
        copyfile(EMPRESAS_NFSE_TEMPLATE_PATH, EMPRESAS_NFSE_PATH)
    if not os.path.exists(EMPRESAS_NFE_PATH):
        copyfile(EMPRESAS_NFE_TEMPLATE_PATH, EMPRESAS_NFE_PATH)

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

        print("Rota alterada para:", page.route)

        if page.route == "/":
            home_view = HomeView(page)
            print("Entrou na HomeView")
            page.views.append(home_view)
        elif page.route == "/nfe":
            nfe_view = NfeView(page)
            print("Entrou na NfeView")
            page.views.append(nfe_view)
        elif page.route == "/nfse":
            nfse_view = NfseView(page)
            print("Entrou na NfseView")
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
    print("Inicializando aplicação...")

    route_change()


ft.run(main=main, assets_dir="../assets")
