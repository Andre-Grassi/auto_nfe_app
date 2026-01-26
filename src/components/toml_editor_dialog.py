"""
Componente genérico de diálogo para edição de arquivos TOML.
Suporta seções com campos key-value e tabelas com linhas editáveis.
"""

from dataclasses import dataclass, field
from typing import Any
import flet as ft

from components.file_input import FileInput, FileType

try:
    import tomllib
except ImportError:
    import tomli as tomllib

try:
    import tomli_w
except ImportError:
    tomli_w = None


@dataclass
class FieldConfig:
    """Configuração de um campo editável."""

    key: str
    label: str = ""
    password: bool = False
    expand: bool = False
    width: int | None = None
    file_picker: bool = False  # Adiciona botão para selecionar arquivo
    folder_picker: bool = False  # Adiciona botão para selecionar pasta


@dataclass
class SectionConfig:
    """Configuração de uma seção TOML com campos key-value."""

    key: str
    label: str
    fields: list[FieldConfig] = field(default_factory=list)


@dataclass
class TableConfig:
    """Configuração de uma tabela TOML (array de objetos)."""

    key: str
    label: str
    columns: list[FieldConfig] = field(default_factory=list)
    checkbox: bool = False  # Exibe checkbox para seleção de linhas
    checkbox_field: str = "selecionada"  # Campo para armazenar estado do checkbox


