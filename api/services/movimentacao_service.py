from datetime import datetime

class MovimentacaoService:
    def __init__(self, repository):
        self.repository = repository

    # ========================
    #      SALDO
    # ========================


# ...existing code...
    def obter_saldo(self, endereco):
        saldos = self.repository.listar_saldos(endereco)
        if not saldos:
            return {
                "endereco": endereco,
                "saldo": 0.0,
                "data_atualizacao": None,
                "saldos": []
            }

        primary = saldos[0]
        return {
            "endereco": endereco,
            "saldo": float(primary["saldo"]),
            "data_atualizacao": primary.get("data_atualizacao"),
            "saldos": [
                {
                    "id_moeda": s["id_moeda"],
                    "saldo": float(s["saldo"]),
                    "data_atualizacao": s["data_atualizacao"],
                }
                for s in saldos
            ],
        }



        return {
            "endereco": endereco,
            "saldos": [
                {
                    "id_moeda": s["id_moeda"],
                    "saldo": float(s["saldo"]),
                    "data_atualizacao": s["data_atualizacao"],
                }
                for s in saldos
            ],
        }

    # ========================
    #      DEPÓSITO
    # ========================
    def realizar_deposito(self, endereco, valor):
        id_moeda = 1           # moeda fixa (exemplo)
        taxa = 0.0             # sem taxa
        tipo = "DEPOSITO"
        saldo_atual = self.repository.obter_saldo(endereco, id_moeda)
        novo_saldo = saldo_atual + valor

        self.repository.atualizar_saldo(endereco, id_moeda, novo_saldo)
        id_mov = self.repository.registrar_movimentacao(
            endereco=endereco,
            id_moeda=id_moeda,
            tipo=tipo,
            valor=valor,
            taxa_valor=taxa
        )

        now = datetime.utcnow()

        return {
            "id_movimento": id_mov,
            "endereco": endereco,
            "endereco_carteira": endereco,
            "id_moeda": id_moeda,
            "tipo": tipo,
            "taxa_valor": taxa,
            "valor": valor,
            "saldo_final": novo_saldo,
            "data_hora": now
        }

    # ========================
    #      SAQUE
    # ========================
    def realizar_saque(self, endereco, valor):
        id_moeda = 1
        taxa = 0.0

        saldo_atual = self.repository.obter_saldo(endereco, id_moeda)
        if saldo_atual < valor:
            raise ValueError("Saldo insuficiente.")
        if  valor<0:
            raise ValueError("Valor inválido.")

        novo_saldo = saldo_atual - valor

        self.repository.atualizar_saldo(endereco, id_moeda, novo_saldo)
        id_mov = self.repository.registrar_movimentacao(
            endereco=endereco,
            id_moeda=id_moeda,
            tipo="SAQUE",
            valor=valor,
            taxa_valor=taxa
        )

        return {
            "id_movimento": id_mov,
            "endereco_carteira": endereco,
            "id_moeda": id_moeda,
            "tipo": "SAQUE",
            "valor": valor,
            "taxa_valor": taxa,
            "data_hora": datetime.now(),
            "saldo_final": novo_saldo
        }

    # ========================
    #      CONVERSÃO
    # ========================
    def realizar_conversao(self, endereco, valor):
        id_moeda_origem = 1
        id_moeda_destino = 2

        saldo_atual = self.repository.obter_saldo(endereco, id_moeda_origem)
        if saldo_atual < valor:
            raise ValueError("Saldo insuficiente.")

        taxa = 0.02
        taxa_valor = valor * taxa
        valor_convertido = valor - taxa_valor
        cotacao = 1.5  # exemplo

        # Atualiza saldos
        self.repository.atualizar_saldo(
            endereco, id_moeda_origem, saldo_atual - valor
        )

        saldo_destino_atual = self.repository.obter_saldo(endereco, id_moeda_destino)
        self.repository.atualizar_saldo(
            endereco, id_moeda_destino, saldo_destino_atual + valor_convertido
        )

        dados = {
            "id_moeda_origem": id_moeda_origem,
            "id_moeda_destino": id_moeda_destino,
            "valor_origem": valor,
            "valor_destino": valor_convertido,
            "taxa_percentual": taxa,
            "taxa_valor": taxa_valor,
            "cotacao_utilizada": cotacao
        }

        id_conv = self.repository.registrar_conversao(endereco, dados)

        return {
            "id_conversao": id_conv,
            "endereco": endereco,
            "valor_convertido": valor_convertido,
        }
        endereco_origem, id_moeda, saldo_origem - valor - taxa_valor
# ========================================
# TRANSFERÊNCIA (CORRIGIDA)
# ========================================
def realizar_transferencia(self, endereco_origem, endereco_destino, valor, chave_privada=None):

    id_moeda = 1
    taxa = 0.02
    taxa_valor = valor * taxa

    # ---------------------------
    # Validações iniciais
    # ---------------------------
    if valor <= 0:
        raise ValueError("Valor da transferência precisa ser positivo.")

    if not endereco_destino:
        raise ValueError("Endereço de destino não pode ser vazio.")

    if chave_privada is None:
        raise ValueError("Chave privada é obrigatória para transferência.")

    # ---------------------------
    # Verificar saldo
    # ---------------------------
    saldo_origem = self.repository.obter_saldo(endereco_origem, id_moeda)
    if saldo_origem < valor + taxa_valor:
        raise ValueError("Saldo insuficiente para transferência.")

    # ---------------------------
    # Realizar transferência
    # ---------------------------
    transferencia = self.repository.realizar_transferencia(
        origem=endereco_origem,
        destino=endereco_destino,
        id_moeda=id_moeda,
        valor=valor,
        taxa_valor=taxa_valor,
        chave_privada=chave_privada
    )

    if not transferencia:
        raise ValueError("Erro ao registrar transferência.")

    return transferencia