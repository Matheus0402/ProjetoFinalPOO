from abc import ABC, abstractmethod
from dominio.excecoes import RAInvalidoError, CPFInvalidoError


def formatar_ra(ra: str) -> str:
    ra = ra.strip().lower()  # tira espaços e deixa tudo minúsculo

    # RA válido: 8 caracteres, começa com 'a' e o resto são só números
    if len(ra) != 8 or ra[0] != "a" or not ra[1:].isdigit():
        raise RAInvalidoError("RA inválido! Use o formato a + 7 números (ex: a2669560).")

    return ra


def formatar_cpf(cpf: str) -> str:
    # tira os pontos, traço e espaços: "123.456.789-09" vira "12345678909"
    cpf = cpf.strip().replace(".", "").replace("-", "")

    # CPF válido (aqui): 11 caracteres e todos números
    if len(cpf) != 11 or not cpf.isdigit():
        raise CPFInvalidoError("CPF inválido! Use 11 números (ex: 123.456.789-09).")

    return cpf


def formatar_identificacao(texto: str) -> str:
    # Se começa com 'a' é um RA, senão é tratado como CPF
    texto = texto.strip().lower()

    if texto[:1] == "a":
        return formatar_ra(texto)
    return formatar_cpf(texto)


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

    def tem_direito_gratuidade(self) -> bool:
        return False  # por padrão não tem; quem pode (Aluno) troca para True

    def pode_comprar_meia(self) -> bool:
        return False  # por padrão não pode; só o Aluno troca para True

    @property
    def historico_inscricoes(self):
        return self._historico_inscricoes


class Aluno(Participante):
    def __init__(self, nome: str, email: str, ra: str):
        ra = formatar_ra(ra)  # valida e corrige o RA antes de guardar
        super().__init__(nome, email, ra)

    def tipo(self) -> str:
        return "Aluno"

    def tem_direito_gratuidade(self) -> bool:
        return True

    def pode_comprar_meia(self) -> bool:
        return True


class Visitante(Participante):
    # pessoa de fora da UTFPR, identificada pelo CPF
    def __init__(self, nome: str, email: str, cpf: str):
        cpf = formatar_cpf(cpf)  # valida e limpa o CPF antes de guardar
        super().__init__(nome, email, cpf)

    def tipo(self) -> str:
        return "Visitante"


class Organizador(Usuario):
    def __init__(self, nome: str, email: str, identificacao: str):
        super().__init__(nome, email, identificacao)

    def tipo(self) -> str:
        return "Organizador"