from datetime import datetime
from decimal import ROUND_DOWN, Decimal
import os
import requests
from sqlalchemy import text
from api.persistence.db import get_connection

class MovimentacaoService:
    def __init__(self, repository):
        self.repository = repository

    # ========================
    #      SALDO
    # ========================

    def obter_saldos(self, endereco):
        with get_connection() as conn:
            result = conn.execute(text("""
                SELECT 
                    m.codigo AS moeda,
                    COALESCE(s.saldo, 0) AS saldo,
                    s.data_atualizacao
                FROM moeda m
                LEFT JOIN saldo_carteira s 
                    ON m.id_moeda = s.id_moeda 
                    AND s.endereco_carteira = :endereco
                ORDER BY m.id_moeda
            """), {"endereco": endereco}).fetchall()
            
            return [
                {
                    "moeda": row.moeda,
                    "saldo": float(row.saldo),
                    "data_atualizacao": str(row.data_atualizacao)
                }
                for row in result
            ]


    # ========================
    #      DEPÓSITO
    # ========================
    def realizar_deposito(self, endereco, valor, codigo):
        if valor <= 0:
            raise ValueError("O valor do depósito deve ser maior que zero")

        id_moeda = self.repository.obter_id_moeda(codigo)
        if id_moeda is None:
            raise ValueError(f"Moeda '{codigo}' não encontrada")

        tipo = "DEPOSITO"
        taxa = 0.0

        saldo_atual = self.repository.obter_saldo(endereco, id_moeda) or 0.0
        novo_saldo = saldo_atual + valor

        self.repository.atualizar_saldo(endereco, id_moeda, novo_saldo)

        id_mov = self.repository.registrar_movimentacao(
            endereco=endereco,
            id_moeda=id_moeda,
            tipo=tipo,
            valor=valor,
            taxa_valor=taxa
        )

        now = datetime.utcnow()

        return {
    "id_movimento": id_mov,
    "endereco_carteira": endereco,
    "id_moeda": id_moeda,
    "tipo": tipo,
    "valor": valor,
    "taxa_valor": taxa,
    "saldo_final": novo_saldo,
    "data_hora": now
}

    # ========================
    #      SAQUE
    # ========================
    def realizar_saque(self, endereco, valor):
        id_moeda = 1
        taxa = 0.0

        saldo_atual = self.repository.obter_saldo(endereco, id_moeda)
        if saldo_atual < valor:
            raise ValueError("Saldo insuficiente.")
        if  valor<0:
            raise ValueError("Valor inválido.")

        novo_saldo = saldo_atual - valor

        self.repository.atualizar_saldo(endereco, id_moeda, novo_saldo)
        id_mov = self.repository.registrar_movimentacao(
            endereco=endereco,
            id_moeda=id_moeda,
            tipo="SAQUE",
            valor=valor,
            taxa_valor=taxa
        )

        return {
            "id_movimento": id_mov,
            "endereco_carteira": endereco,
            "id_moeda": id_moeda,
            "tipo": "SAQUE",
            "valor": valor,
            "taxa_valor": taxa,
            "data_hora": datetime.now(),
            "saldo_final": novo_saldo
        }

    # ========================
    #      CONVERSÃO
    # ========================
    def converter(self, endereco: str, moeda_origem: str, moeda_destino: str, valor_origem: float):
        id_origem = self.repository.obter_id_moeda(moeda_origem)
        id_destino = self.repository.obter_id_moeda(moeda_destino)
        if id_origem is None or id_destino is None:
            raise ValueError("Moeda origem ou destino inválida.")
        
        saldo_origem = Decimal(str(self.repository.obter_saldo(endereco, id_origem)))
        valor_origem = Decimal(str(valor_origem))

        if valor_origem <= 0:
            raise ValueError("Valor deve ser positivo.")
        
        if saldo_origem < valor_origem:
            raise ValueError("Saldo insuficiente.")
        
        rates = self.get_cotacao_coinbase(moeda_origem)
        if moeda_destino not in rates:
            raise ValueError("Cotação para moeda destino não encontrada.")
        
        cotacao_str = rates[moeda_destino]
        cotacao = Decimal(cotacao_str)

        valor_destino = (valor_origem * cotacao).quantize(Decimal('0.00000001'), rounding=ROUND_DOWN)
        taxa_percentual = self.taxa_percentual
        taxa_valor = (valor_origem * taxa_percentual).quantize(Decimal('0.00000001'), rounding=ROUND_DOWN)

        novo_saldo_origem = (saldo_origem - valor_origem).quantize(Decimal('0.00000001'), rounding=ROUND_DOWN)
        if novo_saldo_origem < 0:
            raise ValueError("Saldo insuficiente após aplicar a taxa.")
        
        saldo_destino = Decimal(str(self.repository.obter_saldo(endereco, id_destino)))   
        novo_saldo_destino = (saldo_destino + (valor_origem - taxa_valor) * cotacao).quantize(Decimal('0.00000001'), rounding=ROUND_DOWN)

        with get_connection() as conn:
            trans = conn.begin()
            try:
                conn.execute(
                    text("""
                    INSERT INTO saldo_carteira (endereco_carteira, id_moeda, saldo, data_atualizacao)
                    VALUES (:endereco, :id_moeda, :saldo, NOW())
                    ON DUPLICATE KEY UPDATE saldo = :saldo, data_atualizacao = NOW()
                    """),
                    {"endereco": endereco, "id_moeda": id_origem, "saldo": float(novo_saldo_origem)}
                )
                conn.execute(
                    text("""
                    INSERT INTO saldo_carteira (endereco_carteira, id_moeda, saldo, data_atualizacao)
                    VALUES (:endereco, :id_moeda, :saldo, NOW())
                    ON DUPLICATE KEY UPDATE saldo = :saldo, data_atualizacao = NOW()
                    """),
                    {"endereco": endereco, "id_moeda": id_destino, "saldo": float(novo_saldo_destino)}
                )

                q = text("""
                        INSERT INTO conversao(endereco_carteira, id_moeda_origem, id_moeda_destino, valor_origem,
                            valor_destino, taxa_percentual, taxa_valor, cotacao_utilizada, data_hora)
                        VALUES (:endereco, :origem, :destino, :valor_origem,
                            :valor_destino, :taxa_percentual, :taxa_valor, :cotacao, NOW())
                    """)

                conn.execute(q, {
                    "endereco": endereco,
                    "origem": id_origem,
                    "destino": id_destino,
                    "valor_origem": float(valor_origem),
                    "valor_destino": float(valor_destino),
                    "taxa_percentual": float(taxa_percentual),
                    "taxa_valor": float(taxa_valor),
                    "cotacao": float(cotacao),
                    "data_hora": datetime.utcnow()
                })
                last = conn.execute(text("SELECT LAST_INSERT_ID() AS id_conversao")).fetchone()
                id_conversao = int(last[0]) if last else None

                trans.commit()
            except Exception:
                trans.rollback()
                raise

        return {
            "id_conversao": id_conversao,
            "endereco_carteira": endereco,
            "id_moeda_origem": id_origem,
            "id_moeda_destino": id_destino,
            "valor_origem": str(valor_origem),
            "valor_destino": str(valor_destino),
            "taxa_percentual": str(taxa_percentual),
            "taxa_valor": str(taxa_valor),
            "cotacao_utilizada": str(cotacao),
            "data_hora":  datetime.utcnow().isoformat()
        }
    
    def get_cotacao_coinbase(self, codigo_origem):
        base = os.getenv("COINBASE_API_BASE", "https://api.coinbase.com/v2")
        url = f"{base}/exchange-rates?currency={codigo_origem}"
        r =requests.get(url, timeout=5)
        r.raise_for_status()
        data = r.json()
        return data["data"]["rates"]
        endereco_origem, id_moeda, saldo_origem - valor - taxa_valor
