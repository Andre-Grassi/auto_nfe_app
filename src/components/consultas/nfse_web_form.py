import flet as ft

# Certifique-se de que o import aponta para onde você salvou o componente FileInput
from components.file_input import FileInput, FileType


class NfseWebForm(ft.Column):
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
        self.usuario_input = ft.TextField(
            label="Usuário", hint_text="Digite o usuário", width=300
        )

        self.senha_input = ft.TextField(
            label="Senha",
            hint_text="Digite a senha",
            password=True,
            can_reveal_password=True,
            width=300,
        )

        # CNPJs - seletor de arquivo .txt
        self.cnpjs_file_input = FileInput(
            self._page, label="Arquivo de CNPJs (.txt)", icon=ft.Icons.TEXT_SNIPPET
        )
        self.cnpjs_file_input.width = 300

        # Datas
        self.data_inicial_input = ft.TextField(
            label="Data Inicial",
            hint_text="dd/mm/aaaa",
            width=300,
            suffix_icon=ft.Icons.CALENDAR_TODAY,
        )

        self.data_final_input = ft.TextField(
            label="Data Final",
            hint_text="dd/mm/aaaa",
            width=300,
            suffix_icon=ft.Icons.CALENDAR_TODAY,
        )

        # Download path - seletor de pasta
        self.download_folder_input = FileInput(
            self._page,
            label="Pasta de Download",
            icon=ft.Icons.FOLDER_OPEN,
            file_type=FileType.FOLDER,
        )
        self.download_folder_input.width = 300

        # --- Layout (Grid) ---
        # Linha 1: Usuário | Senha | Arquivo CNPJs
        row1 = ft.Row(
            [self.usuario_input, self.senha_input, self.cnpjs_file_input],
            alignment=ft.MainAxisAlignment.CENTER,
            spacing=20,
        )

        # Linha 2: Data Inicial | Data Final | Pasta Download
        row2 = ft.Row(
            [
                self.data_inicial_input,
                self.data_final_input,
                self.download_folder_input,
            ],
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
            "usuario": self.usuario_input.value,
            "senha": self.senha_input.value,
            "cnpjs_file": self.cnpjs_file_input.value,
            "data_inicial": self.data_inicial_input.value,
            "data_final": self.data_final_input.value,
            "download_path": self.download_folder_input.value,
        }
