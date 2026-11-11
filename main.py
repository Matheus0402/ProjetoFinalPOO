from dominio.usuario import Aluno, Visitante, Organizador, formatar_identificacao
from dominio.evento import Evento, Categoria
from dominio.gerenciador import GerenciadorDeEventos
from dominio.excecoes import EventoError


def ler_numero(texto: str) -> int:
    # Se o usuário digitar letra, devolve -1 em vez de quebrar o programa
    try:
        return int(input(texto))
    except ValueError:
        return -1


def ler_decimal(texto: str) -> float:
    # Aceita vírgula ou ponto (25,50 ou 25.50). Se der erro, devolve -1
    try:
        return float(input(texto).replace(",", "."))
    except ValueError:
        return -1.0


def listar_eventos(gerenciador):
    print("\n--- Eventos Cadastrados ---")
    if len(gerenciador.eventos) == 0:
        print("Nenhum evento cadastrado.")
    for idx, ev in enumerate(gerenciador.eventos, 1):
        vagas = ev.capacidade_maxima - ev.ingressos_vendidos
        aviso = " (GRATUITO PARA ALUNOS)" if ev.gratuito_para_alunos else ""
        print(f"{idx}. {ev.nome} [{ev.categoria.nome}] - Preço base: R$ {ev.preco_base:.2f} - Vagas restantes: {vagas}/{ev.capacidade_maxima}{aviso}")
        for s in ev.sessoes:
            print(f"   -> Sessão: {s.data_hora} | Local: {s.local}")


def escolher_evento(gerenciador):
    # Mostra a lista e devolve o evento escolhido (ou None se for inválido)
    for idx, ev in enumerate(gerenciador.eventos, 1):
        print(f"{idx}. {ev.nome}")
    idx_e = ler_numero("Número do evento: ") - 1
    if idx_e < 0 or idx_e >= len(gerenciador.eventos):
        print("Evento inválido.")
        return None
    return gerenciador.eventos[idx_e]


def menu_participante(gerenciador):
    while True:
        print("\n=== ÁREA DO PARTICIPANTE ===")
        print("1. Cadastrar Participante")
        print("2. Listar Eventos Disponíveis")
        print("3. Comprar Ingresso / Realizar Inscrição")
        print("4. Voltar")
        opcao = input("Escolha uma opção: ")

        if opcao == "1":
            print("1. Aluno da UTFPR (usa RA)")
            print("2. Visitante (usa CPF)")
            tipo_cadastro = input("Tipo de participante: ")
            if tipo_cadastro != "1" and tipo_cadastro != "2":
                print("Tipo inválido.")
                continue

            nome = input("Nome: ")
            email = input("E-mail: ")
            try:
                if tipo_cadastro == "1":
                    ra = input("RA (ex: a2669560): ")
                    participante = Aluno(nome, email, ra)  # aqui o RA é validado e corrigido
                else:
                    cpf = input("CPF (ex: 123.456.789-09): ")
                    participante = Visitante(nome, email, cpf)  # aqui o CPF é validado e limpo
                gerenciador.cadastrar_participante(participante)
                print(f"{participante.tipo()} '{participante.nome}' cadastrado com sucesso! Identificação: {participante.identificacao}")
            except EventoError as erro:
                print(f"Erro: {erro}")

        elif opcao == "2":
            listar_eventos(gerenciador)

        elif opcao == "3":
            identificacao = input("Digite seu RA ou CPF: ")
            try:
                identificacao = formatar_identificacao(identificacao)
            except EventoError as erro:
                print(f"Erro: {erro}")
                continue

            participante_sel = gerenciador.buscar_participante(identificacao)
            if participante_sel is None:
                print("RA/CPF não encontrado. Faça o cadastro primeiro!")
                continue

            print(f"\nOlá, {participante_sel.nome}!")
            print("Selecione o Evento:")
            evento_sel = escolher_evento(gerenciador)
            if evento_sel is None:
                continue

            # O gerenciador decide quais ingressos existem para esse participante
            opcoes = gerenciador.ingressos_disponiveis(evento_sel, participante_sel)
            if evento_sel.eh_gratuito_para(participante_sel):
                print("\nEste evento é gratuito para alunos da UTFPR!")

            print("\nSelecione o Tipo de Ingresso:")
            for i in range(len(opcoes)):
                print(f"{i + 1}. {opcoes[i].nome_tipo()} (R$ {opcoes[i].calcular_preco_final():.2f})")
            tipo = ler_numero("Tipo: ") - 1
            if tipo < 0 or tipo >= len(opcoes):
                print("Opção inválida.")
                continue
            ingresso = opcoes[tipo]

            try:
                inscricao = gerenciador.realizar_inscricao(participante_sel, evento_sel, ingresso, "Cartão de Crédito")
                print("\nInscrição realizada com sucesso!")
                print(inscricao.comprovante.obter_resumo())
            except EventoError as err:
                print(f"\nErro ao realizar inscrição: {err}")

        elif opcao == "4":
            break
        else:
            print("Opção inválida!")


