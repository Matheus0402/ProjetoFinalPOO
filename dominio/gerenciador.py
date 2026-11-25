from dominio.usuario import Participante, Organizador
from dominio.excecoes import DadosInvalidosError, EventoError, ParticipanteJaCadastradoError
from dominio.evento import Evento, Categoria
from dominio.ingresso import Ingresso, IngressoInteira, IngressoMeia, IngressoVIP, IngressoGratuito
from dominio.observador import Observavel

class Comprovante:
    def __init__(self, codigo_inscricao: str, participante: Participante, valor_total: float, forma_pagamento: str):
        self._codigo_inscricao = codigo_inscricao
        self._participante_nome = participante.nome
        self._valor_total = valor_total
        self._forma_pagamento = forma_pagamento

    def obter_resumo(self) -> str:
        return (f"Comprovante [{self._codigo_inscricao}] | Titular: {self._participante_nome}"
                f" | Total Pago: R$ {self._valor_total:.2f} | Pagamento: {self._forma_pagamento}")


class Inscricao:
    def __init__(self, codigo: str, participante: Participante, evento: Evento, ingresso: Ingresso, forma_pagamento: str):
        self._codigo = codigo
        self._participante = participante
        self._evento = evento
        self._ingresso = ingresso
        
        # Incrementa venda e cria comprovante por composição
        self._evento.incrementar_vendas()
        self._comprovante = Comprovante(codigo, participante, ingresso.calcular_preco_final(), forma_pagamento)
        self._participante.adicionar_inscricao(self)

    @property
    def comprovante(self) -> Comprovante:
        return self._comprovante

    @property
    def codigo(self) -> str:
        return self._codigo

    @property
    def participante(self) -> Participante:
        return self._participante

    @property
    def evento(self) -> Evento:
        return self._evento

    @property
    def ingresso(self) -> Ingresso:
        return self._ingresso


class Pagamento:
    FORMAS_DISPONIVEIS = ("Pix", "Cartão de Crédito", "Cartão de Débito")

    @staticmethod
    def processar_pagamento(valor: float, forma: str) -> bool:
        # Simulação: aprova valores positivos com uma forma cadastrada.
        return valor > 0 and forma in Pagamento.FORMAS_DISPONIVEIS


class GerenciadorDeEventos(Observavel): # adicionado oberservavel, estabelecendo a heranca
    def __init__(self):
        super().__init__() # adicionado dentro do construtor, pra inicializar a lista de oberservadores da classe pai
        self._eventos = []
        self._categorias = []
        self._participantes = []
        self._organizadores = []
        self._inscricoes = []
        self._proximo_codigo = 1

    def cadastrar_evento(self, evento: Evento):
        self._eventos.append(evento)
        self.notificar_observadores()

    def cadastrar_categoria(self, categoria: Categoria):
        # Agregação: as categorias existem aqui, independentes dos eventos
        for existente in self._categorias:
            if existente.nome.casefold() == categoria.nome.casefold():
                raise DadosInvalidosError("Já existe uma categoria com esse nome.")
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
        for insc in self.inscricoes_do_evento(evento):
            total += insc.ingresso.calcular_preco_final()
        return total

    def inscricoes_do_evento(self, evento: Evento):
        return [inscricao for inscricao in self._inscricoes if inscricao.evento is evento]

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

    def realizar_inscricao(self, participante: Participante, evento: Evento, ingresso: Ingresso, forma_pagamento: str = "") -> Inscricao:
        for inscricao in self.inscricoes_do_evento(evento):
            if inscricao.participante.identificacao == participante.identificacao:
                raise EventoError(f"Você já tem uma inscrição confirmada para '{evento.nome}'.")

        valor = ingresso.calcular_preco_final() # polimorfismo trabalhando

        if valor == 0:
            forma_pagamento = "Sem cobrança"
        elif not Pagamento.processar_pagamento(valor, forma_pagamento):
            raise EventoError("Pagamento simulado não aprovado. Escolha uma forma de pagamento válida.")
        else:
            forma_pagamento += " (simulado)"

        codigo = f"INS-{self._proximo_codigo:04d}"
        nova_inscricao = Inscricao(codigo, participante, evento, ingresso, forma_pagamento)
        self._inscricoes.append(nova_inscricao)
        self._proximo_codigo += 1
        self.notificar_observadores() # queremos notificar uma alteração somente depois que a inscrição for realizada com sucesso | Se o evento estiver lotado ou a inscrição for duplicada, uma exceção interromperá o método antes de chegar à notificação.
        return nova_inscricao

    def cancelar_inscricao(self, participante: Participante, codigo: str):
        for inscricao in self._inscricoes:
            if inscricao.codigo == codigo and inscricao.participante is participante:
                participante.remover_inscricao(inscricao)
                self._inscricoes.remove(inscricao)
                inscricao.evento.liberar_vaga()
                self.notificar_observadores()
                return

    raise EventoError("Inscrição não encontrada para este participante.")
    @property
    def eventos(self):
        return self._eventos

    @property
    def categorias(self):
        return self._categorias

    @property
    def participantes(self):
        return self._participantes
