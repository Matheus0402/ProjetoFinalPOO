class Observavel:
    def __init__(self):
        self._observadores = [] # cria a lista dos observadores

    def adicionar_observador(self, observador): # registra a funcao que deseja receber notificacao
        self._observadores.append(observador)

    def remover_observador(self, observador): # retira uma funcao da lista de observadores
        self._observadores.remove(observador)
 
    def notificar_observadores(self): # percorre a lista e executa cada funcao registrada
        for observador in self._observadores:
            observador()