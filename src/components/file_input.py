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
        icon: ft.Icons = ft.Icons.FOLDER_OPEN,
    ):
        """
        Componente que junta um Input de Texto com um Seletor de Arquivos nativo.
        """
        super().__init__()
        self.file_type = file_type
        self._page = page
        self.vertical_alignment = ft.CrossAxisAlignment.CENTER
        self.spacing = 10

        # 2. O Campo de Texto (Visível)
        self.text_field = ft.TextField(
            label=label,
            expand=True,  # Ocupa o espaço disponível
            read_only=False,  # O usuário ainda pode digitar se quiser
        )

        # 3. O Botão que abre a janela
        self.pick_button = ft.IconButton(
            icon=icon,
            tooltip="Selecionar Arquivo",
            on_click=self._open_picker_dialog,
        )

        # Adiciona na linha (Row)
        self.controls = [self.text_field, self.pick_button]

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
            # Pega o caminho do primeiro arquivo
            file_path = files[0].path

            if not file_path:
                return

            # Preenche o input visualmente
            self.text_field.value = file_path
            self.text_field.update()

    def _on_folder_picked(self, folder_path: str | None):
        """
        Chamado quando o usuário escolhe uma pasta na janela.
        """
        if folder_path:
            # Preenche o input visualmente
            self.text_field.value = folder_path
            self.text_field.update()

    @property
    def value(self):
        """Atalho para pegar o valor do texto de fora"""
        return self.text_field.value

    @value.setter
    def value(self, new_value: str):
        """Atalho para settar o valor do texto de fora"""
        self.text_field.value = new_value
        self.text_field.update()
