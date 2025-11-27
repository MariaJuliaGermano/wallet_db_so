-- =========================================================
--  Script de criação da base, usuário,
--  Projeto: Carteira Digital
--  Banco:   MySQL 8+
-- =========================================================

-- 1) Criação da base de homologação
CREATE DATABASE IF NOT EXISTS wallet_homolog
    DEFAULT CHARACTER SET utf8mb4
    DEFAULT COLLATE utf8mb4_0900_ai_ci;

-- 2) Criação do usuário restrito para a API
--    (ajuste a senha conforme necessário)


    CREATE USER 'wallet_api_homolog'@'%' IDENTIFIED BY 'api123';
    GRANT SELECT, INSERT, UPDATE, DELETE ON wallet_homolog.* TO'wallet_api_homolog'@'%';
    FLUSH PRIVILEGES;

-- 3) Grants: apenas DML (sem CREATE/DROP/ALTER)
GRANT SELECT, INSERT, UPDATE, DELETE
    ON wallet_homolog.*
    TO 'wallet_api_homolog'@'%';

FLUSH PRIVILEGES;

-- 4) Usar a base
USE wallet_homolog;

-- ================================
--  TABELA CARTEIRA
-- ================================
CREATE TABLE CARTEIRA (
    id INT AUTO_INCREMENT PRIMARY KEY,
    endereco_carteira VARCHAR(255) UNIQUE NOT NULL,
    hash_chave_privada VARCHAR(255) NOT NULL,
    data_criacao DATETIME DEFAULT NOW(),
    status ENUM ('ATIVA' , 'BLOQUEADA') default 'ATIVA' 
);


-- ===========================
--   TABELA: MOEDA
-- ===========================
CREATE TABLE MOEDA (
    id_moeda SMALLINT PRIMARY KEY AUTO_INCREMENT,
    codigo VARCHAR(10) NOT NULL UNIQUE,
    nome VARCHAR(50) NOT NULL,
    tipo VARCHAR(10) NOT NULL
);

-- ===========================
--   TABELA: SALDO_CARTEIRA
-- ===========================
CREATE TABLE SALDO_CARTEIRA (
    endereco_carteira VARCHAR(255) NOT NULL,
    id_moeda SMALLINT NOT NULL,
    saldo DECIMAL(18,8) DEFAULT 0,
    data_atualizacao DATETIME DEFAULT CURRENT_TIMESTAMP,

    PRIMARY KEY (endereco_carteira, id_moeda),

    FOREIGN KEY (endereco_carteira)
        REFERENCES CARTEIRA(endereco_carteira)
        ON DELETE CASCADE,

    FOREIGN KEY (id_moeda)
        REFERENCES MOEDA(id_moeda)
);

-- ===========================
--   TABELA: DEPOSITO_SAQUE
-- ===========================
CREATE TABLE DEPOSITO_SAQUE (
    id_movimento BIGINT PRIMARY KEY AUTO_INCREMENT,
    endereco_carteira VARCHAR(100) NOT NULL,
    id_moeda SMALLINT NOT NULL,
    tipo VARCHAR(20) NOT NULL,  -- "DEPOSITO" ou "SAQUE"
    valor DECIMAL(18,8) NOT NULL,
    taxa_valor DECIMAL(18,8) DEFAULT 0,
    data_hora DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,

    FOREIGN KEY (endereco_carteira)
        REFERENCES CARTEIRA(endereco_carteira),

    FOREIGN KEY (id_moeda)
        REFERENCES MOEDA(id_moeda)
);

-- ===========================
--   TABELA: CONVERSAO
-- ===========================
CREATE TABLE CONVERSAO (
    id_conversao BIGINT PRIMARY KEY AUTO_INCREMENT,
    endereco_carteira VARCHAR(100) NOT NULL,
    id_moeda_origem SMALLINT NOT NULL,
    id_moeda_destino SMALLINT NOT NULL,
    valor_origem DECIMAL(18,8) NOT NULL,
    valor_destino DECIMAL(18,8) NOT NULL,
    taxa_percentual DECIMAL(18,8) NOT NULL,
    taxa_valor DECIMAL(18,8) NOT NULL,
    cotacao_utilizada DECIMAL(18,8) NOT NULL,
    data_hora DATETIME DEFAULT CURRENT_TIMESTAMP,

    FOREIGN KEY (endereco_carteira)
        REFERENCES CARTEIRA(endereco_carteira),

    FOREIGN KEY (id_moeda_origem)
        REFERENCES MOEDA(id_moeda),

    FOREIGN KEY (id_moeda_destino)
        REFERENCES MOEDA(id_moeda)
);

-- ===========================
--   TABELA: TRANSFERENCIA
-- ===========================
CREATE TABLE TRANSFERENCIA (
    id_transferencia BIGINT PRIMARY KEY AUTO_INCREMENT,
    endereco_origem VARCHAR(100) NOT NULL,
    endereco_destino VARCHAR(100) NOT NULL,
    id_moeda SMALLINT NOT NULL,
    valor DECIMAL(18,8) NOT NULL,
    taxa_valor DECIMAL(18,8) NOT NULL,
    data_hora DATETIME DEFAULT CURRENT_TIMESTAMP,

    FOREIGN KEY (endereco_origem)
        REFERENCES CARTEIRA(endereco_carteira),

    FOREIGN KEY (endereco_destino)
        REFERENCES CARTEIRA(endereco_carteira),

    FOREIGN KEY (id_moeda)
        REFERENCES MOEDA(id_moeda)
);

SELECT 'Base wallet_homolog e tabelas criadas com sucesso!' AS mensagem;