def menu_organizador(gerenciador):
    codigo = input("Código do organizador: ")
    organizador = gerenciador.buscar_organizador(codigo.strip())
    if organizador is None:
        print("Organizador não encontrado.")
        return

    while True:
        print(f"\n=== ÁREA DO ORGANIZADOR ({organizador.nome}) ===")
        print("1. Criar Evento")
        print("2. Adicionar Sessão a um Evento")
        print("3. Relatório de Vendas")
        print("4. Voltar")
        opcao = input("Escolha uma opção: ")

        if opcao == "1":
            nome = input("Nome do evento: ")
            capacidade = ler_numero("Capacidade máxima: ")
            preco = ler_decimal("Preço base (R$): ")
            resposta = input("Gratuito para alunos da UTFPR? (s/n): ")
            gratuito = resposta.strip().lower() == "s"

            print("Categorias:")
            for idx, cat in enumerate(gerenciador.categorias, 1):
                print(f"{idx}. {cat.nome}")
            pos = ler_numero("Número da categoria: ") - 1
            if pos < 0 or pos >= len(gerenciador.categorias):
                print("Categoria inválida.")
                continue

            try:
                evento = Evento(nome, capacidade, gerenciador.categorias[pos], preco, gratuito)
                gerenciador.cadastrar_evento(evento)
                print(f"Evento '{evento.nome}' criado com sucesso!")
            except EventoError as erro:
                print(f"Erro: {erro}")

        elif opcao == "2":
            if len(gerenciador.eventos) == 0:
                print("Nenhum evento cadastrado.")
                continue
            evento_sel = escolher_evento(gerenciador)
            if evento_sel is None:
                continue
            data_hora = input("Data e hora (ex: 15/11/2026 14:00): ")
            local = input("Local: ")
            try:
                evento_sel.adicionar_sessao(data_hora, local)
                print("Sessão adicionada com sucesso!")
            except EventoError as erro:
                print(f"Erro: {erro}")

        elif opcao == "3":
            print("\n--- Relatório de Vendas ---")
            if len(gerenciador.eventos) == 0:
                print("Nenhum evento cadastrado.")
            for ev in gerenciador.eventos:
                total = gerenciador.calcular_arrecadacao(ev)
                print(f"{ev.nome}: {ev.ingressos_vendidos}/{ev.capacidade_maxima} ingressos vendidos | Arrecadado: R$ {total:.2f}")

        elif opcao == "4":
            break
        else:
            print("Opção inválida!")


def menu_principal():
    gerenciador = GerenciadorDeEventos()

    # Dados de teste pré-carregados
    cat_tech = Categoria("Tecnologia")
    cat_arte = Categoria("Cultura")
    cat_palestra = Categoria("Palestra")
    gerenciador.cadastrar_categoria(cat_tech)
    gerenciador.cadastrar_categoria(cat_arte)
    gerenciador.cadastrar_categoria(cat_palestra)

    gerenciador.cadastrar_organizador(Organizador("Organização UTFPR", "eventos@utfpr.edu.br", "admin"))

    ev1 = Evento("Tech Conference 2026", 2, cat_tech, 100.0)  # Limite 2 para teste de lotação
    ev1.adicionar_sessao("15/11/2026 14:00", "Auditório Bloco D")

    ev2 = Evento("Festival de Jazz", 50, cat_arte, 60.0)
    ev2.adicionar_sessao("20/11/2026 20:00", "Auditório Bloco N313")

    gerenciador.cadastrar_evento(ev1)
    gerenciador.cadastrar_evento(ev2)

    while True:
        print("\n=== SISTEMA DE GESTÃO DE EVENTOS ===")
        print("1. Área do Participante")
        print("2. Área do Organizador")
        print("3. Sair")
        opcao = input("Escolha uma opção: ")

        if opcao == "1":
            menu_participante(gerenciador)
        elif opcao == "2":
            menu_organizador(gerenciador)
        elif opcao == "3":
            print("Saindo do sistema...")
            break
        else:
            print("Opção inválida!")


if __name__ == "__main__":
    menu_principal()