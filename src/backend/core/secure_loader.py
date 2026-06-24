import os
import pathlib
import sys
import logging

# Garante saída UTF-8 no console do Windows para evitar erros de codificação com emojis
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

from dotenv import load_dotenv

# Configuração do Logger Estruturado V8
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] (%(name)s) %(message)s",
    handlers=[
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger("V8Core")


def get_project_root():
    """
    Retorna o caminho absoluto da raiz do projeto (app_geral_login).
    Calculado a partir de: src/backend/core/secure_loader.py
    """
    # .parent (core) -> .parent (backend) -> .parent (src) -> .parent (raiz)
    return pathlib.Path(__file__).resolve().parent.parent.parent.parent


def cleanup_system_files():
    """Limpa arquivos desktop.ini APENAS dentro da pasta do projeto."""
    root = get_project_root()
    count = 0

    logger.info("🔍 Iniciando varredura em: %s", root)

    # rglob busca de forma recursiva apenas dentro do diretório raiz definido
    for path in root.rglob("desktop.ini"):
        try:
            path.unlink()  # Remove o arquivo
            count += 1
        except Exception as e:
            # Registra o erro em modo debug em vez de silenciar cegamente
            logger.debug("Falha ao remover arquivo de sistema %s: %s", path, e)
            continue

    logger.info("🧹 Limpeza concluída: %d arquivos removidos.", count)


def load_secure_environment():
    """Carrega o .env localizado na raiz do projeto."""
    root = get_project_root()
    env_path = root / ".env"

    if not env_path.exists():
        logger.error("🚨 ERRO: Arquivo .env não encontrado em: %s", env_path)
        return False

    load_dotenv(dotenv_path=env_path)

    # Validação simples
    if not os.getenv("SECRET_KEY"):
        logger.warning("⚠️ AVISO: SECRET_KEY não encontrada no arquivo .env")
        return False

    logger.info("🔐 Ambiente carregado com sucesso.")
    return True


if __name__ == "__main__":
    print("🚀 --- INICIALIZADOR V8 ---")
    cleanup_system_files()

    if load_secure_environment():
        print("✅ Tudo pronto para iniciar o servidor.")
    else:
        print("❌ Falha na validação de segurança.")
