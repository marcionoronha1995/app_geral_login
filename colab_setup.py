import os
import sys

# Garante saída UTF-8 no console do Windows para evitar erros de codificação com emojis
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")


def connect_colab_workspace():
    """
    Garante que o ambiente esteja rodando localmente (Local Runtime).
    A execução na nuvem do Google Colab é bloqueada nesta arquitetura.
    """
    # Verificação segura baseada em variáveis de ambiente (evita alertas do Linter)
    in_cloud = "COLAB_RELEASE_TAG" in os.environ

    if in_cloud:
        print("🚨 ALERTA DE ARQUITETURA: Execução na Nuvem Detectada!")
        print("Este projeto foi configurado para rodar estritamente de forma LOCAL.")
        print("\nPara resolver:")
        print("1. Na sua máquina, execute o script 'colab_local_bridge.py'.")
        print("2. No Google Colab, clique na seta ao lado do botão 'Conectar'.")
        print("3. Selecione 'Conectar a um ambiente de execução local' e cole o link.")
        # Interrompe a execução do notebook caso esteja na nuvem
        raise RuntimeError("Conecte-se ao Local Runtime para continuar.")

    print("🖥️ Execução Local validada (Colab via Local Runtime ou Terminal).")
    print(f"📂 Diretório ativo: {os.getcwd()}")
    print(
        "💡 O sistema possui acesso direto aos arquivos locais e variáveis de ambiente."
    )


if __name__ == "__main__":
    connect_colab_workspace()
