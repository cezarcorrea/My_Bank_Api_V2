# 🚀 GUIA DE IMPLEMENTAÇÃO - Quick Start

## 📋 Checklist de Implementação

### ✅ Pré-requisitos
- [ ] Python 3.11+
- [ ] Poetry ou pip instalados
- [ ] Git
- [ ] VS Code ou editor preferido

---

## 🔧 1. Instalação Inicial

### Passo 1: Clonar/Atualizar Projeto
```bash
cd My_Bank_Api
git pull origin main  # Se usar git
```

### Passo 2: Instalar Dependências
```bash
# Com Poetry (recomendado)
poetry install

# Ou com pip
pip install -r requirements.txt
```

**Verificar instalação:**
```bash
python -c "import slowapi; print('✓ slowapi instalado')"
```

---

## 🔐 2. Configurar Variáveis de Ambiente

### Passo 1: Editar `.env`
```bash
# Abrir arquivo .env
code .env

# Verificar conteúdo (deve ter):
ENVIRONMENT="local"
DATABASE_URL="sqlite:///./bank.db"
JWT_SECRET="your-secret-key-change-in-production"  # ⚠️ MUDAR ISTO!
JWT_ALGORITHM="HS256"
JWT_EXPIRATION_HOURS=0.25
JWT_REFRESH_EXPIRATION_DAYS=7
MAX_LOGIN_ATTEMPTS=5
LOGIN_ATTEMPT_WINDOW=3600
RATE_LIMIT_REQUESTS=100
RATE_LIMIT_PERIOD=60
```

### Passo 2: Gerar Secret Seguro (Produção)
```bash
# Python
python -c "import secrets; print(secrets.token_urlsafe(32))"

# Bash
openssl rand -base64 32

# Resultará em algo como:
# wB7_zQ4kJpXmN9hR2cF5vL3sT8dY6gB1aZ0eX9pL2kM=
```

---

## 🗄️ 3. Executar Migrations

```bash
# Ver status atual
alembic current

# Executar todas as migrations
alembic upgrade head

# Verificar se funcionou
alembic current

# Deve mostrar:
# INFO  [alembic.runtime.migration] Running upgrade 45492ce1fbf6 -> 8a1b2c3d4e5f
```

---

## 🚀 4. Iniciar Aplicação

### Terminal 1: Iniciar Server
```bash
# Modo desenvolvimento (com reload automático)
poetry run uvicorn src.main:app --reload

# Ou direto
uvicorn src.main:app --reload --log-level info

# Deve mostrar:
# INFO:     Uvicorn running on http://127.0.0.1:8000
# INFO:     Iniciando aplicação...
# INFO:     Conectado ao banco de dados
```

### Verificar no navegador
```
http://localhost:8000/docs
```

---

## ✅ 5. Testar Melhorias Implementadas

### 5.1 Health Check
```bash
curl http://localhost:8000/health

# Esperado:
# {
#   "status": "healthy",
#   "database": "connected",
#   "version": "2.0.0"
# }
```

### 5.2 Login com Refresh Token
```bash
curl -X POST http://localhost:8000/auth/login \
  -H "Content-Type: application/json" \
  -d '{"user_id": 1}'

# Esperado:
# {
#   "access_token": "eyJ0eXAiOiJKV1QiLCJhbGc...",
#   "refresh_token": "eyJ0eXAiOiJKV1QiLCJhbGc...",
#   "token_type": "bearer",
#   "expires_in": 900
# }
```

### 5.3 Usar Token de Acesso
```bash
# Salvar token (copiar de cima)
export ACCESS_TOKEN="eyJ0eXAiOiJKV1QiLCJhbGc..."

# Listar contas
curl http://localhost:8000/accounts/?limit=5 \
  -H "Authorization: Bearer $ACCESS_TOKEN"

# Esperado:
# []  ou lista de contas
```

### 5.4 Criar Nova Conta
```bash
curl -X POST http://localhost:8000/accounts/ \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer $ACCESS_TOKEN" \
  -d '{
    "user_id": 123,
    "balance": 1000.00
  }'

# Esperado:
# {
#   "id": 1,
#   "user_id": 123,
#   "balance": "1000.00",
#   "created_at": "2026-01-11T12:00:00+00:00"
# }
```

### 5.5 Criar Transação
```bash
curl -X POST http://localhost:8000/transactions/ \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer $ACCESS_TOKEN" \
  -d '{
    "account_id": 1,
    "type": "deposit",
    "amount": 500.00
  }'

# Esperado:
# {
#   "id": 1,
#   "account_id": 1,
#   "type": "deposit",
#   "amount": "500.00",
#   "timestamp": "2026-01-11T12:00:00+00:00"
# }
```

### 5.6 Listar Todas Transações (NOVA ROTA)
```bash
curl http://localhost:8000/transactions/?limit=10 \
  -H "Authorization: Bearer $ACCESS_TOKEN"

# Esperado:
# [
#   {
#     "id": 1,
#     "account_id": 1,
#     "type": "deposit",
#     "amount": "500.00",
#     "timestamp": "2026-01-11T12:00:00+00:00"
#   }
# ]
```