# ========================================
# TRANSFERÊNCIA (CORRIGIDA)
# ========================================
    def realizar_transferencia(self, endereco_origem, endereco_destino, valor, chave_privada=None):

        id_moeda = 1
        taxa = 0.02
        taxa_valor = valor * taxa

        # ---------------------------
        # Validações iniciais
        # ---------------------------
        if valor <= 0:
            raise ValueError("Valor da transferência precisa ser positivo.")

        if not endereco_destino:
            raise ValueError("Endereço de destino não pode ser vazio.")

        if chave_privada is None:
            raise ValueError("Chave privada é obrigatória para transferência.")

        # ---------------------------
        # Verificar saldo
        # ---------------------------
        saldo_origem = self.repository.obter_saldo(endereco_origem, id_moeda)
        if saldo_origem < valor + taxa_valor:
            raise ValueError("Saldo insuficiente para transferência.")

        # ---------------------------
        # Realizar transferência
        # ---------------------------
        transferencia = self.repository.realizar_transferencia(
            origem=endereco_origem,
            destino=endereco_destino,
            id_moeda=id_moeda,
            valor=valor,
            taxa_valor=taxa_valor,
            chave_privada=chave_privada
        )

        if not transferencia:
            raise ValueError("Erro ao registrar transferência.")

        return transferencia