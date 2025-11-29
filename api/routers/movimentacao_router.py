from fastapi import APIRouter, Depends, HTTPException, Path
from typing import List

from api.services import carteira_service
from api.services.conversao_service import ConversaoService
from api.services.movimentacao_service import MovimentacaoService
from api.persistence.repositories.movimentacao_repository import MovimentacaoRepository

from api.models.movimentacao_models import (
    SaldoResponse,
    DepositoRequest,
    DepositoResponse,
    SaqueRequest,
    SaqueResponse,
    ConversaoRequest,
    ConversaoResponse,
    TransferenciaRequest,
    TransferenciaResponse
)


router = APIRouter(
    prefix="/carteiras",
    tags=["movimentações"]
)


def get_mov_service() -> MovimentacaoService:
    repo = MovimentacaoRepository()
    return MovimentacaoService(repo)

def get_conv_service() -> ConversaoService:
    repo = MovimentacaoRepository()
    return ConversaoService(repo)


# ===========================
#        SALDO
# ===========================

@router.get("/{endereco}/saldos", response_model=SaldoResponse)
def obter_saldos(endereco: str):
    service = get_mov_service()
    saldos = service.obter_saldos(endereco)
    return {
        "endereco": endereco,
        "saldos": saldos,
        "data_atualizacao": saldos[0]["data_atualizacao"] if saldos else None
    }

# ===========================
#        DEPÓSITO
# ===========================

@router.post("/{endereco}/depositar", response_model=DepositoResponse, status_code=201)
def depositar(
    endereco: str,
    request: DepositoRequest,
    service: MovimentacaoService = Depends(get_mov_service)
):
    try:
        return service.realizar_deposito(endereco, request.valor, request.moeda)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

# ===========================
#        SAQUE
# ===========================

@router.post("/{endereco}/saques", response_model=SaqueResponse, status_code=201)
def sacar(
    endereco: str,
    body: SaqueRequest,
    service: MovimentacaoService = Depends(get_mov_service)
):
    try:
        return service.realizar_saque(endereco, body.valor)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


# ===========================
#        CONVERSÃO
# ===========================

@router.post("/{endereco}/conversoes", response_model=ConversaoResponse)
def converter(endereco: str = Path(...),body: ConversaoRequest = ...,service: ConversaoService = Depends(get_conv_service)
):
    try:
        # usar os campos corretos do body
        result = service.converter(
            endereco,
            body.moeda_origem,
            body.moeda_destino,
            body.valor_origem
        )
        return result
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# ===========================
#       TRANSFERÊNCIA
# ===========================

@router.post("/{endereco_origem}/transferencias", response_model=TransferenciaResponse, status_code=201)
def transferir(
    endereco_origem: str,
    body: TransferenciaRequest,
    service: MovimentacaoService = Depends(get_mov_service)
):
    try:
        return service.realizar_transferencia(
            endereco_origem=endereco_origem,
            endereco_destino=body.endereco_destino,
            valor=body.valor,
        )
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
