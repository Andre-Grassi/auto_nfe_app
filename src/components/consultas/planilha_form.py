import flet as ft

# Certifique-se de que o import aponta para onde você salvou o componente FileInput
from components.file_input import FileInput


class PlanilhaForm(ft.Column):
    def __init__(self, page: ft.Page):
        """
        Formulário principal.
        Recebe 'page' para permitir que os FileInputs abram janelas nativas.
        """
        super().__init__()
        self._page = page
        self.spacing = 30
        self.alignment = ft.MainAxisAlignment.CENTER

        # --- Campos de Entrada Simples ---
        self.cnpj_input = ft.TextField(
            label="CNPJ", hint_text="Digite o CNPJ", width=300
        )

        self.password_input = ft.TextField(
            label="Senha",
            hint_text="Senha do Certificado",
            password=True,
            can_reveal_password=True,
            width=300,
        )

        # --- Campos de Entrada com Seletor de Arquivo (FileInput) ---

        # 1. Certificado
        self.cert_input = FileInput(
            self._page, label="Certificado A1", icon=ft.Icons.BADGE
        )
        self.cert_input.width = 300  # Força a largura para alinhar com o grid

        # 2. Planilha
        self.sheet_input = FileInput(
            self._page, label="Planilha de Relação", icon=ft.Icons.TABLE_CHART
        )
        self.sheet_input.width = 300

        # 3. Pasta de Destino
        self.folder_input = FileInput(
            self._page, label="Pasta para direcionar XMLs", icon=ft.Icons.FOLDER_OPEN
        )
        self.folder_input.width = 300

        # --- Layout (Grid) ---
        # Linha 1: CNPJ | Certificado | Senha
        row1 = ft.Row(
            [self.cnpj_input, self.cert_input, self.password_input],
            alignment=ft.MainAxisAlignment.CENTER,
            spacing=20,
        )

        # Linha 2: Planilha | Pasta
        row2 = ft.Row(
            [self.sheet_input, self.folder_input],
            alignment=ft.MainAxisAlignment.CENTER,
            spacing=20,
        )

        self.controls.extend([row1, row2])

    def get_values(self):
        """
        Retorna os valores dos campos.
        Nota: O FileInput possui uma propriedade .value que retorna o texto interno.
        """
        return {
            "cnpj": self.cnpj_input.value,
            "cert_path": self.cert_input.value,
            "password": self.password_input.value,
            "sheet_path": self.sheet_input.value,
            "folder_path": self.folder_input.value,
        }
