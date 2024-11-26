# personagens/personagem.py
"""Classe para manipulação de personagens"""

class Personagem:
    """Atributos do personagem"""

    def __init__(self, nome, player, st, dx, iq, ht, pva=None, pfa=None, pma=None, ponto_ini=0, ponto_rec=0):
        self.nome = nome
        self.player = player
        self.st = st
        self.dx = dx
        self.iq = iq
        self.ht = ht
        self.pva = pva if pva is not None else self.pv
        self.pfa = pfa if pfa is not None else self.pf
        self.pma = pma if pma is not None else int(self.iq - 6)
        self.ponto_int = ponto_ini
        self.ponto_rec = ponto_rec

    # Calculos Atributos Avançados
    @property
    def pv(self):
        """Calcula o Pontos de Vida do personagem"""
        return self.st

    @property
    def vtd(self):
        """Calcula a Vontade do personagem"""
        return self.iq

    @property
    def per(self):
        """Calcula a Percepção do personagem"""
        return self.iq

    @property
    def pf(self):
        """Calcula os Pontos de Fatiga do personagem"""
        return self.ht

    @property
    def carga_basica(self):
        """Calcula o quanto o personagem pode carregar de peso"""
        return round((self.st**2)/5)

    @property
    def velocidade_basica(self):
        """Calcula a Velocidade de Reação do personagem"""
        return (self.dx+self.ht)/4

    @property
    def deslocamento_basico(self):
        """Calcula o quando o personagem pode andar no turno"""
        return (self.dx+self.ht)//4

    @property
    def esquiva(self):
        """calcula o valor da esquiva"""
        return round(self.velocidade_basica+3)

    @property
    def pm(self):
        """calcula o valor da esquiva"""
        return int(self.iq-4)
