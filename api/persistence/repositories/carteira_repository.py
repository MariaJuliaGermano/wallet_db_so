import os
import secrets
import hashlib
from typing import Dict, Any, Optional, List

from sqlalchemy import text

from api.persistence.db import get_connection


class CarteiraRepository:
    """
    Acesso a dados da carteira usando SQLAlchemy Core + SQL puro.
    """

    def criar(self) -> Dict[str, Any]:
        """
        Gera chave pública, chave privada, salva no banco (apenas hash da privada)
        e retorna os dados da carteira + chave privada em claro.
        """
        # 1) Geração das chaves
        private_key_size:int = int(os.getenv("PRIVATE_KEY_SIZE"))
        public_key_size:int = int(os.getenv("PUBLIC_KEY_SIZE"))
        chave_privada = secrets.token_hex(private_key_size)      # 32 bytes -> 64 hex chars (configurável depois)
        endereco = secrets.token_hex(public_key_size)           # "chave pública" simplificada
        hash_privada = hashlib.sha256(chave_privada.encode()).hexdigest()

        with get_connection() as conn:
            # 2) INSERT
            conn.execute(
                text("""
                    INSERT INTO carteira (endereco_carteira, hash_chave_privada)
                    VALUES (:endereco, :hash_privada)
                """),
                {"endereco": endereco, "hash_privada": hash_privada},
            )

            conn.execute(
                text("""
                    INSERT INTO saldo_carteira (endereco_carteira, id_moeda, saldo, data_atualizacao)
                    VALUES (:endereco, 1, 0.0, NOW(),)
                    VALUES (:endereco, 2, 0.0, NOW(),)
                    VALUES (:endereco, 3, 0.0, NOW(),)
                    VALUES (:endereco, 4, 0.0, NOW(),)
                    VALUES (:endereco, 5, 0.0, NOW(),)
                """),
                {"endereco": endereco, "id_moeda": 1, "saldo": 0.0, "data_atualizacao": "NOW()"},
                {"endereco": endereco, "id_moeda": 2, "saldo": 0.0, "data_atualizacao": "NOW()"},
                {"endereco": endereco, "id_moeda": 3, "saldo": 0.0, "data_atualizacao": "NOW()"},
                {"endereco": endereco, "id_moeda": 4, "saldo": 0.0, "data_atualizacao": "NOW()"},
                {"endereco": endereco, "id_moeda": 5, "saldo": 0.0, "data_atualizacao": "NOW()"},
            )

            # 3) SELECT para retornar a carteira criada
            row = conn.execute(
                text("""
                    SELECT endereco_carteira,
                        data_criacao,
                        status,
                        hash_chave_privada
                        FROM carteira
                        WHERE endereco_carteira = :endereco
                """),
                {"endereco": endereco, "id_moeda": 1, "saldo": 0.0, "data_atualizacao": "NOW()"},
                {"endereco": endereco, "id_moeda": 2, "saldo": 0.0, "data_atualizacao": "NOW()"},
                {"endereco": endereco, "id_moeda": 3, "saldo": 0.0, "data_atualizacao": "NOW()"},
                {"endereco": endereco, "id_moeda": 4, "saldo": 0.0, "data_atualizacao": "NOW()"},
                {"endereco": endereco, "id_moeda": 5, "saldo": 0.0, "data_atualizacao": "NOW()"},
            ).mappings().first()

        carteira = dict(row)
        carteira["chave_privada"] = chave_privada
        return carteira

    def buscar_por_endereco(self, endereco_carteira: str) -> Optional[Dict[str, Any]]:
        with get_connection() as conn:
            row = conn.execute(
                text("""
                    SELECT endereco_carteira,
                           data_criacao,
                           status,
                           hash_chave_privada
                      FROM carteira
                     WHERE endereco_carteira = :endereco
                """),
                {"endereco": endereco_carteira},
            ).mappings().first()

        return dict(row) if row else None

    def listar(self) -> List[Dict[str, Any]]:
        with get_connection() as conn:
            rows = conn.execute(
                text("""
                    SELECT endereco_carteira,
                           data_criacao,
                           status,
                           hash_chave_privada
                      FROM carteira
                """)
            ).mappings().all()

        return [dict(r) for r in rows]

    def atualizar_status(self, endereco_carteira: str, status: str) -> Optional[Dict[str, Any]]:
        with get_connection() as conn:
            conn.execute(
                text("""
                    UPDATE carteira
                       SET status = :status
                     WHERE endereco_carteira = :endereco
                """),
                {"status": status, "endereco": endereco_carteira},
            )

            row = conn.execute(
                text("""
                    SELECT endereco_carteira,
                           data_criacao,
                           status,
                           hash_chave_privada
                      FROM carteira
                     WHERE endereco_carteira = :endereco
                """),
                {"endereco": endereco_carteira},
            ).mappings().first()

        return dict(row) if row else None
    
    