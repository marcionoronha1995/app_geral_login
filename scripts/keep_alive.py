import os
import sys
import datetime
import urllib.request
import pathlib

# Ajusta o caminho para carregar as variáveis locais da raiz
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../")))

from dotenv import load_dotenv

# Garante saída UTF-8 no console do Windows para evitar erros de codificação com emojis
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

root = pathlib.Path(__file__).resolve().parent.parent
load_dotenv(dotenv_path=root / ".env")

SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")
WEB_APP_URL = os.getenv("WEB_APP_URL")

# Arquivo de log para registrar as execuções
LOG_FILE = root / "keep_alive_log.txt"


def write_log(message):
    timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    log_line = f"[{timestamp}] {message}\n"
    print(log_line.strip())
    with open(LOG_FILE, "a", encoding="utf-8") as f:
        f.write(log_line)


def ping_supabase():
    if not SUPABASE_URL or not SUPABASE_KEY or SUPABASE_URL.startswith("INSIRA"):
        write_log("⚠️ Supabase não configurado no .env. Ignorando ping do banco.")
        return False
        
    try:
        from supabase import create_client, Client
        supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)
        
        # Consulta simples para manter a instância do banco ativa
        supabase.table("tenants").select("cnpj").limit(1).execute()
        write_log("✅ Conexão com o Supabase validada (Banco mantido ativo).")
        return True
    except Exception as e:
        write_log(f"❌ Erro de conexão com o Supabase: {e}")
        return False


def ping_web_app():
    if not WEB_APP_URL or WEB_APP_URL.startswith("INSIRA"):
        write_log("⚠️ URL do Web App não configurada no .env. Ignorando ping HTTP.")
        return False
        
    try:
        req = urllib.request.Request(WEB_APP_URL, headers={"User-Agent": "V8 Keep Alive Daemon"})
        with urllib.request.urlopen(req, timeout=10) as res:
            if res.status == 200:
                write_log(f"✅ Web App ({WEB_APP_URL}) ativo (Status 200).")
                return True
            else:
                write_log(f"⚠️ Web App respondeu com status {res.status}.")
                return False
    except Exception as e:
        write_log(f"❌ Erro ao acessar o Web App: {e}")
        return False


if __name__ == "__main__":
    write_log("🚀 --- INICIANDO EXECUÇÃO DO KEEP-ALIVE ---")
    ping_supabase()
    ping_web_app()
    write_log("🏁 --- FIM DA EXECUÇÃO ---")