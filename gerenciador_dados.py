# gerenciador_dados.py
import sqlite3
from personagem import Personagem

class GerenciadorDados:
    """Classe criada para gerenciar todos os dados do personagem"""
    def __init__(self, banco_dados='ficha_gurps.db'):
        # Conectar ao banco de dados e criar as tabelas
        self.conexao = sqlite3.connect(banco_dados)
        self.cursor = self.conexao.cursor()
        self.criar_tabelas()

    def criar_tabelas(self):
        """Criação das tabelas"""
        # Criação da tabela do Personagem
        self.cursor.execute('''CREATE TABLE IF NOT EXISTS Personagem (
                                id INTEGER PRIMARY KEY,
                                nome TEXT NOT NULL,
                                player TEXT,
                                st INTEGER,
                                dx INTEGER,
                                iq INTEGER,
                                ht INTEGER,
                                pva INTEGER,
                                pfa INTEGER,
                                pma INTEGER)''')
        # Criação da tabela de Pericias
        self.cursor.execute('''CREATE TABLE IF NOT EXISTS Pericias (
                            id INTEGER PRIMARY KEY AUTOINCREMENT,
                            personagem_id INTEGER,
                            nome TEXT,
                            atributo TEXT,
                            dificuldade TEXT,
                            pontos_gastos INTEGER,
                            bloqueio INTEGER DEFAULT 0,
                            aparar_fisico INTEGER DEFAULT 0,
                            aparar_magico INTEGER DEFAULT 0,
                            poder_magico INTEGER DEFAULT 0,
                            descricao TEXT,
                            FOREIGN KEY(personagem_id) REFERENCES Personagem(id)
                            )''')
        # Criação da tabela de Inventário
        self.cursor.execute('''CREATE TABLE IF NOT EXISTS Inventario (
                            id INTEGER PRIMARY KEY AUTOINCREMENT,
                            personagem_id INTEGER,
                            nome TEXT,
                            quantidade INTEGER,
                            peso REAL,
                            FOREIGN KEY(personagem_id) REFERENCES Personagem(id)
                            )''')
        # Criação da tabela de Vantagens
        self.cursor.execute('''CREATE TABLE IF NOT EXISTS Vantagens (
                            id INTEGER PRIMARY KEY AUTOINCREMENT,
                            personagem_id INTEGER,
                            nome TEXT,
                            descricao TEXT,
                            pontos INTEGER,
                            FOREIGN KEY(personagem_id) REFERENCES Personagem(id)
                            )''')
        # Criação da tabela de Desvantagens
        self.cursor.execute('''CREATE TABLE IF NOT EXISTS Desvantagens (
                            id INTEGER PRIMARY KEY AUTOINCREMENT,
                            personagem_id INTEGER,
                            nome TEXT,
                            descricao TEXT,
                            pontos INTEGER,
                            FOREIGN KEY(personagem_id) REFERENCES Personagem(id)
                            )''')
        # Criação da tabela de Anotações
        self.cursor.execute('''CREATE TABLE IF NOT EXISTS anotacoes (
                            personagem_id INTEGER PRIMARY KEY,
                            texto TEXT
                            )''')
        self.conexao.commit()

    def fechar_conexao(self):
        """Fecha a conexão com o banco de dados."""
        self.conexao.close()

# Dados do Personagem
    def salvar_personagem(self, personagem):
        """Salva o personagem no banco de dados, incluindo pontos iniciais e recebidos."""
        if self.carregar_personagem(1):
            self.cursor.execute(
                '''UPDATE Personagem 
                SET nome = ?, player = ?, st = ?, dx = ?, iq = ?, ht = ?, 
                    pva = ?, pfa = ?, pma = ?, ponto_ini = ?, ponto_rec = ?
                WHERE id = 1''',
                (personagem.nome, personagem.player, personagem.st, personagem.dx,
                personagem.iq, personagem.ht, personagem.pva, personagem.pfa,
                personagem.pma, personagem.ponto_int, personagem.ponto_rec)
            )
        else:
            self.cursor.execute(
                '''INSERT INTO Personagem 
                (id, nome, player, st, dx, iq, ht, pva, pfa, pma, ponto_ini, ponto_rec)
                VALUES (1, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)''',
                (personagem.nome, personagem.player, personagem.st, personagem.dx,
                personagem.iq, personagem.ht, personagem.pva, personagem.pfa,
                personagem.pma, personagem.ponto_int, personagem.ponto_rec)
            )
        self.conexao.commit()

    def carregar_personagem(self, personagem_id):
        """Carrega um personagem do banco de dados, incluindo os novos campos."""
        self.cursor.execute("SELECT * FROM Personagem WHERE id = ?", (personagem_id,))
        personagem_dados = self.cursor.fetchone()

        if personagem_dados:
            return Personagem(
                nome=personagem_dados[1],
                player=personagem_dados[2],
                st=personagem_dados[3],
                dx=personagem_dados[4],
                iq=personagem_dados[5],
                ht=personagem_dados[6],
                pva=personagem_dados[7],
                pfa=personagem_dados[8],
                pma=personagem_dados[9],
                ponto_ini=personagem_dados[10],
                ponto_rec=personagem_dados[11],
            )
        return None

    def obter_primeiro_personagem(self):
        """Busca o primeiro personagem salvo no banco e retorna seu ID."""
        self.cursor.execute("SELECT id FROM Personagem ORDER BY id LIMIT 1")
        resultado = self.cursor.fetchone()
        return resultado[0] if resultado else None

