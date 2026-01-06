import flet as ft
from typing import List


class FileInput(ft.Row):
    def __init__(
        self, page: ft.Page, label: str, icon: ft.Icons = ft.Icons.FOLDER_OPEN
    ):
        """
        Componente que junta um Input de Texto com um Seletor de Arquivos nativo.
        """
        super().__init__()
        self._page = page
        self.vertical_alignment = ft.CrossAxisAlignment.CENTER
        self.spacing = 10

        # 1. Configura o FilePicker (o diálogo do sistema)
        self.file_picker = ft.FilePicker()
        # OBRIGATÓRIO: O FilePicker deve estar no overlay da página para funcionar
        # self._page.overlay.append(self.file_picker)

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
        files = await self.file_picker.pick_files(allow_multiple=False)
        self._on_file_picked(files)

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

    @property
    def value(self):
        """Atalho para pegar o valor do texto de fora"""
        return self.text_field.value
