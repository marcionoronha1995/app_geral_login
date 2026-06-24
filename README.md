# Core Framework - Ecossistema Multi-Tenant v2.0 (Orquestrador de Segurança)

![Status](https://img.shields.io/badge/Status-Operacional-brightgreen)
![Python](https://img.shields.io/badge/Python-3.10+-blue)
![Security](https://img.shields.io/badge/Security-Triple%20Lock%20%2B%20RSA%20Code%20Signing-red)

O **Core Framework** é uma infraestrutura de segurança e autenticação centralizada, projetada para validar conexões e autorizações entre múltiplos serviços e empresas (Multi-Tenant). Ele atua como um **Orquestrador de Autenticação baseada em JWT** e implementa um sistema de **Autodefesa Criptográfica (Code Signing)**.

---

## 🏗️ Pilares de Engenharia & Segurança

### 1. Segurança "Triple Lock" (Tranca Tripla)
Nenhuma chave de comunicação é gerada sem a validação simultânea de:
* **CNPJ:** Identificação e direcionamento correto do Tenant (empresa).
* **CPF:** Rastreabilidade do operador físico responsável pela transação.
* **Credenciais (User/Senha):** Verificação de autenticidade.
* Se os dados do Triple Lock forem válidos, o Orquestrador libera uma chave de sessão temporária (**Token JWT** assinado) com expiração de 1 hora.

### 2. Selo de Integridade Criptográfica (Anti-Tamper)
O sistema impede modificações de código diretamente no servidor de produção usando criptografia assimétrica RSA:
* **Desenvolvimento ("Berço"):** Possui a chave privada (`private_key.pem`). Ao iniciar o projeto localmente, os hashes SHA-256 de todos os arquivos críticos são calculados, assinados com a chave privada e guardados no manifesto `signature.json`.
* **Produção ("Servidor"):** Possui apenas a chave pública (`public_key.pem`). Durante o boot do servidor, o sistema verifica a assinatura do manifesto e valida se os hashes físicos de todos os arquivos em disco coincidem. Se qualquer linha de código for alterada na produção, a validação falha e o boot é abortado imediatamente.

---

## 🛠️ Stack Tecnológica

* **Backend:** Python 3.10+ (Flask)
* **Criptografia:** PyJWT (para tokens de sessão), cryptography (chaves assimétricas RSA-2048 e SHA-256)
* **Linter/Style:** Ruff
* **Logs:** Módulo padrão `logging` com formatação estruturada em console UTF-8.

---

## 📁 Estrutura do Projeto

```text
app_geral_login /
├── docs/                      # Documentação técnica detalhada do sistema
│   └── documentacao_sistema.md
├── scripts/                   
│   ├── seal_project.py        # Script local para assinar os hashes do código (RSA)
│   └── test_client.py         # Cliente de simulação de requisições de teste
├── src/                     
│   └── backend/             
│       ├── core/            
│       │   ├── exceptions.py  # Exceção de segurança customizada (V8SecurityException)
│       │   ├── secure_loader.py # Carregador de variáveis do .env e configuração de logs
│       │   └── metadata/      # Chaves de segurança (.pem) e Manifesto assinado (.json)
│       ├── database/        
│       │   └── database_mock.py # Base mockada de verificação do Triple Lock
│       └── app.py             # Servidor principal e endpoints de API (Flask)
├── tests/                     # Testes de integração
├── v8_security_gate.py        # Decorador (@secure_gate) para proteção de rotas via JWT
├── v8_sentinel.py             # Sentinel de validação e verificação de integridade no boot
├── init_env.py                # Inicializador e verificador de dependências
├── start_all.py               # Orquestrador local de boot de serviços
├── requirements.txt           # Bibliotecas de produção com versões fixadas (pinned)
└── README.md                  # Este guia
```

---

## 🚀 Guia de Execução e Testes

### 1. Inicializar o Ambiente
Verifique e instale as dependências com versões congeladas:
```bash
python init_env.py
```

### 2. Executar o Servidor (Orquestrador)
Inicie a aplicação utilizando execução baseada em módulos Python (a partir do diretório raiz):
```bash
python -m src.backend.app
```
*(Nota: Durante a execução no "berço", o script `start_all.py` atualizará automaticamente o selo de integridade antes do boot).*

### 3. Rodar os Testes Automatizados da API
Com o servidor rodando em um terminal, abra outro console e execute:
```bash
python scripts/test_client.py
```
O script testará automaticamente o bloqueio de chaves incorretas (HTTP 401), a emissão do Token JWT sob login correto (HTTP 200), o bloqueio de acessos sem token ou com tokens falsos (HTTP 403) e o consumo bem-sucedido com token válido.

