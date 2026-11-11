from abc import ABC, abstractmethod
from dominio.excecoes import RAInvalidoError


def formatar_ra(ra: str) -> str:
    ra = ra.strip().lower()  # tira espaços e deixa tudo minúsculo

    # RA válido: 8 caracteres, começa com 'a' e o resto são só números
    if len(ra) != 8 or ra[0] != "a" or not ra[1:].isdigit():
        raise RAInvalidoError("RA inválido! Use o formato a + 7 números (ex: a2669560).")

    return ra


class Usuario(ABC):
    def __init__(self, nome: str, email: str, identificacao: str):
        self._nome = nome
        self._email = email
        self._identificacao = identificacao

    @abstractmethod
    def tipo(self) -> str:
        pass

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


class Aluno(Participante):
    def __init__(self, nome: str, email: str, ra: str):
        ra = formatar_ra(ra)  # valida e corrige o RA antes de guardar
        super().__init__(nome, email, ra)

    def tipo(self) -> str:
        return "Aluno"


class Organizador(Usuario):
    def __init__(self, nome: str, email: str, identificacao: str):
        super().__init__(nome, email, identificacao)

    def tipo(self) -> str:
        return "Organizador"