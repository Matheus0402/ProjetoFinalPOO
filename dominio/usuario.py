from abc import ABC

class Usuario(ABC):
    def __init__(self, nome: str, email: str, identificacao: str):
        self._nome = nome
        self._email = email
        self._identificacao = identificacao

    @property
    def nome(self) -> str:
        return self._nome

    @property
    def email(self) -> str:
        return self._email

    @property
    def identificacao(self) -> str:
        return self._identificacao


class Participante(Usuario):
    def __init__(self, nome: str, email: str, identificacao: str):
        super().__init__(nome, email, identificacao)
        self._historico_inscricoes = []

    def adicionar_inscricao(self, inscricao):
        self._historico_inscricoes.append(inscricao)

    @property
    def historico_inscricoes(self):
        return self._historico_inscricoes


class Organizador(Usuario):
    def __init__(self, nome: str, email: str, identificacao: str, empresa: str):
        super().__init__(nome, email, identificacao)
        self._empresa = empresa
