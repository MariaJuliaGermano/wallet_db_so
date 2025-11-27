from pydantic import BaseModel, Field, PositiveFloat
from datetime import datetime
from typing import Optional


# ---------- SALDO ----------
class Saldo(BaseModel):
    id_moeda: int
    saldo: float
    data_atualizacao: datetime


# ---------- DEPÓSITO / SAQUE ----------
class MovimentoBase(BaseModel):
    id_moeda: int
    valor: float


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


class SaqueRequest(BaseModel):
    valor: float
    chave_privada: str


class ConversaoRequest(BaseModel):
    moeda_origem: str = Field(..., example="BTC")
    moeda_destino: str = Field(..., example="USD")
    valor: PositiveFloat = Field(..., example=0.001)

    chave_privada: str | None = Field(None, description="Chave privada exigida se a regra requer autenticação.")



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


class SaldoResponse(BaseModel):
    endereco: str
    saldo: float
    data_atualizacao: datetime

class DepositoResponse(BaseModel):
    id_movimento: int
    endereco_carteira: str
    id_moeda: int
    tipo: str
    valor: float
    taxa_valor: float
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

    