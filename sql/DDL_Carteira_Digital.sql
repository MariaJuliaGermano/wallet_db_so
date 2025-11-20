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

-- =========================================================
--  Tabelas (Aluno deve fazer o modelo)
-- =========================================================














-- ================================
--  CRIAÇÃO DO BANCO
-- ================================
CREATE DATABASE IF NOT EXISTS wallet_homolog;
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
-- ================================
--  TABELA MOEDA
-- ================================
CREATE TABLE MOEDA (
    id INT AUTO_INCREMENT PRIMARY KEY,
    sigla VARCHAR(10) UNIQUE NOT NULL
);

-- POPULAR MOEDAS OBRIGATÓRIAS
INSERT INTO MOEDA (sigla) VALUES
('BTC'),
('ETH'),
('SOL'),
('USD');

-- ================================
--  TABELA SALDO_CARTEIRA
-- ================================
CREATE TABLE SALDO_CARTEIRA (
    id INT AUTO_INCREMENT PRIMARY KEY,
    carteira_id INT NOT NULL,
    moeda_id INT NOT NULL,
    saldo DECIMAL(18,8) DEFAULT 0,
    FOREIGN KEY (carteira_id) REFERENCES CARTEIRA(id),
    FOREIGN KEY (moeda_id) REFERENCES MOEDA(id),
    UNIQUE (carteira_id, moeda_id)
);

-- ================================
--  TABELA DEPOSITO_SAQUE
-- ================================
CREATE TABLE DEPOSITO_SAQUE (
    id INT AUTO_INCREMENT PRIMARY KEY,
    carteira_id INT NOT NULL,
    moeda_id INT NOT NULL,
    valor DECIMAL(18,8) NOT NULL,
    tipo ENUM('DEPOSITO', 'SAQUE') NOT NULL,
    taxa DECIMAL(18,8),
    data DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (carteira_id) REFERENCES CARTEIRA(id),
    FOREIGN KEY (moeda_id) REFERENCES MOEDA(id)
);

-- ================================
--  TABELA CONVERSAO
-- ================================
CREATE TABLE CONVERSAO (
    id INT AUTO_INCREMENT PRIMARY KEY,
    carteira_id INT NOT NULL,
    moeda_origem_id INT NOT NULL,
    moeda_destino_id INT NOT NULL,
    valor_origem DECIMAL(18,8) NOT NULL,
    valor_destino DECIMAL(18,8) NOT NULL,
    taxa_conversao DECIMAL(18,8),
    data DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (carteira_id) REFERENCES CARTEIRA(id),
    FOREIGN KEY (moeda_origem_id) REFERENCES MOEDA(id),
    FOREIGN KEY (moeda_destino_id) REFERENCES MOEDA(id)
);

-- ================================
--  TABELA TRANSFERENCIA
-- ================================
CREATE TABLE TRANSFERENCIA (
    id INT AUTO_INCREMENT PRIMARY KEY,
    carteira_origem INT NOT NULL,
    carteira_destino INT NOT NULL,
    moeda_id INT NOT NULL,
    valor DECIMAL(18,8) NOT NULL,
    taxa DECIMAL(18,8),
    data DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (carteira_origem) REFERENCES CARTEIRA(id),
    FOREIGN KEY (carteira_destino) REFERENCES CARTEIRA(id),
    FOREIGN KEY (moeda_id) REFERENCES MOEDA(id)
);

-- ================================
-- TUDO CRIADO COM SUCESSO
-- ================================
SELECT 'Base wallet_homolog e tabelas criadas com sucesso!' AS mensagem;