from datetime import datetime
from decimal import Decimal, getcontext, ROUND_DOWN
from email.mime import text
from api.persistence.repositories.movimentacao_repository import MovimentacaoRepository
from api.persistence.db import get_connection
import os
import requests

getcontext().prec = 28  

class ConversaoService:
    def __init__(self, repository: MovimentacaoRepository):
        self.repository = repository
        self.taxa_percentual = Decimal(os.getenv("TAXA_CONVERSAO_PERCENTUAL", "0.02"))

    def get_cotacao_coinbase(self, codigo_origem):
        base = os.getenv("COINBASE_API_BASE", "https://api.coinbase.com/v2")
        url = f"{base}/exchange-rates?currency={codigo_origem}"
        for tentativa in range(3):
            try:    
                    r =requests.get(url, timeout=15)
                    r.raise_for_status()
                    data = r.json()
                    return data["data"]["rates"]
            except Exception:
                if tentativa == 2:
                    raise 
        raise ValueError("Não foi possível obter as cotações da Coinbase")
    
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

        try:
            with get_connection() as conn:
                self.repository.atualizar_saldo(endereco, id_origem, novo_saldo_origem)
                self.repository.atualizar_saldo(endereco, id_destino, novo_saldo_destino)

                self.repository.registrar_movimentacao(endereco, id_origem, "CONVERSAO", -valor_origem, taxa_valor)
                self.repository.registrar_movimentacao(endereco, id_destino, "CONVERSAO", valor_destino, 0.0)

                id_conversao = self.repository.registrar_conversao(endereco, {
                    "id_moeda_origem": id_origem,
                    "id_moeda_destino": id_destino,
                    "valor_origem": float(valor_origem),
                    "valor_destino": float(valor_destino),
                    "taxa_percentual": float(self.taxa_percentual),
                    "taxa_valor": float(taxa_valor),
                    "cotacao_utilizada": float(cotacao)
                })

        except Exception:
            conn.rollback()
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