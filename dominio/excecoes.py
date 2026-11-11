class EventoError(Exception):
    """Erro base do sistema (todos os nossos erros herdam dele)."""
    pass


class RAInvalidoError(EventoError):
    pass


class ParticipanteJaCadastradoError(EventoError):
    pass


class LotacaoEsgotadaError(EventoError):
    pass


class DadosInvalidosError(EventoError):
    pass


class CPFInvalidoError(EventoError):
    pass