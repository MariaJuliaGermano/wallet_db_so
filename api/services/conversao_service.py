from decimal import Decimal, getcontext, ROUND_DOWN
from email.mime import text
from api.persistence.repositories.movimentacao_repository import MovimentacaoRepository
from api.persistence.db import get_connection
import os
import requests

getcontext().prec = 28  

class ConversaoService:
    def __init__(self):
        self.repo = MovimentacaoRepository()
        self.conv_repo = MovimentacaoRepository()
        self.taxa_percentual = Decimal(os.getenv("TAXA_CONVERSAO_PERCENTUAL", "0.02"))

    def get_cotacao_coinbase(self, codigo_origem):
        base = os.getenv("COINBASE_API_BASE", "https://api.coinbase.com/v2")
        url = f"{base}/exchange-rates?currency={codigo_origem}"
        r =requests.get(url, timeout=5)
        r.raise_for_status()
        data = r.json()
        return data["data"]["rates"]
    
    def converter(self, endereco, req):
        id_origem = self.conv_repo.obter_id_moeda_por_codigo(req.moeda_origem)
        id_destino = self.conv_repo.obter_id_moeda_por_codigo(req.moeda_destino)
        if id_origem is None or id_destino is None:
            raise ValueError("Moeda origem ou destino inválida.")
        
        saldo_origem = Decimal(str(self.repo.obter_saldo(endereco, id_origem)))
        valor_origem = Decimal(str(req.valor_origem))

        if valor_origem <= 0:
            raise ValueError("Valor deve ser positivo.")
        
        if saldo_origem < valor_origem:
            raise ValueError("Saldo insuficiente.")
        
        rates = self.get_cotacao_coinbase(req.moeda_origem)
        if req.moeda_destino not in rates:
            raise ValueError("Cotação para moeda destino não encontrada.")
        
        cotacao_str = rates[req.moeda_destino]
        cotacao = Decimal(cotacao_str)

        valor_destino = (valor_origem * cotacao).quantize(Decimal('0.00000001'), rounding=ROUND_DOWN)
        taxa_percentual = self.taxa_percentual
        taxa_valor = (valor_origem * taxa_percentual).quantize(Decimal('0.00000001'), rounding=ROUND_DOWN)

        novo_saldo_origem = (saldo_origem - valor_origem).quantize(Decimal('0.00000001'), rounding=ROUND_DOWN)
        if novo_saldo_origem < 0:
            raise ValueError("Saldo insuficiente após aplicar a taxa.")
        
        saldo_destino = Decimal(str(self.repo.obter_saldo(endereco, id_destino)))   
        novo_saldo_destino = (saldo_destino + (valor_origem - taxa_valor) * cotacao).quantize(Decimal('0.00000001'), rounding=ROUND_DOWN)

        with get_connection() as conn:
            trans = conn.begin()
            try:
                conn.execute(
                    """
                    INSERT INTO saldo_carteira (endereco_carteira, id_moeda, saldo, data_atualizacao)
                    VALUES (:endereco, :id_moeda, :saldo, NOW())
                    ON DUPLICATE KEY UPDATE saldo = :saldo, data_atualizacao = NOW()
                    """,
                    {"endereco": endereco, "id_moeda": id_origem, "saldo": float(novo_saldo_origem)}
                )
                conn.execute(
                    """
                    INSERT INTO saldo_carteira (endereco_carteira, id_moeda, saldo, data_atualizacao)
                    VALUES (:endereco, :id_moeda, :saldo, NOW())
                    ON DUPLICATE KEY UPDATE saldo = :saldo, data_atualizacao = NOW()
                    """,
                    {"endereco": endereco, "id_moeda": id_destino, "saldo": float(novo_saldo_destino)}
                )

                q = text("""
    INSERT INTO conversao
        (endereco_carteira, id_moeda_origem, id_moeda_destino, valor_origem,
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
                    "cotacao": float(cotacao)
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
            "data_hora": None
        }