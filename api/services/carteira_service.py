from typing import List

from api.persistence.repositories.carteira_repository import CarteiraRepository
from api.models.carteira_models import Carteira, CarteiraCriada


class CarteiraService:
    def __init__(self, carteira_repo: CarteiraRepository):
        self.carteira_repo = carteira_repo

    def criar_carteira(self) -> CarteiraCriada:
        row = self.carteira_repo.criar()
        # row tem: endereco_carteira, data_criacao, status, hash_chave_privada, chave_privada
        # não expomos o hash
        return CarteiraCriada(
            endereco_carteira=row["endereco_carteira"],
            data_criacao=row["data_criacao"],
            status=row["status"],
            chave_privada=row["chave_privada"],
        )

    def buscar_por_endereco(self, endereco_carteira: str) -> Carteira:
        row = self.carteira_repo.buscar_por_endereco(endereco_carteira)
        if not row:
            raise ValueError("Carteira não encontrada")

        return Carteira(
            endereco_carteira=row["endereco_carteira"],
            data_criacao=row["data_criacao"],
            status=row["status"],
        )

    def listar(self) -> List[Carteira]:
        rows = self.carteira_repo.listar()
        return [
            Carteira(
                endereco_carteira=r["endereco_carteira"],
                data_criacao=r["data_criacao"],
                status=r["status"],
            )
            for r in rows
        ]

    def bloquear(self, endereco_carteira: str) -> Carteira:
        row = self.carteira_repo.atualizar_status(endereco_carteira, "BLOQUEADA")
        if not row:
            raise ValueError("Carteira não encontrada")

        return Carteira(
            endereco_carteira=row["endereco_carteira"],
            data_criacao=row["data_criacao"],
            status=row["status"],
        )