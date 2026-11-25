from tkinter import messagebox, ttk

from dominio.excecoes import EventoError
from dominio.gerenciador import Pagamento


class TelaInscricao(ttk.Frame):
    def __init__(self, pai, gerenciador, criar_combo, participante_atual):
        super().__init__(pai, padding=16)
        self.gerenciador = gerenciador
        self.participante_atual = participante_atual
        self.opcoes_ingresso = []

        self.combo_evento = criar_combo(self, 0, "Evento")
        self.combo_evento.bind("<<ComboboxSelected>>", self._atualizar_ingressos)
        self.combo_tipo = criar_combo(self, 1, "Tipo de ingresso")
        self.combo_tipo.bind("<<ComboboxSelected>>", self._atualizar_pagamento)
        self.combo_pagamento = criar_combo(self, 2, "Pagamento simulado", Pagamento.FORMAS_DISPONIVEIS)
        ttk.Button(self, text="Confirmar inscrição", command=self._realizar_compra, style="Primario.TButton").grid(row=3, column=1, sticky="e", pady=10)

    def atualizar_eventos(self):
        selecao = self.combo_evento.current()
        self.combo_evento["values"] = [evento.nome for evento in self.gerenciador.eventos]
        if selecao >= 0:
            self.combo_evento.current(selecao)
        self._atualizar_ingressos()

    def _atualizar_ingressos(self, evento_tk=None):
        participante = self.participante_atual()
        indice = self.combo_evento.current()
        self.opcoes_ingresso = []
        if participante is not None and indice >= 0:
            evento = self.gerenciador.eventos[indice]
            self.opcoes_ingresso = self.gerenciador.ingressos_disponiveis(evento, participante)

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
        if 0 <= indice < len(self.opcoes_ingresso) and self.opcoes_ingresso[indice].calcular_preco_final() > 0:
            self.combo_pagamento.config(state="readonly")
        else:
            self.combo_pagamento.config(state="disabled")

    def _realizar_compra(self):
        participante = self.participante_atual()
        indice_evento = self.combo_evento.current()
        indice_ingresso = self.combo_tipo.current()
        if participante is None or indice_evento < 0 or indice_ingresso < 0:
            messagebox.showwarning("Inscrição", "Entre como participante e escolha o evento e o ingresso.")
            return

        evento = self.gerenciador.eventos[indice_evento]
        ingresso = self.opcoes_ingresso[indice_ingresso]
        forma = self.combo_pagamento.get()
        if ingresso.calcular_preco_final() > 0 and not forma:
            messagebox.showwarning("Inscrição", "Escolha a forma de pagamento.")
            return

        try:
            inscricao = self.gerenciador.realizar_inscricao(participante, evento, ingresso, forma)
        except EventoError as erro:
            messagebox.showerror("Inscrição não realizada", str(erro))
            return


        messagebox.showinfo("Inscrição confirmada", inscricao.comprovante.obter_resumo())
