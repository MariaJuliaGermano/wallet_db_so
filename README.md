
# Projeto Carteira Digital 🪙

Este projeto é um *template* inicial para implementar uma **API de Carteira Digital** 
na disciplina Projeto Banco de Dados:

- **FastAPI**
- **MySQL**
- **SQLAlchemy (Core, sem ORM)**
- **SQL puro para DDL/DML**
- Integração com API pública da **Coinbase** para conversão de moedas

A carteira permite:

- Criar carteiras (com chave pública e chave privada)
- Ver saldos por moeda (BTC, ETH, SOL, USD)
- Fazer **depósitos**
- Fazer **saques** (com taxa e validação da chave privada)
- Fazer **conversão entre moedas** (usando cotação da Coinbase)
- Fazer **transferência entre carteiras**

---

## 1. Pré-requisitos

Antes de começar, você precisa ter instalado no seu computador:

- Python 3.10+
- MySQL 8+
- git (opcional)

Verifique as versões:

```bash
python --version
mysql --version
```

---

## 2. Clonar ou baixar o projeto

```bash
git clone https://github.com/timotrob/WalletDb_v2.git
cd projeto_carteira_digital
```

Ou extraia o ZIP e abra o terminal dentro da pasta do projeto.

---

## 3. Criar e ativar o ambiente virtual (venv)

### Windows:
```bash
python -m venv venv
.env\Scripts\Activate
```

### Linux/Mac:
```bash
python3 -m venv venv
source venv/bin/activate
```

---

## 4. Instalar dependências

```bash
pip install -r requirements.txt
```

---

## 5. Criar o banco e usuário no MySQL

Execute:

```sql
SOURCE /sql/DDL_Carteira_Digital.sql;
```

Isso irá:

- Criar o banco `wallet_homolog`
- Criar usuário restrito `wallet_api_homolog`
A Criação das tabelas não está incluindo,
deve ser gerado pelo aluno.

---

## 6. Criar o arquivo `.env`

Crie o arquivo `.env` na raiz do projeto:

```env
DB_HOST=localhost
DB_PORT=3306
DB_USER=wallet_api_homolog
DB_PASSWORD=????
DB_NAME=wallet_homolog
TAXA_SAQUE_PERCENTUAL=0.01
TAXA_CONVERSAO_PERCENTUAL=0.02
TAXA_TRANSFERENCIA_PERCENTUAL=0.01
PRIVATE_KEY_SIZE=32
PUBLIC_KEY_SIZE=16
```

---

## 7. Estrutura do projeto

```
projeto_carteira_digital/
│
├── api/
│   ├── main.py
│   ├── models/
│   ├── routers/
│   ├── services/
│   └── persistence/
│       │── repositories/
│       └── db.py
│
├── sql/DDL_Carteira_Digital.sql
├── requirements.txt
└── .env
```

---

## 8. Subir a API

```bash
uvicorn api.main:app --reload
```

Acesse:

👉 http://127.0.0.1:8000/docs

---

## 9. Testes básicos

### Criar carteira:
POST /carteiras

### Ver saldo:
GET /carteiras/{endereco}/saldos

### Depósito:
POST /carteiras/{endereco}/depositos

### Saque:
POST /carteiras/{endereco}/saques

### Conversão:
POST /carteiras/{endereco}/conversoes

### Transferência:
POST /carteiras/{endereco_origem}/transferencias

---

## 10. Problemas comuns

- Banco não encontrado → conferir `.env`
- MySQL parado → iniciar serviço
- ImportError → verificar `__init__.py`

---

## 11. Boa implementação! 🚀
