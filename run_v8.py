import pathlib
import subprocess
import sys

# Garante saída UTF-8 no console do Windows para evitar erros de codificação com emojis
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")


def launch_server_external():
    # Caminho da raiz do projeto
    root = pathlib.Path(__file__).parent.resolve()

    # Comando para o PowerShell:
    # 1. Ajusta a política de execução (para permitir o script do venv)
    # 2. Ativa o ambiente virtual (.venv)
    # 3. Roda o servidor Flask
    powershell_cmd = (
        f"start powershell -NoExit -ExecutionPolicy Bypass -Command "
        f"\"& {{ cd '{root}'; "
        f".\\.venv\\Scripts\\Activate.ps1; "
        f'python src/backend/app.py }}"'
    )

    print("🚀 Abrindo servidor em janela externa do PowerShell...")
    try:
        # shell=True é necessário para usar o comando 'start' do Windows
        subprocess.Popen(powershell_cmd, shell=True)
        print("✅ Janela disparada com sucesso.")
    except Exception as e:
        print(f"❌ Erro ao abrir o PowerShell: {e}")


if __name__ == "__main__":
    launch_server_external()
