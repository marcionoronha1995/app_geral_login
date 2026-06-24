import importlib.metadata
import os
import pathlib
import subprocess
import sys

# Garante saída UTF-8 no console do Windows para evitar erros de codificação com emojis
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

# Lista de dependências essenciais lidas a partir de requirements.txt
def get_requirements():
    root = pathlib.Path(__file__).parent.resolve()
    req_file = root / "requirements.txt"
    if req_file.exists():
        with open(req_file, "r", encoding="utf-8") as f:
            return [line.strip() for line in f if line.strip() and not line.strip().startswith("#")]
    # Fallback caso o arquivo não seja encontrado
    return [
        "python-dotenv",
        "flask",
        "pandas",
        "openpyxl",
        "ruff",
        "jupyter_http_over_ws",
    ]


REQUIREMENTS = get_requirements()


def detect_environment():
    """Detecta onde o código está rodando."""
    if "COLAB_RELEASE_TAG" in os.environ:
        return "COLAB"
    if "PYTHONANYWHERE_DOMAIN" in os.environ:
        return "PYTHONANYWHERE"
    return "LOCAL"


def install_missing_dependencies():
    """Verifica e instala bibliotecas faltantes usando importlib (Padrão Python 3.14)."""
    missing = []
    
    # Mapeia o nome do pacote para a string completa de instalação
    packages_to_check = {}
    for x in REQUIREMENTS:
        # Extrai o nome limpo do pacote (antes de ==, >=, etc.)
        pkg_name = x.split("==")[0].split(">=")[0].split("<=")[0].split(" ")[0].strip()
        # Normaliza para o formato padrão do importlib.metadata
        pkg_name = pkg_name.replace("_", "-").lower()
        packages_to_check[pkg_name] = x

    for pkg_name, full_spec in packages_to_check.items():
        try:
            importlib.metadata.version(pkg_name)
        except importlib.metadata.PackageNotFoundError:
            # Caso especial para pacotes que usam nomes diferentes no importlib vs pip
            # jupyter_http_over_ws pode ser verificado como jupyter-http-over-ws
            missing.append(full_spec)

    if missing:
        print(f"📦 Bibliotecas faltantes: {', '.join(missing)}")
        if detect_environment() != "LOCAL":
            print("🚨 ERRO: Execução em produção/nuvem detectada. Não é permitida a instalação dinâmica de pacotes via pip.")
            sys.exit(1)
            
        print("Wait... Sincronizando ambiente...")
        try:
            # sys.executable garante o uso do seu .venv
            subprocess.check_call([sys.executable, "-m", "pip", "install", *missing])
            print("✅ Sincronização concluída.")
        except Exception as e:
            print(f"❌ Erro na instalação: {e}")
            sys.exit(1)
    else:
        print("💎 Ambiente 100% atualizado.")


def verify_essentials():
    """Garante segurança e limpeza."""
    root = pathlib.Path(__file__).parent.resolve()

    # Verificação do .env
    if not (root / ".env").exists():
        print("⚠️ Criando .env base...")
        with open(root / ".env", "w") as f:
            f.write("SECRET_KEY=chave_v8_local\nDEBUG=True\n")

    # Executa a limpeza profissional de arquivos desktop.ini
    try:
        from src.backend.core.secure_loader import cleanup_system_files

        cleanup_system_files()
    except ImportError:
        print("ℹ️ Módulo secure_loader aguardando configuração.")


if __name__ == "__main__":
    print(f"🖥️  Sistema: {detect_environment()} | Python: {sys.version.split()[0]}")

    install_missing_dependencies()
    verify_essentials()

    print("\n🚀 PROJETO PRONTO PARA CODAR.")
