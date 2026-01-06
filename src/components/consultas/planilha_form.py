import flet as ft


class PlanilhaForm(ft.Column):
    def __init__(self):
        super().__init__()
        self.spacing = 30
        self.alignment = ft.MainAxisAlignment.CENTER

        # Campos de Entrada
        self.cnpj_input = ft.TextField(label="CNPJ", hint_text="Value", width=300)
        self.cert_input = ft.TextField(
            label="Certificado A1", hint_text="Value", width=300
        )
        self.password_input = ft.TextField(
            label="Senha",
            hint_text="Value",
            password=True,
            can_reveal_password=True,
            width=300,
        )
        self.sheet_input = ft.TextField(
            label="Planilha de Relação", hint_text="Value", width=300
        )
        self.folder_input = ft.TextField(
            label="Pasta para direcionar XMLs baixados", hint_text="Value", width=300
        )

        # Layout dos Campos (Grid simples para 2 colunas)
        row1 = ft.Row(
            [self.cnpj_input, self.cert_input, self.password_input],
            alignment=ft.MainAxisAlignment.CENTER,
            spacing=20,
        )
        row2 = ft.Row(
            [self.sheet_input, self.folder_input],
            alignment=ft.MainAxisAlignment.CENTER,
            spacing=20,
        )

        self.controls.extend([row1, row2])
