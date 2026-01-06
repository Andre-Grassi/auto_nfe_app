import flet as ft
import asyncio


from auto_nfe import ClientNfe


async def main(page: ft.Page):
    # --- Janela ---
    page.title = "Auto Nfe"
    page.theme_mode = ft.ThemeMode.DARK
    page.padding = 40
    page.vertical_alignment = ft.MainAxisAlignment.START
    page.horizontal_alignment = ft.CrossAxisAlignment.CENTER

    # Título
    title = ft.Text("Auto Nfe", size=40, weight=ft.FontWeight.BOLD)

    # Campos de Entrada
    cnpj_input = ft.TextField(label="CNPJ", hint_text="Value", width=300)
    cert_input = ft.TextField(label="Certificado A1", hint_text="Value", width=300)
    password_input = ft.TextField(
        label="Senha",
        hint_text="Value",
        password=True,
        can_reveal_password=True,
        width=300,
    )
    sheet_input = ft.TextField(
        label="Planilha de Relação", hint_text="Value", width=300
    )
    folder_input = ft.TextField(
        label="Pasta para direcionar XMLs baixados", hint_text="Value", width=300
    )

    # Layout dos Campos (Grid simples para 2 colunas)
    campos_grid = ft.Column(
        [
            ft.Row(
                [cnpj_input, cert_input, password_input],
                alignment=ft.MainAxisAlignment.CENTER,
                spacing=20,
            ),
            ft.Row(
                [sheet_input, folder_input],
                alignment=ft.MainAxisAlignment.CENTER,
                spacing=20,
            ),
        ],
        spacing=30,
        alignment=ft.MainAxisAlignment.CENTER,
    )

    # Elementos da Área de Ação (Botão e Progresso)
    progress_text = ft.Text("Baixando notas...", size=16, visible=False)
    progress_bar = ft.ProgressBar(
        width=400, value=0, visible=False, color=ft.Colors.BLUE
    )

    async def download_sheet():
        progress_bar.value = 0

        client = ClientNfe(
            cnpj=cnpj_input.value,
            cert_pfx_path=cert_input.value,
            cert_password=password_input.value,
        )

        client.consulta_planilha(sheet_input.value)

        for i in range(1, 101):
            progress_bar.value = i / 100
            page.update()
            await asyncio.sleep(0.05)  # Simula tempo de processamento

        # Opcional: Restaurar o botão após o download
        # progress_text.visible = False
        # progress_bar.visible = False
        # btn_baixar.visible = True
        # page.update()

    async def on_download_click(e):
        # Validação simples (apenas verifica se não está vazio)
        if all(
            [
                cnpj_input.value,
                cert_input.value,
                password_input.value,
                sheet_input.value,
                folder_input.value,
            ]
        ):
            # Muda para o estado de processamento
            btn_baixar.visible = False
            progress_text.visible = True
            progress_bar.visible = True
            page.update()

            await download_sheet()
        else:
            # Mostra um erro se algum campo estiver vazio
            page.snack_bar = ft.SnackBar(
                content=ft.Text("Por favor, preencha todos os campos!")
            )
            page.snack_bar.open = True
            page.update()

    btn_baixar = ft.ElevatedButton(
        "Baixar",
        icon=ft.Icons.DOWNLOAD,
        on_click=on_download_click,
        style=ft.ButtonStyle(
            shape=ft.RoundedRectangleBorder(radius=20),
            padding=ft.padding.symmetric(horizontal=30, vertical=15),
        ),
    )

    # Container para a Área de Ação para manter o layout
    area_acao = ft.Column(
        [btn_baixar, progress_text, progress_bar],
        alignment=ft.MainAxisAlignment.CENTER,
        horizontal_alignment=ft.CrossAxisAlignment.CENTER,
        spacing=10,
    )

    # Adicionando elementos à página
    page.add(
        title,
        ft.Divider(height=50, color="transparent"),  # Espaçamento
        campos_grid,
        ft.Divider(height=50, color="transparent"),  # Espaçamento
        area_acao,
    )


ft.run(main=main)
