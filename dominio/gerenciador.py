from dominio.usuario import Participante
from dominio.excecoes import EventoError, ParticipanteJaCadastradoError
from dominio.evento import Evento, Categoria
from dominio.ingresso import Ingresso

class Comprovante:
    def __init__(self, codigo_inscricao: str, participante: Participante, valor_total: float):
        self._codigo_inscricao = codigo_inscricao
        self._participante_nome = participante.nome
        self._valor_total = valor_total

    def obter_resumo(self) -> str:
        return f"Comprovante [{self._codigo_inscricao}] | Titular: {self._participante_nome} | Total Pago: R$ {self._valor_total:.2f}"


class Inscricao:
    def __init__(self, codigo: str, participante: Participante, evento: Evento, ingresso: Ingresso):
        self._codigo = codigo
        self._participante = participante
        self._evento = evento
        self._ingresso = ingresso
        
        # Incrementa venda e cria comprovante por composição
        self._evento.incrementar_vendas()
        self._comprovante = Comprovante(codigo, participante, ingresso.calcular_preco_final())
        self._participante.adicionar_inscricao(self)

    @property
    def comprovante(self) -> Comprovante:
        return self._comprovante

    @property
    def evento(self) -> Evento:
        return self._evento

    @property
    def ingresso(self) -> Ingresso:
        return self._ingresso


class Pagamento:
    @staticmethod
    def processar_pagamento(valor: float, forma: str) -> bool:
        # Simulação de processamento de pagamento
        return True


class GerenciadorDeEventos:
    def __init__(self):
        self._eventos = []
        self._participantes = []
        self._inscricoes = []

    def cadastrar_evento(self, evento: Evento):
        self._eventos.append(evento)

    def cadastrar_participante(self, participante: Participante):
        if self.buscar_participante(participante.identificacao) is not None:
            raise ParticipanteJaCadastradoError("Já existe um participante com esse RA!")
        self._participantes.append(participante)

    def buscar_participante(self, identificacao: str):
        for p in self._participantes:
            if p.identificacao == identificacao:
                return p
        return None  # não achou (como retornar NULL em C)

    def realizar_inscricao(self, participante: Participante, evento: Evento, ingresso: Ingresso, forma_pagamento: str) -> Inscricao:
        valor = ingresso.calcular_preco_final()
        
        # Dependência com a classe Pagamento
        if Pagamento.processar_pagamento(valor, forma_pagamento):
            codigo = f"INS-{len(self._inscricoes) + 1:04d}"
            nova_inscricao = Inscricao(codigo, participante, evento, ingresso)
            self._inscricoes.append(nova_inscricao)
            return nova_inscricao
        else:
            raise EventoError("Falha no processamento do pagamento.")

    @property
    def eventos(self):
        return self._eventos

    @property
    def participantes(self):
        return self._participantes