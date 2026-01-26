import os
import datetime
import flet as ft

try:
    import tomllib
except ImportError:
    import tomli as tomllib

from components.file_input import FileInput, FileType
from components.load_profile_btn import LoadProfileBtn
from components.empresas_editor_dialog import EmpresasEditorDialog
from components.toml_editor_dialog import (
    TomlEditorDialog,
    SectionConfig,
    FieldConfig,
)

from config.paths import PROFILE_PATH, EMPRESAS_NFSE_PATH


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

        # --- Credenciais ---
        self.load_profile_btn = LoadProfileBtn(self._load_profile)

        # Editor de credenciais NFSe (profile.toml seção [nfse])
        self.profile_editor = TomlEditorDialog(
            page=self._page,
            file_path=PROFILE_PATH,
            title="Editar Credenciais NFSe",
            config=[
                SectionConfig(
                    key="nfse",
                    label="Credenciais NFSe",
                    fields=[
                        FieldConfig(key="usuario", label="Usuário"),
                        FieldConfig(key="senha", label="Senha", password=True),
                        FieldConfig(key="pasta_relatorio", label="Pasta Relatório", folder_picker=True),
                    ],
                ),
            ],
        )

        btn_edit_profile = ft.Button(
            content=ft.Row(
                [ft.Icon(ft.Icons.EDIT), ft.Text("Editar Credenciais")],
                spacing=5,
            ),
            on_click=self.profile_editor.open,
        )

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

        # ====== Empresas/CNPJs Editor ======
        self.empresas_editor = EmpresasEditorDialog(
            page=self._page,
            file_path=EMPRESAS_NFSE_PATH,
            title="Gerenciar Empresas",
        )

        # Botão para abrir editor de empresas
        btn_edit_empresas = ft.Button(
            content=ft.Text("Empresas"),
            icon=ft.Icons.BUSINESS,
            on_click=self.empresas_editor.open,
            width=150,
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
            [self.load_profile_btn, btn_edit_profile],
            alignment=ft.MainAxisAlignment.CENTER,
            spacing=20,
        )

        # Linha 2: Usuário | Senha | Botão Empresas
        row2 = ft.Row(
            [self.usuario_input, self.senha_input, btn_edit_empresas],
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
        CNPJs/CPFs são obtidos do editor de empresas (apenas selecionados).
        """
        return {
            "usuario": self.usuario_input.value,
            "senha": self.senha_input.value,
            "cnpjs": self.empresas_editor.get_selected_cnpj_cpf(),
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
            self.download_folder_input.value = nfse_data.get("pasta_relatorio", "")

            # Atualiza a interface
            self.usuario_input.update()
            self.senha_input.update()
            self.download_folder_input.update()
            self.update()

            print("Perfil carregado com sucesso!")

        except FileNotFoundError:
            print(f"Arquivo profile.toml não encontrado em: {PROFILE_PATH}")
        except Exception as ex:
            print(f"Erro ao carregar perfil: {ex}")
