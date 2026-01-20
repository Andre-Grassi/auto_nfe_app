import flet as ft
import asyncio

# --- Views ---
from views.home import HomeView
from views.nfe import NfeView
from views.nfse import NfseView

# --- Client Nfe ---
from auto_nfe import ClientNfe


async def main(page: ft.Page):
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


ft.run(main=main)
