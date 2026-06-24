import os
import sys

# Garante saída UTF-8 no console do Windows para evitar erros de codificação com emojis
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

from flask import Flask, request
import datetime
import jwt

from src.backend.core.exceptions import V8SecurityException
from src.backend.core.secure_loader import load_secure_environment
from src.backend.database.database_mock import validate_tenant_credentials
from v8_security_gate import secure_gate
from v8_sentinel import sentinel

app = Flask(__name__)

# Validação de Segurança V8 e Selo de Integridade
if load_secure_environment():
    app.config["SECRET_KEY"] = os.getenv("SECRET_KEY")
    app.config["DEBUG"] = os.getenv("DEBUG") == "True"
    
    # Executa verificação criptográfica do Selo de Integridade no boot
    try:
        sentinel.verify_integrity()
    except V8SecurityException as e:
        print(f"❌ ERRO CRÍTICO DE INTEGRIDADE: {e}")
        sys.exit(1)
else:
    print("❌ ERRO: Não foi possível carregar as configurações de segurança.")
    sys.exit(1)


@app.errorhandler(V8SecurityException)
def handle_v8_security_error(error):
    """
    Tratamento de exceção de segurança global:
    Retorna uma resposta HTTP 403 (Forbidden) amigável em formato JSON.
    """
    return {
        "status": "Erro de Permissão",
        "mensagem": str(error)
    }, 403


@app.route("/api/v1/auth", methods=["POST"])
def autenticar():
    """
    Endpoint de Autenticação do Orquestrador de Segurança.
    Valida CNPJ, CPF, usuário e senha contra a base mockada (Triple Lock).
    Retorna um token JWT assinado caso passe nas verificações.
    """
    dados = request.get_json()
    if not dados:
        return {"status": "Erro", "mensagem": "Corpo da requisição JSON inválido ou ausente."}, 400
        
    cnpj = dados.get("cnpj")
    cpf = dados.get("cpf")
    username = dados.get("username")
    password = dados.get("password")
    
    if not all([cnpj, cpf, username, password]):
        return {"status": "Erro", "mensagem": "Dados do 'Triple Lock' ausentes (cnpj, cpf, username, password)."}, 400
        
    user_data = validate_tenant_credentials(cnpj, cpf, username, password)
    if not user_data:
        return {"status": "Erro", "mensagem": "Acesso Negado: Credenciais ou chaves incorretas."}, 401
        
    # Gera o Token de Sessão assinado criptograficamente
    payload = {
        "cnpj": user_data["cnpj"],
        "cpf": user_data["cpf"],
        "empresa": user_data["empresa"],
        "operador": user_data["operador"],
        "perfil": user_data["perfil"],
        "exp": datetime.datetime.now(datetime.timezone.utc) + datetime.timedelta(hours=1)
    }
    
    token = jwt.encode(payload, app.config["SECRET_KEY"], algorithm="HS256")
    
    return {
        "status": "Sucesso",
        "mensagem": "Autenticado com sucesso! Token de sessão gerado.",
        "token": token
    }, 200


@app.route("/")
def index():
    return {
        "status": "Online",
        "modulo": "Core Login",
        "tecnologia": "Flask + Python 3.14",
        "ambiente": "Desenvolvimento",
    }


# Nova Rota Protegida pelos Cadeados do V8
@app.route("/api/v1/protegido")
@sentinel.validate_gate(required_key_level="MASTER")
@secure_gate(required_permission="EXECUTE_TASK")
def rota_protegida():
    return {
        "status": "Sucesso",
        "mensagem": "Acesso concedido! O ambiente é seguro e as chaves são válidas.",
    }


if __name__ == "__main__":
    print("🚀 Servidor V8 Ativo: http://127.0.0.1:5000")
    app.run(host="0.0.0.0", port=5000)
