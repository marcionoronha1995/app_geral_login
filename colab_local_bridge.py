import pathlib
import subprocess
import sys

# Garante saída UTF-8 no console do Windows para evitar erros de codificação com emojis
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")


def launch_colab_local_server():
    # Caminho absoluto da raiz do seu projeto V8
    root = pathlib.Path(__file__).parent.resolve()

    print("🔧 Preparando Local Runtime para o Google Colab...")
    print(f"📂 Diretório: {root}")

    # Comando PowerShell para:
    # 1. Ativar o seu ambiente virtual (.venv)
    # 2. Instalar a extensão de segurança do Google (se faltar)
    # 3. Iniciar o servidor Jupyter com permissão para o domínio do Colab
    powershell_cmd = (
        f"start powershell -NoExit -ExecutionPolicy Bypass -Command "
        f"\"& {{ cd '{root}'; "
        f".\\.venv\\Scripts\\Activate.ps1; "
        f"pip install -q jupyter_http_over_ws; "
        f"jupyter serverextension enable --py jupyter_http_over_ws; "
        f"jupyter notebook "
        f"--NotebookApp.allow_origin='https://colab.research.google.com' "
        f"--ip=127.0.0.1 "
        f"--port=8888 "
        f'--NotebookApp.port_retries=0 }}"'
    )

    try:
        subprocess.Popen(powershell_cmd, shell=True)
        print("\n✅ Janela do PowerShell aberta!")
        print("🔗 Copie o link (URL com token) que aparecerá no PowerShell.")
    except Exception as e:
        print(f"❌ Erro ao disparar o PowerShell: {e}")


if __name__ == "__main__":
    launch_colab_local_server()
