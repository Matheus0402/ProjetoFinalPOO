import tkinter as tk
from tkinter import messagebox, simpledialog, ttk

from dominio.evento import Categoria, Evento
from dominio.excecoes import EventoError


class TelaOrganizador(ttk.Frame):
    def __init__(self, pai, gerenciador, criar_campo, criar_combo, organizador_atual):
        super().__init__(pai, padding=16)
        self.gerenciador = gerenciador
        self.organizador_atual = organizador_atual

        quadro = ttk.LabelFrame(self, text="Novo evento com a primeira sessão", padding=8)
        quadro.pack(fill="x")
        self.entry_evento = criar_campo(quadro, 0, "Nome do evento")
        self.combo_categoria = criar_combo(quadro, 1, "Categoria", [cat.nome for cat in self.gerenciador.categorias])
        self.combo_categoria.current(0)
        self.entry_capacidade = criar_campo(quadro, 2, "Capacidade máxima")
        self.entry_preco = criar_campo(quadro, 3, "Preço base (R$)")
        self.entry_data = criar_campo(quadro, 4, "Data e hora")
        self.entry_local = criar_campo(quadro, 5, "Local")
        self.gratuito_alunos = tk.BooleanVar()
        ttk.Checkbutton(quadro, text="Gratuito para alunos da UTFPR", variable=self.gratuito_alunos).grid(row=6, column=1, sticky="w")
        ttk.Button(quadro, text="Publicar evento", command=self._criar_evento, style="Primario.TButton").grid(row=7, column=1, sticky="e", pady=6)

    def criar_categoria(self):
        if self.organizador_atual() is None:
            return
        nome = simpledialog.askstring("Criar categoria", "Nome da nova categoria:", parent=self.winfo_toplevel())
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

    def _criar_evento(self):
        if self.organizador_atual() is None:
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

        
        for campo in (self.entry_evento, self.entry_capacidade, self.entry_preco, self.entry_data, self.entry_local):
            campo.delete(0, tk.END)
        self.gratuito_alunos.set(False)
        messagebox.showinfo("Evento publicado", f"{evento.nome} já está na lista de eventos.")