# Dados das pericias
    def salvar_pericia(self, personagem_id, dados_pericia):
        """Salva uma perícia no banco de dados vinculada ao personagem_id, incluindo informações extras."""
        self.cursor.execute('''INSERT INTO Pericias (personagem_id, nome, atributo,
                            dificuldade, pontos_gastos, bloqueio, aparar_fisico,
                            aparar_magico, poder_magico, descricao)
                            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)''',
                            (personagem_id, dados_pericia["nome"], dados_pericia["atributo"],
                            dados_pericia["dificuldade"], dados_pericia["pontos_gastos"],
                            dados_pericia["bloqueio"], dados_pericia["aparar_fisico"],
                            dados_pericia["aparar_magico"],
                            dados_pericia["poder_magico"], dados_pericia["descricao"]))
        self.conexao.commit()
        print(f"Perícia '{dados_pericia['nome']}' salva com sucesso para o personagem {personagem_id}.")

    def carregar_pericias(self, personagem_id):
        """Carrega todas as perícias associadas a um personagem do banco de dados, incluindo informações extras."""
        self.cursor.execute('''SELECT id, nome, atributo, dificuldade, pontos_gastos,
                            bloqueio, aparar_fisico, aparar_magico,
                            poder_magico, descricao
                            FROM Pericias WHERE personagem_id = ?''', (personagem_id,))
        pericias = self.cursor.fetchall()

        # Converte cada registro de perícia em um dicionário para facilitar o carregamento
        lista_pericias = []
        for pericia in pericias:
            pericia_dict = {
                "id": pericia[0],
                "nome": pericia[1],
                "atributo": pericia[2],
                "dificuldade": pericia[3],
                "pontos_gastos": pericia[4],
                "bloqueio": pericia[5],
                "aparar_fisico": pericia[6],
                "aparar_magico": pericia[7],
                "poder_magico": pericia[8],
                "descricao": pericia[9]
            }
            lista_pericias.append(pericia_dict)

        return lista_pericias

    def excluir_pericia(self, pericia_id):
        """Remove uma perícia do banco de dados usando seu ID."""
        self.cursor.execute("DELETE FROM Pericias WHERE id = ?", (pericia_id,))
        self.conexao.commit()

    def atualizar_pericia(self, pericia_id, dados_pericia):
        """Atualiza uma perícia existente no banco de dados, incluindo informações extras."""
        self.cursor.execute('''UPDATE Pericias
                            SET nome = ?, atributo = ?, dificuldade = ?, pontos_gastos = ?,
                                bloqueio = ?, aparar_fisico = ?,
                                aparar_magico = ?, poder_magico = ?, descricao = ?
                            WHERE id = ?''',
                            (dados_pericia["nome"], dados_pericia["atributo"],
                            dados_pericia["dificuldade"], dados_pericia["pontos_gastos"], 
                            dados_pericia["bloqueio"],
                            dados_pericia["aparar_fisico"], dados_pericia["aparar_magico"],
                            dados_pericia["poder_magico"], dados_pericia["descricao"],
                            pericia_id))
        self.conexao.commit()

