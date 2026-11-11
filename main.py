from dominio.usuario import Participante, Organizador
from dominio.evento import Evento, Categoria
from dominio.ingresso import IngressoInteira, IngressoMeia, IngressoVIP
from dominio.gerenciador import GerenciadorDeEventos

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
        print("1. Cadastrar Participante")
        print("2. Listar Eventos Disponíveis")
        print("3. Comprar Ingresso / Realizar Inscrição")
        print("4. Sair")
        opcao = input("Escolha uma opção: ")

        if opcao == "1":
            nome = input("Nome: ")
            email = input("E-mail: ")
            cpf = input("CPF: ")
            p = Participante(nome, email, cpf)
            gerenciador.cadastrar_participante(p)
            print(f"Participante '{nome}' cadastrado com sucesso!")

        elif opcao == "2":
            print("\n--- Eventos Cadastrados ---")
            for idx, ev in enumerate(gerenciador.eventos, 1):
                vagas = ev.capacidade_maxima - ev.ingressos_vendidos
                print(f"{idx}. {ev.nome} [{ev.categoria.nome}] - Vagas restantes: {vagas}/{ev.capacidade_maxima}")
                for s in ev.sessoes:
                    print(f"   -> Sessão: {s.data_hora} | Local: {s.local}")

        elif opcao == "3":
            if not gerenciador.participantes:
                print("Erro: Nenhum participante cadastrado no sistema!")
                continue

            print("\nSelecione o Participante:")
            for idx, p in enumerate(gerenciador.participantes, 1):
                print(f"{idx}. {p.nome} ({p.identificacao})")
            idx_p = int(input("Número do participante: ")) - 1
            participante_sel = gerenciador.participantes[idx_p]

            print("\nSelecione o Evento:")
            for idx, ev in enumerate(gerenciador.eventos, 1):
                print(f"{idx}. {ev.nome}")
            idx_e = int(input("Número do evento: ")) - 1
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
                print("\n Inscrição realizada com sucesso!")
                print(inscricao.comprovante.obter_resumo())
            except Exception as err:
                print(f"\n Erro ao realizar inscrição: {err}")

        elif opcao == "4":
            print("Saindo do sistema...")
            break
        else:
            print("Opção inválida!")

if __name__ == "__main__":
    menu_principal()
