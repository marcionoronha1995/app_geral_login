import pathlib
import subprocess
import sys

# Garante saída UTF-8 no console do Windows para evitar erros de codificação com emojis
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

import init_env

# Configurações de Identidade do Projeto
PROJECT_NAME = "App Geral Login - V8"


def run_step(description, command_list):
    """Executa um comando de sistema e reporta o status."""
    print(f"🔹 {description}...")
    try:
        subprocess.check_call(
            [sys.executable] + command_list, stdout=subprocess.DEVNULL
        )
        return True
    except Exception as e:
        print(f"❌ Falha em {description}: {e}")
        return False


def setup_environment():
    root = pathlib.Path(__file__).parent.resolve()

    print(f"--- 🚀 INICIALIZANDO {PROJECT_NAME} ---")

    # 1. Limpeza de Cache do PIP (Resolve os avisos de Deserialization)
    run_step("Limpando cache do instalador", ["-m", "pip", "cache", "purge"])

    # 2. Sincronização de Ambiente (usando init_env.py)
    init_env.install_missing_dependencies()

    # 3. Verificações Essenciais (Limpeza de sistema e geração de .env)
    init_env.verify_essentials()

    # 4. Atualização automática do Selo de Integridade no Berço
    run_step("Atualizando selo de integridade (Code Signing)", ["scripts/seal_project.py"])

    # 5. Abertura das Janelas de Serviço (PowerShell Externo)
    launch_services(root)


def launch_services(root):
    """Abre o Servidor Flask e o Jupyter para Colab em janelas separadas."""
    print("🖥️  Disparando serviços em janelas externas...")

    try:
        from colab_local_bridge import launch_colab_local_server
        from run_v8 import launch_server_external

        # Centraliza as chamadas usando as funções robustas já existentes
        launch_server_external()
        launch_colab_local_server()
    except ImportError as e:
        print(f"❌ Erro ao importar serviços externos: {e}")


if __name__ == "__main__":
    setup_environment()
    print("\n✅ AMBIENTE TOTALMENTE OPERACIONAL.")
