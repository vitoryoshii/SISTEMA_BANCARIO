import textwrap
from sistema_banco.services import ContaService, GerenteService
from utils.utils import data_hora

def menu_cliente(conta_service):
    while True:
        dh = data_hora()
        opcao_cliente = input(textwrap.dedent(f'''
        ===== MENU CLIENTE - {dh} =====
        [1] DEPOSITAR
        [2] SACAR
        [3] EXTRATO
        [4] TROCAR CONTA
        [0] VOLTAR
        ==============================================
        Escolha uma opção:
        '''))

        operacoes_cliente = {
            '1': conta_service.depositar,
            '2': conta_service.sacar,
            '3': conta_service.extrato,
            '4': conta_service.trocar_conta
        }

        if opcao_cliente == "0":
            conta_service.limpar_conta()
            break
        elif opcao_cliente in operacoes_cliente:
            operacoes_cliente[opcao_cliente]()
        else:
            print("\n@@@ Opção inválida! @@@")

def menu_principal():
    dh = data_hora()
    menu_texto = f'''
    ==== BANCO DIGITAL - {dh} ====
    [1] ACESSO CLIENTE
    [2] ACESSO FUNCIONARIO
    [0] VOLTAR
    =============================================
    Escolha uma opção: '''
            
    return input(textwrap.dedent(menu_texto))

def menu_gerente(gerente_service):
    while True:
        dh = data_hora()
        opcao_gerente = input(textwrap.dedent(f'''
        ==== MENU GERENTE - {dh} ====
        [1] CRIAR USUÁRIO
        [2] CRIAR CONTA
        [3] LISTAR USUÁRIOS
        [4] LISTAR CONTAS
        [5] VISUALIZAR EXTRATO (qualquer conta)
        [0] VOLTAR
        ============================================
        Escolha uma opção: '''))

        operacoes_gerente = {
            '1': gerente_service.criar_usuario,
            '2': gerente_service.criar_conta,
            '3': gerente_service.listar_usuarios,
            '4': gerente_service.listar_contas,
            '5': gerente_service.visualizar_extrato
        }

        if opcao_gerente == "0":
            break
        elif opcao_gerente in operacoes_gerente:
            operacoes_gerente[opcao_gerente]()
        else:
            print("\n@@@ Opção inválida! @@@")

def main():
    conta_service = ContaService()
    gerente_service = GerenteService()

    while True:

        opcao = menu_principal()
        
        if opcao == "1":
            if conta_service.autenticar_cliente():
                menu_cliente(conta_service)
        elif opcao == "2":
            menu_gerente(gerente_service)
        elif opcao == "0":
            conta_service.limpar_conta()
            print("\n=== Sistema encerrado. ===")
            break
        else:
            print("\n@@@ Opção inválida! @@@")

if __name__ == "__main__":
    main()