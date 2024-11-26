# interface_grafica.py
"""Biblioteca do layout"""

from kivy.app import App
from kivy.lang import Builder
from kivy.uix.screenmanager import Screen, ScreenManager
from kivy.config import Config
from kivy.uix.label import Label
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.textinput import TextInput
from kivy.uix.button import Button
from kivy.uix.spinner import Spinner
from kivy.clock import Clock
from kivy.uix.checkbox import CheckBox
from kivy.uix.popup import Popup

from personagem import Personagem
from regras_calculos import CalculoPericia,RolagemDados,CalculoDano,CalculoAtributosCombate

Config.set('graphics', 'width', '500')
Config.set('graphics', 'height', '800')

class GerenciadorTelas(ScreenManager):
    """Gerencia as diferentes telas do aplicativo"""

class TelaAtributos(Screen):
    """Inicializa a tela_atributos principal"""

    def criar_layout_combate(self):
        """Criar o layout das pericias de combate na tela atributos"""

    def exibir_pericias_combate(self):
        """Coloca as pericias de combate na tela atributos"""

        personagem_id = App.get_running_app().personagem_id
        pericias_combate = App.get_running_app().gerenciador_dados.carregar_pericias_combate(personagem_id)

        # Limpe o layout antes de exibir novas perícias
        self.ids.pericias_combate_layout.clear_widgets()

        for pericia in pericias_combate:
            # Crie o layout para a perícia e adicione ao layout principal da tela de atributos
            pericia_label = Label(text=pericia['nome'])
            self.ids.pericias_combate_layout.add_widget(pericia_label)

class TelaPericias(Screen):
    """Classe para a tela de perícias"""
    def __init__(self,**kwargs):
        super(TelaPericias, self).__init__(**kwargs)
        self.mostrar_botoes_deletar = False

# Layout
    def alternar_botao_del(self):
        """Alterna a visibilidade dos botões de deletar em cada perícia."""
        self.mostrar_botoes_deletar = not self.mostrar_botoes_deletar
        for pericia_box in self.ids.pericias_layout.children:
            botao_deletar = pericia_box.pericia_widgets["botao_deletar"]
            botao_deletar.opacity = 1 if self.mostrar_botoes_deletar else 0
            botao_deletar.disabled = not self.mostrar_botoes_deletar

    def criar_layout_pericia(self, pericia=None):
        """Cria e retorna o layout para uma nova perícia, com campos preenchidos, se fornecido."""
        pericia_box = BoxLayout(orientation='horizontal', size_hint_y=None, height=30, spacing=1)

        # Atribui o ID do banco de dados diretamente ao layout `pericia_box`, se disponível
        pericia_box.pericia_id = pericia["id"] if pericia and "id" in pericia else None

        # Dicionário para armazenar os widgets da perícia com identificadores
        pericia_widgets = {}

        # Botao Expandir
        pericia_widgets["botao_expandir"] = Button(text="+", size_hint_x=0.05, on_press=lambda instance: self.abrir_janela_info_extra(pericia))

        # Campo de Nome
        pericia_widgets["nome"] = Label(size_hint_x=0.6, text=pericia["nome"] if pericia else "")

        pericia_widgets["atributo"] =Label( text=pericia["atributo"] if pericia else "??", size_hint_x=0.1)
        pericia_widgets["slash"] = Label(size_hint_x=0.005, text='/', font_size='20sp')
        pericia_widgets["dificuldade"] = Label(text=pericia["dificuldade"] if pericia else "?", size_hint_x=0.1)

        pericia_widgets["pontos_gastos"] = Label(text=str(pericia["pontos_gastos"]) if pericia else "0", size_hint_x=0.1)
        # Outros campos e botões
        pericia_widgets["mod_pts"] = Label(size_hint_x=0.1)
        pericia_widgets["mod_extra"] = TextInput(size_hint_x=0.12, multiline=False, hint_text="Mod",)
        pericia_widgets["botao_rolar"] = Button(size_hint_x=0.1, text='3d6', on_press=lambda instance: self.rolar_pericia(pericia_box))
        pericia_widgets["botao_deletar"] = Button(text="x", size_hint_x=0.05, opacity=0, disabled=True, on_press=lambda instance: self.excluir_pericia(pericia_box))

        # Adiciona widgets ao layout da perícia e ao BoxLayout
        for widget in pericia_widgets.values():
            pericia_box.add_widget(widget)

        pericia_widgets["bloqueio"] = CheckBox(size_hint_x=0.1, active=pericia.get("bloqueio", False) if pericia else False)
        pericia_widgets["aparar_fisico"] = CheckBox(size_hint_x=0.1, active=pericia.get("aparar_fisico", False) if pericia else False)
        pericia_widgets["aparar_magico"] = CheckBox(size_hint_x=0.1, active=pericia.get("aparar_magico", False) if pericia else False)
        pericia_widgets["poder_magico"] = CheckBox(size_hint_x=0.1, active=pericia.get("poder_magico", False) if pericia else False)
        pericia_widgets["descricao"] = TextInput(hint_text="Descrição da perícia", multiline=True, text=pericia.get("descricao", "") if pericia else "")

        # Anexa o dicionário de widgets ao BoxLayout para referência futura
        pericia_box.pericia_widgets = pericia_widgets

        return pericia_box

