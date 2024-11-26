# rolagem_dados.py
"""Funções para rolagem de dados"""

import re
import random

class RolagemDados:
    """Classe para rolar dados"""

    def rolar_1d6(self):
        """Rola um dado de 6 lados"""
        return random.randint(1, 6)

    def rolar_3d6(self):
        """Rola três dados de 6 lados"""
        return [random.randint(1, 6) for _ in range(3)]

class CalculoPericia:
    """Classe criada para centrelizar o calculo dos mod"""
    # Dicionário com os custos para cada dificuldade e modificador
    tabela_mod = {
        "F": {0:-4, 1: +0, 3: +1, 7: +2, 15: +3, 27: +4, 43: +5, 63: +6, 87: +7, 111: +8},  # Fácil
        "M": {0:-5, 1: -1, 3: +0, 7: +1, 15: +2, 27: +3, 43: +4, 63: +5, 87: +6, 111: +7},  # Médio
        "D": {0:-6, 1: -2, 3: -1, 7: +0, 15: +1, 27: +2, 43: +3, 63: +4, 87: +5, 111: +6},  # Difícil
       "MD": {0:-9, 1: -3, 3: -2, 7: -1, 15: +0, 27: +1, 43: +2, 63: +3, 87: +4, 111: +5}  # Muito Difícil
    }

    @classmethod
    def cal_mod(cls, dificuldade, modificador):
        """Calcula o modificador das pericias"""
        if dificuldade in cls.tabela_mod and modificador in cls.tabela_mod[dificuldade]:
            return cls.tabela_mod[dificuldade][modificador]
        else:
            return None  # Retorna None se a dificuldade ou o modificador não estiverem na tabela

class CalculoDano:
    """Classe para calcular o dano de armas melee com base no atributo ST"""

    # Tabela de dano baseada em ST
    tabela_dano = {
        1:  {"GDP": "1d6-6", "BAL": "1d6-5"},
        2:  {"GDP": "1d6-6", "BAL": "1d6-5"},
        3:  {"GDP": "1d6-5", "BAL": "1d6-4"},
        4:  {"GDP": "1d6-5", "BAL": "1d6-4"},
        5:  {"GDP": "1d6-4", "BAL": "1d6-3"},
        6:  {"GDP": "1d6-4", "BAL": "1d6-3"},
        7:  {"GDP": "1d6-3", "BAL": "1d6-2"},
        8:  {"GDP": "1d6-3", "BAL": "1d6-2"},
        9:  {"GDP": "1d6-2", "BAL": "1d6-1"},
        10: {"GDP": "1d6-2", "BAL": "1d6+0"},
        11: {"GDP": "1d6-1", "BAL": "1d6+1"},
        12: {"GDP": "1d6-1", "BAL": "1d6+2"},
        13: {"GDP": "1d6+0", "BAL": "2d6-1"},
        14: {"GDP": "1d6+0", "BAL": "2d6+0"},
        15: {"GDP": "1d6+1", "BAL": "2d6+1"},
        16: {"GDP": "1d6+1", "BAL": "2d6+2"},
        17: {"GDP": "1d6+2", "BAL": "3d6-1"},
        18: {"GDP": "1d6+2", "BAL": "3d6+0"},
        19: {"GDP": "2d6-1", "BAL": "3d6+1"},
        20: {"GDP": "2d6-1", "BAL": "3d6+2"}
    }

    @classmethod
    def interface_dano(cls, st, tipo="GDP"):
        """Calcula o dano com base no ST e no tipo de dano (GDP ou BAL)"""
        if st in cls.tabela_dano:
            return cls.tabela_dano[st].get(tipo, "Dano não definido")
        else:
            return "ST fora do alcance"

    @staticmethod
    def calcular_dano(dano_string):
        """Calcula o dano com base em uma string no formato 'XdY+Z' ou 'XdY-Z'."""

        # Extrai os valores usando regex
        match = re.match(r'(\d+)d(\d+)([+-]\d+)?', dano_string)
        if not match:
            print("Formato de dano inválido.")
            return None

        # Número de dados, lados do dado e modificador
        num_dados = int(match.group(1))
        lados_dado = int(match.group(2))
        extra = int(match.group(3) or 0)

        # Rola os dados e soma o resultado
        total_dano = sum(random.randint(1, lados_dado) for _ in range(num_dados))

        # Aplica o modificador extra
        total_dano += extra

        return max(total_dano,1)

class CalculoAtributosCombate:
    """Classe para centralizar os cálculos de atributos de combate."""

    @staticmethod
    def calcular(pericias, atributos):
        """Calcula bloqueio, aparar físico, aparar mágico e PMM.
        
        Args:
            pericias (list): Lista de dicionários com dados das perícias.
            atributos (dict): Dicionário com valores dos atributos.

        Returns:
            dict: Valores calculados de combate: bloqueio, aparar_fisico, aparar_magico, e pmm.
        """
        bloqueio = 0
        aparar_fisico = 0
        aparar_magico = 0
        pmm = atributos["iq"]-6  # Valor padrão se nenhuma perícia tiver o checkbox PM marcado

        for pericia in pericias:
            # Calcula o nível de habilidade apenas para a perícia específica
            nivel_habilidade = pericia["mod_pts"] + atributos.get(pericia["atributo"], 0)

            # Verifica se o checkbox de Bloqueio está marcado e calcula
            if pericia.get("bloqueio"):
                bloqueio = nivel_habilidade // 2 + 3

            # Verifica se o checkbox de Aparar Físico está marcado e calcula
            if pericia.get("aparar_fisico"):
                aparar_fisico = nivel_habilidade // 2 + 3

            # Verifica se o checkbox de Aparar Mágico está marcado e calcula
            if pericia.get("aparar_magico"):
                aparar_magico = nivel_habilidade // 2 + 3

            # Verifica se o checkbox PM está marcado e calcula o PMM
            if pericia.get("poder_magico"):
                pmm = nivel_habilidade

        return {
            "bloqueio": bloqueio,
            "aparar_fisico": aparar_fisico,
            "aparar_magico": aparar_magico,
            "pmm": pmm,
        }