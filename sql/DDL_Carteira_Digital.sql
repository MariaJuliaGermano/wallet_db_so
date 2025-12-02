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


    DROP USER IF EXISTS 'wallet_api_homolog'@'%';
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

INSERT INTO moeda (id_moeda, codigo, nome, tipo) VALUES (1, 'BTC', 'Bitcoin', 'crypto');
INSERT INTO moeda (id_moeda, codigo, nome, tipo) VALUES (2, 'USD', 'US Dollar', 'currency');
INSERT INTO moeda (id_moeda, codigo, nome, tipo) VALUES (3, 'ETH', 'Etherium', 'crypto');
INSERT INTO moeda (id_moeda, codigo, nome, tipo) VALUES (4, 'BRL', 'Real brasileiro ', 'currency');
INSERT INTO moeda (id_moeda, codigo, nome, tipo) VALUES (5, 'SOL', 'Solana ', 'crypto');

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

DELIMITER $$

CREATE PROCEDURE sp_realizar_transferencia(
    IN p_origem VARCHAR(255),     
    IN p_destino VARCHAR(255),    
    IN p_moeda SMALLINT,    
    IN p_valor DECIMAL(18, 8),   
    IN p_taxa DECIMAL(18, 8),    
    IN p_chave_privada VARCHAR(255)
)
BEGIN
    DECLARE v_saldo_origem DECIMAL(18, 8);
    DECLARE v_hash_armazenado VARCHAR(255);
    DECLARE v_status_origem VARCHAR(20);
    DECLARE v_existe_destino INT DEFAULT 0;

    DECLARE EXIT HANDLER FOR SQLEXCEPTION
    BEGIN
        ROLLBACK;
        RESIGNAL;
    END;

    START TRANSACTION;

    SELECT 
        C.hash_chave_privada, 
        C.status, 
        S.saldo 
    INTO 
        v_hash_armazenado, 
        v_status_origem, 
        v_saldo_origem
    FROM CARTEIRA C
    LEFT JOIN SALDO_CARTEIRA S 
        ON C.endereco_carteira = S.endereco_carteira 
        AND S.id_moeda = p_moeda
    WHERE C.endereco_carteira = p_origem
    FOR UPDATE;

    SELECT COUNT(*) INTO v_existe_destino
    FROM CARTEIRA 
    WHERE endereco_carteira = p_destino;

    -- ================= VALIDAÇÕES =================

    -- A. Carteira origem existe?
    IF v_hash_armazenado IS NULL THEN
        SIGNAL SQLSTATE '45000' SET MESSAGE_TEXT = 'Erro: Carteira de origem não existe.';

    -- B. Carteira está bloqueada?
    ELSEIF v_status_origem = 'BLOQUEADA' THEN
        SIGNAL SQLSTATE '45000' SET MESSAGE_TEXT = 'Erro: Carteira de origem bloqueada.';

    -- C. Senha confere? (Assumindo comparação direta. Se for hash real, usar SHA2())
    ELSEIF v_hash_armazenado <> p_chave_privada THEN
        SIGNAL SQLSTATE '45000' SET MESSAGE_TEXT = 'Erro: Chave privada incorreta.';

    -- D. Destino existe?
    ELSEIF v_existe_destino = 0 THEN
        SIGNAL SQLSTATE '45000' SET MESSAGE_TEXT = 'Erro: Carteira de destino não existe.';

    -- E. Tem saldo na moeda específica?
    -- (Nota: IFNULL trata caso a pessoa nunca tenha tido saldo naquela moeda, retornando 0)
    ELSEIF IFNULL(v_saldo_origem, 0) < (p_valor + p_taxa) THEN
        SIGNAL SQLSTATE '45000' SET MESSAGE_TEXT = 'Erro: Saldo insuficiente nesta moeda.';

    ELSE
        -- ================= EXECUÇÃO =================

        -- 1. Debitar da Origem (Atualiza SALDO_CARTEIRA)
        UPDATE SALDO_CARTEIRA 
        SET saldo = saldo - (p_valor + p_taxa),
            data_atualizacao = NOW()
        WHERE endereco_carteira = p_origem AND id_moeda = p_moeda;

        -- 2. Creditar no Destino (Upsert - Cria ou Atualiza)
        -- Se o destino não tiver registro dessa moeda, cria. Se tiver, soma.
        INSERT INTO SALDO_CARTEIRA (endereco_carteira, id_moeda, saldo, data_atualizacao)
        VALUES (p_destino, p_moeda, p_valor, NOW())
        ON DUPLICATE KEY UPDATE 
            saldo = saldo + p_valor,
            data_atualizacao = NOW();

        -- 3. Gerar Recibo (Tabela TRANSFERENCIA)
        INSERT INTO TRANSFERENCIA (endereco_origem, endereco_destino, id_moeda, valor, taxa_valor)
        VALUES (p_origem, p_destino, p_moeda, p_valor, p_taxa);

        COMMIT;
        SELECT 'Transferência realizada com sucesso!' AS mensagem;
        
    END IF;

