from dominio.usuario import Aluno, formatar_ra
from dominio.evento import Evento, Categoria
from dominio.ingresso import IngressoInteira, IngressoMeia, IngressoVIP
from dominio.gerenciador import GerenciadorDeEventos
from dominio.excecoes import EventoError


def ler_numero(texto: str) -> int:
    # Se o usuário digitar letra, devolve -1 em vez de quebrar o programa
    try:
        return int(input(texto))
    except ValueError:
        return -1


def menu_principal():
    gerenciador = GerenciadorDeEventos()

    # Dados de teste pré-carregados
    cat_tech = Categoria("Tecnologia")
    cat_arte = Categoria("Cultura")

    ev1 = Evento("Tech Conference 2026", 2, cat_tech)  # Limite 2 para teste de lotação
    ev1.adicionar_sessao("15/11/2026 14:00", "Auditório Central")

    ev2 = Evento("Festival de Jazz", 50, cat_arte)
    ev2.adicionar_sessao("20/11/2026 20:00", "Teatro Municipal")

    gerenciador.cadastrar_evento(ev1)
    gerenciador.cadastrar_evento(ev2)

    while True:
        print("\n=== SISTEMA DE GESTÃO DE EVENTOS ===")
        print("1. Cadastrar Aluno")
        print("2. Listar Eventos Disponíveis")
        print("3. Comprar Ingresso / Realizar Inscrição")
        print("4. Sair")
        opcao = input("Escolha uma opção: ")

        if opcao == "1":
            nome = input("Nome: ")
            email = input("E-mail: ")
            ra = input("RA (ex: a2669560): ")
            try:
                aluno = Aluno(nome, email, ra)  # aqui o RA é validado e corrigido
                gerenciador.cadastrar_participante(aluno)
                print(f"Aluno '{aluno.nome}' cadastrado com sucesso! RA: {aluno.identificacao}")
            except EventoError as erro:
                print(f"Erro: {erro}")

        elif opcao == "2":
            print("\n--- Eventos Cadastrados ---")
            for idx, ev in enumerate(gerenciador.eventos, 1):
                vagas = ev.capacidade_maxima - ev.ingressos_vendidos
                print(f"{idx}. {ev.nome} [{ev.categoria.nome}] - Vagas restantes: {vagas}/{ev.capacidade_maxima}")
                for s in ev.sessoes:
                    print(f"   -> Sessão: {s.data_hora} | Local: {s.local}")

        elif opcao == "3":
            ra = input("Digite seu RA: ")
            try:
                ra = formatar_ra(ra)
            except EventoError as erro:
                print(f"Erro: {erro}")
                continue

            participante_sel = gerenciador.buscar_participante(ra)
            if participante_sel is None:
                print("RA não encontrado. Faça o cadastro primeiro!")
                continue

            print(f"\nOlá, {participante_sel.nome}!")
            print("Selecione o Evento:")
            for idx, ev in enumerate(gerenciador.eventos, 1):
                print(f"{idx}. {ev.nome}")
            idx_e = ler_numero("Número do evento: ") - 1
            if idx_e < 0 or idx_e >= len(gerenciador.eventos):
                print("Evento inválido.")
                continue
            evento_sel = gerenciador.eventos[idx_e]

            print("\nSelecione o Tipo de Ingresso (Preço Base R$ 100,00):")
            print("1. Inteira (R$ 100.00)")
            print("2. Meia-Entrada (R$ 50.00)")
            print("3. VIP (R$ 130.00)")
            tipo = input("Tipo: ")

            preco_base = 100.0
            if tipo == "1":
                ingresso = IngressoInteira(preco_base)
            elif tipo == "2":
                ingresso = IngressoMeia(preco_base)
            elif tipo == "3":
                ingresso = IngressoVIP(preco_base)
            else:
                print("Opção inválida.")
                continue

            try:
                inscricao = gerenciador.realizar_inscricao(participante_sel, evento_sel, ingresso, "Cartão de Crédito")
                print("\nInscrição realizada com sucesso!")
                print(inscricao.comprovante.obter_resumo())
            except EventoError as err:
                print(f"\nErro ao realizar inscrição: {err}")

        elif opcao == "4":
            print("Saindo do sistema...")
            break
        else:
            print("Opção inválida!")


if __name__ == "__main__":
    menu_principal()