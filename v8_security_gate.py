import functools
import os
import jwt
from flask import request

from src.backend.core.exceptions import V8SecurityException


def secure_gate(required_permission):
    """
    O Orquestrador Universal: Valida o token JWT recebido no cabeçalho HTTP da API.
    """

    def decorator(func):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            # 1. Valida o ambiente em memória
            secret_key = os.getenv("SECRET_KEY")
            if not secret_key:
                raise V8SecurityException("❌ Falha de Integridade: Ambiente inseguro (SECRET_KEY ausente).")

            # 2. Extrai o Token JWT do cabeçalho da requisição (Authorization: Bearer <TOKEN>)
            auth_header = request.headers.get("Authorization")
            if not auth_header or not auth_header.startswith("Bearer "):
                raise V8SecurityException("❌ Acesso Negado: Token de autorização ausente ou malformatado.")

            token = auth_header.split(" ")[1]

            # 3. Decodifica e valida a assinatura/expiração do Token JWT
            try:
                decoded_token = jwt.decode(token, secret_key, algorithms=["HS256"])
            except jwt.ExpiredSignatureError:
                raise V8SecurityException("❌ Acesso Negado: O token de sessão está expirado.")
            except jwt.InvalidTokenError as e:
                raise V8SecurityException(f"❌ Acesso Negado: Token de sessão inválido. {e}")

            # 4. (Opcional) Validação complementar baseada em perfis/permissões
            perfil = decoded_token.get("perfil")
            if required_permission == "EXECUTE_TASK" and perfil not in ["ADMIN", "OPERATOR"]:
                raise V8SecurityException("❌ Acesso Negado: Nível de permissão insuficiente para esta tarefa.")

            print(f"🔒 [V8-GATE] Processamento '{func.__name__}' autorizado para CNPJ: {decoded_token.get('cnpj')}.")
            return func(*args, **kwargs)

        return wrapper

    return decorator


# --- Exemplo de uso em qualquer programa ---
@secure_gate(required_permission="EXECUTE_TASK")
def agendar_atividade(dados):
    # Esta função só executa se passar pelo portal de segurança acima
    print("📅 Atividade agendada com sucesso.")
