# app_principal.py

from interface_grafica import InterfaceGrafica
from gerenciador_dados import GerenciadorDados
from regras_calculos import RolagemDados
from personagem import Personagem  # Importe a classe Personagem

def main():
    """Função principal para iniciar o aplicativo."""
    gerenciador_dados = GerenciadorDados()

    # Tente carregar o personagem com ID 1
    personagem_id = 1
    if not gerenciador_dados.carregar_personagem(personagem_id):
        # Se o personagem com ID 1 não existir, crie um novo personagem padrão
        novo_personagem = Personagem("Nome do personagem", "Seu nome", 10, 10, 10, 10)
        personagem_id = gerenciador_dados.salvar_personagem(novo_personagem)

    rolagem_dados = RolagemDados()
    app = InterfaceGrafica(gerenciador_dados, rolagem_dados)
    app.personagem_id = personagem_id  # Define o personagem_id inicial na interface

    # Executa o aplicativo e fecha o banco ao finalizar
    app.run()
    gerenciador_dados.fechar_conexao()

if __name__ == '__main__':
    main()