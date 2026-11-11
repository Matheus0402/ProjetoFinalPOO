from dominio.usuario import Participante, Organizador
from dominio.excecoes import EventoError, ParticipanteJaCadastradoError
from dominio.evento import Evento, Categoria
from dominio.ingresso import Ingresso, IngressoInteira, IngressoMeia, IngressoVIP, IngressoGratuito

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
        self._categorias = []
        self._participantes = []
        self._organizadores = []
        self._inscricoes = []

    def cadastrar_evento(self, evento: Evento):
        self._eventos.append(evento)

    def cadastrar_categoria(self, categoria: Categoria):
        # Agregação: as categorias existem aqui, independentes dos eventos
        self._categorias.append(categoria)

    def cadastrar_organizador(self, organizador: Organizador):
        self._organizadores.append(organizador)

    def buscar_organizador(self, identificacao: str):
        for o in self._organizadores:
            if o.identificacao == identificacao:
                return o
        return None

    def calcular_arrecadacao(self, evento: Evento) -> float:
        total = 0.0
        for insc in self._inscricoes:
            if insc.evento is evento:
                total += insc.ingresso.calcular_preco_final()
        return total

    def cadastrar_participante(self, participante: Participante):
        if self.buscar_participante(participante.identificacao) is not None:
            raise ParticipanteJaCadastradoError("Já existe um participante com esse RA/CPF!")
        self._participantes.append(participante)

    def buscar_participante(self, identificacao: str):
        for p in self._participantes:
            if p.identificacao == identificacao:
                return p
        return None  # não achou (como retornar NULL em C)

    def ingressos_disponiveis(self, evento: Evento, participante: Participante):
        # Se o evento é gratuito para esse participante, só existe o ingresso gratuito
        if evento.eh_gratuito_para(participante):
            return [IngressoGratuito(evento.preco_base)]
        ingressos = [IngressoInteira(evento.preco_base)]
        if participante.pode_comprar_meia():  # meia-entrada só para quem tem direito
            ingressos.append(IngressoMeia(evento.preco_base))
        ingressos.append(IngressoVIP(evento.preco_base))
        return ingressos

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
    def categorias(self):
        return self._categorias

    @property
    def participantes(self):
        return self._participantes