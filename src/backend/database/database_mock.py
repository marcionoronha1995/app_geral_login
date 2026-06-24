import sys

# Garante saída UTF-8 no console do Windows para evitar erros de codificação com emojis
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

# Mock de banco de dados para autenticação e verificação do "Triple Lock" (Tranca Tripla)
VALID_TENANTS = {
    "12345678000199": {  # CNPJ da Empresa A
        "nome_empresa": "Empresa Alfa Core Ltda",
        "operadores": {
            "11122233344": {  # CPF do Operador
                "username": "operador_alfa",
                "password": "senha_segura_alfa_123",
                "nome_operador": "Márcio Noronha",
                "perfil": "ADMIN"
            }
        }
    },
    "98765432000188": {  # CNPJ da Empresa B
        "nome_empresa": "Empresa Beta Services S.A.",
        "operadores": {
            "55566677788": {
                "username": "operador_beta",
                "password": "senha_segura_beta_456",
                "nome_operador": "Carlos Silva",
                "perfil": "OPERATOR"
            }
        }
    }
}


def validate_tenant_credentials(cnpj, cpf, username, password):
    """
    Valida as chaves do Triple Lock contra a base mockada.
    Retorna os dados do operador se válido, ou None caso contrário.
    """
    tenant = VALID_TENANTS.get(cnpj)
    if not tenant:
        return None
        
    operador = tenant["operadores"].get(cpf)
    if not operador:
        return None
        
    if operador["username"] == username and operador["password"] == password:
        return {
            "cnpj": cnpj,
            "cpf": cpf,
            "empresa": tenant["nome_empresa"],
            "operador": operador["nome_operador"],
            "perfil": operador["perfil"]
        }
        
    return None