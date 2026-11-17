import tkinter as tk
from pathlib import Path
from tkinter import messagebox, simpledialog, ttk

from dominio.dados_iniciais import carregar_dados_iniciais
from dominio.evento import Categoria, Evento
from dominio.excecoes import EventoError
from dominio.gerenciador import GerenciadorDeEventos, Pagamento
from dominio.usuario import Aluno, Visitante, formatar_identificacao
from gui.consultas import ConsultasGUI
from gui.estilos import configurar_estilos


class SistemaEventosGUI:
    def __init__(self, root: tk.Tk):
        self.root = root
        self.root.title("Agenda de Eventos - UTFPR Apucarana")
        self.root.geometry("880x620")
        self.root.minsize(710, 575)

        self.gerenciador = GerenciadorDeEventos()
        self.participante = None
        self.organizador = None
        self.opcoes_ingresso = []
        carregar_dados_iniciais(self.gerenciador)
        configurar_estilos(self.root)
        self._criar_widgets()
        self._sair_da_area()
        self._atualizar_listas()

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
        self.aba_cadastro = ttk.Frame(self.conteudo, padding=16)
        self.aba_compra = ttk.Frame(self.conteudo, padding=16)
        self.aba_organizador = ttk.Frame(self.conteudo, padding=16)
        self.tela_menu = ttk.Frame(self.conteudo, padding=20)

        self._criar_agenda()
        self._criar_acesso()
        self._criar_cadastro()
        self._criar_inscricao()
        self._criar_organizador()
        self.consultas = ConsultasGUI(self.conteudo, self.gerenciador, self._criar_tabela, self._combo,
                                     self._cancelar_inscricao)
        self._criar_menu()

    def _criar_menu(self):
        ttk.Label(self.tela_menu, text="O que você quer fazer?", font=("Arial", 16, "bold")).pack(anchor="w")
        ttk.Label(self.tela_menu, text="Escolha uma opção para continuar.", style="Apoio.TLabel").pack(anchor="w", pady=(4, 14))
        botoes = ttk.Frame(self.tela_menu)
        botoes.pack(anchor="w")
        ttk.Button(botoes, text="Ver agenda", command=lambda: self._mostrar_tela(self.aba_eventos),
                   style="Primario.TButton").grid(row=0, column=0, sticky="ew", padx=(0, 8))
        self.botao_inscricao = ttk.Button(botoes, text="Fazer inscrição", command=lambda: self._mostrar_tela(self.aba_compra))
        self.botao_inscricao.grid(row=0, column=1, sticky="ew", padx=(0, 8))
        self.botao_minhas = ttk.Button(botoes, text="Minhas inscrições", command=self._mostrar_minhas_inscricoes)
        self.botao_minhas.grid(row=0, column=2, sticky="ew", padx=(0, 8))
        self.botao_evento = ttk.Button(botoes, text="Publicar evento", command=lambda: self._mostrar_tela(self.aba_organizador))
        self.botao_evento.grid(row=0, column=1, sticky="ew", padx=(0, 8))
        self.botao_categoria = ttk.Button(botoes, text="Criar categoria", command=self._criar_categoria)
        self.botao_categoria.grid(row=0, column=2, sticky="ew", padx=(0, 8))
        self.botao_relatorio = ttk.Button(botoes, text="Ver confirmados", command=self._mostrar_relatorio)
        self.botao_relatorio.grid(row=0, column=3, sticky="ew")

    def _mostrar_tela(self, tela):
        if self.participante is None and self.organizador is None:
            if tela not in (self.aba_acesso, self.aba_cadastro):
                return
        if tela in (self.aba_compra, self.consultas.tela_minhas_inscricoes) and self.participante is None:
            return
        if tela in (self.aba_organizador, self.consultas.tela_confirmados) and self.organizador is None:
            return

        if self.tela_atual is not None:
            self.tela_atual.pack_forget()
        tela.pack(fill="both", expand=True)
        self.tela_atual = tela
        estado = "disabled" if tela in (self.aba_acesso, self.tela_menu) else "normal"
        self.botao_voltar.config(state=estado)

    def _voltar(self):
        if self.participante is None and self.organizador is None:
            self._mostrar_tela(self.aba_acesso)
        else:
            self._mostrar_tela(self.tela_menu)

    def _criar_cabecalho(self):
        branco = "#ffffff"
        cabecalho = tk.Frame(self.root, bg=branco)
        cabecalho.pack(fill="x")

        caminho_logo = Path(__file__).parent / "imagens" / "utfpr_apucarana.png"
        if caminho_logo.is_file():
            # A referência fica no objeto para a imagem continuar visível.
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

        self.tabela_eventos = self._criar_tabela(self.aba_eventos, (
            ("evento", "Evento", 250), ("data", "Data e hora", 150),
            ("local", "Local", 190), ("vagas", "Vagas", 80),
        ))
        self.tabela_eventos.tag_configure("alternada", background="#f3f6f9")
        ttk.Button(self.aba_eventos, text="Atualizar lista", command=self._atualizar_listas).pack(anchor="e")

    def _criar_tabela(self, tela, colunas):
        quadro = ttk.Frame(tela)
        quadro.pack(fill="both", expand=True, pady=8)
        tabela = ttk.Treeview(quadro, columns=[coluna[0] for coluna in colunas], show="headings", selectmode="none")
        for coluna, titulo, largura in colunas:
            tabela.heading(coluna, text=titulo)
            tabela.column(coluna, width=largura, minwidth=65, anchor="center" if coluna == "vagas" else "w")

        barra = ttk.Scrollbar(quadro, orient="vertical", command=tabela.yview)
        tabela.configure(yscrollcommand=barra.set)
        barra.pack(side="right", fill="y")
        tabela.pack(side="left", fill="both", expand=True)
        return tabela

    def _campo(self, quadro, linha, titulo):
        ttk.Label(quadro, text=titulo).grid(row=linha, column=0, sticky="w", pady=4)
        campo = ttk.Entry(quadro, width=35)
        campo.grid(row=linha, column=1, sticky="ew", padx=8, pady=4)
        return campo

    def _combo(self, quadro, linha, titulo, valores=()):
        ttk.Label(quadro, text=titulo).grid(row=linha, column=0, sticky="w", pady=4)
        combo = ttk.Combobox(quadro, state="readonly", width=33, values=valores)
        combo.grid(row=linha, column=1, sticky="ew", padx=8, pady=4)
        return combo

    def _criar_acesso(self):
        ttk.Label(self.aba_acesso, text="Acesse a agenda do campus", font=("Arial", 16, "bold")).pack(anchor="w", pady=(0, 10))
        participante = ttk.LabelFrame(self.aba_acesso, text="Participante", padding=12)
        participante.pack(fill="x", pady=(0, 10))
        self.entry_identificacao = self._campo(participante, 0, "RA ou CPF")
        ttk.Button(participante, text="Entrar como participante", command=self._entrar_participante, style="Primario.TButton").grid(row=1, column=1, sticky="e")
        ttk.Button(participante, text="Primeiro acesso? Cadastre-se",
                   command=lambda: self._mostrar_tela(self.aba_cadastro)).grid(row=1, column=0, sticky="w", padx=(0, 4))

        organizador = ttk.LabelFrame(self.aba_acesso, text="Organizador", padding=12)
        organizador.pack(fill="x")
        self.entry_codigo = self._campo(organizador, 0, "Código do organizador")
        ttk.Button(organizador, text="Entrar como organizador", command=self._entrar_organizador).grid(row=1, column=1, sticky="e")

    def _criar_cadastro(self):
        self.combo_perfil = self._combo(self.aba_cadastro, 0, "Perfil", ("Aluno da UTFPR", "Visitante"))
        self.combo_perfil.current(0)
        self.entry_nome = self._campo(self.aba_cadastro, 1, "Nome")
        self.entry_email = self._campo(self.aba_cadastro, 2, "E-mail")
        self.entry_documento = self._campo(self.aba_cadastro, 3, "RA do aluno ou CPF do visitante")
        ttk.Button(self.aba_cadastro, text="Cadastrar e entrar", command=self._cadastrar_participante, style="Primario.TButton").grid(row=4, column=1, sticky="e", pady=10)

    def _criar_inscricao(self):
        self.combo_evento = self._combo(self.aba_compra, 0, "Evento")
        self.combo_evento.bind("<<ComboboxSelected>>", self._atualizar_ingressos)
        self.combo_tipo = self._combo(self.aba_compra, 1, "Tipo de ingresso")
        self.combo_tipo.bind("<<ComboboxSelected>>", self._atualizar_pagamento)
        self.combo_pagamento = self._combo(self.aba_compra, 2, "Pagamento simulado", Pagamento.FORMAS_DISPONIVEIS)
        ttk.Button(self.aba_compra, text="Confirmar inscrição", command=self._realizar_compra, style="Primario.TButton").grid(row=3, column=1, sticky="e", pady=10)

    def _criar_organizador(self):
        quadro = ttk.LabelFrame(self.aba_organizador, text="Novo evento com a primeira sessão", padding=8)
        quadro.pack(fill="x")
        self.entry_evento = self._campo(quadro, 0, "Nome do evento")
        self.combo_categoria = self._combo(quadro, 1, "Categoria", [cat.nome for cat in self.gerenciador.categorias])
        self.combo_categoria.current(0)
        self.entry_capacidade = self._campo(quadro, 2, "Capacidade máxima")
        self.entry_preco = self._campo(quadro, 3, "Preço base (R$)")
        self.entry_data = self._campo(quadro, 4, "Data e hora")
        self.entry_local = self._campo(quadro, 5, "Local")
        self.gratuito_alunos = tk.BooleanVar()
        ttk.Checkbutton(quadro, text="Gratuito para alunos da UTFPR", variable=self.gratuito_alunos).grid(row=6, column=1, sticky="w")
        ttk.Button(quadro, text="Publicar evento", command=self._criar_evento, style="Primario.TButton").grid(row=7, column=1, sticky="e", pady=6)

    def _criar_categoria(self):
        if self.organizador is None:
            return
        nome = simpledialog.askstring("Criar categoria", "Nome da nova categoria:", parent=self.root)
        if nome is None:
            return
        try:
            categoria = Categoria(nome)
            self.gerenciador.cadastrar_categoria(categoria)
        except EventoError as erro:
            messagebox.showerror("Categoria não criada", str(erro))
            return

        self.combo_categoria["values"] = [cat.nome for cat in self.gerenciador.categorias]
        self.combo_categoria.set(categoria.nome)
        messagebox.showinfo("Categoria criada", f"{categoria.nome} já pode ser usada em um evento.")

    def _sair_da_area(self):
        self.participante = None
        self.organizador = None
        self._mostrar_tela(self.aba_acesso)
        self.status.config(text="Acesso ao sistema")
        self.botao_sair.config(state="disabled")

    def _abrir_area(self, saudacao):
        if self.organizador is None:
            self.botao_inscricao.grid()
            self.botao_minhas.grid()
            self.botao_evento.grid_remove()
            self.botao_categoria.grid_remove()
            self.botao_relatorio.grid_remove()
        else:
            self.botao_inscricao.grid_remove()
            self.botao_minhas.grid_remove()
            self.botao_evento.grid()
            self.botao_categoria.grid()
            self.botao_relatorio.grid()
        self._mostrar_tela(self.tela_menu)
        self.status.config(text=saudacao)
        self.botao_sair.config(state="normal")

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
        self.organizador = self.gerenciador.buscar_organizador(codigo)
        if self.organizador is None:
            messagebox.showwarning("Organizador não encontrado", "Confira o código informado.")
            return
        self._abrir_area(f"Organizador: {self.organizador.nome}")

    def _abrir_area_participante(self, participante):
        self.participante = participante
        self._abrir_area(f"{participante.tipo()}: {participante.nome}")
        self._atualizar_ingressos()

    def _cadastrar_participante(self):
        nome = self.entry_nome.get().strip()
        email = self.entry_email.get().strip()
        documento = self.entry_documento.get().strip()
        if not nome or not email or not documento:
            messagebox.showwarning("Cadastro", "Preencha nome, e-mail e RA ou CPF.")
            return

        try:
            if self.combo_perfil.current() == 0:
                participante = Aluno(nome, email, documento)
            else:
                participante = Visitante(nome, email, documento)
            self.gerenciador.cadastrar_participante(participante)
        except EventoError as erro:
            messagebox.showerror("Cadastro não realizado", str(erro))
            return

        for campo in (self.entry_nome, self.entry_email, self.entry_documento):
            campo.delete(0, tk.END)
        self._abrir_area_participante(participante)

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

        selecao = self.combo_evento.current()
        self.combo_evento["values"] = [evento.nome for evento in self.gerenciador.eventos]
        if selecao >= 0:
            self.combo_evento.current(selecao)
        self._atualizar_ingressos()

    def _atualizar_ingressos(self, evento_tk=None):
        indice = self.combo_evento.current()
        self.opcoes_ingresso = []
        if self.participante is not None and indice >= 0:
            evento = self.gerenciador.eventos[indice]
            self.opcoes_ingresso = self.gerenciador.ingressos_disponiveis(evento, self.participante)

        self.combo_tipo.set("")
        self.combo_tipo["values"] = [
            f"{ingresso.nome_tipo()} (R$ {ingresso.calcular_preco_final():.2f})"
            for ingresso in self.opcoes_ingresso
        ]
        if self.opcoes_ingresso:
            self.combo_tipo.current(0)
        self._atualizar_pagamento()

    def _atualizar_pagamento(self, evento_tk=None):
        indice = self.combo_tipo.current()
        self.combo_pagamento.set("")
        if indice >= 0 and self.opcoes_ingresso[indice].calcular_preco_final() > 0:
            self.combo_pagamento.config(state="readonly")
        else:
            self.combo_pagamento.config(state="disabled")

    def _realizar_compra(self):
        indice_evento = self.combo_evento.current()
        indice_ingresso = self.combo_tipo.current()
        if self.participante is None or indice_evento < 0 or indice_ingresso < 0:
            messagebox.showwarning("Inscrição", "Entre como participante e escolha o evento e o ingresso.")
            return

        evento = self.gerenciador.eventos[indice_evento]
        ingresso = self.opcoes_ingresso[indice_ingresso]
        forma = self.combo_pagamento.get()
        if ingresso.calcular_preco_final() > 0 and not forma:
            messagebox.showwarning("Inscrição", "Escolha a forma de pagamento.")
            return

        try:
            inscricao = self.gerenciador.realizar_inscricao(self.participante, evento, ingresso, forma)
        except EventoError as erro:
            messagebox.showerror("Inscrição não realizada", str(erro))
            return

        self._atualizar_listas()
        messagebox.showinfo("Inscrição confirmada", inscricao.comprovante.obter_resumo())

    def _criar_evento(self):
        if self.organizador is None:
            return
        try:
            capacidade = int(self.entry_capacidade.get())
            preco = float(self.entry_preco.get().replace(",", "."))
        except ValueError:
            messagebox.showwarning("Dados inválidos", "Use um número inteiro para capacidade e um número para preço.")
            return

        categoria = self.gerenciador.categorias[self.combo_categoria.current()]
        try:
            evento = Evento(self.entry_evento.get(), capacidade, categoria, preco, self.gratuito_alunos.get())
            evento.adicionar_sessao(self.entry_data.get(), self.entry_local.get())
            self.gerenciador.cadastrar_evento(evento)
        except EventoError as erro:
            messagebox.showerror("Evento não publicado", str(erro))
            return

        self._atualizar_listas()
        for campo in (self.entry_evento, self.entry_capacidade, self.entry_preco, self.entry_data, self.entry_local):
            campo.delete(0, tk.END)
        self.gratuito_alunos.set(False)
        messagebox.showinfo("Evento publicado", f"{evento.nome} já está na lista de eventos.")

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

        self._atualizar_listas()
        self.consultas.preencher_minhas_inscricoes(self.participante)
        messagebox.showinfo("Inscrição cancelada", "A vaga voltou a ficar disponível na agenda.")

    def _mostrar_relatorio(self):
        if self.organizador is None:
            return
        self.consultas.preencher_confirmados()
        self._mostrar_tela(self.consultas.tela_confirmados)