# manipulação de pericias
    def salvar_pericias(self):
        """Salva ou atualiza as perícias exibidas na interface no banco de dados."""
        app = App.get_running_app()
        personagem_id = app.personagem_id  # ID do personagem atual

        for pericia_box in self.ids.pericias_layout.children:
            pericia_id = pericia_box.pericia_id

            # Crie o dicionário de dados da perícia com todas as chaves necessárias
            dados_pericia = {
                "id": pericia_id,
                "nome": pericia_box.pericia_widgets["nome"].text,
                "atributo": pericia_box.pericia_widgets["atributo"].text,
                "dificuldade": pericia_box.pericia_widgets["dificuldade"].text,
                "pontos_gastos": int(pericia_box.pericia_widgets["pontos_gastos"].text),
                "bloqueio": pericia_box.pericia_widgets["bloqueio"].active,
                "aparar_fisico": pericia_box.pericia_widgets["aparar_fisico"].active,
                "aparar_magico": pericia_box.pericia_widgets["aparar_magico"].active,
                "poder_magico": pericia_box.pericia_widgets["poder_magico"].active,
                "descricao": pericia_box.pericia_widgets["descricao"].text
            }

            # Verifica se a perícia já existe no banco de dados
            if pericia_id:
                app.gerenciador_dados.atualizar_pericia(pericia_id, dados_pericia)
            else:
                novo_id = app.gerenciador_dados.salvar_pericia(personagem_id, dados_pericia)
                pericia_box.pericia_id = novo_id
        self.calcular_atributos_combate()

    def carregar_pericias(self):
        """Carrega todas as perícias do banco de dados para a interface."""
        app = App.get_running_app()
        personagem_id = app.personagem_id

        # Limpa todas as perícias da interface antes de carregar novamente
        self.ids.pericias_layout.clear_widgets()

        # Carrega as perícias do banco de dados
        pericias = app.gerenciador_dados.carregar_pericias(personagem_id)

        for pericia in pericias:
            # Adiciona a perícia ao layout
            self.adicionar_pericia(pericia)

            # Calcula o modificador de acordo com os pontos gastos e dificuldade
            pontos_gastos = int(pericia["pontos_gastos"])
            dificuldade = pericia["dificuldade"]
            mod = CalculoPericia.cal_mod(dificuldade, pontos_gastos)

            # Verifica se o modificador é válido antes de formatá-lo
            mod_for = f"+{mod}" if mod is not None and mod > 0 else str(mod) if mod is not None else "0"

            # Atualiza o campo de modificador
            pericia_box = self.ids.pericias_layout.children[0]  # A última perícia adicionada
            pericia_box.pericia_widgets["mod_pts"].text = mod_for

            # Atualiza os checkboxes e a descrição
            bloqueio_widget = pericia_box.pericia_widgets.get("bloqueio")
            if bloqueio_widget:
                bloqueio_widget.active = bool(pericia.get("bloqueio", False))

            aparar_fisico_widget = pericia_box.pericia_widgets.get("aparar_fisico")
            if aparar_fisico_widget:
                aparar_fisico_widget.active = bool(pericia.get("aparar_fisico", False))

            aparar_magico_widget = pericia_box.pericia_widgets.get("aparar_magico")
            if aparar_magico_widget:
                aparar_magico_widget.active = bool(pericia.get("aparar_magico", False))

            poder_magico_widget = pericia_box.pericia_widgets.get("poder_magico")
            if poder_magico_widget:
                poder_magico_widget.active = bool(pericia.get("poder_magico", False))

            descricao_widget = pericia_box.pericia_widgets.get("descricao")
            if descricao_widget:
                descricao_widget.text = pericia.get("descricao", "")
                
        self.calcular_atributos_combate()

    def adicionar_pericia(self, pericia=None):
        """Adiciona uma nova perícia na interface chamando criar_layout_pericia."""
        # Cria o layout da perícia e adiciona ao layout principal
        nova_pericia = self.criar_layout_pericia(pericia)
        self.ids.pericias_layout.add_widget(nova_pericia)

    def excluir_pericia(self, pericia_box):
        """Exclui uma perícia da interface e do banco de dados."""
        pericia_id = pericia_box.pericia_id  # Obtém o ID da perícia do layout

        # Verifica se o ID da perícia existe e remove do banco de dados
        if pericia_id:
            app = App.get_running_app()
            app.gerenciador_dados.excluir_pericia(pericia_id)  # Exclui do banco de dados

        # Remove o layout da perícia da interface
        self.ids.pericias_layout.remove_widget(pericia_box)

    def rolar_pericia(self, pericia_box):
        """Rola o resultado da perícia e exibe o resultado baseado nos modificadores e atributo."""
        app = App.get_running_app()

        # Nome do atributo e valor
        atributo_nome = pericia_box.pericia_widgets["atributo"].text.lower() + '_input'

        try:
            # Tenta acessar o valor do atributo na tela TelaAtributos
            atributo_valor = int(app.root.ids.tela_atributos.ids[atributo_nome].text)
        except KeyError:
            print(f"Erro: O atributo '{atributo_nome}' não foi encontrado na tela de atributos.")
            atributo_valor = 0  # Define um valor padrão se o atributo não for encontrado
        except ValueError:
            print(f"Erro: O valor do atributo '{atributo_nome}' não é um número válido.")
            atributo_valor = 0  # Define um valor padrão se o valor não for válido

        # Obtém os modificadores da perícia
        mod_pts = int(pericia_box.pericia_widgets["mod_pts"].text)
        mod_extra = int(pericia_box.pericia_widgets["mod_extra"].text or 0)
        total_pericia = atributo_valor + mod_pts + mod_extra

        # Realiza a rolagem de 3d6
        rolagem = sum(RolagemDados().rolar_3d6())

        # Referência ao widget `resultado_3d6_tela_pericias` para exibir o resultado da rolagem
        resultado_widget = self.ids.resultado_3d6_tela_pericias
        if resultado_widget:
            # Define a cor do texto com base no sucesso ou falha
            if rolagem <= total_pericia:
                resultado_texto = f"(D={total_pericia}/R={rolagem})"
                resultado_widget.color = (0, 1, 0, 1)  # Verde para sucesso
            else:
                resultado_texto = f"(D={total_pericia}/R={rolagem})"
                resultado_widget.color = (1, 0, 0, 1)  # Vermelho para falha
            resultado_widget.text = resultado_texto
        else:
            print("Widget `resultado_3d6_tela_pericias` não encontrado.")

    def alternar_conteudo_extra(self, pericia_box):
        """Alterna a visibilidade do conteúdo extra associado à perícia."""
        # Se o conteúdo extra ainda não foi criado, crie-o agora
        if not hasattr(pericia_box, "conteudo_extra"):
            conteudo_extra = BoxLayout(orientation='vertical', size_hint_y=None, height=100, spacing=5)

            # Adicione checkboxes e o campo de descrição
            checkbox1 = CheckBox()
            checkbox2 = CheckBox()
            conteudo_extra.add_widget(Label(text="Checkbox 1"))
            conteudo_extra.add_widget(checkbox1)
            conteudo_extra.add_widget(Label(text="Checkbox 2"))
            conteudo_extra.add_widget(checkbox2)
            descricao = TextInput(hint_text="Descrição da perícia", size_hint_y=None, height=60, multiline=True)
            conteudo_extra.add_widget(descricao)

            # Salve o conteúdo extra no `pericia_box`
            pericia_box.conteudo_extra = conteudo_extra
        else:
            conteudo_extra = pericia_box.conteudo_extra

        # Alternar a visibilidade removendo ou adicionando o conteúdo extra
        if conteudo_extra.parent:
            pericia_box.remove_widget(conteudo_extra)  # Remova se já está visível
        else:
            pericia_box.add_widget(conteudo_extra)  # Adicione se não está visível

    def abrir_janela_info_extra(self, pericia):
        """Abre um popup com informações extras da perícia e salva as alterações."""
        # Cria o layout principal
        if pericia is None:
            pericia = {
            "nome": "",
            "atributo": "ST",
            "dificuldade": "F",
            "pontos_gastos": 0,
            "mod_pericia": 0,
            "mod_extra": 0,
            "bloqueio": False,
            "aparar_fisico": False,
            "aparar_magico": False,
            "poder_magico": False,
            "descricao": ""
        }
        conteudo = BoxLayout(orientation='vertical', spacing=3)

        # Primeiro BoxLayout horizontal
        box1 = BoxLayout(orientation='horizontal', size_hint_y=None, height=30, spacing=1)
        nome_input = TextInput(size_hint_x=0.6, multiline=False, text=pericia.get("nome", ""), hint_text="Nome da perícia")
        atributo_spinner = Spinner(text=pericia.get("atributo", "ST"), values=["ST", "DX", "IQ", "HT"], size_hint_x=0.1)
        dificuldade_spinner = Spinner(text=pericia.get("dificuldade", "F"), values=["F", "M", "D", "MD"], size_hint_x=0.1)
        pontos_spinner = Spinner(text=str(pericia.get("pontos_gastos", "0")), values=["0", "1", "3", "7", "15", "27", "43", "63", "87", "111"], size_hint_x=0.1)
        mod_input = TextInput(size_hint_x=0.1, multiline=False, readonly=True, text=str(pericia.get("mod_pericia", "0")), hint_text="MOD")
        mod_extra_input = TextInput(size_hint_x=0.1, multiline=False, text=str(pericia.get("mod_extra", "0")), hint_text="MOD Extra")
        box1.add_widget(nome_input)
        box1.add_widget(atributo_spinner)
        box1.add_widget(Label(text="/", font_size='20sp', size_hint_x=0.005))
        box1.add_widget(dificuldade_spinner)
        box1.add_widget(pontos_spinner)
        conteudo.add_widget(box1)

        # Segundo BoxLayout horizontal
        box2 = BoxLayout(orientation='horizontal', spacing=10, size_hint_y=None, height=30)
        bloqueio_checkbox = CheckBox(size_hint_x=0.1, active=pericia.get("bloqueio", False))
        aparar_fisico_checkbox = CheckBox(size_hint_x=0.1, active=pericia.get("aparar_fisico", False))
        aparar_magico_checkbox = CheckBox(size_hint_x=0.1, active=pericia.get("aparar_magico", False))
        poder_magico_checkbox = CheckBox(size_hint_x=0.1, active=pericia.get("poder_magico", False))
        box2.add_widget(Label(text="Bloqueio:", size_hint_x=0.55))
        box2.add_widget(bloqueio_checkbox)
        box2.add_widget(Label(text="Aparar Físico:", size_hint_x=0.73))
        box2.add_widget(aparar_fisico_checkbox)
        box2.add_widget(Label(text="Aparar Mágico:", size_hint_x=0.73))
        box2.add_widget(aparar_magico_checkbox)
        box2.add_widget(Label(text="PM:", size_hint_x=0.1))
        box2.add_widget(poder_magico_checkbox)
        conteudo.add_widget(box2)

        # Campo de descrição
        descricao_input = TextInput(hint_text="Descrição da perícia", multiline=True, text=pericia.get("descricao", ""))
        conteudo.add_widget(descricao_input)

        # Botão de fechar
        botao_fechar = Button(text="Fechar", size_hint_y=None, height=40)

        # Função para salvar as informações antes de fechar o Popup
        def salvar_e_fechar(_):
            # Atualiza o dicionário da perícia com os novos valores
            pericia["nome"] = nome_input.text
            pericia["atributo"] = atributo_spinner.text
            pericia["dificuldade"] = dificuldade_spinner.text
            pericia["pontos_gastos"] = int(pontos_spinner.text)
            pericia["mod_pericia"] = int(mod_input.text)
            pericia["mod_extra"] = int(mod_extra_input.text)
            pericia["bloqueio"] = bloqueio_checkbox.active
            pericia["aparar_fisico"] = aparar_fisico_checkbox.active
            pericia["aparar_magico"] = aparar_magico_checkbox.active
            pericia["poder_magico"] = poder_magico_checkbox.active
            pericia["descricao"] = descricao_input.text

            # Certifique-se de que todos os campos necessários estão presentes no dicionário
            campos_necessarios = ["id", "nome", "atributo", "dificuldade", "pontos_gastos", "mod_pericia", "mod_extra",
                                "bloqueio", "aparar_fisico", "aparar_magico", "poder_magico", "descricao"]

            for campo in campos_necessarios:
                if campo not in pericia:
                    # Define valores padrão para campos ausentes
                    pericia[campo] = 0 if campo in ["pontos_gastos", "mod_pericia", "mod_extra"] else False if campo in ["bloqueio", "aparar_fisico", "aparar_magico", "poder_magico"] else ""

            # Salva as informações no banco de dados
            app = App.get_running_app()
            if "id" in pericia and pericia["id"]:
                app.gerenciador_dados.atualizar_pericia(pericia["id"], pericia)
            else:
                # Se a perícia não tem ID, crie uma nova entrada no banco de dados
                personagem_id = app.personagem_id
                novo_id = app.gerenciador_dados.salvar_pericia(personagem_id, pericia)
                pericia["id"] = novo_id

            self.carregar_pericias()
            popup.dismiss()

        botao_fechar.bind(on_press=salvar_e_fechar) # pylint: disable=E1101
        conteudo.add_widget(botao_fechar)

        # Cria e exibe o Popup
        popup = Popup(title="Detalhes da Perícia", content=conteudo, size_hint=(0.8, 0.6))
        popup.open()

    def calcular_atributos_combate(self):
        """Chama a lógica de cálculo de atributos de combate e atualiza a interface."""
        app = App.get_running_app()
        tela_atributos = app.root.ids.tela_atributos

        # Coleta os atributos da interface
        atributos = {
            "st": int(tela_atributos.ids.st_input.text),
            "dx": int(tela_atributos.ids.dx_input.text),
            "iq": int(tela_atributos.ids.iq_input.text),
            "ht": int(tela_atributos.ids.ht_input.text),
        }

        # Coleta as perícias da interface
        pericias = []
        for pericia_box in self.ids.pericias_layout.children:
            pericia_widgets = pericia_box.pericia_widgets
            pericias.append({
                "mod_pts": int(pericia_widgets["mod_pts"].text),
                "atributo": pericia_widgets["atributo"].text.lower(),
                "bloqueio": pericia_widgets.get("bloqueio", None) and pericia_widgets["bloqueio"].active,
                "aparar_fisico": pericia_widgets.get("aparar_fisico", None) and pericia_widgets["aparar_fisico"].active,
                "aparar_magico": pericia_widgets.get("aparar_magico", None) and pericia_widgets["aparar_magico"].active,
                "poder_magico": pericia_widgets.get("poder_magico", None) and pericia_widgets["poder_magico"].active,
            })

        # Calcula os valores
        atributos_combate = CalculoAtributosCombate.calcular(pericias, atributos)

        # Atualiza a interface com os resultados
        tela_atributos.ids.bloqueio_input.text = str(atributos_combate["bloqueio"])
        tela_atributos.ids.apararf_input.text = str(atributos_combate["aparar_fisico"])
        tela_atributos.ids.apararm_input.text = str(atributos_combate["aparar_magico"])
        tela_atributos.ids.pmm_input.text = str(atributos_combate["pmm"])

