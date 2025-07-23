"""
O ponto de entrada principal para a aplicação Terminal Dogma.
Este script inicializa e executa o sistema de deliberação.
"""
# Adicione estas duas linhas
import logging
logging.getLogger('langchain_google_genai').setLevel(logging.ERROR)

from .system import DogmaSystem
from .exceptions import ATFieldInterference, CentralDogmaLockdown
from . import ui


def main():
    """
    Função principal que cria uma instância do DogmaSystem e inicia seu loop de execução.
    Inclui um bloco de tratamento de exceções para capturar erros críticos durante a inicialização.
    """
    try:
        # Inicializa o sistema Dogma
        dogma_system = DogmaSystem()
        
        # Inicia o loop principal do sistema
        dogma_system.run()
        
    except ATFieldInterference as e:
        # Cria um controlador UI temporário para exibir o erro
        ui_controller = ui.UIController()
        ui_controller.display_error(str(e))
        
    except CentralDogmaLockdown as e:
        # Cria um controlador UI temporário para exibir o erro
        ui_controller = ui.UIController()
        ui_controller.display_error(str(e))
        
    except KeyboardInterrupt:
        # Trata interrupção do usuário (Ctrl+C)
        ui_controller = ui.UIController()
        ui_controller.display_shutdown()
        
    except Exception as e:
        # Trata erros inesperados
        ui_controller = ui.UIController()
        ui_controller.display_error(f"Erro crítico na inicialização: {str(e)}")


if __name__ == "__main__":
    # Este é o padrão em Python para tornar um arquivo executável como um script.
    # O código dentro deste bloco só roda quando você executa `python -m src.dogma_core.main`.
    main()