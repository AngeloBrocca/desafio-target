"""Desafio - 3 programas em Python (apenas biblioteca padrão)."""
import json
from datetime import date, datetime
from decimal import Decimal, ROUND_HALF_UP
from itertools import count

CENTAVOS = Decimal("0.01")


def moeda(valor: Decimal) -> str:
    """Formata como R$ 1.234,56"""
    v = f"{valor.quantize(CENTAVOS, ROUND_HALF_UP):,.2f}"
    return "R$ " + v.replace(",", "X").replace(".", ",").replace("X", ".")


# --------------------------------------------------------------------------
# 1) COMISSÃO DE VENDEDORES
# --------------------------------------------------------------------------
VENDAS_JSON = """
{"vendas": [
{"vendedor": "João Silva", "valor": 1200.50}, {"vendedor": "João Silva", "valor": 950.75},
{"vendedor": "João Silva", "valor": 1800.00}, {"vendedor": "João Silva", "valor": 1400.30},
{"vendedor": "João Silva", "valor": 1100.90}, {"vendedor": "João Silva", "valor": 1550.00},
{"vendedor": "João Silva", "valor": 1700.80}, {"vendedor": "João Silva", "valor": 250.30},
{"vendedor": "João Silva", "valor": 480.75},  {"vendedor": "João Silva", "valor": 320.40},
{"vendedor": "Maria Souza", "valor": 2100.40}, {"vendedor": "Maria Souza", "valor": 1350.60},
{"vendedor": "Maria Souza", "valor": 950.20},  {"vendedor": "Maria Souza", "valor": 1600.75},
{"vendedor": "Maria Souza", "valor": 1750.00}, {"vendedor": "Maria Souza", "valor": 1450.90},
{"vendedor": "Maria Souza", "valor": 400.50},  {"vendedor": "Maria Souza", "valor": 180.20},
{"vendedor": "Maria Souza", "valor": 90.75},
{"vendedor": "Carlos Oliveira", "valor": 800.50},  {"vendedor": "Carlos Oliveira", "valor": 1200.00},
{"vendedor": "Carlos Oliveira", "valor": 1950.30}, {"vendedor": "Carlos Oliveira", "valor": 1750.80},
{"vendedor": "Carlos Oliveira", "valor": 1300.60}, {"vendedor": "Carlos Oliveira", "valor": 300.40},
{"vendedor": "Carlos Oliveira", "valor": 500.00},  {"vendedor": "Carlos Oliveira", "valor": 125.75},
{"vendedor": "Ana Lima", "valor": 1000.00}, {"vendedor": "Ana Lima", "valor": 1100.50},
{"vendedor": "Ana Lima", "valor": 1250.75}, {"vendedor": "Ana Lima", "valor": 1400.20},
{"vendedor": "Ana Lima", "valor": 1550.90}, {"vendedor": "Ana Lima", "valor": 1650.00},
{"vendedor": "Ana Lima", "valor": 75.30},   {"vendedor": "Ana Lima", "valor": 420.90},
{"vendedor": "Ana Lima", "valor": 315.40}
]}
"""


def comissao_venda(valor: Decimal) -> Decimal:
    if valor < 100:
        return Decimal("0")
    if valor < 500:
        return valor * Decimal("0.01")
    return valor * Decimal("0.05")


def desafio_1():
    # parse_float=Decimal evita erros de ponto flutuante em dinheiro
    dados = json.loads(VENDAS_JSON, parse_float=Decimal)
    totais: dict[str, Decimal] = {}
    for venda in dados["vendas"]:
        nome = venda["vendedor"]
        totais[nome] = totais.get(nome, Decimal("0")) + comissao_venda(venda["valor"])

    print("\n=== Comissão por vendedor ===")
    for nome, total in totais.items():
        print(f"{nome:<18} {moeda(total):>14}")


# --------------------------------------------------------------------------
# 2) MOVIMENTAÇÃO DE ESTOQUE
# --------------------------------------------------------------------------
ESTOQUE_JSON = """
{"estoque": [
{"codigoProduto": 101, "descricaoProduto": "Caneta Azul", "estoque": 150},
{"codigoProduto": 102, "descricaoProduto": "Caderno Universitário", "estoque": 75},
{"codigoProduto": 103, "descricaoProduto": "Borracha Branca", "estoque": 200},
{"codigoProduto": 104, "descricaoProduto": "Lápis Preto HB", "estoque": 320},
{"codigoProduto": 105, "descricaoProduto": "Marcador de Texto Amarelo", "estoque": 90}
]}
"""


