import os
import sys
import bcrypt
import logging
from supabase import create_client, Client

# Garante saída UTF-8 no console do Windows para evitar erros de codificação com emojis
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

logger = logging.getLogger("V8Core")

# Inicialização do Cliente Supabase
SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")

if not SUPABASE_URL or not SUPABASE_KEY:
    logger.warning("⚠️ AVISO: SUPABASE_URL ou SUPABASE_KEY não configuradas no .env. O banco rodará em modo local simulado.")
    supabase_client = None
else:
    try:
        supabase_client: Client = create_client(SUPABASE_URL, SUPABASE_KEY)
        logger.info("🔌 Conectado ao banco de dados Supabase com sucesso.")
    except Exception as e:
        logger.error("❌ Erro ao conectar ao Supabase: %s. Rodando em modo local simulado.", e)
        supabase_client = None


# Mock Fallback (para testes sem conexão externa)
MOCK_TENANTS = {
    "12345678000199": {
        "nome_empresa": "Empresa Alfa Core Ltda",
        "operadores": {
            "11122233344": {
                "username": "operador_alfa",
                "password_hash": "$2b$12$YaKK33gKQgkg3fhLXKu.Au4Nenbs7SfAsK4angA/9ynu2TYpSO1RS",  # senha_segura_alfa_123
                "nome_operador": "Márcio Noronha",
                "perfil": "ADMIN"
            }
        }
    }
}


def validate_tenant_credentials(cnpj, cpf, username, password):
    """
    Valida as chaves do Triple Lock contra o Supabase (ou fallback local).
    Retorna os dados do operador se válido, ou None caso contrário.
    """
    # 1. Tenta validar no Supabase se o cliente estiver ativo
    if supabase_client is not None:
        try:
            response = supabase_client.table("operators") \
                .select("*, tenants(nome_empresa)") \
                .eq("tenant_cnpj", cnpj) \
                .eq("cpf", cpf) \
                .eq("username", username) \
                .execute()
                
            if response.data:
                user_data = response.data[0]
                hash_salvo = user_data.get("password_hash")
                
                # Compara a senha digitada com o hash Bcrypt
                if hash_salvo and bcrypt.checkpw(password.encode("utf-8"), hash_salvo.encode("utf-8")):
                    return {
                        "cnpj": cnpj,
                        "cpf": cpf,
                        "empresa": user_data["tenants"]["nome_empresa"],
                        "operador": user_data["nome_operador"],
                        "perfil": user_data["perfil"]
                    }
            return None
        except Exception as e:
            logger.error("❌ Falha na consulta ao Supabase: %s. Utilizando fallback local.", e)

    # 2. Fallback local/mock se o Supabase não estiver configurado ou falhar
    tenant = MOCK_TENANTS.get(cnpj)
    if not tenant:
        return None
        
    operador = tenant["operadores"].get(cpf)
    if not operador:
        return None
        
    if operador["username"] == username:
        hash_salvo = operador["password_hash"]
        if bcrypt.checkpw(password.encode("utf-8"), hash_salvo.encode("utf-8")):
            return {
                "cnpj": cnpj,
                "cpf": cpf,
                "empresa": tenant["nome_empresa"],
                "operador": operador["nome_operador"],
                "perfil": operador["perfil"]
            }
        
    return None