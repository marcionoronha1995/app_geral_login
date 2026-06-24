import urllib.request
import json
import sys

# Garante saída UTF-8 no console do Windows para evitar erros de codificação com emojis
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

BASE_URL = "http://127.0.0.1:5000"


def send_post(url, data):
    req = urllib.request.Request(
        url,
        data=json.dumps(data).encode("utf-8"),
        headers={"Content-Type": "application/json"},
        method="POST"
    )
    try:
        with urllib.request.urlopen(req) as res:
            return res.status, json.loads(res.read().decode("utf-8"))
    except urllib.error.HTTPError as e:
        try:
            return e.code, json.loads(e.read().decode("utf-8"))
        except Exception:
            return e.code, {"erro": "Erro de conexão/resposta malformatada"}


def send_get(url, token=None):
    headers = {}
    if token:
        headers["Authorization"] = f"Bearer {token}"
    req = urllib.request.Request(url, headers=headers, method="GET")
    try:
        with urllib.request.urlopen(req) as res:
            return res.status, json.loads(res.read().decode("utf-8"))
    except urllib.error.HTTPError as e:
        try:
            return e.code, json.loads(e.read().decode("utf-8"))
        except Exception:
            return e.code, {"erro": "Erro de conexão/resposta malformatada"}


def run_tests():
    print("🧪 --- INICIANDO TESTES DO CLIENTE LOCAL ---")
    
    # 1. Credenciais corretas do Triple Lock (de database_mock.py)
    credentials_ok = {
        "cnpj": "12345678000199",
        "cpf": "11122233344",
        "username": "operador_alfa",
        "password": "senha_segura_alfa_123"
    }

    # 2. Credenciais incorretas para testar bloqueio
    credentials_bad = {
        "cnpj": "12345678000199",
        "cpf": "11122233344",
        "username": "operador_alfa",
        "password": "senha_errada"
    }

    print("\n1️⃣  Testando autenticação com credenciais INCORRETAS...")
    status, res = send_post(f"{BASE_URL}/api/v1/auth", credentials_bad)
    print(f"Status HTTP: {status}")
    print(f"Resposta JSON: {res}")
    
    print("\n2️⃣  Testando autenticação com credenciais CORRETAS...")
    status, res = send_post(f"{BASE_URL}/api/v1/auth", credentials_ok)
    print(f"Status HTTP: {status}")
    print(f"Resposta JSON: {res}")
    
    token = res.get("token")
    if not token:
        print("❌ Falha crítica: Não foi possível obter o token de sessão!")
        return

    print("\n3️⃣  Testando acesso à Rota Protegida SEM enviar o Token...")
    status, res = send_get(f"{BASE_URL}/api/v1/protegido")
    print(f"Status HTTP: {status}")
    print(f"Resposta JSON: {res}")

    print("\n4️⃣  Testando acesso à Rota Protegida com Token INVÁLIDO...")
    status, res = send_get(f"{BASE_URL}/api/v1/protegido", token="token_falso_123")
    print(f"Status HTTP: {status}")
    print(f"Resposta JSON: {res}")

    print("\n5️⃣  Testando acesso à Rota Protegida com Token VÁLIDO...")
    status, res = send_get(f"{BASE_URL}/api/v1/protegido", token=token)
    print(f"Status HTTP: {status}")
    print(f"Resposta JSON: {res}")


if __name__ == "__main__":
    run_tests()