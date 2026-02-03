import flet as ft
from typing import List
from enum import Enum


class FileType(Enum):
    FILE = "file"
    FOLDER = "folder"


class FileInput(ft.Row):
    def __init__(
        self,
        page: ft.Page,
        label: str,
        file_type: FileType = FileType.FILE,
        icon: str | None = None,
        text_input: bool = True,
    ):
        """
        Componente que junta um Input de Texto com um Seletor de Arquivos nativo.

        Args:
            page: Página do Flet.
            label: Label do campo.
            file_type: Tipo de seleção (FILE ou FOLDER).
            icon: Ícone personalizado. Se None, usa ícone padrão baseado em file_type.
            text_input: Se True, mostra campo de texto + botão de ícone.
                       Se False, mostra apenas um botão com label e ícone.
        """
        super().__init__()
        self.file_type = file_type
        self._page = page
        self._label = label
        self._text_input = text_input
        self._value: str = ""
        self.vertical_alignment = ft.CrossAxisAlignment.CENTER
        self.spacing = 10

        # Define ícone dinamicamente se não foi passado
        if icon is None:
            icon = (
                ft.Icons.DESCRIPTION
                if file_type == FileType.FILE
                else ft.Icons.FOLDER_OPEN
            )
        self._icon = icon

        if text_input:
            # Modo com campo de texto + botão de ícone
            self.text_field = ft.TextField(
                label=label,
                expand=True,
                read_only=False,
            )

            self.pick_button = ft.IconButton(
                icon=icon,
                tooltip="Selecionar Arquivo",
                on_click=self._open_picker_dialog,
            )

            self.controls = [self.text_field, self.pick_button]
        else:
            # Modo apenas botão com label + ícone dentro
            self.text_field = None  # Não tem campo de texto neste modo

            self.pick_button = ft.Button(
                content=ft.Row(
                    [
                        ft.Text(label, expand=True),
                        ft.Icon(icon),
                    ],
                    alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                    vertical_alignment=ft.CrossAxisAlignment.CENTER,
                ),
                on_click=self._open_picker_dialog,
                style=ft.ButtonStyle(
                    shape=ft.RoundedRectangleBorder(radius=8),
                    padding=ft.padding.symmetric(horizontal=15, vertical=12),
                ),
            )

            self.controls = [self.pick_button]

    async def _open_picker_dialog(self, _):
        """
        Abre a janela nativa de seleção de arquivos.
        """
        file_picker = ft.FilePicker()

        if self.file_type == FileType.FILE:
            files = await file_picker.pick_files(allow_multiple=False)
            self._on_file_picked(files)
        elif self.file_type == FileType.FOLDER:
            folder_path = await file_picker.get_directory_path()
            self._on_folder_picked(folder_path)
        else:
            raise ValueError("Tipo de arquivo desconhecido para FileInput")

    def _on_file_picked(self, files: List[ft.FilePickerFile]):
        """
        Chamado quando o usuário escolhe um arquivo na janela.
        """
        if files and len(files) > 0:
            file_path = files[0].path

            if not file_path:
                return

            self._set_value(file_path)

    def _on_folder_picked(self, folder_path: str | None):
        """
        Chamado quando o usuário escolhe uma pasta na janela.
        """
        if folder_path:
            self._set_value(folder_path)

    def _set_value(self, new_value: str):
        """Define o valor internamente e atualiza a UI."""
        self._value = new_value

        if self._text_input and self.text_field:
            # Modo texto: atualiza o campo de texto
            self.text_field.value = new_value
            self.text_field.update()
        else:
            # Modo botão: atualiza o texto dentro do botão
            self.pick_button.content = ft.Row(
                [
                    ft.Text(new_value if new_value else self._label, expand=True),
                    ft.Icon(self._icon),
                ],
                alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                vertical_alignment=ft.CrossAxisAlignment.CENTER,
            )
            self.pick_button.update()

    @property
    def value(self):
        """Atalho para pegar o valor do texto de fora"""
        if self._text_input and self.text_field:
            return self.text_field.value
        return self._value

    @value.setter
    def value(self, new_value: str):
        """Atalho para settar o valor do texto de fora"""
        try:
            self._set_value(new_value)
        except RuntimeError:
            # Warn
            print("FileInput: Adicione o controle à pagina antes de settar o value")
