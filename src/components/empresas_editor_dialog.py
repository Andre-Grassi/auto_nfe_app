"""
Componente de diálogo para edição de lista de empresas armazenada em TOML.
"""

import flet as ft

try:
    import tomllib
except ImportError:
    import tomli as tomllib

try:
    import tomli_w
except ImportError:
    tomli_w = None


class EmpresasEditorDialog:
    """
    Diálogo para gerenciar lista de empresas com CNPJ/CPF.

    Cada empresa possui: nome, cnpj_cpf, selecionada (bool).
    Dados são persistidos em arquivo TOML.
    """

    def __init__(
        self,
        page: ft.Page,
        file_path: str,
        title: str = "Gerenciar Empresas",
        root_key: str = "empresas",
    ):
        """
        Args:
            page: Página do Flet para exibir o diálogo.
            file_path: Caminho para o arquivo TOML.
            title: Título do diálogo.
            root_key: Chave raiz no TOML (padrão: "empresas").
        """
        self._page = page
        self._file_path = file_path
        self._root_key = root_key
        self._data: list[dict] = []

        # Container para os rows da lista de empresas
        self._list = ft.Column(
            spacing=2,
            scroll=ft.ScrollMode.AUTO,
        )

        # Botão para adicionar nova empresa
        btn_add = ft.TextButton(
            content=ft.Text("+ Adicionar Empresa"),
            on_click=self._add_row,
        )

        # Dialog
        self._dialog = ft.AlertDialog(
            modal=True,
            title=ft.Text(title, size=18, weight=ft.FontWeight.W_500),
            content=ft.Container(
                content=ft.Column([self._list, btn_add]),
                width=600,
                height=400,
            ),
            actions=[
                ft.TextButton("Cancelar", on_click=self._close),
                ft.TextButton("Salvar", on_click=self._save),
            ],
            actions_alignment=ft.MainAxisAlignment.END,
        )

    @property
    def dialog(self) -> ft.AlertDialog:
        """Retorna o AlertDialog para uso externo se necessário."""
        return self._dialog

    def open(self, e=None):
        """Abre o diálogo e carrega dados do TOML."""
        self._load_data()
        self._refresh_list()
        self._page.show_dialog(self._dialog)

    def get_selected_cnpj_cpf(self) -> list[str]:
        """Retorna lista de CNPJ/CPF onde selecionada=True."""
        self._load_data()
        return [
            emp.get("cnpj_cpf", "")
            for emp in self._data
            if emp.get("selecionada", False)
        ]

    def _load_data(self):
        """Carrega dados do arquivo TOML."""
        try:
            with open(self._file_path, "rb") as f:
                data = tomllib.load(f)
            self._data = data.get(self._root_key, [])
        except FileNotFoundError:
            self._data = []
        except Exception as ex:
            print(f"Erro ao ler {self._file_path}: {ex}")
            self._data = []

    def _save(self, e):
        """Salva dados no arquivo TOML."""
        if tomli_w is None:
            print("Erro: tomli_w não está instalado. Execute: pip install tomli-w")
            self._page.pop_dialog()
            return

        try:
            with open(self._file_path, "wb") as f:
                tomli_w.dump({self._root_key: self._data}, f)
            print(f"Dados salvos em: {self._file_path}")
        except Exception as ex:
            print(f"Erro ao salvar {self._file_path}: {ex}")

        self._page.pop_dialog()

    def _close(self, e):
        """Fecha o diálogo sem salvar."""
        self._page.pop_dialog()

    def _add_row(self, e):
        """Adiciona uma nova empresa vazia à lista."""
        self._data.append({"nome": "", "cnpj_cpf": "", "selecionada": True})
        self._refresh_list()

    def _remove_row(self, index: int):
        """Remove uma empresa da lista."""
        if 0 <= index < len(self._data):
            self._data.pop(index)
            self._refresh_list()

    def _update_field(self, index: int, field: str, value):
        """Atualiza um campo da empresa na memória."""
        if 0 <= index < len(self._data):
            self._data[index][field] = value

    def _refresh_list(self):
        """Recria a lista de empresas no editor."""
        self._list.controls.clear()
        for i, emp in enumerate(self._data):
            row = self._create_row(
                i,
                emp.get("nome", ""),
                emp.get("cnpj_cpf", ""),
                emp.get("selecionada", False),
            )
            self._list.controls.append(row)

        # Só chama update se já estiver na página
        try:
            self._list.update()
        except RuntimeError:
            pass  # Controle ainda não adicionado à página

    def _create_row(self, index: int, nome: str, cnpj_cpf: str, selecionada: bool):
        """Cria uma linha de empresa para o editor."""
        checkbox = ft.Checkbox(
            value=selecionada,
            on_change=lambda e, idx=index: self._update_field(
                idx, "selecionada", e.control.value
            ),
        )

        nome_field = ft.TextField(
            value=nome,
            hint_text="Nome da empresa",
            expand=True,
            border_color=ft.Colors.TRANSPARENT,
            on_change=lambda e, idx=index: self._update_field(
                idx, "nome", e.control.value
            ),
        )

        cnpj_cpf_field = ft.TextField(
            value=cnpj_cpf,
            hint_text="CNPJ/CPF",
            width=160,
            border_color=ft.Colors.TRANSPARENT,
            on_change=lambda e, idx=index: self._update_field(
                idx, "cnpj_cpf", e.control.value
            ),
        )

        delete_btn = ft.IconButton(
            icon=ft.Icons.DELETE_OUTLINE,
            icon_color=ft.Colors.RED_400,
            tooltip="Remover empresa",
            on_click=lambda e, idx=index: self._remove_row(idx),
        )

        return ft.Container(
            content=ft.Row(
                [checkbox, nome_field, cnpj_cpf_field, delete_btn],
                spacing=10,
                vertical_alignment=ft.CrossAxisAlignment.CENTER,
            ),
            bgcolor=ft.Colors.SURFACE_CONTAINER_HIGH,
            border_radius=8,
            padding=ft.Padding(left=10, right=10, top=5, bottom=5),
        )
