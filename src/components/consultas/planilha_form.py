import flet as ft
import re

# Certifique-se de que o import aponta para onde você salvou o componente FileInput
from components.file_input import FileInput, FileType


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

        self.controls.extend([row1, row2])

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

