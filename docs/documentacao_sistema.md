# Documentação Técnica - Core Framework & Orquestrador de Segurança V8

Esta documentação descreve as especificações de engenharia, a arquitetura modular, o fluxo de operação, a segurança de integridade de código (Code Signing), a integração com banco de dados em nuvem e a suíte de testes do **Orquestrador de Segurança V8**.

---

## 1. Visão Geral do Sistema

O **Orquestrador de Segurança V8** é uma infraestrutura centralizada projetada para autenticar, autorizar e monitorar transações entre múltiplos programas em uma arquitetura híbrida (Multi-Tenant).

O sistema é pautado sobre dois pilares fundamentais:
1. **Tranca Tripla (Triple Lock):** Identificação mútua e robusta baseada na validação simultânea de **CNPJ** (Empresa), **CPF** (Operador) e credenciais de segurança (Usuário/Senha).
2. **Selo de Integridade (Code Signing):** Mecanismo de autodefesa que utiliza criptografia assimétrica (RSA) para impedir que o código-fonte seja alterado diretamente em servidores de produção.

---

## 2. Estrutura de Módulos (Subsistemas)

O ecossistema está organizado de forma modular na raiz do projeto `app_geral_login`:

```text
app_geral_login /
├── docs/                      # Documentação técnica detalhada
│   └── documentacao_sistema.md
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
│           └── database_mock.py # Conector de banco de dados (Supabase + fallback local)
│
├── v8_security_gate.py        # Decorador (@secure_gate) para validação de Tokens JWT nas rotas
├── v8_sentinel.py             # Decorador (@validate_gate) e verificação criptográfica do boot
├── init_env.py                # Verificador dinâmico de dependências locais
├── start_all.py               # Orquestrador local de boot de serviços
└── requirements.txt           # Dependências de produção fixadas
```

---

## 3. Integração com Banco de Dados (Supabase + Fallback)

O orquestrador é integrado ao **Supabase (PostgreSQL)** para gerenciar os Tenants e Operadores ativos. A comunicação é realizada de forma segura através do protocolo HTTPS (REST API), o que elimina bloqueios de portas em ambientes restritos (como o PythonAnywhere gratuito).

### Esquema do Banco de Dados (Schema)
* **Tabela `tenants` (Empresas):**
  * `cnpj` (Texto, Chave Primária)
  * `nome_empresa` (Texto)
* **Tabela `operators` (Operadores / Usuários):**
  * `id` (UUID, Chave Primária)
  * `tenant_cnpj` (Texto, Chave Estrangeira para `tenants.cnpj`)
  * `cpf` (Texto)
  * `username` (Texto)
  * `password_hash` (Texto) - Hashes criptográficos gerados com Bcrypt
  * `nome_operador` (Texto)
  * `perfil` (Texto)

### Segurança e Criptografia de Senhas
O sistema não armazena nem trafega senhas em formato aberto na base de dados. Toda validação de autenticação utiliza o algoritmo **Bcrypt** para comparar o hash gravado no banco de dados com a senha enviada pelo chamador.

### Mecanismo de Fallback Local
Se o sistema for iniciado sem as chaves externas configuradas no `.env`, o orquestrador ativa automaticamente um **fallback em memória local** (com hashes Bcrypt locais). Isso garante que o sistema permaneça funcional para testes e desenvolvimento offline, sem prejudicar o ciclo de vida da aplicação.

---

## 4. Funcionamento e Fluxos de Operação

### Fluxo 1: Boot e Autoverificação de Integridade
Antes de disponibilizar qualquer API na rede, o orquestrador valida se o seu próprio código-fonte não foi adulterado.

* O servidor executa `sentinel.verify_integrity()`.
* O validador carrega a chave pública (`public_key.pem`) e a assinatura de segurança (`signature.json`).
* Ele decodifica a assinatura digital e verifica que todos os arquivos `.py` no servidor batem com a chave.
* Caso haja qualquer alteração física em algum script, o boot é abortado com erro.

### Fluxo 2: Autenticação Triple Lock e Emissão de Token (JWT)
Para operar no ecossistema, os programas chamadores precisam autenticar enviando o Triple Lock.

* O chamador faz um POST `/api/v1/auth` enviando CNPJ, CPF, usuário e senha em formato JSON seguro (HTTPS).
* O conector consulta os dados no banco de dados.
* Se as chaves baterem e o hash Bcrypt validar a senha, o orquestrador emite um token JWT de sessão (válido por 1 hora) assinado criptograficamente com a `SECRET_KEY` do servidor.

### Fluxo 3: Consumo de APIs Protegidas
Uma vez de posse do Token JWT, o programa chamador pode efetuar requisições nos endpoints de serviços protegidos.

* O chamador faz um GET na rota protegida enviando o token no header `Authorization: Bearer <token>`.
* O decorador `@secure_gate` intercepta, decodifica o token usando a chave secreta e valida o perfil/permissão de acesso.
* Se correto, a chamada é executada. Caso contrário, retorna HTTP 403 Forbidden.

---

## 5. Segurança de Integridade (Code Sealing)

Para evitar que invasores alterem códigos diretamente no servidor de produção, o orquestrador emprega o processo de **Assinatura de Código Assimétrica**:

* **O Berço (Desenvolvimento):** O desenvolvedor possui a chave privada `private_key.pem`. Toda vez que o projeto é iniciado localmente, o `seal_project.py` gera uma nova assinatura criptográfica no `signature.json`.
* **A Produção (Servidor):** O servidor possui apenas a chave pública `public_key.pem`. A chave pública consegue *verificar* se a assinatura do manifesto é válida, mas **não consegue gerar novas assinaturas**. A chave privada *nunca* deve ser enviada ao servidor de produção.

---

## 6. Guia de Testes

### Preparação do Ambiente
Crie um arquivo `.env` baseado nos placeholders e instale as dependências:
```bash
python init_env.py
```

### Configuração do Banco
Preencha os valores de URL e Chave de Serviço no `.env` para apontar ao seu banco em nuvem. Se deixados em branco, o sistema funcionará no modo simulado local automaticamente.

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
1. Adicione um comentário no final de qualquer script Python do projeto.
2. Tente iniciar o servidor com `python -m src.backend.app`.
3. Verifique que o servidor falhará no boot, abortando com o erro:
   `❌ ERRO CRÍTICO DE INTEGRIDADE: O arquivo foi alterado no servidor: v8_security_gate.py`.
4. Remova o comentário para reestabelecer o funcionamento normal.
