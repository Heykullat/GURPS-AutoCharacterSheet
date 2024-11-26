# pericias.py
"""Arquivo Utilizado para manipulação dos atributos de uma pericia"""

class Pericia:
    """Classe responsavel pela manipulação das pericias"""
    def __init__(self, nome="", atributo="", dificuldade="",
                 pontos_gastos=0, mod_pericia=None, mod_extra=None):
        self.nome = nome
        self.atributo = atributo
        self.dificuldade = dificuldade
        self.pontos_gastos = pontos_gastos
        self.mod_pericia = mod_pericia
        self.mod_extra = mod_extra

    def to_dict(self):
        """função que converte uma pericias em dicionario"""
        return {
            "nome": self.nome,
            "atributo": self.atributo,
            "dificuldade": self.dificuldade,
            "pontos_gastos": self.pontos_gastos,
            "mod_pericia": self.mod_pericia,
            "mod_extra": self.mod_extra
        }

    @classmethod
    def from_dict(cls, data):
        """função que converte um dicionario de pericia em atributos"""
        return cls(
            nome=data.get("nome", ""),
            atributo=data.get("atributo", ""),
            dificuldade=data.get("dificuldade", ""),
            pontos_gastos=data.get("pontos_gastos", 0),
            mod_pericia=data.get("mod_pericia"),
            mod_extra=data.get("mod_extra")
            )