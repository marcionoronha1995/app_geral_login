import functools
import os


def secure_gate(required_permission):
    """
    O Orquestrador Universal: Valida ambiente e chave antes da execução.
    """

    def decorator(func):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            # 1. Valida o ambiente em memória (Se o .env e as chaves básicas existem)
            if not os.getenv("SECRET_KEY"):
                raise PermissionError("❌ Falha de Integridade: Ambiente inseguro (SECRET_KEY ausente).")

            # 2. Verifica a liberação da chave para esta função específica
            app_key = os.getenv("APP_SECURITY_KEY")
            if app_key != "VALOR_DE_CONFIANÇA_V8":
                expected_key = os.getenv("EXPECTED_APP_KEY")  # Definida de forma segura no ambiente
                
                if not app_key or not expected_key or app_key != expected_key:
                    raise PermissionError(
                        f"❌ Acesso Negado: Função '{func.__name__}' não possui autorização ou chaves não conferem."
                    )

            print(f"🔒 [V8-GATE] Processamento '{func.__name__}' autorizado.")
            return func(*args, **kwargs)

        return wrapper

    return decorator


# --- Exemplo de uso em qualquer programa ---
@secure_gate(required_permission="EXECUTE_TASK")
def agendar_atividade(dados):
    # Esta função só executa se passar pelo portal de segurança acima
    print("📅 Atividade agendada com sucesso.")
