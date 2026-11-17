from tkinter import ttk


def configurar_estilos(root):
    fundo = "#f3f6f9"
    branco = "#ffffff"
    texto = "#172333"
    azul = "#0059b8"
    borda = "#cbd6e2"
    root.configure(bg=fundo)

    estilo = ttk.Style(root)
    # O tema clam permite usar as mesmas cores dos botões no Windows e no Linux.
    estilo.theme_use("clam")
    estilo.configure("TFrame", background=branco)
    estilo.configure("Barra.TFrame", background=fundo)
    estilo.configure("TLabel", background=branco, foreground=texto)
    estilo.configure("Apoio.TLabel", foreground="#506174")
    estilo.configure("Status.TLabel", background=fundo, foreground=azul, font=("Arial", 10, "bold"))
    estilo.configure("TLabelframe", background=branco, bordercolor=borda)
    estilo.configure("TLabelframe.Label", background=branco, foreground=texto, font=("Arial", 10, "bold"))
    estilo.configure("TCheckbutton", background=branco, foreground=texto)
    estilo.map("TCheckbutton", background=[("active", branco)])

    # TButton é o estilo comum. Primario.TButton destaca a ação principal.
    estilo.configure("TButton", background=branco, foreground=azul, bordercolor=azul,
                     lightcolor=branco, darkcolor=branco, focuscolor=azul, padding=(12, 6))
    estilo.map("TButton",
               background=[("disabled", fundo), ("pressed", "#d9eaff"), ("active", "#eaf4ff")],
               foreground=[("disabled", "#536475")],
               bordercolor=[("disabled", borda)])
    estilo.configure("Primario.TButton", background=azul, foreground=branco, bordercolor=azul,
                     lightcolor=azul, darkcolor=azul, focuscolor=branco, font=("Arial", 10, "bold"))
    estilo.map("Primario.TButton",
               background=[("disabled", fundo), ("pressed", "#004087"), ("active", "#004d9e")],
               foreground=[("disabled", "#536475")])

    estilo.configure("Treeview", background=branco, fieldbackground=branco, foreground=texto,
                     bordercolor=borda, rowheight=28)
    estilo.configure("Treeview.Heading", background="#eaf1f8", foreground=texto, font=("Arial", 10, "bold"))
