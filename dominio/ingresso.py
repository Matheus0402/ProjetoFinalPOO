from abc import ABC, abstractmethod

class Ingresso(ABC):
    def __init__(self, preco_base: float):
        self._preco_base = preco_base

    @abstractmethod
    def calcular_preco_final(self) -> float:
        pass

    @abstractmethod
    def nome_tipo(self) -> str:
        pass

    @property
    def preco_base(self) -> float:
        return self._preco_base


class IngressoInteira(Ingresso):
    def calcular_preco_final(self) -> float:
        return self._preco_base

    def nome_tipo(self) -> str:
        return "Inteira"


class IngressoMeia(Ingresso):
    def calcular_preco_final(self) -> float:
        return self._preco_base * 0.50

    def nome_tipo(self) -> str:
        return "Meia-Entrada"


class IngressoVIP(Ingresso):
    def calcular_preco_final(self) -> float:
        return self._preco_base * 1.30  # Adicional de 30% por benefícios VIP

    def nome_tipo(self) -> str:
        return "VIP"


class IngressoGratuito(Ingresso):
    def calcular_preco_final(self) -> float:
        return 0.0

    def nome_tipo(self) -> str:
        return "Gratuito"