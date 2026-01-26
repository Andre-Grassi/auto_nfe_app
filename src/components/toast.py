"""
Componente de notificações toast com animação de fade e stacking.
Exibe notificações no canto superior direito da tela.
"""

import asyncio
from enum import Enum
from dataclasses import dataclass
import flet as ft


class ToastType(Enum):
    """Tipos de notificação com cores e ícones padrão."""

    SUCCESS = "success"
    ERROR = "error"
    WARNING = "warning"
    INFO = "info"


# Configurações visuais por tipo
_TOAST_STYLES = {
    ToastType.SUCCESS: {
        "bgcolor": ft.Colors.GREEN_700,
        "icon": ft.Icons.CHECK_CIRCLE,
    },
    ToastType.ERROR: {
        "bgcolor": ft.Colors.RED_700,
        "icon": ft.Icons.ERROR,
    },
    ToastType.WARNING: {
        "bgcolor": ft.Colors.ORANGE_700,
        "icon": ft.Icons.WARNING,
    },
    ToastType.INFO: {
        "bgcolor": ft.Colors.BLUE_700,
        "icon": ft.Icons.INFO,
    },
}


@dataclass
class _ToastItem:
    """Representa um toast ativo."""

    container: ft.Container
    task: asyncio.Task | None = None


class ToastManager:
    """
    Gerenciador de notificações toast.

    Exibe notificações no canto superior direito com animação de fade
    e suporte a stacking (empilhamento).

    Uso:
        toast = ToastManager(page)
        toast.success("Operação concluída!")
        toast.error("Falha ao salvar")
    """

    def __init__(
        self,
        page: ft.Page,
        max_toasts: int = 5,
        default_duration_ms: int = 3000,
    ):
        """
        Args:
            page: Página do Flet.
            max_toasts: Número máximo de toasts simultâneos.
            default_duration_ms: Duração padrão em milissegundos.
        """
        self._page = page
        self._max_toasts = max_toasts
        self._default_duration_ms = default_duration_ms
        self._toasts: list[_ToastItem] = []

        # Container de overlay para os toasts (canto superior direito)
        self._overlay = ft.Column(
            spacing=8,
            alignment=ft.MainAxisAlignment.START,
        )

        # Posiciona no canto superior direito
        self._overlay_container = ft.Container(
            content=self._overlay,
            right=20,
            top=20,
            animate_opacity=300,
        )

        # Adiciona ao overlay da página
        if self._overlay_container not in page.overlay:
            page.overlay.append(self._overlay_container)
            try:
                page.update()
            except RuntimeError:
                pass

    def show(
        self,
        message: str,
        toast_type: ToastType = ToastType.INFO,
        duration_ms: int | None = None,
        icon: ft.Icons | None = None,
    ):
        """
        Exibe uma notificação toast.

        Args:
            message: Texto da notificação.
            toast_type: Tipo (SUCCESS, ERROR, WARNING, INFO).
            duration_ms: Duração em ms (None = default).
            icon: Ícone personalizado (None = ícone padrão do tipo).
        """
        duration = duration_ms or self._default_duration_ms
        style = _TOAST_STYLES.get(toast_type, _TOAST_STYLES[ToastType.INFO])

        toast_icon = icon or style["icon"]
        bgcolor = style["bgcolor"]

        # Cria o container do toast
        toast_container = ft.Container(
            content=ft.Row(
                [
                    ft.Icon(toast_icon, color=ft.Colors.WHITE, size=20),
                    ft.Text(
                        message,
                        color=ft.Colors.WHITE,
                        size=14,
                        weight=ft.FontWeight.W_500,
                        expand=True,
                    ),
                ],
                spacing=10,
                vertical_alignment=ft.CrossAxisAlignment.CENTER,
            ),
            bgcolor=bgcolor,
            padding=ft.Padding(left=15, right=15, top=12, bottom=12),
            border_radius=8,
            opacity=1.0,
            animate_opacity=ft.Animation(300, ft.AnimationCurve.EASE_OUT),
            width=320,
            shadow=ft.BoxShadow(
                spread_radius=1,
                blur_radius=10,
                color=ft.Colors.with_opacity(0.3, ft.Colors.BLACK),
                offset=ft.Offset(0, 2),
            ),
        )

        # Se atingiu o limite, remove o mais antigo
        if len(self._toasts) >= self._max_toasts:
            self._remove_oldest()

        # Adiciona ao overlay
        toast_item = _ToastItem(container=toast_container)
        self._toasts.append(toast_item)
        self._overlay.controls.insert(0, toast_container)

        try:
            self._overlay.update()
        except RuntimeError:
            pass

        # Inicia task de remoção com fade
        async def dismiss_task():
            await self._auto_dismiss(toast_item, duration)

        toast_item.task = self._page.run_task(dismiss_task)

    async def _auto_dismiss(self, toast_item: _ToastItem, duration_ms: int):
        """Remove o toast após a duração com fade out."""
        # Aguarda a duração
        await asyncio.sleep(duration_ms / 1000)

        # Fade out
        toast_item.container.opacity = 0
        try:
            toast_item.container.update()
        except RuntimeError:
            pass

        # Aguarda animação de fade
        await asyncio.sleep(0.3)

        # Remove do overlay
        self._remove_toast(toast_item)

    def _remove_toast(self, toast_item: _ToastItem):
        """Remove um toast do overlay."""
        if toast_item in self._toasts:
            self._toasts.remove(toast_item)
        if toast_item.container in self._overlay.controls:
            self._overlay.controls.remove(toast_item.container)
        try:
            self._overlay.update()
        except RuntimeError:
            pass

    def _remove_oldest(self):
        """Remove o toast mais antigo (primeiro da lista)."""
        if self._toasts:
            oldest = self._toasts[0]
            # Cancela a task se existir
            if oldest.task and not oldest.task.done():
                oldest.task.cancel()
            self._remove_toast(oldest)

    # --- Métodos de conveniência ---

    def success(self, message: str, **kwargs):
        """Exibe toast de sucesso."""
        self.show(message, ToastType.SUCCESS, **kwargs)

    def error(self, message: str, **kwargs):
        """Exibe toast de erro."""
        self.show(message, ToastType.ERROR, **kwargs)

    def warning(self, message: str, **kwargs):
        """Exibe toast de aviso."""
        self.show(message, ToastType.WARNING, **kwargs)

    def info(self, message: str, **kwargs):
        """Exibe toast informativo."""
        self.show(message, ToastType.INFO, **kwargs)
