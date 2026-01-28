import flet as ft
import threading
import asyncio
from datetime import date, datetime

from auto_nfe import ClientNfseWeb, CancelledException

from components.consultas.nfse_web_form import NfseWebForm
from components.download_btn import DownloadBtn
from config.paths import CHROME_PROFILE_PATH


class NfseView(ft.View):

    def __init__(self, page: ft.Page):
        super().__init__(
            route="/nfse",
            appbar=ft.AppBar(
                title=ft.Text("Consultar NFS-e"),
                leading=ft.IconButton(
                    icon=ft.Icons.ARROW_BACK,
                    on_click=lambda e: asyncio.create_task(self.go_back(e, page)),
                ),
            ),
        )

        # Título
        self.title = ft.Text("Auto Nfe", size=40, weight=ft.FontWeight.BOLD)

        # --- Elementos do Formulário de Planilha ---
        self.nfse_web_form = NfseWebForm(page)

        # --- Elementos da Área de Ação (Botão e Progresso) ---
        self.download_btn = DownloadBtn(self.handle_download)

        # Botão Cancelar (mesmo estilo do DownloadBtn, mas vermelho)
        self.cancel_btn = ft.Button(
            content=ft.Text("Cancelar"),
            on_click=self.handle_cancel,
            style=ft.ButtonStyle(
                shape=ft.RoundedRectangleBorder(radius=20),
                padding=ft.padding.symmetric(horizontal=30, vertical=15),
                bgcolor=ft.Colors.RED_700,
            ),
            icon=ft.Icons.CANCEL,
            visible=False,  # Escondido por padrão
        )

        self.progress_text = ft.Text("Baixando notas...", size=16, visible=False)
        self.progress_bar = ft.ProgressBar(
            width=400, value=0, visible=False, color=ft.Colors.BLUE
        )

        # Container para a Área de Ação para manter o layout
        self.action_area = ft.Column(
            [self.download_btn, self.cancel_btn, self.progress_text, self.progress_bar],
            alignment=ft.MainAxisAlignment.CENTER,
            horizontal_alignment=ft.CrossAxisAlignment.CENTER,
            spacing=10,
        )

        self.dlg_nfse_status = ft.AlertDialog(
            title=ft.Text("Status do Download do NFSe"), content=ft.Text("Alerta: ")
        )

        self.controls = [
            self.title,
            self.nfse_web_form,
            ft.Divider(height=50, color="Transparent"),
            self.action_area,
        ]

        # --- Alinhamento ---
        self.vertical_alignment = ft.MainAxisAlignment.CENTER
        self.horizontal_alignment = ft.CrossAxisAlignment.CENTER

        # --- Estado interno ---
        self._client: ClientNfseWeb | None = None
        self._cancel_event: threading.Event | None = None

    async def update_progress_ui(self, current_step, total_steps):
        """
        Callback chamado pelo Backend para atualizar a UI.
        """
        percentage = current_step / total_steps
        print(f"Progresso: {percentage*100:.2f}%")

        # Atualiza os valores visuais
        self.progress_bar.value = percentage
        self.progress_text.value = f"Baixando Relatórios: {current_step}/{total_steps}"

        # Atualiza a view
        self.progress_bar.update()
        self.progress_text.update()
        self.page.update()
        self.update()

    async def _run_background_task(self):
        """
        Lógica pesada que roda em uma Thread separada.
        """

        form_data = self.form_data
        self._cancel_event = threading.Event()

        def task_progress(current, total):

            async def run():
                await self.update_progress_ui(current, total)

            self.page.run_task(run)

        def task_notification(message: str):

            async def run():
                self.dlg_nfse_status.content = ft.Text(message)
                self.page.show_dialog(self.dlg_nfse_status)
                self.page.update()
                await asyncio.sleep(2)
                self.page.pop_dialog()
                self.page.update()

            self.page.run_task(run)

        try:
            data_inicial = datetime.strptime(
                form_data["data_inicial"], "%d/%m/%Y"
            ).date()
            data_final = datetime.strptime(form_data["data_final"], "%d/%m/%Y").date()

            self._client = ClientNfseWeb(
                usuario=form_data["usuario"],
                senha=form_data["senha"],
                cnpjs=form_data["cnpjs"],
                data_inicial=data_inicial,
                data_final=data_final,
                profile_path=CHROME_PROFILE_PATH,
                download_path=form_data["download_path"],
                headless=False,
            )

            # Executa função bloqueante em thread separada
            await asyncio.to_thread(
                self._client.consulta_relatorios,
                callback_progress=task_progress,
                cancel_event=self._cancel_event,
            )

            # Sucesso
            self.progress_text.value = "Download completado com sucesso!"
            self.progress_text.color = ft.Colors.GREEN
            self.progress_bar.value = 1.0

        except CancelledException:
            # Cancelamento gracioso - esconde UI
            self.progress_bar.visible = False
            self.progress_text.visible = False

        except Exception as e:
            # Erro inesperado
            self.progress_text.value = f"Erro: {str(e)}"
            self.progress_text.color = ft.Colors.RED

        finally:
            # Limpa referências
            self._client = None
            self._cancel_event = None

            # Restaura o botão independentemente do resultado
            self.download_btn.disabled = False
            self.download_btn.content = "Baixar"
            self.cancel_btn.visible = False
            self.cancel_btn.disabled = False
            self.update()

    def handle_download(self, e):
        """
        Evento de clique do botão. Prepara a UI e inicia a Thread.
        """
        # 1. Obtém dados do formulário
        form_data = self.nfse_web_form.get_values()

        # Validação simples
        if not form_data:
            self.page.snack_bar = ft.SnackBar(
                ft.Text("Por favor, preencha todos os campos!")
            )
            self.page.snack_bar.open = True
            self.page.update()
            return

        self.form_data = form_data

        # 2. Configura UI para estado de "Carregando"
        self.download_btn.disabled = True
        self.cancel_btn.visible = True  # Mostra botão cancelar
        self.progress_text.visible = True
        self.progress_bar.visible = True
        self.progress_text.value = "Iniciando conexão..."
        self.progress_text.color = ft.Colors.WHITE
        self.update()

        # 3. Inicia a Thread
        self.page.run_task(self._run_background_task)

    def handle_cancel(self, e):
        """
        Cancela a execução do consulta_relatorios via cancel_event.
        """
        if self._cancel_event:
            self._cancel_event.set()

        self.progress_text.value = "Cancelando..."
        self.progress_text.color = ft.Colors.ORANGE
        self.cancel_btn.disabled = True
        self.update()

    async def go_back(self, e, page: ft.Page):
        # se houver mais de uma view, remove a atual e navega para a anterior
        if len(page.views) > 1:
            page.views.pop()
            top_view = page.views[-1]
            if top_view.route:
                await page.push_route(top_view.route)
            else:
                await page.push_route("/")
        else:
            # fallback: vai para a rota raiz
            await page.push_route("/")
