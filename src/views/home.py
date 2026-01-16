import flet as ft
import asyncio


class HomeView(ft.View):
    def __init__(self, page: ft.Page):
        super().__init__(route="/")

        # Título
        self.title = ft.Text("Auto Nfe", size=40, weight=ft.FontWeight.BOLD)

        # Botões de navegação
        self.btn_nfe = ft.ElevatedButton(
            content="Consultar NF-e",
            icon=ft.Icons.SEARCH,
            width=220,
            height=50,
            on_click=lambda _: asyncio.create_task(self.go_to_nfe_view(page)),
            style=ft.ButtonStyle(
                bgcolor=ft.Colors.WHITE,
                color=ft.Colors.DEEP_PURPLE,
                shape=ft.RoundedRectangleBorder(radius=25),
            ),
        )

        self.btn_nfse = ft.ElevatedButton(
            content="Consultar NFS-e",
            icon=ft.Icons.SEARCH,
            width=220,
            height=50,
            on_click=lambda _: asyncio.create_task(self.go_to_nfse_view(page)),
            style=ft.ButtonStyle(
                bgcolor=ft.Colors.WHITE,
                color=ft.Colors.DEEP_PURPLE,
                shape=ft.RoundedRectangleBorder(radius=25),
            ),
        )

        # Layout dos botões
        self.buttons_column = ft.Column(
            [self.btn_nfe, self.btn_nfse],
            alignment=ft.MainAxisAlignment.CENTER,
            horizontal_alignment=ft.CrossAxisAlignment.CENTER,
            spacing=20,
        )

        self.controls = [
            ft.Container(height=50),  # Espaçamento superior
            self.title,
            ft.Container(height=80),  # Espaçamento entre título e botões
            self.buttons_column,
        ]

        # --- Alinhamento ---
        self.vertical_alignment = ft.MainAxisAlignment.CENTER
        self.horizontal_alignment = ft.CrossAxisAlignment.CENTER

    async def go_to_nfe_view(self, page: ft.Page):
        await page.push_route("/nfe")

    async def go_to_nfse_view(self, page: ft.Page):
        await page.push_route("/nfse")
