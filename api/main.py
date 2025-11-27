from fastapi import FastAPI
from api.routers import conversao_router
from api.routers.conversoes_router import router as conversoes_router
from api.routers.carteira_router import router as carteira_router
from api.routers.movimentacao_router import router as movimentacao_router
from api.routers.deposito_saques_router import router as deposito_saques_router
from api.routers.transferencia_router import router as transferencia_router
from api.routers.saldo_carteira_router import router as saldo_carteira_router
from api.routers.moeda_router import router as moeda_router

def create_app() -> FastAPI:
    app = FastAPI(
        title="Carteira Digital API",
        version="1.0.0",
        description="API educacional de carteira digital com SQL puro e FastAPI.",
    )

    app.include_router(carteira_router)
    app.include_router(movimentacao_router)
    app.include_router(conversao_router.router)  # ✅ CORRIGIDO
    app.include_router(conversoes_router)
    app.include_router(deposito_saques_router)
    app.include_router(transferencia_router)
    app.include_router(saldo_carteira_router)
    app.include_router(moeda_router)

    return app

app = create_app()

@app.get("/")
def hello_root():
    return {"message": "Hello World"}