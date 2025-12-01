from fastapi import APIRouter, Depends, HTTPException
from typing import List

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


# ===========================
#        SALDO
# ===========================

@router.get("/{endereco}/saldos", response_model=SaldoResponse)
def obter_saldo(
    endereco: str,
    service: MovimentacaoService = Depends(get_mov_service)
):
    try:
        return service.obter_saldo(endereco)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))


# ===========================
#        DEPÓSITO
# ===========================

@router.post("/{endereco}/depositos", response_model=DepositoResponse, status_code=201)
def depositar(
    endereco: str,
    body: DepositoRequest,
    service: MovimentacaoService = Depends(get_mov_service)
):
    try:
        return service.realizar_deposito(endereco, body.valor)
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

@router.post("/{endereco}/conversoes", response_model=ConversaoResponse, status_code=201)
def converter(
    endereco: str,
    body: ConversaoRequest,
    service: MovimentacaoService = Depends(get_mov_service)
):
    try:
        return service.realizar_conversao(endereco, body.valor)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


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
           chave_privada=body.chave_privada  #modificado
)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
