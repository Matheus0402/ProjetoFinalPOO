import tkinter as tk
from tkinter import ttk

from dominio.usuario import Aluno, Participante, Visitante


class ParticipanteFactory:
    """Padrão Factory Method: centraliza a criação de instâncias de Participante."""

    @staticmethod
    def criar_participante(perfil: str, nome: str, email: str, documento: str) -> Participante:
        if perfil == "Aluno da UTFPR":
            return Aluno(nome, email, documento)
        return Visitante(nome, email, documento)


class WidgetFactory:
    """Padrão Factory Method: padroniza a criação de componentes visuais do Tkinter."""

    @staticmethod
    def criar_campo(quadro, linha: int, titulo: str) -> ttk.Entry:
        ttk.Label(quadro, text=titulo).grid(row=linha, column=0, sticky="w", pady=4)
        campo = ttk.Entry(quadro, width=35)
        campo.grid(row=linha, column=1, sticky="ew", padx=8, pady=4)
        return campo

    @staticmethod
    def criar_combo(quadro, linha: int, titulo: str, valores=()) -> ttk.Combobox:
        ttk.Label(quadro, text=titulo).grid(row=linha, column=0, sticky="w", pady=4)
        combo = ttk.Combobox(quadro, state="readonly", width=33, values=valores)
        combo.grid(row=linha, column=1, sticky="ew", padx=8, pady=4)
        return combo

    @staticmethod
    def criar_tabela(tela, colunas) -> ttk.Treeview:
        quadro = ttk.Frame(tela)
        quadro.pack(fill="both", expand=True, pady=8)
        tabela = ttk.Treeview(
            quadro,
            columns=[coluna[0] for coluna in colunas],
            show="headings",
            selectmode="none",
        )
        for coluna, titulo, largura in colunas:
            tabela.heading(coluna, text=titulo)
            tabela.column(
                coluna,
                width=largura,
                minwidth=65,
                anchor="center" if coluna == "vagas" else "w",
            )

        barra = ttk.Scrollbar(quadro, orient="vertical", command=tabela.yview)
        tabela.configure(yscrollcommand=barra.set)
        barra.pack(side="right", fill="y")
        tabela.pack(side="left", fill="both", expand=True)
        return tabela
