import tkinter as tk
from pathlib import Path
from tkinter import messagebox, ttk

from dominio.dados_iniciais import carregar_dados_iniciais
from dominio.excecoes import EventoError
from dominio.gerenciador import GerenciadorDeEventos
from dominio.usuario import formatar_identificacao
from gui.consultas import ConsultasGUI
from gui.estados_gui import (
    EstadoDeslogado,
    EstadoOrganizador,
    EstadoParticipante,
    EstadoSessaoGUI,
)
from gui.estilos import configurar_estilos
from gui.fabrica_gui import WidgetFactory
from gui.tela_cadastro import TelaCadastro
from gui.tela_inscricao import TelaInscricao
from gui.tela_organizador import TelaOrganizador


class SistemaEventosGUI:
    def __init__(self, root: tk.Tk):
        self.root = root
        self.root.title("Agenda de Eventos - UTFPR Apucarana")
        self.root.geometry("880x620")
        self.root.minsize(710, 575)

        self.gerenciador = GerenciadorDeEventos()
        self.participante = None
        self.organizador = None
        self.estado_atual: EstadoSessaoGUI = EstadoDeslogado()

        carregar_dados_iniciais(self.gerenciador)
        configurar_estilos(self.root)
        self._criar_widgets()

        # Padrão Observer: inscreve callbacks de atualização automática da interface
        self.gerenciador.adicionar_observador(self._atualizar_listas)
        self.gerenciador.adicionar_observador(self._atualizar_minhas_inscricoes)
        self.gerenciador.adicionar_observador(self._atualizar_confirmados)

        self._alterar_estado(EstadoDeslogado())
        self._atualizar_listas()

    def _alterar_estado(self, novo_estado: EstadoSessaoGUI):
        self.estado_atual = novo_estado
        self.estado_atual.configurar_interface(self)

    def _criar_widgets(self):
        self._criar_cabecalho()
        topo = ttk.Frame(self.root, padding=(18, 9), style="Barra.TFrame")
        topo.pack(fill="x")
        self.status = ttk.Label(topo, style="Status.TLabel")
        self.status.pack(side="left")
        self.botao_sair = ttk.Button(topo, text="Sair da área", command=self._sair_da_area)
        self.botao_sair.pack(side="right")
        self.botao_voltar = ttk.Button(topo, text="Voltar", command=self._voltar)
        self.botao_voltar.pack(side="right", padx=(0, 8))

        self.conteudo = ttk.Frame(self.root)
        self.conteudo.pack(fill="both", expand=True, padx=18, pady=(0, 16))
        self.tela_atual = None
        self.aba_eventos = ttk.Frame(self.conteudo, padding=16)
        self.aba_acesso = ttk.Frame(self.conteudo, padding=16)

        self.aba_cadastro = TelaCadastro(
            self.conteudo,
            self.gerenciador,
            WidgetFactory.criar_campo,
            WidgetFactory.criar_combo,
            self._abrir_area_participante,
        )
        self.aba_compra = TelaInscricao(
            self.conteudo,
            self.gerenciador,
            WidgetFactory.criar_combo,
            lambda: self.participante,
        )
        self.aba_organizador = TelaOrganizador(
            self.conteudo,
            self.gerenciador,
            WidgetFactory.criar_campo,
            WidgetFactory.criar_combo,
            lambda: self.organizador,
        )
        self.tela_menu = ttk.Frame(self.conteudo, padding=20)

        self._criar_agenda()
        self._criar_acesso()
        self.consultas = ConsultasGUI(
            self.conteudo,
            self.gerenciador,
            WidgetFactory.criar_tabela,
            WidgetFactory.criar_combo,
            self._cancelar_inscricao,
        )
        self._criar_menu()

    def _criar_menu(self):
        ttk.Label(self.tela_menu, text="O que você quer fazer?", font=("Arial", 16, "bold")).pack(anchor="w")
        ttk.Label(self.tela_menu, text="Escolha uma opção para continuar.", style="Apoio.TLabel").pack(anchor="w", pady=(4, 14))
        botoes = ttk.Frame(self.tela_menu)
        botoes.pack(anchor="w")
        ttk.Button(
            botoes,
            text="Ver agenda",
            command=lambda: self._mostrar_tela(self.aba_eventos),
            style="Primario.TButton",
        ).grid(row=0, column=0, sticky="ew", padx=(0, 8))
        self.botao_inscricao = ttk.Button(
            botoes, text="Fazer inscrição", command=lambda: self._mostrar_tela(self.aba_compra)
        )
        self.botao_inscricao.grid(row=0, column=1, sticky="ew", padx=(0, 8))
        self.botao_minhas = ttk.Button(
            botoes, text="Minhas inscrições", command=self._mostrar_minhas_inscricoes
        )
        self.botao_minhas.grid(row=0, column=2, sticky="ew", padx=(0, 8))
        self.botao_evento = ttk.Button(
            botoes, text="Publicar evento", command=lambda: self._mostrar_tela(self.aba_organizador)
        )
        self.botao_evento.grid(row=0, column=1, sticky="ew", padx=(0, 8))
        self.botao_categoria = ttk.Button(
            botoes, text="Criar categoria", command=self.aba_organizador.criar_categoria
        )
        self.botao_categoria.grid(row=0, column=2, sticky="ew", padx=(0, 8))
        self.botao_relatorio = ttk.Button(
            botoes, text="Ver confirmados", command=self._mostrar_relatorio
        )
        self.botao_relatorio.grid(row=0, column=3, sticky="ew")

    def _mostrar_tela(self, tela):
        if not self.estado_atual.pode_acessar_tela(self, tela):
            return

        if self.tela_atual is not None:
            self.tela_atual.pack_forget()
        tela.pack(fill="both", expand=True)
        self.tela_atual = tela
        estado = "disabled" if tela == self.estado_atual.tela_inicial(self) else "normal"
        self.botao_voltar.config(state=estado)

    def _voltar(self):
        self._mostrar_tela(self.estado_atual.tela_inicial(self))

    def _criar_cabecalho(self):
        branco = "#ffffff"
        cabecalho = tk.Frame(self.root, bg=branco)
        cabecalho.pack(fill="x")

        caminho_logo = Path(__file__).parent / "imagens" / "utfpr_apucarana.png"
        if caminho_logo.is_file():
            self.logo_utfpr = tk.PhotoImage(master=self.root, file=str(caminho_logo))
            tk.Label(cabecalho, image=self.logo_utfpr, bg=branco).pack(side="left", padx=20, pady=12)

        titulos = tk.Frame(cabecalho, bg=branco)
        titulos.pack(side="left", padx=12, pady=16)
        tk.Label(titulos, text="Agenda de Eventos", font=("Arial", 22, "bold"), bg=branco, fg="#172333").pack(anchor="w")
        tk.Label(titulos, text="UTFPR Apucarana  •  Projeto acadêmico de POO", bg=branco, fg="#506174").pack(anchor="w", pady=(4, 0))
        tk.Frame(self.root, bg="#ffcc00", height=4).pack(fill="x")

    def _criar_agenda(self):
        ttk.Label(self.aba_eventos, text="Programação do campus", font=("Arial", 14, "bold")).pack(anchor="w")
        ttk.Label(self.aba_eventos, text="As vagas são compartilhadas pelas sessões de um mesmo evento.", style="Apoio.TLabel").pack(anchor="w", pady=(3, 4))

        self.tabela_eventos = WidgetFactory.criar_tabela(
            self.aba_eventos,
            (
                ("evento", "Evento", 250),
                ("data", "Data e hora", 150),
                ("local", "Local", 190),
                ("vagas", "Vagas", 80),
            ),
        )
        self.tabela_eventos.tag_configure("alternada", background="#f3f6f9")
        ttk.Button(self.aba_eventos, text="Atualizar lista", command=self._atualizar_listas).pack(anchor="e")

    def _criar_acesso(self):
        ttk.Label(self.aba_acesso, text="Acesse a agenda do campus", font=("Arial", 16, "bold")).pack(anchor="w", pady=(0, 10))
        participante = ttk.LabelFrame(self.aba_acesso, text="Participante", padding=12)
        participante.pack(fill="x", pady=(0, 10))
        self.entry_identificacao = WidgetFactory.criar_campo(participante, 0, "RA ou CPF")
        ttk.Button(participante, text="Entrar como participante", command=self._entrar_participante, style="Primario.TButton").grid(row=1, column=1, sticky="e")
        ttk.Button(
            participante,
            text="Primeiro acesso? Cadastre-se",
            command=lambda: self._mostrar_tela(self.aba_cadastro),
        ).grid(row=1, column=0, sticky="w", padx=(0, 4))

        organizador = ttk.LabelFrame(self.aba_acesso, text="Organizador", padding=12)
        organizador.pack(fill="x")
        self.entry_codigo = WidgetFactory.criar_campo(organizador, 0, "Código do organizador")
        ttk.Button(organizador, text="Entrar como organizador", command=self._entrar_organizador).grid(row=1, column=1, sticky="e")

    def _sair_da_area(self):
        self._alterar_estado(EstadoDeslogado())

    def _entrar_participante(self):
        try:
            identificacao = formatar_identificacao(self.entry_identificacao.get())
        except EventoError as erro:
            messagebox.showerror("Identificação inválida", str(erro))
            return

        participante = self.gerenciador.buscar_participante(identificacao)
        if participante is None:
            messagebox.showwarning("Participante não encontrado", "Faça o cadastro antes de entrar.")
            return

        self.entry_identificacao.delete(0, tk.END)
        self._abrir_area_participante(participante)

    def _entrar_organizador(self):
        codigo = self.entry_codigo.get().strip()
        self.entry_codigo.delete(0, tk.END)
        organizador = self.gerenciador.buscar_organizador(codigo)
        if organizador is None:
            messagebox.showwarning("Organizador não encontrado", "Confira o código informado.")
            return
        self._alterar_estado(EstadoOrganizador(organizador))

    def _abrir_area_participante(self, participante):
        self._alterar_estado(EstadoParticipante(participante))

    def _atualizar_listas(self):
        for linha in self.tabela_eventos.get_children():
            self.tabela_eventos.delete(linha)
        for indice, evento in enumerate(self.gerenciador.eventos):
            vagas = evento.capacidade_maxima - evento.ingressos_vendidos
            ocupacao = f"{vagas}/{evento.capacidade_maxima}"
            nome = f"{evento.nome} [{evento.categoria.nome}]"
            etiquetas = ("alternada",) if indice % 2 else ()
            if not evento.sessoes:
                self.tabela_eventos.insert("", tk.END, values=(nome, "A definir", "A definir", ocupacao), tags=etiquetas)
            for sessao in evento.sessoes:
                self.tabela_eventos.insert("", tk.END, values=(nome, sessao.data_hora, sessao.local, ocupacao), tags=etiquetas)

        self.aba_compra.atualizar_eventos()

    def _atualizar_minhas_inscricoes(self):
        if self.participante is not None:
            self.consultas.preencher_minhas_inscricoes(self.participante)

    def _atualizar_confirmados(self):
        if self.organizador is not None:
            self.consultas.preencher_confirmados()

    def _mostrar_minhas_inscricoes(self):
        if self.participante is None:
            return
        self.consultas.preencher_minhas_inscricoes(self.participante)
        self._mostrar_tela(self.consultas.tela_minhas_inscricoes)

    def _cancelar_inscricao(self):
        if self.participante is None:
            return
        codigo = self.consultas.codigo_inscricao_selecionada()
        if not codigo:
            messagebox.showwarning("Cancelar inscrição", "Selecione uma inscrição na tabela.")
            return
        if not messagebox.askyesno("Cancelar inscrição", f"Cancelar a inscrição {codigo} e liberar a vaga?"):
            return

        try:
            self.gerenciador.cancelar_inscricao(self.participante, codigo)
        except EventoError as erro:
            messagebox.showerror("Inscrição não cancelada", str(erro))
            return

        messagebox.showinfo("Inscrição cancelada", "A vaga voltou a ficar disponível na agenda.")

    def _mostrar_relatorio(self):
        if self.organizador is None:
            return
        self.consultas.preencher_confirmados()
        self._mostrar_tela(self.consultas.tela_confirmados)
