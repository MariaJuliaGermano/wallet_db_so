from typing import List, Dict, Any
from sqlalchemy import text
from api.persistence.db import get_connection


class MovimentacaoRepository:

    # ---------------- SALDOS ----------------
    def listar_saldos(self, endereco: str) -> List[Dict[str, Any]]:
        with get_connection() as conn:
            query = text("""
                SELECT id_moeda,
                       endereco_carteira,
                       saldo,
                       data_atualizacao
                  FROM saldo_carteira
                 WHERE endereco_carteira = :endereco
            """)

            result = conn.execute(query, {"endereco": endereco}).mappings().all()
            return [dict(r) for r in result]

    # ---------------- DEPÓSITO / SAQUE ----------------
    def registrar_movimentacao(self, endereco: str, id_moeda: int, quantidade: float) -> None:
        """
        Registra movimentação + atualiza saldo (depósito ou saque).
        quantidade > 0 = depósito
        quantidade < 0 = saque
        """

        with get_connection() as conn:

            # Inserir movimentação
            conn.execute(
                text("""
                    INSERT INTO movimentacoes (endereco_carteira, id_moeda, quantidade)
                    VALUES (:endereco, :id_moeda, :quantidade)
                """),
                {"endereco": endereco, "id_moeda": id_moeda, "quantidade": quantidade},
            )

            # Atualizar saldo
            conn.execute(
                text("""
                    UPDATE saldo_carteira
                       SET saldo = saldo + :quantidade,
                           data_atualizacao = CURRENT_TIMESTAMP
                     WHERE endereco_carteira = :endereco
                       AND id_moeda = :id_moeda
                """),
                {"endereco": endereco, "id_moeda": id_moeda, "quantidade": quantidade},
            )

    # ---------------- ATUALIZAR SALDO DIRETO ----------------
    def atualizar_saldo(self, endereco, id_moeda, valor_final):
        conn = get_connection()
        cursor = conn.cursor()

        query = """
            INSERT INTO saldo_carteira (endereco_carteira, id_moeda, saldo, data_atualizacao)
            VALUES (%s, %s, %s, NOW())
            ON DUPLICATE KEY UPDATE saldo = VALUES(saldo), data_atualizacao = NOW()
        """

        cursor.execute(query, (endereco, id_moeda, valor_final))
        cursor.close()
        conn.close()

    # ---------------- CONSULTA SALDO ATUAL ----------------
    def obter_saldo(self, endereco, id_moeda):
        conn = get_connection()
        cursor = conn.cursor()

        query = """
            SELECT saldo
              FROM saldo_carteira
             WHERE endereco_carteira = %s AND id_moeda = %s
        """

        cursor.execute(query, (endereco, id_moeda))
        result = cursor.fetchone()

        cursor.close()
        conn.close()

        if result:
            return float(result[0])
        return 0.0

    # ---------------- CONVERSÃO ----------------
    def registrar_conversao(self, endereco, c):
        conn = get_connection()
        cursor = conn.cursor(dictionary=True)

        query = """
            INSERT INTO conversao
            (endereco_carteira, id_moeda_origem, id_moeda_destino, valor_origem, 
             valor_destino, taxa_percentual, taxa_valor, cotacao_utilizada, data_hora)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, NOW())
        """

        cursor.execute(query, (
            endereco,
            c["id_moeda_origem"],
            c["id_moeda_destino"],
            c["valor_origem"],
            c["valor_destino"],
            c["taxa_percentual"],
            c["taxa_valor"],
            c["cotacao_utilizada"]
        ))
        cursor.execute("SELECT LAST_INSERT_ID() AS id_conversao")
        item = cursor.fetchone()

        cursor.close()
        conn.close()
        return item["id_conversao"]

    # ---------------- TRANSFERÊNCIA ----------------
    def registrar_transferencia(self, origem, destino, id_moeda, valor, taxa_valor):
        conn = get_connection()
        cursor = conn.cursor(dictionary=True)

        query = """
            INSERT INTO transferencia
                (endereco_origem, endereco_destino, id_moeda, valor, taxa_valor, data_hora)
            VALUES (%s, %s, %s, %s, %s, NOW())
        """

        cursor.execute(query, (origem, destino, id_moeda, valor, taxa_valor))
        cursor.execute("SELECT LAST_INSERT_ID() AS id_transferencia")
        item = cursor.fetchone()

        cursor.close()
        conn.close()
        return item["id_transferencia"]
