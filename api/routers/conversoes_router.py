from fastapi import APIRouter, Depends, HTTPException, Path
from api.models.movimentacao_models import ConversaoRequest, ConversaoResponse
from api.persistence.repositories.movimentacao_repository import MovimentacaoRepository
from api.services.conversao_service import ConversaoService
from api.services.movimentacao_service import MovimentacaoService

router = APIRouter(
    prefix="/carteiras",
    tags=["Conversões"]
)

def get_conv_service() -> ConversaoService:
    repo = MovimentacaoRepository()
    return ConversaoService(repo)


@router.post("/{endereco}/conversoes", response_model=ConversaoResponse)
def converter(endereco: str = Path(...), body: ConversaoRequest = ..., service: ConversaoService = Depends(get_conv_service)):
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
