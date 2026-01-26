import flet as ft
import threading
import asyncio
from datetime import date, datetime

from auto_nfe import ClientNfseWeb

from components.consultas.nfse_web_form import NfseWebForm
from components.download_btn import DownloadBtn


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

            client = ClientNfseWeb(
                usuario=form_data["usuario"],
                senha=form_data["senha"],
                cnpjs=form_data["cnpjs"],
                data_inicial=data_inicial,
                data_final=data_final,
                download_path=form_data["download_path"],
                headless=False
            )

            await client.consulta_relatorios(
                callback_progress=task_progress,
            )

            # Sucesso
            self.progress_text.value = "Download completado com sucesso!"
            self.progress_text.color = ft.Colors.GREEN
            self.progress_bar.value = 1.0

        except Exception as e:
            # Erro
            self.progress_text.value = f"Erro: {str(e)}"
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
        self.progress_text.visible = True
        self.progress_bar.visible = True
        self.progress_text.value = "Iniciando conexão..."
        self.progress_text.color = ft.Colors.WHITE
        self.update()

        # 3. Inicia a Thread
        # Passamos form_data como argumento para a thread não acessar a UI diretamente
        # lock = threading.Lock()
        # self.lock = lock
        self.page.run_task(self._run_background_task)

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
