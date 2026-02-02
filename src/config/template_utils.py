"""
Utilitários para acessar templates de configuração.

Usa importlib.resources para acessar arquivos .toml empacotados
no módulo config.templates. Funciona tanto em desenvolvimento
quanto em apps Flet bundled.
"""

from importlib import resources
from pathlib import Path


def get_template_content(template_name: str) -> str:
    """
    Lê o conteúdo de um arquivo template.

    Args:
        template_name: Nome do arquivo template (ex: "profile_template.toml")

    Returns:
        Conteúdo do template como string
    """
    template_files = resources.files("config.templates")
    template_path = template_files.joinpath(template_name)
    return template_path.read_text(encoding="utf-8")


def write_template_to_file(template_name: str, destination: str | Path) -> None:
    """
    Escreve o conteúdo de um template para um arquivo de destino.

    Args:
        template_name: Nome do arquivo template (ex: "profile_template.toml")
        destination: Caminho de destino para escrever o arquivo
    """
    content = get_template_content(template_name)
    dest_path = Path(destination)
    dest_path.parent.mkdir(parents=True, exist_ok=True)
    dest_path.write_text(content, encoding="utf-8")


def ensure_config_file(config_path: str | Path, template_name: str) -> bool:
    """
    Garante que um arquivo de configuração existe.
    Se não existir, cria a partir do template.

    Args:
        config_path: Caminho do arquivo de configuração
        template_name: Nome do template a usar se arquivo não existir

    Returns:
        True se o arquivo foi criado, False se já existia
    """
    path = Path(config_path)
    if not path.exists():
        write_template_to_file(template_name, path)
        return True
    return False