class TelaInventario(Screen):
    """Classe responsavel por carrega o inventario"""
    def __init__(self, **kwargs):
        super(TelaInventario, self).__init__(**kwargs)
        self.mostrar_botoes_deletar = False  # Inicialmente, os botões de deletar não são exibidos

    def alternar_botao_del(self):
        """Alterna a visibilidade dos botões de deletar em cada item do inventário."""
        self.mostrar_botoes_deletar = not self.mostrar_botoes_deletar
        for inv_box in self.ids.inv_layout.children:
            botao_deletar = inv_box.inv_widgets["botao_deletar"]
            botao_deletar.opacity = 1 if self.mostrar_botoes_deletar else 0
            botao_deletar.disabled = not self.mostrar_botoes_deletar

    def criar_layout_item(self,item=None):
        """responsavel por criar layout do inventario"""
        inv_box = BoxLayout(orientation='horizontal', size_hint_y=None, height=30, spacing=1)

        # Atribui o ID do banco de dados diretamente ao layout `inv_box`, se disponível
        inv_box.item_id = item["id"] if item and "id" in item else None

        # Dicionário para armazenar os widgets da perícia com identificadores
        inv_widgets = {}

        # Botao Expandir

        # Campo de Nome
        inv_widgets["nome"] = TextInput(size_hint_x=0.65, multiline=False, text=(item.get("nome","")) if item else "", hint_text="Nome")
        inv_widgets["quant"] = TextInput(size_hint_x=0.1, multiline=False, text=str(item.get("quantidade",0)) if item else "", hint_text="0")
        inv_widgets["peso"] = TextInput(size_hint_x=0.1, multiline=False, text=str(item.get("peso",0.0)) if item else "", hint_text="Kg")
        inv_widgets["botao_deletar"] = Button(text="x", size_hint_x=0.05, opacity=0, disabled=True, on_press=lambda instance: self.excluir_item(inv_box))

        # Adiciona widgets ao layout da perícia e ao BoxLayout
        for widget in inv_widgets.values():
            inv_box.add_widget(widget)

        # Anexa o dicionário de widgets ao BoxLayout para referência futura
        inv_box.inv_widgets = inv_widgets
        return inv_box

    def adicionar_item(self, item=None):
        """Adiciona um novo item na interface chamando criar_layout_item."""
        novo_item = self.criar_layout_item(item)
        self.ids.inv_layout.add_widget(novo_item)

    def salvar_inventario(self):
        """Salva os itens do inventário no banco de dados sem duplicar."""
        app = App.get_running_app()
        personagem_id = app.personagem_id  # ID do personagem atual

        # Obter os itens atuais do banco de dados
        itens_existentes = app.gerenciador_dados.carregar_inventario(personagem_id)
        nomes_itens_existentes = {item["nome"] for item in itens_existentes}

        for inv_box in self.ids.inv_layout.children:
            item_nome = inv_box.inv_widgets["nome"].text
            item_quantidade = int(inv_box.inv_widgets["quant"].text)
            item_peso = float(inv_box.inv_widgets["peso"].text)

            # Verificar se o item já existe pelo nome
            if not item_nome in nomes_itens_existentes:
                # Salvar o novo item no banco de dados
                dados_item = {
                    "nome": item_nome,
                    "quantidade": item_quantidade,
                    "peso": item_peso
                }
                app.gerenciador_dados.salvar_item_inventario(personagem_id, dados_item)

    def carregar_inventario(self):
        """Carrega os itens do inventário do banco de dados."""
        app = App.get_running_app()
        personagem_id = app.personagem_id

        # Limpa o layout antes de carregar os itens
        self.ids.inv_layout.clear_widgets()

        # Carrega os itens do banco de dados
        itens = app.gerenciador_dados.carregar_inventario(personagem_id)

        for item in itens:
            self.adicionar_item(item)

    def excluir_item(self, inv_box):
        """Exclui um item do inventário."""
        app = App.get_running_app()

        # Remove o item do banco de dados se ele tiver um ID associado
        item_id = inv_box.item_id
        if item_id:
            app.gerenciador_dados.excluir_item_inventario(item_id)

        # Remove o item do layout
        self.ids.inv_layout.remove_widget(inv_box)

