import flet as ft


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
        self.file_picker = ft.FilePicker(on_upload=self._on_file_picked)
        # OBRIGATÓRIO: O FilePicker deve estar no overlay da página para funcionar
        self._page.overlay.append(self.file_picker)

        # 2. O Campo de Texto (Visível)
        self.text_field = ft.TextField(
            label=label,
            expand=True,  # Ocupa o espaço disponível
            read_only=False,  # O usuário ainda pode digitar se quiser
        )

        # 3. O Botão que abre a janela
        self.pick_button = ft.IconButton(
            icon=icon,
            tooltip="Selecionar Arquivo",  # UI em Português
            on_click=self._open_picker_dialog,
        )

        # Adiciona na linha (Row)
        self.controls = [self.text_field, self.pick_button]

    async def _open_picker_dialog(self, _):
        """
        Abre a janela nativa de seleção de arquivos.
        """
        await self.file_picker.pick_files(allow_multiple=False)

    def _on_file_picked(self, e: ft.FilePickerUploadEvent):
        """
        Chamado quando o usuário escolhe um arquivo na janela.
        """
        if e.data and len(e.data) > 0:
            # Pega o caminho do primeiro arquivo
            file_path = e.data[0].path

            # Preenche o input visualmente
            self.text_field.value = file_path
            self.text_field.update()

    @property
    def value(self):
        """Atalho para pegar o valor do texto de fora"""
        return self.text_field.value
