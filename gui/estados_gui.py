from abc import ABC, abstractmethod


class EstadoSessaoGUI(ABC):
    """Padrão State: define o comportamento de navegação e permissões da interface."""

    @abstractmethod
    def configurar_interface(self, app):
        pass

    @abstractmethod
    def pode_acessar_tela(self, app, tela) -> bool:
        pass

    @abstractmethod
    def tela_inicial(self, app):
        pass


class EstadoDeslogado(EstadoSessaoGUI):
    def configurar_interface(self, app):
        app.participante = None
        app.organizador = None
        app.status.config(text="Acesso ao sistema")
        app.botao_sair.config(state="disabled")
        app._mostrar_tela(self.tela_inicial(app))

    def pode_acessar_tela(self, app, tela) -> bool:
        return tela in (app.aba_acesso, app.aba_cadastro)

    def tela_inicial(self, app):
        return app.aba_acesso


class EstadoParticipante(EstadoSessaoGUI):
    def __init__(self, participante):
        self.participante = participante

    def configurar_interface(self, app):
        app.participante = self.participante
        app.organizador = None
        app.botao_inscricao.grid()
        app.botao_minhas.grid()
        app.botao_evento.grid_remove()
        app.botao_categoria.grid_remove()
        app.botao_relatorio.grid_remove()
        app.status.config(text=f"{self.participante.tipo()}: {self.participante.nome}")
        app.botao_sair.config(state="normal")
        app.aba_compra.atualizar_eventos()
        app._mostrar_tela(self.tela_inicial(app))

    def pode_acessar_tela(self, app, tela) -> bool:
        return tela in (
            app.tela_menu,
            app.aba_eventos,
            app.aba_compra,
            app.consultas.tela_minhas_inscricoes,
        )

    def tela_inicial(self, app):
        return app.tela_menu


class EstadoOrganizador(EstadoSessaoGUI):
    def __init__(self, organizador):
        self.organizador = organizador

    def configurar_interface(self, app):
        app.organizador = self.organizador
        app.participante = None
        app.botao_inscricao.grid_remove()
        app.botao_minhas.grid_remove()
        app.botao_evento.grid()
        app.botao_categoria.grid()
        app.botao_relatorio.grid()
        app.status.config(text=f"Organizador: {self.organizador.nome}")
        app.botao_sair.config(state="normal")
        app._mostrar_tela(self.tela_inicial(app))

    def pode_acessar_tela(self, app, tela) -> bool:
        return tela in (
            app.tela_menu,
            app.aba_eventos,
            app.aba_organizador,
            app.consultas.tela_confirmados,
        )

    def tela_inicial(self, app):
        return app.tela_menu
