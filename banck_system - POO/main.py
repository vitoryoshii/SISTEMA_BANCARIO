import textwrap
from sistema_banco.persistencia import carregar_dados_separados, salvar_usuarios_csv, salvar_contas_csv
from sistema_banco.servicos import depositar, sacar, exibir_extrato, criar_conta, listar_contas, criar_usuario, listar_usuarios
from sistema_banco.utils import data_hora

def menu():
        menu_texto = f'''
        ==================== MENU =====================
        ============= {data_hora()} =============

        [1] DEPOSITAR         [5] CRIAR USUÁRIO
        [2] SACAR             [6] LISTAR USUÁRIOS
        [3] EXTRATO           [7] LISTAR CONTAS
        [4] CRIAR CONTA       [0] SAIR
        ===============================================
        Escolha uma opção: '''
        
        return input(textwrap.dedent(menu_texto))

def main():
    usuarios, contas = carregar_dados_separados()

    operacoes = {
            '1': lambda: depositar(usuarios),
            '2': lambda: sacar(usuarios),
            '3': lambda: exibir_extrato(usuarios),
            '4': lambda: criar_conta(len(contas) + 1, usuarios, contas),
            '5': lambda: criar_usuario(usuarios),
            '6': lambda: listar_usuarios(usuarios),
            '7': lambda: listar_contas(usuarios),
        }
    
    while True:
        opcao = menu()

        if opcao == '0':
           print("Salvando dados e saindo do sistema...")
           salvar_usuarios_csv(usuarios)
           salvar_contas_csv(contas)
           break
        elif opcao in operacoes:
            operacoes[opcao]()
        else:
            print("\n@@@ Opção inválida! Tente novamente. @@@\n")

if __name__ == "__main__":
    main()