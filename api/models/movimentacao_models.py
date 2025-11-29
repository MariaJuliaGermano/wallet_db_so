from pydantic import BaseModel, Field, PositiveFloat
from datetime import datetime
from typing import List, Optional


# ---------- SALDO ----------
class Saldo(BaseModel):
    id_moeda: int
    saldo: float
    data_atualizacao: datetime


# ---------- DEPÓSITO / SAQUE ----------
class MovimentoBase(BaseModel):
    id_moeda: int
    valor: float

class DepositoRequest(BaseModel):
    valor: float
    moeda: str


class MovimentoCriado(BaseModel):
    id_movimento: int
    endereco_carteira: str
    id_moeda: int
    tipo: str       # "deposito" ou "saque"
    valor: float
    taxa_valor: float
    data_hora: datetime


# ---------- CONVERSÃO ----------
class ConversaoBase(BaseModel):
    id_moeda_origem: int
    id_moeda_destino: int
    valor_origem: float


class ConversaoCriada(BaseModel):
    id_conversao: int
    endereco_carteira: str
    id_moeda_origem: int
    id_moeda_destino: int
    valor_origem: float
    valor_destino: float
    taxa_percentual: float
    taxa_valor: float
    cotacao_utilizada: float
    data_hora: datetime


# ---------- TRANSFERÊNCIA ----------
class TransferenciaBase(BaseModel):
    endereco_destino: str
    id_moeda: int
    valor: float


class TransferenciaCriada(BaseModel):
    id_transferencia: int
    endereco_origem: str
    endereco_destino: str
    id_moeda: int
    valor: float
    taxa_valor: float
    data_hora: datetime


from pydantic import BaseModel
from datetime import datetime
from typing import Optional


# ------------ Requests ------------
class DepositoRequest(BaseModel):
    valor: float
    moeda: str


class SaqueRequest(BaseModel):
    valor: float
    chave_privada: str


class ConversaoRequest(BaseModel):
    moeda_origem: str = Field(..., description="Código da moeda de origem, ex: BTC")
    moeda_destino: str = Field(..., description="Código da moeda destino, ex: BRL")
    valor_origem: PositiveFloat = Field(..., description="Valor a debitar na moeda origem (positivo)")


class TransferenciaRequest(BaseModel):
    endereco_destino: str
    valor: float
    chave_privada: str


# ------------ Responses ------------
class MovimentacaoResponse(BaseModel):
    id: int
    tipo: str
    endereco_origem: str
    endereco_destino: Optional[str]
    valor: float
    data_movimentacao: datetime

class SaldoItem(BaseModel):
    moeda: str
    saldo: float
    data_atualizacao: Optional[str]

class SaldoResponse(BaseModel):
    endereco: str
    saldos: List[SaldoItem]
    data_atualizacao: Optional[str]

class DepositoResponse(BaseModel):
    id_movimento: int
    endereco_carteira: str
    id_moeda: int
    tipo: str
    valor: float
    taxa_valor: float
    saldo_final: float
    data_hora: datetime
class SaqueResponse(BaseModel):
    id_movimento: int
    endereco_carteira: str
    id_moeda: int
    tipo: str
    valor: float
    taxa_valor: float
    data_hora: datetime
class ConversaoResponse(BaseModel):
    id_conversao: int
    endereco_carteira: str
    id_moeda_origem: int
    id_moeda_destino: int
    valor_origem: float
    valor_destino: float
    taxa_percentual: float
    taxa_valor: float
    cotacao_utilizada: float
    data_hora: datetime

class TransferenciaResponse(BaseModel):
    id_transferencia: int
    endereco_origem: str
    endereco_destino: str
    id_moeda: int
    valor: float
    taxa_valor: float
    data_hora: datetime

    