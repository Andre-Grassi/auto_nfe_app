import flet as ft
import re

try:
    import tomllib
except ImportError:
    import tomli as tomllib

from components.file_input import FileInput, FileType
from components.toml_editor_dialog import (
    TomlEditorDialog,
    TableConfig,
    FieldConfig,
)
from config.paths import EMPRESAS_NFE_PATH


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

        # --- Perfis ---
        # Editor de perfis NFe (empresas_nfe.toml)
        self.profile_editor = TomlEditorDialog(
            page=self._page,
            file_path=EMPRESAS_NFE_PATH,
            title="Editar Perfis NFe",
            config=[
                TableConfig(
                    key="empresas",
                    label="Perfis de Empresa",
                    columns_per_row=3,  # Divide em 2 linhas visuais
                    columns=[
                        FieldConfig(key="nome", label="Nome", expand=True),
                        FieldConfig(key="cnpj_cpf", label="CNPJ/CPF", width=150),
                        FieldConfig(key="caminho_certificado", label="Certificado", file_picker=True),
                        FieldConfig(key="senha", label="Senha", password=True, width=120),
                        FieldConfig(key="caminho_relacao", label="Planilha", file_picker=True),
                        FieldConfig(key="pasta_xml", label="Pasta XML", folder_picker=True),
                    ],
                ),
            ],
        )

        # Botão Carregar Perfil (abre seletor)
        btn_load_profile = ft.Button(
            content=ft.Row(
                [ft.Icon(ft.Icons.DOWNLOAD), ft.Text("Carregar Perfil")],
                spacing=5,
            ),
            on_click=self._show_profile_selector,
        )

        # Botão Editar Perfis
        btn_edit_profiles = ft.Button(
            content=ft.Row(
                [ft.Icon(ft.Icons.EDIT), ft.Text("Editar Perfis")],
                spacing=5,
            ),
            on_click=self.profile_editor.open,
        )

        # --- Campos de Entrada Simples ---
        self.cnpj_cpf_input = ft.TextField(
            label="CNPJ/CPF", hint_text="Digite o CNPJ ou CPF", width=300
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
            self._page,
            label="Pasta para direcionar XMLs",
            icon=ft.Icons.FOLDER_OPEN,
            file_type=FileType.FOLDER,
        )
        self.folder_input.width = 300

        # --- Layout (Grid) ---
        # Linha 0: Botões de Perfil
        row0 = ft.Row(
            [btn_load_profile, btn_edit_profiles],
            alignment=ft.MainAxisAlignment.CENTER,
            spacing=20,
        )

        # Linha 1: CNPJ | Certificado | Senha
        row1 = ft.Row(
            [self.cnpj_cpf_input, self.cert_input, self.password_input],
            alignment=ft.MainAxisAlignment.CENTER,
            spacing=20,
        )

        # Linha 2: Planilha | Pasta
        row2 = ft.Row(
            [self.sheet_input, self.folder_input],
            alignment=ft.MainAxisAlignment.CENTER,
            spacing=20,
        )

        self.controls.extend([row0, row1, row2])

    def _get_profiles(self) -> list[dict]:
        """Carrega lista de perfis do arquivo TOML."""
        try:
            with open(EMPRESAS_NFE_PATH, "rb") as f:
                data = tomllib.load(f)
            return data.get("empresas", [])
        except Exception:
            return []

    def _show_profile_selector(self, e):
        """Exibe diálogo para selecionar perfil."""
        profiles = self._get_profiles()

        if not profiles:
            self._page.snack_bar = ft.SnackBar(
                ft.Text("Nenhum perfil encontrado. Clique em 'Editar Perfis' para criar.")
            )
            self._page.snack_bar.open = True
            self._page.update()
            return

        # Cria lista de opções
        options = []
        for i, profile in enumerate(profiles):
            nome = profile.get("nome", f"Perfil {i+1}")
            cnpj = profile.get("cnpj_cpf", "")
            options.append(
                ft.ListTile(
                    leading=ft.Icon(ft.Icons.BUSINESS),
                    title=ft.Text(nome),
                    subtitle=ft.Text(cnpj),
                    on_click=lambda ev, idx=i: self._load_profile(idx),
                )
            )

        # Diálogo de seleção
        dlg = ft.AlertDialog(
            title=ft.Text("Selecionar Perfil"),
            content=ft.Container(
                content=ft.Column(options, scroll=ft.ScrollMode.AUTO),
                width=400,
                height=300,
            ),
            actions=[ft.TextButton("Cancelar", on_click=lambda e: self._page.pop_dialog())],
        )
        self._page.show_dialog(dlg)

    def _load_profile(self, index: int):
        """Carrega os dados de um perfil específico nos campos."""
        self._page.pop_dialog()

        profiles = self._get_profiles()
        if 0 <= index < len(profiles):
            profile = profiles[index]

            # Preenche os campos
            self.cnpj_cpf_input.value = profile.get("cnpj_cpf", "")
            self.cert_input.value = profile.get("caminho_certificado", "")
            self.password_input.value = profile.get("senha", "")
            self.sheet_input.value = profile.get("caminho_relacao", "")
            self.folder_input.value = profile.get("pasta_xml", "")

            # Atualiza a interface
            try:
                self.cnpj_cpf_input.update()
                self.password_input.update()
                self.update()
            except RuntimeError:
                pass

    def _clean_cnpj_cpf(self, value: str) -> str:
        """Remove caracteres não numéricos do CNPJ/CPF."""
        return re.sub(r"\D", "", value or "")

    def _set_field_error(self, field: ft.TextField, has_error: bool):
        """Define a borda do campo como vermelha se houver erro."""
        if has_error:
            field.border_color = ft.Colors.RED_400
        else:
            field.border_color = None  # Volta ao padrão
        try:
            field.update()
        except RuntimeError:
            pass

    def validate_inputs(self) -> tuple[bool, str | None]:
        """
        Valida todos os campos do formulário.
        Retorna (True, None) se todos estão válidos.
        Retorna (False, mensagem_erro) caso contrário.
        Campos inválidos ficam com borda vermelha.
        """
        errors = []

        # Validação CNPJ/CPF
        cnpj_cpf_clean = self._clean_cnpj_cpf(self.cnpj_cpf_input.value)
        cnpj_cpf_valid = len(cnpj_cpf_clean) in (11, 14)  # CPF=11, CNPJ=14
        self._set_field_error(self.cnpj_cpf_input, not cnpj_cpf_valid)
        if not cnpj_cpf_valid:
            errors.append("CNPJ/CPF deve ter 11 (CPF) ou 14 (CNPJ) dígitos")

        # Validação Certificado (não vazio)
        cert_valid = bool(self.cert_input.value and self.cert_input.value.strip())
        self._set_field_error(self.cert_input.text_field, not cert_valid)
        if not cert_valid:
            errors.append("Certificado é obrigatório")

        # Validação Senha (não vazia)
        password_valid = bool(self.password_input.value and self.password_input.value.strip())
        self._set_field_error(self.password_input, not password_valid)
        if not password_valid:
            errors.append("Senha é obrigatória")

        # Validação Planilha (não vazia)
        sheet_valid = bool(self.sheet_input.value and self.sheet_input.value.strip())
        self._set_field_error(self.sheet_input.text_field, not sheet_valid)
        if not sheet_valid:
            errors.append("Planilha é obrigatória")

        # Validação Pasta (não vazia)
        folder_valid = bool(self.folder_input.value and self.folder_input.value.strip())
        self._set_field_error(self.folder_input.text_field, not folder_valid)
        if not folder_valid:
            errors.append("Pasta de destino é obrigatória")

        if errors:
            return (False, "; ".join(errors))
        return (True, None)

    def get_values(self):
        """
        Retorna os valores dos campos.
        Nota: O FileInput possui uma propriedade .value que retorna o texto interno.
        O CNPJ/CPF é retornado apenas com dígitos.
        """
        return {
            "cnpj_cpf": self._clean_cnpj_cpf(self.cnpj_cpf_input.value),
            "cert_path": self.cert_input.value,
            "password": self.password_input.value,
            "sheet_path": self.sheet_input.value,
            "folder_path": self.folder_input.value,
        }

