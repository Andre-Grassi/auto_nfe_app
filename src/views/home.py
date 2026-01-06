import flet as ft
import threading
import time

from auto_nfe import ClientNfe

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

        # --- Alinhamento ---
        self.vertical_alignment = ft.MainAxisAlignment.CENTER
        self.horizontal_alignment = ft.CrossAxisAlignment.CENTER

    def update_progress_ui(self, current_step, total_steps):
        """
        Callback chamado pelo Backend para atualizar a UI.
        """
        percentage = current_step / total_steps

        # Atualiza os valores visuais
        self.progress_bar.value = percentage
        self.progress_text.value = f"Baixando XMLs: {current_step}/{total_steps}"

        # Atualiza a view
        self.update()

    def _run_background_task(self, form_data):
        """
        Lógica pesada que roda em uma Thread separada.
        """
        try:
            client = ClientNfe(
                cnpj=form_data["cnpj"],
                cert_pfx_path=form_data["cert_path"],
                cert_password=form_data["password"],
            )

            client.consulta_planilha(
                form_data["sheet_path"],
                form_data["folder_path"],
                self.update_progress_ui,
            )

            # Sucesso
            self.progress_text.value = "Download completado com sucesso!"
            self.progress_text.color = ft.Colors.GREEN
            self.progress_bar.value = 1.0

        except Exception as e:
            # Erro
            self.progress_text.value = f"Error: {str(e)}"
            self.progress_text.color = ft.Colors.RED

        finally:
            # Restaura o botão independentemente do resultado
            self.download_btn.disabled = False
            self.download_btn.content = "Baixar"
            self.update()

    def handle_download(self, e):
        """
        Evento de clique do botão. Prepara a UI e inicia a Thread.
        """
        # 1. Obtém dados do formulário (precisa implementar get_values no PlanilhaForm)
        form_data = self.planilha_form.get_values()

        # Validação simples
        if not form_data:
            self.page.snack_bar = ft.SnackBar(
                ft.Text("Por favor, preencha todos os campos!")
            )
            self.page.snack_bar.open = True
            self.page.update()
            return

        # 2. Configura UI para estado de "Carregando"
        self.download_btn.disabled = True
        self.progress_text.visible = True
        self.progress_bar.visible = True
        self.progress_text.value = "Iniciando conexão..."
        self.progress_text.color = ft.Colors.WHITE
        self.update()

        # 3. Inicia a Thread
        # Passamos form_data como argumento para a thread não acessar a UI diretamente
        t = threading.Thread(
            target=self._run_background_task, args=(form_data,), daemon=True
        )
        t.start()
