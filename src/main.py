import flet as ft
import asyncio

# --- Views ---
from views.home import HomeView

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
    def route_change():
        page.views.clear()

        print("Rota alterada para:", page.route)

        if page.route == "/":
            home_view = HomeView()
            print("Entrou na HomeView")
            page.views.append(home_view)

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
