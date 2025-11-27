from fastapi import APIRouter

router = APIRouter(
    prefix="/deposito-saques",
    tags=["Depósitos e Saques"]
)

@router.get("/teste")
def teste():
    return {"mensagem": "deposito_saques_router está funcionando ✅"}
