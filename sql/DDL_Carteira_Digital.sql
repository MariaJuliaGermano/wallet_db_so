USE wallet_homolog;

-- ================================
--  TABELA CARTEIRA (Nome ajustado para minúsculo)
-- ================================
CREATE TABLE IF NOT EXISTS carteira (
    id INT AUTO_INCREMENT PRIMARY KEY,
    endereco_carteira VARCHAR(255) UNIQUE NOT NULL,
    hash_chave_privada VARCHAR(255) NOT NULL,
    data_criacao DATETIME DEFAULT NOW(),
    status ENUM ('ATIVA' , 'BLOQUEADA') default 'ATIVA' 
);

-- ===========================
--   TABELA: MOEDA
-- ===========================
CREATE TABLE IF NOT EXISTS moeda (
    id_moeda SMALLINT PRIMARY KEY AUTO_INCREMENT,
    codigo VARCHAR(10) NOT NULL UNIQUE,
    nome VARCHAR(50) NOT NULL,
    tipo VARCHAR(10) NOT NULL
);

INSERT INTO moeda (id_moeda, codigo, nome, tipo) VALUES 
(1, 'BTC', 'Bitcoin', 'crypto'),
(2, 'USD', 'US Dollar', 'currency'),
(3, 'ETH', 'Etherium', 'crypto'),
(4, 'BRL', 'Real brasileiro ', 'currency'),
(5, 'SOL', 'Solana ', 'crypto');

-- ===========================
--   TABELA: SALDO_CARTEIRA
-- ===========================
CREATE TABLE IF NOT EXISTS saldo_carteira (
    endereco_carteira VARCHAR(255) NOT NULL,
    id_moeda SMALLINT NOT NULL,
    saldo DECIMAL(18,8) DEFAULT 0,
    data_atualizacao DATETIME DEFAULT CURRENT_TIMESTAMP,

    PRIMARY KEY (endereco_carteira, id_moeda),

    FOREIGN KEY (endereco_carteira)
        REFERENCES carteira(endereco_carteira)
        ON DELETE CASCADE,

    FOREIGN KEY (id_moeda)
        REFERENCES moeda(id_moeda)
);

-- ===========================
--   TABELA: DEPOSITO_SAQUE
-- ===========================
CREATE TABLE IF NOT EXISTS deposito_saque (
    id_movimento BIGINT PRIMARY KEY AUTO_INCREMENT,
    endereco_carteira VARCHAR(100) NOT NULL,
    id_moeda SMALLINT NOT NULL,
    tipo VARCHAR(20) NOT NULL,
    valor DECIMAL(18,8) NOT NULL,
    taxa_valor DECIMAL(18,8) DEFAULT 0,
    data_hora DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,

    FOREIGN KEY (endereco_carteira) REFERENCES carteira(endereco_carteira),
    FOREIGN KEY (id_moeda) REFERENCES moeda(id_moeda)
);

-- ===========================
--   TABELA: CONVERSAO
-- ===========================
CREATE TABLE IF NOT EXISTS conversao (
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

    FOREIGN KEY (endereco_carteira) REFERENCES carteira(endereco_carteira),
    FOREIGN KEY (id_moeda_origem) REFERENCES moeda(id_moeda),
    FOREIGN KEY (id_moeda_destino) REFERENCES moeda(id_moeda)
);

-- ===========================
--   TABELA: TRANSFERENCIA
-- ===========================
CREATE TABLE IF NOT EXISTS transferencia (
    id_transferencia BIGINT PRIMARY KEY AUTO_INCREMENT,
    endereco_origem VARCHAR(100) NOT NULL,
    endereco_destino VARCHAR(100) NOT NULL,
    id_moeda SMALLINT NOT NULL,
    valor DECIMAL(18,8) NOT NULL,
    taxa_valor DECIMAL(18,8) NOT NULL,
    data_hora DATETIME DEFAULT CURRENT_TIMESTAMP,

    FOREIGN KEY (endereco_origem) REFERENCES carteira(endereco_carteira),
    FOREIGN KEY (endereco_destino) REFERENCES carteira(endereco_carteira),
    FOREIGN KEY (id_moeda) REFERENCES moeda(id_moeda)
);