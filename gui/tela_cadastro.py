import tkinter as tk
from tkinter import messagebox, ttk

from dominio.excecoes import EventoError
from dominio.usuario import Aluno, Visitante


class TelaCadastro(ttk.Frame):
    def __init__(self, pai, gerenciador, criar_campo, criar_combo, ao_cadastrar):
        super().__init__(pai, padding=16)
        self.gerenciador = gerenciador
        self.ao_cadastrar = ao_cadastrar

        self.combo_perfil = criar_combo(self, 0, "Perfil", ("Aluno da UTFPR", "Visitante"))
        self.combo_perfil.current(0)
        self.entry_nome = criar_campo(self, 1, "Nome")
        self.entry_email = criar_campo(self, 2, "E-mail")
        self.entry_documento = criar_campo(self, 3, "RA do aluno ou CPF do visitante")
        ttk.Button(self, text="Cadastrar e entrar", command=self._cadastrar_participante, style="Primario.TButton").grid(row=4, column=1, sticky="e", pady=10)

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
        self.ao_cadastrar(participante)
