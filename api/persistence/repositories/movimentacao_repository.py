from datetime import datetime
import hashlib
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
    def registrar_movimentacao(self, endereco: str, id_moeda: int, tipo: str, valor: float, taxa_valor: float) -> None:
        """
        Registra movimentação + atualiza saldo (depósito ou saque).
        quantidade > 0 = depósito
        quantidade < 0 = saque
        """

        with get_connection() as conn:

            # Inserir movimentação
            conn.execute(
                text("""
                    INSERT INTO DEPOSITO_SAQUE
                        (endereco_carteira, id_moeda, tipo, valor, taxa_valor, data_hora)
                    VALUES (:endereco, :id_moeda, :tipo, :valor, :taxa_valor, NOW())
                """),
                {
                    "endereco": endereco,
                    "id_moeda": id_moeda,
                    "tipo": tipo,
                    "valor": valor,
                    "taxa_valor": taxa_valor,
                },
            )

            # Atualizar saldo
            item = conn.execute(text("SELECT LAST_INSERT_ID() AS id_movimento")).mappings().first()
            return item["id_movimento"] if item else None

    # ---------------- ATUALIZAR SALDO DIRETO ----------------
    def atualizar_saldo(self, endereco, id_moeda, valor_final):
        with get_connection() as conn:
            query = text("""
                INSERT INTO saldo_carteira (endereco_carteira, id_moeda, saldo, data_atualizacao)
                VALUES (:endereco, :id_moeda, :valor_final, NOW())
                ON DUPLICATE KEY UPDATE
                    saldo = :valor_final,
                    data_atualizacao = NOW()
            """)

            conn.execute(query, {
                "endereco": endereco,
                "id_moeda": id_moeda,
                "valor_final": valor_final
            })
            
    def obter_id_moeda(self, codigo: str) -> Any:   
        with get_connection() as conn:
            query = text("""
                SELECT id_moeda
                FROM moeda
                WHERE codigo = :codigo
            """)

            result = conn.execute(query, {"codigo": codigo}).fetchone()
            return result[0] if result is not None else None
       
       

        # ---------------- CONSULTA SALDO ATUAL ----------------
    def obter_saldo(self, endereco, id_moeda):
        with get_connection() as conn:
            query = text("""
                SELECT saldo
                FROM saldo_carteira
                WHERE endereco_carteira = :endereco
                AND id_moeda = :id_moeda
            """)

            result = conn.execute(query, {
                "endereco": endereco,
                "id_moeda": id_moeda
            }).fetchone()

            if result is not None:
                return float(result[0])
            return 0.0


        # ---------------- CONVERSÃO ----------------
    def registrar_conversao(self, endereco, c):
        with get_connection() as conn:
            
            query = text("""
                INSERT INTO conversao
                    (endereco_carteira, id_moeda_origem, id_moeda_destino, valor_origem,
                    valor_destino, taxa_percentual, taxa_valor, cotacao_utilizada, data_hora)
                VALUES (:endereco, :origem, :destino, :valor_origem,
                        :valor_destino, :taxa_percentual, :taxa_valor, :cotacao, NOW())
            """)

            result = conn.execute(query, {
                "endereco": endereco,
                "origem": c["id_moeda_origem"],
                "destino": c["id_moeda_destino"],
                "valor_origem": c["valor_origem"],
                "valor_destino": c["valor_destino"],
                "taxa_percentual": c["taxa_percentual"],
                "taxa_valor": c["taxa_valor"],
                "cotacao": c["cotacao_utilizada"]
            })

            return result.lastrowid
    # ========================================
    #  VALIDAÇÃO CHAVE
    # ========================================

    def verificar_chave_privada(self, endereco, chave_input):
        with get_connection() as conn: 
            sql = text("""SELECT hash_chave_privada FROM CARTEIRA WHERE endereco_carteira = :endereco""")
            resultado = conn.execute(sql, {"endereco": endereco}).fetchone()
            

        if not resultado:
            return False
            
        hash_armazenado = resultado[0]
        hash_input = hashlib.sha256(chave_input.encode()).hexdigest()
        return hash_input == hash_armazenado

    # ========================================
    # TRANSFERÊNCIA 
    # ========================================
    def registrar_transferencia(self, origem, destino, id_moeda, valor, taxa_valor, saldo_origem, saldo_destino):
        with get_connection() as conn:

            conn.execute(
                    text("""
                    INSERT INTO saldo_carteira (endereco_carteira, id_moeda, saldo, data_atualizacao)
                    VALUES (:endereco, :id_moeda, :saldo, NOW())
                    ON DUPLICATE KEY UPDATE saldo = :saldo, data_atualizacao = NOW()
                    """),
                    {"endereco": origem, "id_moeda": id_moeda, "saldo": saldo_origem}
                )
            
            conn.execute(
                    text("""
                    INSERT INTO saldo_carteira (endereco_carteira, id_moeda, saldo, data_atualizacao)
                    VALUES (:endereco, :id_moeda, :saldo, NOW())
                    ON DUPLICATE KEY UPDATE saldo = :saldo, data_atualizacao = NOW()
                    """),
                    {"endereco": destino, "id_moeda": id_moeda, "saldo": saldo_destino}
                )

            query = text("""
                INSERT INTO transferencia
                    (endereco_origem, endereco_destino, id_moeda, valor,
                    taxa_valor, data_hora)
                VALUES (:endereco_origem, :endereco_destino, :id_moeda, :valor,
                        :taxa_valor, NOW())
            """)

            result = conn.execute(query, {
                "endereco_origem": origem,
                "endereco_destino": destino,
                "id_moeda": id_moeda,
                "valor": valor,
                "taxa_valor": taxa_valor,
            })

            return result.lastrowid


