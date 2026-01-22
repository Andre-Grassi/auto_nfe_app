import os
import datetime
import flet as ft

try:
    import tomllib
except ImportError:
    # Fall back to tomli for Python versions < 3.11
    import tomli as tomllib

# Certifique-se de que o import aponta para onde você salvou o componente FileInput
from components.file_input import FileInput, FileType
from components.load_profile_btn import LoadProfileBtn

from utils.utils import get_file_path

from constants import PROFILE_PATH


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

        self.load_profile_btn = LoadProfileBtn(self._load_profile)

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

        # CNPJs - seletor de arquivo .txt + botão de edição
        self.cnpjs_file_input = FileInput(
            self._page, label="Arquivo de CNPJs (.txt)", icon=ft.Icons.TEXT_SNIPPET
        )
        self.cnpjs_file_input.expand = True  # Expande dentro do Row container

        # Editor de CNPJs - Dialog
        self.cnpjs_editor_field = ft.TextField(
            label="CNPJs (um por linha)",
            multiline=True,
            min_lines=10,
            max_lines=15,
            expand=True,
        )

        self.cnpjs_editor_dialog = ft.AlertDialog(
            modal=True,
            title=ft.Text("Editar Lista de CNPJs"),
            content=ft.Container(
                content=self.cnpjs_editor_field,
                width=400,
                height=300,
            ),
            actions=[
                ft.TextButton("Cancelar", on_click=self._close_cnpjs_editor),
                ft.TextButton("Salvar", on_click=self._save_cnpjs),
            ],
            actions_alignment=ft.MainAxisAlignment.END,
        )

        btn_edit_cnpjs = ft.IconButton(
            icon=ft.Icons.EDIT,
            on_click=self._open_cnpjs_editor,
            tooltip="Editar lista de CNPJs",
        )

        # Container Row para CNPJs (FileInput + botão editar)
        self.container_cnpjs = ft.Row(
            [self.cnpjs_file_input, btn_edit_cnpjs],
            width=350,
            spacing=5,
            vertical_alignment=ft.CrossAxisAlignment.CENTER,
        )

        # Datas
        # Funçāo auxiliar para atualizar o campo de texto ao selecionar data
        def on_date_change(e, text_field):
            if e.control.value:
                text_field.value = e.control.value.strftime("%d/%m/%Y")
                text_field.update()

        # 1. DatePicker Data Inicial
        # Definindo datas limites entre 1980 e 2100 para evitar erro de astimezone no Windows
        self.date_picker_inicial = ft.DatePicker(
            on_change=lambda e: on_date_change(e, self.data_inicial_input),
            first_date=datetime.datetime(1980, 1, 1),
            last_date=datetime.datetime(2100, 12, 31),
        )

        # 2. DatePicker Data Final
        self.date_picker_final = ft.DatePicker(
            on_change=lambda e: on_date_change(e, self.data_final_input),
            first_date=datetime.datetime(1980, 1, 1),
            last_date=datetime.datetime(2100, 12, 31),
        )

        # 3. Campos de Texto + Botões
        self.data_inicial_input = ft.TextField(
            label="Data Inicial",
            hint_text="dd/mm/aaaa",
            expand=True,
        )
        btn_data_inicial = ft.IconButton(
            icon=ft.Icons.CALENDAR_MONTH,
            on_click=lambda _: self._page.show_dialog(self.date_picker_inicial),
            tooltip="Selecionar Data Inicial",
        )

        # Container Row para Data Inicial (simulando o FileInput)
        self.container_data_inicial = ft.Row(
            [self.data_inicial_input, btn_data_inicial],
            width=300,
            spacing=10,
            vertical_alignment=ft.CrossAxisAlignment.CENTER,
        )

        self.data_final_input = ft.TextField(
            label="Data Final",
            hint_text="dd/mm/aaaa",
            expand=True,
        )
        btn_data_final = ft.IconButton(
            icon=ft.Icons.CALENDAR_MONTH,
            on_click=lambda _: self._page.show_dialog(self.date_picker_final),
            tooltip="Selecionar Data Final",
        )

        # Container Row para Data Final
        self.container_data_final = ft.Row(
            [self.data_final_input, btn_data_final],
            width=300,
            spacing=10,
            vertical_alignment=ft.CrossAxisAlignment.CENTER,
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
        row1 = ft.Row(
            [self.load_profile_btn],
            alignment=ft.MainAxisAlignment.CENTER,
            spacing=20,
        )

        # Linha 2: Usuário | Senha | Arquivo CNPJs
        row2 = ft.Row(
            [self.usuario_input, self.senha_input, self.container_cnpjs],
            alignment=ft.MainAxisAlignment.CENTER,
            spacing=20,
        )

        # Linha 3: Data Inicial | Data Final | Pasta Download
        row3 = ft.Row(
            [
                self.container_data_inicial,
                self.container_data_final,
                self.download_folder_input,
            ],
            alignment=ft.MainAxisAlignment.CENTER,
            spacing=20,
        )

        self.controls.extend([row1, row2, row3])

    def get_values(self):
        """
        Retorna os valores dos campos.
        Nota: O FileInput possui uma propriedade .value que retorna o texto interno.
        """

        # Carregar lista de cnpjs
        cnpjs_txt = get_file_path(self.cnpjs_file_input.value)
        with open(cnpjs_txt, "r") as f:
            cnpjs = [line.strip() for line in f if line.strip()]

        return {
            "usuario": self.usuario_input.value,
            "senha": self.senha_input.value,
            "cnpjs": cnpjs,
            "data_inicial": self.data_inicial_input.value,
            "data_final": self.data_final_input.value,
            "download_path": self.download_folder_input.value,
        }

    def _load_profile(self, e):
        """Carrega o perfil de credenciais do arquivo profile.toml"""
        try:
            # Lê o arquivo TOML
            with open(PROFILE_PATH, "rb") as f:
                profile_data = tomllib.load(f)

            # Obtém os dados da seção [nfse]
            nfse_data = profile_data.get("nfse", {})

            # Preenche os campos do formulário
            self.usuario_input.value = nfse_data.get("usuario", "")
            self.senha_input.value = nfse_data.get("senha", "")
            self.cnpjs_file_input.value = nfse_data.get("caminho_cnpjs", "")
            self.download_folder_input.value = nfse_data.get("pasta_relatorio", "")

            # Atualiza a interface
            self.usuario_input.update()
            self.senha_input.update()
            self.cnpjs_file_input.update()
            self.download_folder_input.update()
            self.update()

            print("Perfil carregado com sucesso!")

        except FileNotFoundError:
            print(f"Arquivo profile.toml não encontrado em: {PROFILE_PATH}")
        except Exception as ex:
            print(f"Erro ao carregar perfil: {ex}")

    def _open_cnpjs_editor(self, e):
        """Abre o editor de CNPJs e carrega o conteúdo do arquivo."""
        file_path = self.cnpjs_file_input.value
        if file_path:
            try:
                resolved_path = get_file_path(file_path)
                with open(resolved_path, "r", encoding="utf-8") as f:
                    self.cnpjs_editor_field.value = f.read()
            except FileNotFoundError:
                self.cnpjs_editor_field.value = ""
            except Exception as ex:
                print(f"Erro ao ler arquivo de CNPJs: {ex}")
                self.cnpjs_editor_field.value = ""
        else:
            self.cnpjs_editor_field.value = ""

        self._page.show_dialog(self.cnpjs_editor_dialog)

    def _close_cnpjs_editor(self, e):
        """Fecha o editor de CNPJs sem salvar."""
        self._page.pop_dialog()

    def _save_cnpjs(self, e):
        """Salva o conteúdo editado no arquivo de CNPJs."""
        file_path = self.cnpjs_file_input.value
        if file_path:
            try:
                resolved_path = get_file_path(file_path)
                with open(resolved_path, "w", encoding="utf-8") as f:
                    f.write(self.cnpjs_editor_field.value)
                print(f"CNPJs salvos em: {resolved_path}")
            except Exception as ex:
                print(f"Erro ao salvar arquivo de CNPJs: {ex}")
        self._page.pop_dialog()
