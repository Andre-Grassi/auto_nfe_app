import os
import sys


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
