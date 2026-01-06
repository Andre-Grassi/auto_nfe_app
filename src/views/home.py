import flet as ft
from components.consultas.planilha_form import PlanilhaForm
from components.download_btn import DownloadBtn


class HomeView(ft.View):
    def __init__(self):
        super().__init__(route="/")

        # Título
        self.title = ft.Text("Auto Nfe", size=40, weight=ft.FontWeight.BOLD)

        # --- Elementos do Formulário de Planilha ---
        self.planilha_form = PlanilhaForm()

        # --- Elementos da Área de Ação (Botão e Progresso) ---
        self.download_btn = DownloadBtn(self.handle_download)

        self.progress_text = ft.Text("Baixando notas...", size=16, visible=False)
        self.progress_bar = ft.ProgressBar(
            width=400, value=0, visible=False, color=ft.Colors.BLUE
        )

        # Container para a Área de Ação para manter o layout
        self.action_area = ft.Column(
            [self.download_btn, self.progress_text, self.progress_bar],
            alignment=ft.MainAxisAlignment.CENTER,
            horizontal_alignment=ft.CrossAxisAlignment.CENTER,
            spacing=10,
        )

        self.controls = [
            self.title,
            self.planilha_form,
            ft.Divider(height=50, color="Transparent"),
            self.action_area,
        ]

    def handle_download(self, e):
        pass  # Implement download handling logic here
