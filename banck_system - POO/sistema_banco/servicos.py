from .models import Pessoa_fisica, ContaCorrente, Saque, Deposito, Conta
from .utils import filtro_usuarios, recuperar_conta_usuario, getValidaCPF, log_transacao

@log_transacao
def depositar(usuarios):
    cpf = input("Digite o CPF do usuário: ")
    usuario = filtro_usuarios(cpf, usuarios)

    if not usuario:
        print("\n@@@ Cliente não encontrado! @@@")
        return
    
    valor_deposito = float(input("Digite o valor do depósito: "))
    transacao = Deposito(valor_deposito)

    conta = recuperar_conta_usuario(usuario)
    if not conta:
        return
    
    usuario.realizar_transacao(conta, transacao)

@log_transacao
def sacar(usuarios):
    cpf = input("Digite o CPF do usuário: ")
    usuario = filtro_usuarios(cpf, usuarios)

    if not usuario:
        print("\n@@@ Cliente não encontrado! @@@")
        return
    
    valor_saque = float(input("Digite o valor do saque: "))
    transacao = Saque(valor_saque)

    conta = recuperar_conta_usuario(usuario)
    if not conta:
        return
    
    usuario.realizar_transacao(conta, transacao)

@log_transacao
def exibir_extrato(usuarios):
    cpf = input("Digite o CPF do usuário: ")
    usuario = filtro_usuarios(cpf, usuarios)

    if not usuario:
        print("\n@@@ Cliente não encontrado! @@@")
        return
    
    conta = recuperar_conta_usuario(usuario)
    if not conta:
        return
    
    print("\n================ EXTRATO ================")
    extrato = ""
    tem_transacoes = False
    for transacao in conta.historico.gerar_relatorio(tipo_transacao="saque"): #colocar tipo_transacao=None para mostrar todas as transações.
        tem_transacoes = True
        extrato += f"\n{transacao['tipo']}:\n\tR$ {transacao['valor']:.2f}"
        extrato += f" - {transacao['data']}"
    if not tem_transacoes:
        extrato = "Não foram realizadas movimentações."

    print(extrato)
    print(f"\nSALDO: R$ {conta.saldo:.2f}")
    print("\n=========================================")

@log_transacao
def criar_usuario(usuarios):
    print("=== CADASTRO DE USUÁRIO ===")
    print("=== CPF: 000.000.000-00 ===")
    cpf = input("Digite o CPF (apenas números ou com pontuação): ")

    if not getValidaCPF(cpf):
        print("\n@@@ CPF inválido! Tente novamente. @@@")
        return

    usuario = filtro_usuarios(cpf, usuarios)
    if usuario: 
        print("\n@@@ Já existe cliente com esse CPF! @@@")
        return
    
    nome = input("Digite seu nome completo: ")
    data_nascimento = input("Digite sua data de nascimento (dd-mm-aaaa): ")
    endereco = input("Digite seu endereço (Logradouro, número - bairro - cidade/UF): ")

    cliente = Pessoa_fisica(nome=nome, data_nascimento=data_nascimento, endereco=endereco, cpf=cpf)
    usuarios.append(cliente)

    print("=== Usuário criado com sucesso! ===")

@log_transacao
def criar_conta(numero_conta, usuarios, contas):
    cpf = input("Digite o CPF do usuário: ")
    usuario = filtro_usuarios(cpf, usuarios)

    if not usuario:
        print("\n@@@ Usuário não encontrado, fluxo de criação de conta encerrado! @@@")
        return
    
    conta = ContaCorrente.criar_conta(usuario=usuario, numero_conta=numero_conta)
    contas.append(conta)
    usuario.adicionar_conta(conta)

    print("=== Conta criada com sucesso! ===")

def listar_contas(usuarios):
    for usuario in usuarios:
        for conta in usuario.contas:
            print("=" * 50)
            print(f"Nome: {usuario.nome} | Conta: {conta.numero_conta} | Saldo: R$ {conta.saldo:.2f}")

def listar_usuarios(usuarios):
    if not usuarios:
        print("\n@@@ Não há usuários cadastrados. @@@")
        return
    
    print("\n============== LISTA DE USUÁRIOS ==============")
    for usuario in usuarios:
        print(f"Nome: {usuario.nome}")
        print(f"CPF: {usuario.cpf}")
        print(f"Data de Nascimento: {usuario.data_nascimento}")
        print(f"Endereço: {usuario.endereco}")
        print("=" * 50)