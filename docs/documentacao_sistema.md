# Documentação Técnica - Core Framework & Orquestrador de Segurança V8

Esta documentação descreve as especificações de engenharia, a arquitetura modular, o fluxo de operação, a segurança física de código (Code Signing) e o manual de testes do **Orquestrador de Segurança V8**.

---

## 1. Visão Geral do Sistema

O **Orquestrador de Segurança V8** é uma infraestrutura centralizada projetada para autenticar, autorizar e monitorar transações entre múltiplos programas em uma arquitetura híbrida (Multi-Tenant).

O sistema é pautado sobre dois pilares fundamentais:
1. **Tranca Tripla (Triple Lock):** Identificação mútua e indestrutível baseada na validação simultânea de **CNPJ** (Empresa), **CPF** (Operador) e credenciais de segurança (Usuário/Senha).
2. **Selo de Integridade (Code Signing):** Mecanismo de autodefesa que utiliza criptografia assimétrica (RSA) para impedir que o código-fonte seja alterado diretamente em servidores de produção.

---

## 2. Estrutura de Módulos (Subsistemas)

O ecossistema está organizado de forma modular na raiz do projeto `app_geral_login`:

```text
app_geral_login /
├── scripts/
│   ├── seal_project.py        # Calcula hashes e gera o selo criptográfico com chave privada
│   └── test_client.py         # Simulador de chamadas de API do cliente
│
├── src/
│   └── backend/
│       ├── app.py             # Servidor API Flask (Autenticação e endpoints protegidos)
│       ├── core/
│       │   ├── exceptions.py  # Exceção customizada (V8SecurityException)
│       │   └── secure_loader.py # Carregador de ambiente (.env) e logging do sistema
│       └── database/
│           └── database_mock.py # Base de dados mockada de Tenants/Operadores
│
├── v8_security_gate.py        # Decorador (@secure_gate) para validação de Tokens JWT nas rotas
├── v8_sentinel.py             # Decorador (@validate_gate) e verificação criptográfica do boot
├── init_env.py                # Verificador dinâmico de dependências locais
├── start_all.py               # Orquestrador local de boot de serviços
└── requirements.txt           # Dependências de produção fixadas
```

---

## 3. Funcionamento e Fluxos de Operação

### Fluxo 1: Boot e Autoverificação de Integridade
Antes de disponibilizar qualquer API na rede, o orquestrador valida se o seu próprio código-fonte não foi adulterado.

* O servidor é disparado e executa `sentinel.verify_integrity()`.
* O validador carrega a chave pública (`public_key.pem`) e a assinatura de segurança (`signature.json`).
* Ele decodifica a assinatura digital e verifica que todos os arquivos `.py` no servidor batem exatamente com a chave.
* Caso haja qualquer alteração física em algum script, o boot é abortado com erro.

### Fluxo 2: Autenticação Triple Lock e Emissão de Chave (Token JWT)
Para operar no ecossistema, os programas chamadores precisam "pedir permissão" fornecendo o Triple Lock.

* O chamador faz um POST `/api/v1/auth` enviando CNPJ, CPF, usuário e senha.
* O orquestrador valida na base de dados (`database_mock.py`).
* Se válidos, gera um token JWT criptograficamente assinado com validade de 1 hora e retorna ao chamador.

### Fluxo 3: Consumo de APIs Protegidas
Uma vez de posse do Token JWT, o programa chamador pode efetuar requisições nos endpoints de serviços protegidos.

* O chamador faz um GET na rota protegida enviando o token no header `Authorization: Bearer <token>`.
* O decorador `@secure_gate` intercepta, decodifica o token usando a chave secreta e valida o perfil/permissão de acesso.
* Se correto, a chamada é executada. Caso contrário, retorna HTTP 403 Forbidden.

---

## 4. Segurança de Integridade (Code Sealing)

Para evitar que invasores ou desenvolvedores alterem códigos diretamente no servidor de produção (bypassando travas de segurança), o orquestrador emprega o processo de **Assinatura de Código Assemétrica**:

* **O Berço (Desenvolvimento):** O desenvolvedor possui a chave privada `private_key.pem`. Toda vez que o projeto é iniciado, o `seal_project.py` re-sela o projeto gerando uma nova assinatura criptográfica no `signature.json`.
* **A Produção (Servidor):** O servidor possui apenas a chave pública `public_key.pem`. A chave pública consegue *verificar* se a assinatura do manifesto é válida, mas **não consegue gerar novas assinaturas**.
* **Proteção:** Se o código de qualquer arquivo `.py` foi modificado na produção, o hash calculado em runtime será diferente do hash guardado no manifesto. O invasor não pode re-assinar o manifesto porque não possui a chave privada.

---

## 5. Guia de Testes

### Preparação do Ambiente
Execute a inicialização para instalar dependências e efetuar a limpeza inicial:
```bash
python init_env.py
```

### Execução do Servidor
Inicie o orquestrador:
```bash
python -m src.backend.app
```

### Teste de APIs (Fluxo do Cliente)
Em outro console, execute o cliente de simulação:
```bash
python scripts/test_client.py
```

### Teste de Invasão (Anti-Tamper)
1. Abra o arquivo `v8_security_gate.py` e adicione uma linha de comentário vazia no final.
2. Tente iniciar o servidor com `python -m src.backend.app`.
3. Verifique que o servidor falhará no boot, abortando com o erro:
   `❌ ERRO CRÍTICO DE INTEGRIDADE: O arquivo foi alterado no servidor: v8_security_gate.py`.
4. Remova o comentário para reestabelecer o funcionamento normal.
