import os
import sys

APP_NAME = "auto_nfe_app"

# ====== Base Directories ======


def _get_project_root() -> str:
    """Returns project root (works in dev and after build)."""
    if getattr(sys, "frozen", False):
        return os.path.dirname(sys.executable)
    # Go up from config/ -> src/ -> project_root/
    return os.path.dirname(os.path.dirname(os.path.dirname(__file__)))


PROJECT_ROOT = _get_project_root()
APPDATA_DIR = os.path.join(os.getenv("APPDATA", ""), APP_NAME)
ASSETS_DIR = os.path.join(PROJECT_ROOT, "assets")


# ====== Path Getters ======


def get_appdata_file_path(filename: str) -> str:
    """Get full path to a file in the app's AppData directory."""
    return os.path.join(APPDATA_DIR, filename)


def get_project_path(relative_path: str) -> str:
    """Get full path relative to project root."""
    return os.path.join(PROJECT_ROOT, relative_path)


def get_assets_file_path(filename: str) -> str:
    """Retorna caminho para arquivo no diretório assets do flet."""
    return os.path.join(ASSETS_DIR, filename)


def get_file_path(relative_path: str) -> str:
    """
    Retorna o caminho absoluto para um recurso, funciona em dev e após build.

    Args:
        relative_path: Caminho relativo a partir da raiz do projeto
                        Ex: "profile.toml", "relatorios/cnpjs.txt"

    Returns:
        Caminho absoluto para o recurso
    """
    if getattr(sys, "frozen", False):
        # Executável (PyInstaller, cx_Freeze, etc)
        base_path = os.path.dirname(sys.executable)
    else:
        # Ambiente de desenvolvimento - vai para a raiz do projeto
        base_path = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))

    return os.path.join(base_path, relative_path)


# ====== Specific Paths (shortcuts) ======

PROFILE_PATH = get_appdata_file_path("profile.toml")
PROFILE_TEMPLATE_PATH = get_assets_file_path(
    "profile_template.toml"
)  # No need for complex path resolution, since it's inside assets/
EMPRESAS_NFSE_PATH = get_appdata_file_path("empresas_nfse.toml")
EMPRESAS_NFSE_TEMPLATE_PATH = get_assets_file_path("empresas_nfse_template.toml")
