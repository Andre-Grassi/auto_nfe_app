import flet as ft


class DownloadBtn(ft.Button):
    def __init__(self, on_download_action):
        super().__init__(
            content=ft.Text("Baixar Notas"),
            on_click=on_download_action,
            style=ft.ButtonStyle(
                shape=ft.RoundedRectangleBorder(radius=20),
                padding=ft.padding.symmetric(horizontal=30, vertical=15),
            ),
        )
