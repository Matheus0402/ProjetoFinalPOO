from dominio.excecoes import LotacaoEsgotadaError, DadosInvalidosError


class Categoria:
    def __init__(self, nome: str):
        self._nome = nome

    @property
    def nome(self) -> str:
        return self._nome


class Sessao:
    def __init__(self, data_hora: str, local: str):
        self._data_hora = data_hora
        self._local = local

    @property
    def data_hora(self) -> str:
        return self._data_hora

    @property
    def local(self) -> str:
        return self._local


class Evento:
    def __init__(self, nome: str, capacidade_maxima: int, categoria: Categoria, preco_base: float, gratuito_para_alunos: bool = False):
        if nome.strip() == "":
            raise DadosInvalidosError("O nome do evento não pode ser vazio.")
        if capacidade_maxima <= 0:
            raise DadosInvalidosError("A capacidade deve ser maior que zero.")
        if preco_base < 0:
            raise DadosInvalidosError("O preço não pode ser negativo.")

        self._nome = nome.strip()
        self._capacidade_maxima = capacidade_maxima
        self._categoria = categoria
        self._preco_base = preco_base
        self._gratuito_para_alunos = gratuito_para_alunos
        self._sessoes = []
        self._ingressos_vendidos = 0

    def adicionar_sessao(self, data_hora: str, local: str):
        if data_hora.strip() == "" or local.strip() == "":
            raise DadosInvalidosError("Data/hora e local da sessão não podem ser vazios.")
        # Composição: a sessão é criada e mantida internamente pelo Evento
        sessao = Sessao(data_hora, local)
        self._sessoes.append(sessao)

    def vaga_disponivel(self) -> bool:
        return self._ingressos_vendidos < self._capacidade_maxima

    def incrementar_vendas(self):
        if not self.vaga_disponivel():
            raise LotacaoEsgotadaError(f"Evento '{self._nome}' está com lotação máxima atingida!")
        self._ingressos_vendidos += 1

    @property
    def nome(self) -> str:
        return self._nome

    @property
    def capacidade_maxima(self) -> int:
        return self._capacidade_maxima

    @property
    def ingressos_vendidos(self) -> int:
        return self._ingressos_vendidos

    def eh_gratuito_para(self, participante) -> bool:
        # só é gratuito se o evento for marcado como gratuito E o participante tiver esse direito
        return self._gratuito_para_alunos and participante.tem_direito_gratuidade()

    @property
    def gratuito_para_alunos(self) -> bool:
        return self._gratuito_para_alunos

    @property
    def preco_base(self) -> float:
        return self._preco_base

    @property
    def sessoes(self):
        return self._sessoes

    @property
    def categoria(self) -> Categoria:
        return self._categoria