class TomlEditorDialog:
    """
    Diálogo genérico para editar arquivos TOML.

    Suporta:
    - Seções com campos de texto (SectionConfig)
    - Tabelas com linhas editáveis (TableConfig)
    """

    def __init__(
        self,
        page: ft.Page,
        file_path: str,
        title: str = "Editar Configurações",
        config: list[SectionConfig | TableConfig] | None = None,
    ):
        """
        Args:
            page: Página do Flet para exibir o diálogo.
            file_path: Caminho para o arquivo TOML.
            title: Título do diálogo.
            config: Lista de SectionConfig/TableConfig para renderizar.
        """
        self._page = page
        self._file_path = file_path
        self._config = config or []
        self._data: dict[str, Any] = {}
        self._field_refs: dict[str, ft.TextField] = {}  # Referências para campos de seção
        self._table_lists: dict[str, ft.Column] = {}  # Referências para listas de tabela

        # Container principal do conteúdo
        self._content = ft.Column(
            spacing=20,
            scroll=ft.ScrollMode.AUTO,
            expand=True,
        )

        # Dialog
        self._dialog = ft.AlertDialog(
            modal=True,
            title=ft.Text(title, size=18, weight=ft.FontWeight.W_500),
            content=ft.Container(
                content=self._content,
                width=650,
                height=450,
            ),
            actions=[
                ft.Row(
                    [
                        ft.Container(expand=True),
                        ft.TextButton("Cancelar", on_click=self._close),
                        ft.TextButton("Salvar", on_click=self._save),
                    ],
                    expand=True,
                ),
            ],
        )

    @property
    def dialog(self) -> ft.AlertDialog:
        """Retorna o AlertDialog."""
        return self._dialog

    def open(self, e=None):
        """Abre o diálogo e carrega dados do TOML."""
        self._load_data()
        self._build_content()
        self._page.show_dialog(self._dialog)

    def get_data(self) -> dict[str, Any]:
        """Retorna os dados atuais do TOML."""
        self._load_data()
        return self._data

    def _load_data(self):
        """Carrega dados do arquivo TOML."""
        try:
            with open(self._file_path, "rb") as f:
                self._data = tomllib.load(f)
        except FileNotFoundError:
            self._data = {}
        except Exception as ex:
            print(f"Erro ao ler {self._file_path}: {ex}")
            self._data = {}

    def _save(self, e):
        """Salva dados no arquivo TOML."""
        if tomli_w is None:
            print("Erro: tomli_w não instalado. Execute: pip install tomli-w")
            self._page.pop_dialog()
            return

        # Atualiza dados das seções
        for cfg in self._config:
            if isinstance(cfg, SectionConfig):
                if cfg.key not in self._data:
                    self._data[cfg.key] = {}
                for field_cfg in cfg.fields:
                    ref_key = f"{cfg.key}.{field_cfg.key}"
                    if ref_key in self._field_refs:
                        self._data[cfg.key][field_cfg.key] = self._field_refs[ref_key].value

        try:
            with open(self._file_path, "wb") as f:
                tomli_w.dump(self._data, f)
            print(f"Dados salvos em: {self._file_path}")
        except Exception as ex:
            print(f"Erro ao salvar: {ex}")

        self._page.pop_dialog()

    def _close(self, e):
        """Fecha o diálogo sem salvar."""
        self._page.pop_dialog()

    def _build_content(self):
        """Constrói o conteúdo do diálogo baseado na configuração."""
        self._content.controls.clear()
        self._field_refs.clear()
        self._table_lists.clear()

        for cfg in self._config:
            if isinstance(cfg, SectionConfig):
                self._content.controls.append(self._build_section(cfg))
            elif isinstance(cfg, TableConfig):
                self._content.controls.append(self._build_table(cfg))

    def _build_section(self, cfg: SectionConfig) -> ft.Control:
        """Constrói uma seção com campos key-value."""
        section_data = self._data.get(cfg.key, {})

        fields_column = ft.Column(spacing=10)

        for field_cfg in cfg.fields:
            ref_key = f"{cfg.key}.{field_cfg.key}"

            # Se tem file_picker ou folder_picker, usa FileInput
            if field_cfg.file_picker or field_cfg.folder_picker:
                file_type = FileType.FOLDER if field_cfg.folder_picker else FileType.FILE
                file_input = FileInput(
                    page=self._page,
                    label=field_cfg.label or field_cfg.key,
                    file_type=file_type,
                )
                fields_column.controls.append(file_input)
                file_input.value = str(section_data.get(field_cfg.key, ""))
                self._field_refs[ref_key] = file_input.text_field
            else:
                text_field = ft.TextField(
                    label=field_cfg.label or field_cfg.key,
                    value=str(section_data.get(field_cfg.key, "")),
                    password=field_cfg.password,
                    can_reveal_password=field_cfg.password,
                    expand=field_cfg.expand,
                    width=field_cfg.width,
                )
                self._field_refs[ref_key] = text_field
                fields_column.controls.append(text_field)

        return ft.Container(
            content=ft.Column(
                [
                    ft.Text(cfg.label, size=16, weight=ft.FontWeight.W_500),
                    fields_column,
                ],
                spacing=10,
            ),
            padding=10,
            border=ft.border.all(1, ft.Colors.OUTLINE),
            border_radius=8,
        )

    def _build_table(self, cfg: TableConfig) -> ft.Control:
        """Constrói uma tabela com linhas editáveis."""
        table_data = self._data.get(cfg.key, [])
        if not isinstance(table_data, list):
            table_data = []
            self._data[cfg.key] = table_data

        # Lista de linhas
        list_column = ft.Column(
            spacing=2,
            scroll=ft.ScrollMode.AUTO,
            expand=True,
        )
        self._table_lists[cfg.key] = list_column

        # Popula linhas
        self._refresh_table(cfg)

        # Botão adicionar
        btn_add = ft.TextButton(
            content=ft.Text("+ Adicionar"),
            on_click=lambda e, c=cfg: self._add_table_row(c),
        )

        return ft.Container(
            content=ft.Column(
                [
                    ft.Row(
                        [
                            ft.Text(cfg.label, size=16, weight=ft.FontWeight.W_500),
                            ft.Container(expand=True),
                            btn_add,
                        ],
                    ),
                    list_column,
                ],
                spacing=10,
                expand=True,
            ),
            padding=10,
            border=ft.border.all(1, ft.Colors.OUTLINE),
            border_radius=8,
            expand=True,
        )

    def _refresh_table(self, cfg: TableConfig):
        """Recria as linhas da tabela."""
        list_column = self._table_lists.get(cfg.key)
        if not list_column:
            return

        list_column.controls.clear()
        table_data = self._data.get(cfg.key, [])

        for i, row_data in enumerate(table_data):
            row = self._create_table_row(cfg, i, row_data)
            list_column.controls.append(row)

        try:
            list_column.update()
        except RuntimeError:
            pass

    def _create_table_row(self, cfg: TableConfig, index: int, row_data: dict) -> ft.Control:
        """Cria uma linha da tabela."""
        controls = []

        # Checkbox (se configurado)
        if cfg.checkbox:
            checkbox = ft.Checkbox(
                value=row_data.get(cfg.checkbox_field, False),
                on_change=lambda e, idx=index, c=cfg: self._update_table_field(
                    c.key, idx, c.checkbox_field, e.control.value
                ),
            )
            controls.append(checkbox)

        # Campos
        for field_cfg in cfg.columns:
            text_field = ft.TextField(
                value=str(row_data.get(field_cfg.key, "")),
                hint_text=field_cfg.label,
                expand=field_cfg.expand,
                width=field_cfg.width,
                border_color=ft.Colors.TRANSPARENT,
                on_change=lambda e, idx=index, c=cfg, f=field_cfg: self._update_table_field(
                    c.key, idx, f.key, e.control.value
                ),
            )
            controls.append(text_field)

        # Botão deletar
        delete_btn = ft.IconButton(
            icon=ft.Icons.DELETE_OUTLINE,
            icon_color=ft.Colors.RED_400,
            tooltip="Remover",
            on_click=lambda e, idx=index, c=cfg: self._remove_table_row(c, idx),
        )
        controls.append(delete_btn)

        return ft.Container(
            content=ft.Row(
                controls,
                spacing=10,
                vertical_alignment=ft.CrossAxisAlignment.CENTER,
            ),
            bgcolor=ft.Colors.SURFACE_CONTAINER_HIGH,
            border_radius=8,
            padding=ft.Padding(left=10, right=10, top=5, bottom=5),
        )

    def _update_table_field(self, table_key: str, index: int, field: str, value: Any):
        """Atualiza um campo de uma linha da tabela."""
        table_data = self._data.get(table_key, [])
        if 0 <= index < len(table_data):
            table_data[index][field] = value

    def _add_table_row(self, cfg: TableConfig):
        """Adiciona nova linha à tabela."""
        table_data = self._data.get(cfg.key, [])
        if not isinstance(table_data, list):
            table_data = []
            self._data[cfg.key] = table_data

        new_row = {}
        if cfg.checkbox:
            new_row[cfg.checkbox_field] = True
        for field_cfg in cfg.columns:
            new_row[field_cfg.key] = ""

        table_data.append(new_row)
        self._refresh_table(cfg)

    def _remove_table_row(self, cfg: TableConfig, index: int):
        """Remove uma linha da tabela."""
        table_data = self._data.get(cfg.key, [])
        if 0 <= index < len(table_data):
            table_data.pop(index)
            self._refresh_table(cfg)
