from fastapi import APIRouter, HTTPException, Path
from api.models.movimentacao_models import ConversaoRequest
from api.services.conversao_service import ConversaoService

router = APIRouter(
    prefix="/carteiras",
    tags=["Conversões"]
)

service = ConversaoService()

@router.post("/{endereco}/conversoes", status_code=201)
def converter(endereco: str = Path(...), request: ConversaoRequest = None):
    try:
        return service.converter(endereco, request)
    except Exception as e:
        raise HTTPException(status_code=422, detail=str(e))
