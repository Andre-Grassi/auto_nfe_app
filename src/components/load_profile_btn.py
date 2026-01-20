import flet as ft


class LoadProfileBtn(ft.Button):
    def __init__(self, on_click):
        super().__init__(
            content=ft.Text("Carregar Credenciais"),
            on_click=on_click,
            style=ft.ButtonStyle(
                shape=ft.RoundedRectangleBorder(radius=20),
                padding=ft.padding.symmetric(horizontal=30, vertical=15),
            ),
            icon=ft.Icons.KEY,
        )