class Estoque:
    def __init__(self, produtos: list[dict]):
        self.produtos = {p["codigoProduto"]: p for p in produtos}
        self.movimentacoes: list[dict] = []
        self._ids = count(1)  # identificador único sequencial

    def movimentar(self, codigo: int, tipo: str, quantidade: int, descricao: str) -> int:
        """tipo: 'E' (entrada) ou 'S' (saída). Retorna a quantidade final em estoque."""
        produto = self.produtos.get(codigo)
        if produto is None:
            raise ValueError(f"Produto {codigo} não encontrado.")
        if tipo not in ("E", "S"):
            raise ValueError("Tipo deve ser 'E' (entrada) ou 'S' (saída).")
        if quantidade <= 0:
            raise ValueError("A quantidade deve ser maior que zero.")
        if tipo == "S" and quantidade > produto["estoque"]:
            raise ValueError(f"Estoque insuficiente (disponível: {produto['estoque']}).")

        produto["estoque"] += quantidade if tipo == "E" else -quantidade
        self.movimentacoes.append({
            "id": next(self._ids),
            "codigoProduto": codigo,
            "tipo": "ENTRADA" if tipo == "E" else "SAÍDA",
            "quantidade": quantidade,
            "descricao": descricao,
            "estoqueFinal": produto["estoque"],
        })
        return produto["estoque"]


def desafio_2():
    estoque = Estoque(json.loads(ESTOQUE_JSON)["estoque"])
    print("\n=== Movimentação de estoque ===")
    while True:
        print("\nProdutos:")
        for p in estoque.produtos.values():
            print(f"  {p['codigoProduto']} - {p['descricaoProduto']} (estoque: {p['estoque']})")
        try:
            codigo = input("\nCódigo do produto (Enter para sair): ").strip()
            if not codigo:
                break
            tipo = input("Tipo [E]ntrada / [S]aída: ").strip().upper()
            qtde = int(input("Quantidade: "))
            desc = input("Descrição da movimentação: ").strip()
            final = estoque.movimentar(int(codigo), tipo, qtde, desc)
        except ValueError as erro:
            print(f"Erro: {erro}")
            continue
        mov = estoque.movimentacoes[-1]
        print(f"\nMovimentação #{mov['id']} registrada ({mov['tipo']}: {desc}).")
        print(f"Quantidade final em estoque: {final}")


# --------------------------------------------------------------------------
# 3) JUROS POR ATRASO
# --------------------------------------------------------------------------
def calcular_juros(valor: Decimal, vencimento: date, hoje: date | None = None,
                   taxa_diaria: Decimal = Decimal("0.025")) -> tuple[int, Decimal]:
    """Juros simples: valor * 2,5% * dias de atraso. Retorna (dias_atraso, juros)."""
    hoje = hoje or date.today()
    dias = max((hoje - vencimento).days, 0)
    return dias, (valor * taxa_diaria * dias).quantize(CENTAVOS, ROUND_HALF_UP)


def desafio_3():
    print("\n=== Cálculo de juros ===")
    try:
        valor = Decimal(input("Valor (ex: 1500.00): ").replace(",", "."))
        venc = datetime.strptime(input("Vencimento (dd/mm/aaaa): ").strip(), "%d/%m/%Y").date()
    except Exception:
        print("Entrada inválida.")
        return
    dias, juros = calcular_juros(valor, venc)
    if dias == 0:
        print("Não está vencido: sem juros.")
    else:
        print(f"Dias de atraso: {dias}")
        print(f"Juros: {moeda(juros)}")
        print(f"Total a pagar: {moeda(valor + juros)}")


# --------------------------------------------------------------------------
if __name__ == "__main__":
    while True:
        op = input("\nEscolha o desafio (1, 2, 3) ou Enter para sair: ").strip()
        if op == "1":
            desafio_1()
        elif op == "2":
            desafio_2()
        elif op == "3":
            desafio_3()
        else:
            break