class TelaVantagem(Screen):
    """Classe responsavel por carrega as vantagens e desvantagens"""
    def __init__(self, **kwargs):
        super(TelaVantagem, self).__init__(**kwargs)
        self.mostrar_botoes_deletar = False  # Inicialmente, os botões de deletar estão ocultos

    def alternar_botao_deletar(self):
        """Alterna a visibilidade dos botões de deletar para vantagens e desvantagens."""
        self.mostrar_botoes_deletar = not self.mostrar_botoes_deletar

        # Alterna a visibilidade dos botões de deletar em vantagens
        for vantagem_box in self.ids.vantagem_layout.children:
            botao_deletar = vantagem_box.vantagem_widgets["botao_deletar"]
            botao_deletar.opacity = 1 if self.mostrar_botoes_deletar else 0
            botao_deletar.disabled = not self.mostrar_botoes_deletar

        # Alterna a visibilidade dos botões de deletar em desvantagens
        for desvantagem_box in self.ids.desvantagem_layout.children:
            botao_deletar = desvantagem_box.desvantagem_widgets["botao_deletar"]
            botao_deletar.opacity = 1 if self.mostrar_botoes_deletar else 0
            botao_deletar.disabled = not self.mostrar_botoes_deletar

    def criar_layout_vantagem(self, vantagem=None):
        """Responsável por criar o layout de uma vantagem"""
        vantagem_box = BoxLayout(orientation='horizontal', size_hint_y=None, height=30, spacing=1)

        # Atribui o ID do banco de dados diretamente ao layout `vantagem_box`, se disponível
        vantagem_box.vantagem_id = vantagem["id"] if vantagem and "id" in vantagem else None

        # Dicionário para armazenar os widgets da vantagem com identificadores
        vantagem_widgets = {}

        # Campo de Nome
        vantagem_widgets["nome"] = TextInput(size_hint_x=0.35, multiline=False, text=(vantagem.get("nome","")) if vantagem else "", hint_text="Nome")
        vantagem_widgets["descrição"] = TextInput(size_hint_x=0.55, multiline=False, text=(vantagem.get("descricao","")) if vantagem else "", hint_text="Descrição")
        vantagem_widgets["pontos"] = TextInput(size_hint_x=0.07, multiline=False, text=str(vantagem.get("pontos",0)) if vantagem else "", hint_text="Pts")
        vantagem_widgets["botao_deletar"] = Button(text="x", size_hint_x=0.05, opacity=0, disabled=True, on_press=lambda instance: self.excluir_vantagem(vantagem_box,"vantagem"))

        # Adiciona widgets ao layout da vantagem e ao BoxLayout
        for widget in vantagem_widgets.values():
            vantagem_box.add_widget(widget)

        # Anexa o dicionário de widgets ao BoxLayout para referência futura
        vantagem_box.vantagem_widgets = vantagem_widgets
        return vantagem_box

    def criar_layout_desvantagem(self, desvantagem=None):
        """Responsável por criar o layout de uma desvantagem"""
        desvantagem_box = BoxLayout(orientation='horizontal', size_hint_y=None, height=30, spacing=1)

        # Atribui o ID do banco de dados diretamente ao layout `desvantagem_box`, se disponível
        desvantagem_box.desvantagem_id = desvantagem["id"] if desvantagem and "id" in desvantagem else None

        # Dicionário para armazenar os widgets da desvantagem com identificadores
        desvantagem_widgets = {}

        # Campo de Nome
        desvantagem_widgets["nome"] = TextInput(size_hint_x=0.35, multiline=False, text=(desvantagem.get("nome","")) if desvantagem else "", hint_text="Nome")
        desvantagem_widgets["descrição"] = TextInput(size_hint_x=0.55, multiline=False, text=(desvantagem.get("descricao","")) if desvantagem else "", hint_text="Descrição")
        desvantagem_widgets["pontos"] = TextInput(size_hint_x=0.07, multiline=False, text=str(desvantagem.get("pontos",0)) if desvantagem else "", hint_text="Pts")
        desvantagem_widgets["botao_deletar"] = Button(text="x", size_hint_x=0.05, opacity=0, disabled=True, on_press=lambda instance: self.excluir_vantagem(desvantagem_box,"desvantagem"))

        # Adiciona widgets ao layout da desvantagem e ao BoxLayout
        for widget in desvantagem_widgets.values():
            desvantagem_box.add_widget(widget)

        # Anexa o dicionário de widgets ao BoxLayout para referência futura
        desvantagem_box.desvantagem_widgets = desvantagem_widgets
        return desvantagem_box

    def adicionar_vantagem(self, vantagem=None):
        """Adiciona um novo item na interface chamando criar_layout_vantagem."""
        nova_vantagem = self.criar_layout_vantagem(vantagem)
        self.ids.vantagem_layout.add_widget(nova_vantagem)

    def adicionar_desvantagem(self, desvantagem=None):
        """Adiciona um novo item na interface chamando criar_layout_item."""
        nova_desvantagem = self.criar_layout_desvantagem(desvantagem)
        self.ids.desvantagem_layout.add_widget(nova_desvantagem)

    def salvar_vantagens(self):
        """Salva as vantagens no banco de dados."""
        app = App.get_running_app()
        personagem_id = app.personagem_id

        for vantagem_box in self.ids.vantagem_layout.children:
            vantagem = {
                "nome": vantagem_box.vantagem_widgets["nome"].text,
                "descricao": vantagem_box.vantagem_widgets["descrição"].text,
                "pontos": int(vantagem_box.vantagem_widgets["pontos"].text)
            }
            app.gerenciador_dados.salvar_vantagem(personagem_id, vantagem)

    def carregar_vantagens(self):
        """Carrega as vantagens do banco de dados para a interface."""
        app = App.get_running_app()
        personagem_id = app.personagem_id
        vantagens = app.gerenciador_dados.carregar_vantagens(personagem_id)
        self.ids.vantagem_layout.clear_widgets()
        for vantagem in vantagens:
            self.adicionar_vantagem(vantagem)

    def salvar_desvantagens(self):
        """Salva as desvantagens no banco de dados."""
        app = App.get_running_app()
        personagem_id = app.personagem_id

        for desvantagem_box in self.ids.desvantagem_layout.children:
            desvantagem = {
                "nome": desvantagem_box.desvantagem_widgets["nome"].text,
                "descricao": desvantagem_box.desvantagem_widgets["descrição"].text,
                "pontos": int(desvantagem_box.desvantagem_widgets["pontos"].text)
            }
            app.gerenciador_dados.salvar_desvantagem(personagem_id, desvantagem)

    def carregar_desvantagens(self):
        """Carrega as desvantagens do banco de dados para a interface."""
        app = App.get_running_app()
        personagem_id = app.personagem_id
        desvantagens = app.gerenciador_dados.carregar_desvantagens(personagem_id)
        self.ids.desvantagem_layout.clear_widgets()
        for desvantagem in desvantagens:
            self.adicionar_desvantagem(desvantagem)

    def salvar_tela_vantagem(self):
        """salva a tela vantagem"""
        self.salvar_vantagens()
        self.salvar_desvantagens()

    def carregar_tela_vantagem(self):
        """carrega a tela vantagem"""
        self.carregar_desvantagens()
        self.carregar_vantagens()

    def excluir_vantagem(self, vantagem_box, tipo):
        """Exclui uma vantagem ou desvantagem do layout e do banco de dados."""
        app = App.get_running_app()
        # Identifica a vantagem ou desvantagem a ser excluída com base no tipo
        if tipo == "vantagem":
            vantagem_id = vantagem_box.vantagem_id
            if vantagem_id:
                app.gerenciador_dados.excluir_vantagem(vantagem_id)
            self.ids.vantagem_layout.remove_widget(vantagem_box)
        
        elif tipo == "desvantagem":
            desvantagem_id = vantagem_box.desvantagem_id
            if desvantagem_id:
                app.gerenciador_dados.excluir_desvantagem(desvantagem_id)
            self.ids.desvantagem_layout.remove_widget(vantagem_box)