### 5.7 Obter Transação por ID (NOVA ROTA)
```bash
curl http://localhost:8000/transactions/1 \
  -H "Authorization: Bearer $ACCESS_TOKEN"

# Esperado:
# {
#   "id": 1,
#   "account_id": 1,
#   "type": "deposit",
#   "amount": "500.00",
#   "timestamp": "2026-01-11T12:00:00+00:00"
# }
```

### 5.8 Testar Rate Limiting
```bash
# Fazer 101+ requisições em 1 minuto
for i in {1..110}; do 
  curl -s http://localhost:8000/health | jq '.status'
done

# Esperado:
# - Primeiras 100: "healthy"
# - 101+: 429 Too Many Requests
```

### 5.9 Testar Validação de Paginação
```bash
# Limite muito alto (será limitado a 100)
curl "http://localhost:8000/accounts/?limit=1000" \
  -H "Authorization: Bearer $ACCESS_TOKEN"

# Validação no Swagger automática
```

### 5.10 Testar Conta Duplicada
```bash
# Criar conta 1
curl -X POST http://localhost:8000/accounts/ \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer $ACCESS_TOKEN" \
  -d '{"user_id": 999, "balance": 1000}'

# Tentar criar conta 2 com mesmo user_id
curl -X POST http://localhost:8000/accounts/ \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer $ACCESS_TOKEN" \
  -d '{"user_id": 999, "balance": 2000}'

# Esperado 409 Conflict:
# {
#   "detail": "Conta já existe para o usuário 999"
# }
```

---

## 📊 6. Monitorar Logs

### Ver Logs em Tempo Real
```bash
# Terminal 2 (enquanto server rodando)
tail -f logs/api.log

# Ou via stderr (padrão)
# Verá mensagens como:
# 2026-01-11 12:00:00 - src.security - INFO - Token access gerado para user_id=1
# 2026-01-11 12:00:01 - src.services.account - INFO - Listadas 1 contas
```

### Ver Logs Estruturados
```python
# Em src/main.py (já configurado):
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
```

---

## 🔧 7. Troubleshooting

### Problema: `ModuleNotFoundError: No module named 'slowapi'`
```bash
# Solução:
pip install slowapi
# ou
poetry install
```

### Problema: `JWT_SECRET not found`
```bash
# Verificar .env
cat .env | grep JWT_SECRET

# Se não tiver, adicionar:
echo 'JWT_SECRET="sua-chave-secreta"' >> .env

# Reiniciar aplicação
```

### Problema: `database.disconnect() error`
```bash
# Verificar migration
alembic current

# Fazer downgrade se necessário
alembic downgrade -1
alembic upgrade head
```

### Problema: Porta 8000 em uso
```bash
# Usar outra porta
uvicorn src.main:app --reload --port 8001
```

### Problema: Banco de dados locked
```bash
# Remover banco antigo
rm bank.db

# Reexecutar migrations
alembic upgrade head
```

---

## 📚 8. Próximos Passos

### Leitura Recomendada
1. **README.md** - Documentação completa de todas as 12 melhorias
2. **MELHORIAS_RESUMO.md** - Resumo executivo rápido
3. **CHANGELOG.md** - Histórico de mudanças

### Implementações Futuras
- [ ] Testes automatizados (pytest)
- [ ] Documentação OpenAPI melhorada
- [ ] Integração com Redis para cache
- [ ] Autenticação com OAuth2
- [ ] Testes de carga (locust)
- [ ] Containerização (Docker)
- [ ] CI/CD pipeline (GitHub Actions)

### Melhorias Recomendadas
- [ ] Adicionar CORS mais restritivo
- [ ] Implementar HTTPS em produção
- [ ] Adicionar APM (New Relic, Datadog)
- [ ] Implementar backup automático
- [ ] Adicionar testes de integração

---

## 🎯 9. Checklist Final

- [ ] Dependências instaladas (`poetry install`)
- [ ] `.env` configurado com JWT_SECRET
- [ ] Migrations executadas (`alembic upgrade head`)
- [ ] Server iniciado sem erros
- [ ] Health check retorna 200
- [ ] Login funciona e retorna tokens
- [ ] Transações podem ser criadas e listadas
- [ ] Rate limiting funciona (429 após limite)
- [ ] Logs aparecem em tempo real
- [ ] README.md lido e compreendido

---

## 📞 Suporte

Se encontrar problemas:

1. **Verificar logs:**
   ```bash
   grep "ERROR\|WARNING" logs/
   ```

2. **Testar conexão BD:**
   ```bash
   curl http://localhost:8000/health
   ```

3. **Validar migrations:**
   ```bash
   alembic current
   alembic branches
   ```

4. **Reiniciar tudo:**
   ```bash
   # Terminal 1: Parar server (Ctrl+C)
   # Remover cache
   find . -type d -name __pycache__ -exec rm -r {} +
   # Reiniciar
   uvicorn src.main:app --reload
   ```

---

**Versão:** 2.0.0  
**Última Atualização:** 11 de Janeiro de 2026  
**Status:** ✅ Pronto para Uso