# Dados do Inventário
    def salvar_item_inventario(self, personagem_id, item):
        """Salva um item no inventário vinculado ao personagem_id."""
        self.cursor.execute('''INSERT INTO Inventario (personagem_id, nome, quantidade, peso)
                            VALUES (?, ?, ?, ?)''',
                            (personagem_id, item["nome"], item["quantidade"], item["peso"]))
        self.conexao.commit()

    def carregar_inventario(self, personagem_id):
        """Carrega todos os itens do inventário associados a um personagem."""
        self.cursor.execute("SELECT id, nome, quantidade, peso FROM Inventario WHERE personagem_id = ?", (personagem_id,))
        itens = self.cursor.fetchall()

        # Converte cada item em um dicionário
        lista_itens = []
        for item in itens:
            item_dict = {
                "id": item[0],
                "nome": item[1],
                "quantidade": item[2],
                "peso": item[3]
            }
            lista_itens.append(item_dict)

        return lista_itens

    def excluir_item_inventario(self, item_id):
        """Remove um item do inventário usando seu ID."""
        self.cursor.execute("DELETE FROM Inventario WHERE id = ?", (item_id,))
        self.conexao.commit()

# Dados das Vantagens e Desvantagens
    # Métodos para Vantagens
    def salvar_vantagem(self, personagem_id, vantagem):
        """Salva uma vantagem no banco de dados, evitando duplicatas."""
        self.cursor.execute('''SELECT id FROM Vantagens WHERE personagem_id = ? AND nome = ?''',
                            (personagem_id, vantagem["nome"]))
        resultado = self.cursor.fetchone()

        if not resultado:  # Se não existe uma vantagem com o mesmo nome
            self.cursor.execute('''INSERT INTO Vantagens (personagem_id, nome, descricao, pontos)
                                VALUES (?, ?, ?, ?)''',
                                (personagem_id, vantagem["nome"], vantagem["descricao"], vantagem["pontos"]))
            self.conexao.commit()

    def carregar_vantagens(self, personagem_id):
        """Carrega todas as vantagens associadas a um personagem."""
        self.cursor.execute("SELECT id, nome, descricao, pontos FROM Vantagens WHERE personagem_id = ?", (personagem_id,))
        vantagens = self.cursor.fetchall()
        return [{"id": v[0], "nome": v[1], "descricao": v[2], "pontos": v[3]} for v in vantagens]

    def excluir_vantagem(self, vantagem_id):
        """Exclui uma vantagem do banco de dados."""
        self.cursor.execute("DELETE FROM Vantagens WHERE id = ?", (vantagem_id,))
        self.conexao.commit()

    # Métodos para Desvantagens
    def salvar_desvantagem(self, personagem_id, desvantagem):
        """Salva uma desvantagem no banco de dados, evitando duplicatas."""
        self.cursor.execute('''SELECT id FROM Desvantagens WHERE personagem_id = ? AND nome = ?''',
                            (personagem_id, desvantagem["nome"]))
        resultado = self.cursor.fetchone()

        if not resultado:  # Se não existe uma desvantagem com o mesmo nome
            self.cursor.execute('''INSERT INTO Desvantagens (personagem_id, nome, descricao, pontos)
                                VALUES (?, ?, ?, ?)''',
                                (personagem_id, desvantagem["nome"], desvantagem["descricao"], desvantagem["pontos"]))
            self.conexao.commit()

    def carregar_desvantagens(self, personagem_id):
        """Carrega todas as desvantagens associadas a um personagem."""
        self.cursor.execute("SELECT id, nome, descricao, pontos FROM Desvantagens WHERE personagem_id = ?", (personagem_id,))
        desvantagens = self.cursor.fetchall()
        return [{"id": d[0], "nome": d[1], "descricao": d[2], "pontos": d[3]} for d in desvantagens]

    def excluir_desvantagem(self, desvantagem_id):
        """Exclui uma desvantagem do banco de dados."""
        self.cursor.execute("DELETE FROM Desvantagens WHERE id = ?", (desvantagem_id,))
        self.conexao.commit()

# Dados das Anotações
    def salvar_anotacoes(self, personagem_id, anotacoes):
        """Salva as anotações"""
        cursor = self.conexao.cursor()
        cursor.execute("""
            INSERT INTO anotacoes (personagem_id, texto)
            VALUES (?, ?)
            ON CONFLICT(personagem_id) DO UPDATE SET texto = excluded.texto
        """, (personagem_id, anotacoes))
        self.conexao.commit()

    def carregar_anotacoes(self, personagem_id):
        """Carrega as anotações"""
        cursor = self.conexao.cursor()
        cursor.execute("SELECT texto FROM anotacoes WHERE personagem_id = ?", (personagem_id,))
        resultado = cursor.fetchone()
        return resultado[0] if resultado else ""