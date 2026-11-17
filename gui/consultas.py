import tkinter as tk
from tkinter import ttk


class ConsultasGUI:
    def __init__(self, conteudo, gerenciador, criar_tabela, criar_combo, cancelar_inscricao):
        self.gerenciador = gerenciador
        self.tela_minhas_inscricoes = ttk.Frame(conteudo, padding=16)
        self.tela_confirmados = ttk.Frame(conteudo, padding=16)

        ttk.Label(self.tela_minhas_inscricoes, text="Minhas inscrições", font=("Arial", 14, "bold")).pack(anchor="w")
        self.resumo_minhas = ttk.Label(self.tela_minhas_inscricoes, style="Apoio.TLabel")
        self.resumo_minhas.pack(anchor="w", pady=(3, 4))
        self.tabela_minhas = criar_tabela(self.tela_minhas_inscricoes, (
            ("evento", "Evento", 245), ("data", "Data e hora", 133),
            ("local", "Local", 150), ("ingresso", "Ingresso", 97),
            ("codigo", "Código", 85), ("situacao", "Situação", 85),
        ))
        self.tabela_minhas.configure(selectmode="browse")
        ttk.Button(self.tela_minhas_inscricoes, text="Cancelar inscrição",
                   command=cancelar_inscricao).pack(anchor="e")

        ttk.Label(self.tela_confirmados, text="Confirmados por evento", font=("Arial", 14, "bold")).pack(anchor="w")
        escolha = ttk.Frame(self.tela_confirmados)
        escolha.pack(anchor="w", pady=6)
        self.combo_confirmados = criar_combo(escolha, 0, "Evento")
        self.combo_confirmados.bind("<<ComboboxSelected>>", self._atualizar_confirmados)
        self.resumo_confirmados = ttk.Label(self.tela_confirmados, style="Apoio.TLabel")
        self.resumo_confirmados.pack(anchor="w")
        self.tabela_confirmados = criar_tabela(self.tela_confirmados, (
            ("nome", "Participante", 235), ("perfil", "Perfil", 100),
            ("ingresso", "Ingresso", 110), ("codigo", "Código", 90),
        ))

    def preencher_minhas_inscricoes(self, participante):
        for linha in self.tabela_minhas.get_children():
            self.tabela_minhas.delete(linha)
        inscricoes = participante.historico_inscricoes
        if inscricoes:
            self.resumo_minhas.config(text=f"Total de inscrições confirmadas: {len(inscricoes)}")
        else:
            self.resumo_minhas.config(text="Você ainda não tem inscrições confirmadas.")
        for inscricao in inscricoes:
            evento = inscricao.evento
            detalhes = (inscricao.ingresso.nome_tipo(), inscricao.codigo, "Confirmada")
            if evento.sessoes:
                for sessao in evento.sessoes:
                    self.tabela_minhas.insert("", tk.END, values=(evento.nome, sessao.data_hora, sessao.local, *detalhes))
            else:
                self.tabela_minhas.insert("", tk.END, values=(evento.nome, "A definir", "A definir", *detalhes))

    def preencher_confirmados(self):
        eventos = self.gerenciador.eventos
        self.combo_confirmados["values"] = [f"{i}. {evento.nome}" for i, evento in enumerate(eventos, 1)]
        if eventos:
            self.combo_confirmados.current(0)
        self._atualizar_confirmados()

    def codigo_inscricao_selecionada(self):
        selecao = self.tabela_minhas.selection()
        if selecao:
            return self.tabela_minhas.set(selecao[0], "codigo")
        return None

    def _atualizar_confirmados(self, evento_tk=None):
        for linha in self.tabela_confirmados.get_children():
            self.tabela_confirmados.delete(linha)
        indice = self.combo_confirmados.current()
        if indice < 0:
            self.resumo_confirmados.config(text="Nenhum evento selecionado.")
            return

        evento = self.gerenciador.eventos[indice]
        inscricoes = self.gerenciador.inscricoes_do_evento(evento)
        arrecadacao = self.gerenciador.calcular_arrecadacao(evento)
        resumo = f"Ocupação: {evento.ingressos_vendidos}/{evento.capacidade_maxima} | Arrecadação simulada: R$ {arrecadacao:.2f}"
        if not inscricoes:
            resumo += " | Nenhuma inscrição confirmada."
        self.resumo_confirmados.config(text=resumo)
        for inscricao in inscricoes:
            participante = inscricao.participante
            self.tabela_confirmados.insert("", tk.END, values=(participante.nome,
                participante.tipo(), inscricao.ingresso.nome_tipo(), inscricao.codigo))