END $$

DELIMITER ;


DELIMITER $$

CREATE PROCEDURE sp_realizar_transferencia(
    IN p_origem VARCHAR(255),     
    IN p_destino VARCHAR(255),    
    IN p_moeda SMALLINT,    
    IN p_valor DECIMAL(18, 8),   
    IN p_taxa DECIMAL(18, 8),    
    IN p_chave_privada VARCHAR(255)
)
BEGIN
    DECLARE v_saldo_origem DECIMAL(18, 8);
    DECLARE v_hash_armazenado VARCHAR(255);
    DECLARE v_status_origem VARCHAR(20);
    DECLARE v_existe_destino INT DEFAULT 0;

    DECLARE EXIT HANDLER FOR SQLEXCEPTION
    BEGIN
        ROLLBACK;
        RESIGNAL;
    END;

    START TRANSACTION;

    SELECT 
        C.hash_chave_privada, 
        C.status, 
        S.saldo 
    INTO 
        v_hash_armazenado, 
        v_status_origem, 
        v_saldo_origem
    FROM CARTEIRA C
    LEFT JOIN SALDO_CARTEIRA S 
        ON C.endereco_carteira = S.endereco_carteira 
        AND S.id_moeda = p_moeda
    WHERE C.endereco_carteira = p_origem
    FOR UPDATE;

    SELECT COUNT(*) INTO v_existe_destino
    FROM CARTEIRA 
    WHERE endereco_carteira = p_destino;

    -- ================= VALIDAÇÕES =================

    -- A. Carteira origem existe?
    IF v_hash_armazenado IS NULL THEN
        SIGNAL SQLSTATE '45000' SET MESSAGE_TEXT = 'Erro: Carteira de origem não existe.';

    -- B. Carteira está bloqueada?
    ELSEIF v_status_origem = 'BLOQUEADA' THEN
        SIGNAL SQLSTATE '45000' SET MESSAGE_TEXT = 'Erro: Carteira de origem bloqueada.';

    -- C. Senha confere? (Assumindo comparação direta. Se for hash real, usar SHA2())
    ELSEIF v_hash_armazenado <> p_chave_privada THEN
        SIGNAL SQLSTATE '45000' SET MESSAGE_TEXT = 'Erro: Chave privada incorreta.';

    -- D. Destino existe?
    ELSEIF v_existe_destino = 0 THEN
        SIGNAL SQLSTATE '45000' SET MESSAGE_TEXT = 'Erro: Carteira de destino não existe.';

    -- E. Tem saldo na moeda específica?
    -- (Nota: IFNULL trata caso a pessoa nunca tenha tido saldo naquela moeda, retornando 0)
    ELSEIF IFNULL(v_saldo_origem, 0) < (p_valor + p_taxa) THEN
        SIGNAL SQLSTATE '45000' SET MESSAGE_TEXT = 'Erro: Saldo insuficiente nesta moeda.';

    ELSE
        -- ================= EXECUÇÃO =================

        -- 1. Debitar da Origem (Atualiza SALDO_CARTEIRA)
        UPDATE SALDO_CARTEIRA 
        SET saldo = saldo - (p_valor + p_taxa),
            data_atualizacao = NOW()
        WHERE endereco_carteira = p_origem AND id_moeda = p_moeda;

        -- 2. Creditar no Destino (Upsert - Cria ou Atualiza)
        -- Se o destino não tiver registro dessa moeda, cria. Se tiver, soma.
        INSERT INTO SALDO_CARTEIRA (endereco_carteira, id_moeda, saldo, data_atualizacao)
        VALUES (p_destino, p_moeda, p_valor, NOW())
        ON DUPLICATE KEY UPDATE 
            saldo = saldo + p_valor,
            data_atualizacao = NOW();

        -- 3. Gerar Recibo (Tabela TRANSFERENCIA)
        INSERT INTO TRANSFERENCIA (endereco_origem, endereco_destino, id_moeda, valor, taxa_valor)
        VALUES (p_origem, p_destino, p_moeda, p_valor, p_taxa);

        COMMIT;
        SELECT 'Transferência realizada com sucesso!' AS mensagem;
        
    END IF;

END $$

DELIMITER ;


SELECT 'Base wallet_homolog e tabelas criadas com sucesso!' AS mensagem;