class TelaAnotacao(Screen):
    """Tela com grande Textinput para anotações"""
    def salvar_anotacoes(self):
        """Salva as anotações"""
        app = App.get_running_app()
        personagem_id = app.personagem_id
        anotacoes = self.ids.anotacoes_input.text
        app.gerenciador_dados.salvar_anotacoes(personagem_id, anotacoes)

    def carregar_anotacoes(self):
        """Carrega as anotações"""
        app = App.get_running_app()
        personagem_id = app.personagem_id
        anotacoes = app.gerenciador_dados.carregar_anotacoes(personagem_id)
        self.ids.anotacoes_input.text = anotacoes

class InterfaceGrafica(App):
    """Inicializa a interface gráfica"""

    def __init__(self, gerenciador_dados, rolagem_dados, **kwargs):
        super(InterfaceGrafica, self).__init__(**kwargs)
        self.gerenciador_dados = gerenciador_dados
        self.rolagem_dados = rolagem_dados
        self.personagem_id = None  # Para rastrear o ID do personagem atual

    def build(self):
        return Builder.load_file('interfaces/Interface.kv')

    def salvar_atributos(self):
        """Salva os atributos do personagem, incluindo pontos iniciais e recebidos."""
        try:
            tela_atributos = self.root.ids.tela_atributos
            nome = tela_atributos.ids.personagem_nome.text
            player = tela_atributos.ids.player_nome.text
            st = int(tela_atributos.ids.st_input.text)
            dx = int(tela_atributos.ids.dx_input.text)
            iq = int(tela_atributos.ids.iq_input.text)
            ht = int(tela_atributos.ids.ht_input.text)
            pva = int(tela_atributos.ids.pva_input.text)
            pfa = int(tela_atributos.ids.pfa_input.text)
            pma = int(tela_atributos.ids.pma_input.text)

            ponto_ini = int(tela_atributos.ids.ponto_ini.text or 0)
            ponto_rec = int(tela_atributos.ids.ponto_rec.text or 0)

            # Cria e salva o personagem no banco de dados
            personagem = Personagem(nome, player, st, dx, iq, ht, pva, pfa, pma, ponto_ini, ponto_rec)
            self.personagem_id = self.gerenciador_dados.salvar_personagem(personagem)

        except ValueError as e:
            print(f"Erro ao salvar atributos: Atributo Inválido {e}")
        except AttributeError as e:
            print(f"Erro ao salvar atributos: {e}")

    def carregar_atributos(self):
        """Carrega apenas os atributos do primeiro personagem disponível, incluindo recursos."""
        try:
            if not self.personagem_id:
                self.personagem_id = self.gerenciador_dados.obter_primeiro_personagem()

            if self.personagem_id:
                personagem = self.gerenciador_dados.carregar_personagem(self.personagem_id)
                if personagem:
                    tela_atributos = self.root.ids.tela_atributos
                    # Carrega atributos básicos
                    tela_atributos.ids.personagem_nome.text = personagem.nome
                    tela_atributos.ids.player_nome.text = personagem.player
                    tela_atributos.ids.st_input.text = str(personagem.st)
                    tela_atributos.ids.dx_input.text = str(personagem.dx)
                    tela_atributos.ids.iq_input.text = str(personagem.iq)
                    tela_atributos.ids.ht_input.text = str(personagem.ht)

                    # Carrega recursos: Atual é salvo, Máximo é calculado
                    tela_atributos.ids.pva_input.text = str(personagem.pva)
                    tela_atributos.ids.pvm_input.text = str(personagem.pv)
                    tela_atributos.ids.pfa_input.text = str(personagem.pfa)
                    tela_atributos.ids.pfm_input.text = str(personagem.pf)
                    tela_atributos.ids.pma_input.text = str(personagem.pma)
                    tela_atributos.ids.pmm_input.text = str(personagem.pm)

                    # Carrega atributos avançados
                    tela_atributos.ids.vtd_input.text = str(personagem.vtd)
                    tela_atributos.ids.per_input.text = str(personagem.per)
                    tela_atributos.ids.cb_input.text = str(personagem.carga_basica)
                    tela_atributos.ids.vel_input.text = str(personagem.velocidade_basica)
                    tela_atributos.ids.db_input.text = str(personagem.deslocamento_basico)
                    tela_atributos.ids.esquiva_input.text = str(personagem.esquiva)

                    # Carregar o Dano
                    tela_atributos.ids.gdp_input.text = str(CalculoDano.interface_dano(personagem.st,"GDP"))
                    tela_atributos.ids.bal_input.text = str(CalculoDano.interface_dano(personagem.st,"BAL"))

                    # Atualiza pontos iniciais e recebidos
                    tela_atributos.ids.ponto_ini.text = str(personagem.ponto_int)
                    tela_atributos.ids.ponto_rec.text = str(personagem.ponto_rec)

                    # Calculo dos pontos
                    self.calcular_pontos_pericias()
                    self.calcular_pontos_vantagens()
                    self.calcular_pontos_desvantagens()
                    self.calcular_pontos_atributos()
                    self.calcular_pontos_defeitos()
                    self.calcular_pontos_restantes()

                else:
                    print("Nenhum personagem encontrado para carregar.")
            else:
                print("Nenhum personagem disponível no banco de dados.")

        except AttributeError as e:
            print(f"Erro de atributo ao carregar personagem: {e}")
        except KeyError as e:
            print(f"Erro de chave ao carregar personagem: {e}")
        except TypeError as e:
            print(f"Erro de tipo ao carregar personagem: {e}")
        except ValueError as e:
            print(f"Erro de valor ao carregar personagem: {e}")

    def rolar_1d6(self, aonde):
        """Faz uma rolagem de 1d6 e exibe o resultado temporariamente."""
        try:
            resultado = self.rolagem_dados.rolar_1d6()
            tela = self.root.ids[aonde]
            botao = tela.ids.resultado_1d6  # Obtém o botão que exibe o resultado

            # Salva o texto original e exibe o resultado da rolagem
            texto_original = botao.text
            botao.text = f"[{resultado}]"

            # Agenda a restauração do texto original após 2 segundos
            Clock.schedule_once(lambda dt: self.restaurar_texto_botao(botao, texto_original), 12)
        except AttributeError as e:
            print(f"Erro ao rolar 1d6: {e}")

    def rolar_3d6(self, aonde):
        """Faz uma rolagem de 3d6 e exibe o resultado temporariamente."""
        try:
            resultados = self.rolagem_dados.rolar_3d6()
            total = sum(resultados)
            tela = self.root.ids[aonde]
            botao = tela.ids['resultado_3d6_'+aonde]  # Obtém o botão que exibe o resultado

            # Salva o texto original e exibe o resultado da rolagem
            texto_original = botao.text
            botao.text = f"[{resultados[0]}/{resultados[1]}/{resultados[2]}] = {total}"

            # Agenda a restauração do texto original após 2 segundos
            Clock.schedule_once(lambda dt: self.restaurar_texto_botao(botao, texto_original), 12)
        except AttributeError as e:
            print(f"Erro ao rolar 3d6: {e}")

    def somar(self, recurso_atual_id, valor_input_id):
        """Soma o valor do campo de entrada ao valor atual do recurso."""
        try:
            # Obtenha a tela atual
            tela_atributos = self.root.ids.tela_atributos
            
            # Obtenha o valor atual e o valor para adicionar
            recurso_atual = int(tela_atributos.ids[recurso_atual_id].text)
            valor_adicionar = int(tela_atributos.ids[valor_input_id].text)

            # Calcule o novo valor e atualize o campo de recurso atual
            novo_valor = recurso_atual + valor_adicionar
            tela_atributos.ids[recurso_atual_id].text = str(novo_valor)
        except ValueError:
            print("Por favor, insira valores válidos para a operação.")
        except KeyError as e:
            print(f"Erro ao acessar IDs dos widgets: {e}")

    def subtrair(self, recurso_atual_id, valor_input_id):
        """Subtrai o valor do campo de entrada do valor atual do recurso."""
        try:
            # Obtenha a tela atual
            tela_atributos = self.root.ids.tela_atributos

            # Obtenha o valor atual e o valor para subtrair
            recurso_atual = int(tela_atributos.ids[recurso_atual_id].text)
            valor_subtrair = int(tela_atributos.ids[valor_input_id].text)

            # Calcule o novo valor e atualize o campo de recurso atual
            novo_valor = max(0, recurso_atual - valor_subtrair)  # Evita valores negativos
            tela_atributos.ids[recurso_atual_id].text = str(novo_valor)
        except ValueError:
            print("Por favor, insira valores válidos para a operação.")
        except KeyError as e:
            print(f"Erro ao acessar IDs dos widgets: {e}")

    def salvar_personagem(self):
        """Salva o personagem completo (atributos, perícias, vantagens e desvantagens)."""
        self.salvar_atributos()       # Salva atributos básicos e avançados
        self.root.ids.tela_pericias.salvar_pericias()
        self.root.ids.tela_inventario.salvar_inventario()
        self.root.ids.tela_vantagem.salvar_vantagens()
        self.root.ids.tela_vantagem.salvar_desvantagens()
        self.root.ids.tela_anotacao.salvar_anotacoes()
        print("Personagem salvo com sucesso!")
        
    def carregar_personagem(self):
        """Carrega o personagem completo (atributos, perícias, vantagens e desvantagens)."""
        self.carregar_atributos()
        self.root.ids.tela_pericias.carregar_pericias()
        self.root.ids.tela_inventario.carregar_inventario()
        self.root.ids.tela_vantagem.carregar_vantagens()
        self.root.ids.tela_vantagem.carregar_desvantagens()
        self.root.ids.tela_anotacao.carregar_anotacoes()

    def rolar_dano(self, tipo="GDP"):
        """Rola o dano conforme o tipo de ataque e a ST"""
        tela = self.root.ids.tela_atributos
        personagem = self.gerenciador_dados.carregar_personagem(self.personagem_id)

        # Obtém o valor de dano da tabela usando interface_dano
        dano_string = CalculoDano.interface_dano(personagem.st, tipo)

        # Verifica se o dano_string é válido antes de tentar calcular
        if dano_string:
            dano = CalculoDano.calcular_dano(dano_string)
            botao = None
            texto = None
            # Exibe o resultado no botão correspondente
            if tipo == "GDP":
                botao = tela.ids.dano_gdp_input
                texto = "GDP"
            elif tipo == "BAL":
                botao = tela.ids.dano_bal_input
                texto = "BAL"

            botao.text = f"[{dano}]"

            Clock.schedule_once(lambda dt: self.restaurar_texto_botao(botao, texto), 12)
        else:
            print("Erro: Não foi possível calcular o dano.")

    def restaurar_texto_botao(self, botao, texto_original):
        """Restaura o texto do botão ao valor original."""
        botao.text = texto_original

    def calcular_pontos_pericias(self):
        """Calcula os pontos gastos em perícias, categorizados por dificuldade, e ajusta os sinais para negativos."""
        try:
            app = App.get_running_app()
            personagem_id = app.personagem_id

            if not personagem_id:
                print("Nenhum personagem carregado.")
                return

            # Obter todas as perícias do banco de dados
            pericias = app.gerenciador_dados.carregar_pericias(personagem_id)

            # Inicializar os contadores
            pontos_totais = 0
            pontos_facil = 0
            pontos_medio = 0
            pontos_dificil = 0
            pontos_muito_dificil = 0

            # Iterar pelas perícias para categorizar os pontos
            for pericia in pericias:
                pontos_gastos = pericia.get("pontos_gastos", 0)
                dificuldade = pericia.get("dificuldade", "").upper()

                if dificuldade == "F":
                    pontos_facil += pontos_gastos
                elif dificuldade == "M":
                    pontos_medio += pontos_gastos
                elif dificuldade == "D":
                    pontos_dificil += pontos_gastos
                elif dificuldade == "MD":
                    pontos_muito_dificil += pontos_gastos

                # Contador total
                pontos_totais += pontos_gastos

            # Exibir os valores como negativos
            pontos_totais = -pontos_totais
            pontos_facil = -pontos_facil
            pontos_medio = -pontos_medio
            pontos_dificil = -pontos_dificil
            pontos_muito_dificil = -pontos_muito_dificil

            # Atualizar a interface
            tela_atributos = app.root.ids.tela_atributos
            tela_atributos.ids.ponto_total.text = str(pontos_totais)
            tela_atributos.ids.ponto_p_f.text = str(pontos_facil)
            tela_atributos.ids.ponto_p_m.text = str(pontos_medio)
            tela_atributos.ids.ponto_p_d.text = str(pontos_dificil)
            tela_atributos.ids.ponto_p_md.text = str(pontos_muito_dificil)

        except Exception as e:
            print(f"Erro ao calcular pontos de perícias: {e}")

    def calcular_pontos_vantagens(self):
        """Calcula os pontos gastos em vantagens e ajusta os sinais."""
        try:
            app = App.get_running_app()
            personagem_id = app.personagem_id

            if not personagem_id:
                print("Nenhum personagem carregado.")
                return 0

            # Obter todas as vantagens do banco de dados
            vantagens = app.gerenciador_dados.carregar_vantagens(personagem_id)

            # Somar os pontos de todas as vantagens
            pontos_vantagens = sum(vantagem.get("pontos", 0) for vantagem in vantagens)

            # Exibir como negativo
            pontos_formatados = f"-{pontos_vantagens}" if pontos_vantagens > 0 else str(pontos_vantagens)

            # Atualizar a interface
            tela_atributos = app.root.ids.tela_atributos
            tela_atributos.ids.ponto_vant.text = pontos_formatados

            return -pontos_vantagens  # Retorna como negativo para uso nos cálculos

        except Exception as e:
            print(f"Erro ao calcular pontos de vantagens: {e}")
            return 0

    def calcular_pontos_desvantagens(self):
        """Calcula os pontos ganhos com desvantagens e ajusta os sinais."""
        try:
            app = App.get_running_app()
            personagem_id = app.personagem_id

            if not personagem_id:
                print("Nenhum personagem carregado.")
                return 0

            # Obter todas as desvantagens do banco de dados
            desvantagens = app.gerenciador_dados.carregar_desvantagens(personagem_id)

            # Somar os pontos de todas as desvantagens
            pontos_desvantagens = sum(desvantagem.get("pontos", 0) for desvantagem in desvantagens)

            # Exibir como positivo
            pontos_formatados = f"+{pontos_desvantagens}" if pontos_desvantagens > 0 else str(pontos_desvantagens)

            # Atualizar a interface
            tela_atributos = app.root.ids.tela_atributos
            tela_atributos.ids.ponto_desvan.text = pontos_formatados

            return pontos_desvantagens

        except Exception as e:
            print(f"Erro ao calcular pontos de desvantagens: {e}")
            return 0

    def calcular_pontos_atributos(self):
        """Calcula os pontos ganhos ou gastos com atributos e ajusta os sinais corretamente."""
        try:
            app = App.get_running_app()
            tela_atributos = app.root.ids.tela_atributos

            # Obter valores dos atributos
            st = int(tela_atributos.ids.st_input.text)
            dx = int(tela_atributos.ids.dx_input.text)
            iq = int(tela_atributos.ids.iq_input.text)
            ht = int(tela_atributos.ids.ht_input.text)

            # Inicializar os pontos totais
            pontos_totais = 0

            # Cálculo de pontos de atributos
            if st > 10:
                pontos_totais -= (st - 10) * 10  # Gastos em ST acima de 10
            elif st < 10:
                pontos_totais += (10 - st) * 10  # Ganhos em ST abaixo de 10

            if dx > 10:
                pontos_totais -= (dx - 10) * 20  # Gastos em DX acima de 10
            elif dx < 10:
                pontos_totais += (10 - dx) * 20  # Ganhos em DX abaixo de 10

            if iq > 10:
                pontos_totais -= (iq - 10) * 20  # Gastos em IQ acima de 10
            elif iq < 10:
                pontos_totais += (10 - iq) * 20  # Ganhos em IQ abaixo de 10

            if ht > 10:
                pontos_totais -= (ht - 10) * 10  # Gastos em HT acima de 10
            elif ht < 10:
                pontos_totais += (10 - ht) * 10  # Ganhos em HT abaixo de 10

            # Exibir como positivo ou negativo
            pontos_formatados = f"+{pontos_totais}" if pontos_totais > 0 else str(pontos_totais)

            # Atualizar a interface
            tela_atributos.ids.ponto_atb.text = pontos_formatados

            return pontos_totais

        except Exception as e:
            print(f"Erro ao calcular pontos de atributos: {e}")
            return 0

    def calcular_pontos_defeitos(self):
        """Calcula os pontos de defeitos e ajusta os sinais."""
        try:
            app = App.get_running_app()
            tela_atributos = app.root.ids.tela_atributos

            # Obter pontos iniciais
            pontos_iniciais = int(tela_atributos.ids.ponto_ini.text or 0)

            # Calcular pontos ganhos com desvantagens
            pontos_desvantagens = self.calcular_pontos_desvantagens()

            # Calcular pontos ganhos com atributos negativos
            self.calcular_pontos_atributos()  # Já atualiza a interface com os pontos totais
            pontos_atributos_negativos = int(tela_atributos.ids.ponto_atb.text)
            pontos_atributos_negativos = abs(pontos_atributos_negativos) if pontos_atributos_negativos < 0 else 0

            # Somar pontos de defeitos
            pontos_defeitos = pontos_atributos_negativos + pontos_desvantagens

            # Limitar pontos de defeitos à metade dos pontos iniciais
            metade_pontos_iniciais = pontos_iniciais // 2
            if pontos_defeitos > metade_pontos_iniciais:
                pontos_defeitos = metade_pontos_iniciais

            # Exibir como positivo
            pontos_formatados = f"+{pontos_defeitos}" if pontos_defeitos > 0 else str(pontos_defeitos)

            # Atualizar a interface
            tela_atributos.ids.ponto_def.text = pontos_formatados

            return pontos_defeitos

        except Exception as e:
            print(f"Erro ao calcular pontos de defeitos: {e}")
            return 0

    def calcular_pontos_restantes(self):
        """Calcula os pontos restantes baseados em todos os pontos calculados."""
        try:
            app = App.get_running_app()
            tela_atributos = app.root.ids.tela_atributos

            # Obter valores necessários
            pontos_iniciais = int(tela_atributos.ids.ponto_ini.text or 0)
            pontos_recebidos = int(tela_atributos.ids.ponto_rec.text or 0)
            pontos_defeitos = int(tela_atributos.ids.ponto_def.text or 0)
            pontos_atributos = int(tela_atributos.ids.ponto_atb.text or 0)
            pontos_vantagens = int(tela_atributos.ids.ponto_vant.text or 0)
            pontos_pericias = int(tela_atributos.ids.ponto_total.text or 0)

            # Calcular os pontos restantes
            pontos_restantes = (
                pontos_iniciais
                + pontos_recebidos
                + pontos_defeitos
                - abs(pontos_atributos)
                - abs(pontos_vantagens)
                - abs(pontos_pericias)
            )

            # Atualizar a interface
            tela_atributos.ids.ponto_rest.text = str(pontos_restantes)

            return pontos_restantes

        except Exception as e:
            print(f"Erro ao calcular pontos restantes: {e}")
            return 0