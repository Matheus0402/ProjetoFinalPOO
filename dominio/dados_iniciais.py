from dominio.evento import Categoria, Evento
from dominio.usuario import Organizador


def carregar_dados_iniciais(gerenciador):
    # Exemplos fictícios para demonstrar o projeto, não são eventos oficiais.
    palestra = Categoria("Palestra")
    oficina = Categoria("Oficina")
    cultura = Categoria("Mostra cultural")
    for categoria in (palestra, oficina, cultura, Categoria("Minicurso"),
                      Categoria("Semana acadêmica"), Categoria("Projeto de extensão"),
                      Categoria("Visita técnica")):
        gerenciador.cadastrar_categoria(categoria)

    gerenciador.cadastrar_organizador(
        Organizador("Organização UTFPR", "eventos@utfpr.edu.br", "admin")
    )

    evento = Evento("Palestra de Engenharia de Computação", 60, palestra, 0.0)
    evento.adicionar_sessao("23/11/2026 14:00", "Auditório Bloco D")
    gerenciador.cadastrar_evento(evento)

    evento = Evento("Mostra Cultural do Campus", 50, cultura, 10.0, gratuito_para_alunos=True)
    evento.adicionar_sessao("24/11/2026 19:00", "Auditório N311")
    gerenciador.cadastrar_evento(evento)

    evento = Evento("Oficina de Introdução ao Python", 25, oficina, 0.0)
    evento.adicionar_sessao("25/11/2026 15:30", "Sala de aula (a definir)")
    gerenciador.cadastrar_evento(evento)
