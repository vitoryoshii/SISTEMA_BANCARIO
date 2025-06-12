import textwrap
from datetime import datetime

def log_transacao(func):
    def wrapper(*args, **kwargs):
        data_hora = datetime.now().strftime("%d/%m/%Y %H:%M:%S")
        print(f"[{data_hora}] Transação realizada: {func.__name__}")
        return func(*args, **kwargs)
    return wrapper

def data_transacao():
    # Retorna a data e hora atual formatada
    return datetime.now().strftime("%d/%m/%Y %H:%M")
    
# Função exibe menu
def menu():
    horario_atual = data_transacao()

    menu = f'''
    ===={horario_atual}====
    ========MENU========

    [0]\tDEPOSITAR
    [1]\tSACAR
    [2]\tEXTRATO
    [3]\tNOVA CONTA
    [4]\tLISTAR CONTAS
    [5]\tNOVO USUARIO
    [6]\tLISTAR USUÁRIOS
    [7]\tSAIR

    ====================
    '''
    return int(input(textwrap.dedent(menu)))

# Função Depositar
@log_transacao
def depositar(saldo, transacoes, valor_user, /):
    hora_atual = data_transacao()
    # Verifica se o valor a depositar e maior que zero
    if valor_user > 0:
        saldo += valor_user
        transacoes.append({"tipo": "DEPOSITO", "valor": valor_user, "data": hora_atual})
        print("\n=== Depósito realizado com sucesso! ===")
    else:
        print("\n@@@ Operação falhou! O valor informado é inválido. @@@")
    
    return saldo, transacoes

# Função Sacar
@log_transacao
def sacar(*, saldo, valor_saque, transacoes, numero_saque, limite_saque, limite_saldo):
    hora_atual = data_transacao()

    excedeu_saldo = valor_saque > saldo
    excedeu_limite = valor_saque > limite_saldo
    excedeu_saques = numero_saque >= limite_saque

    if excedeu_saques: # Verifica limite diário de saque.
        print("\n@@@ Operação falhou! Número máximo de saques excedido. @@@")
    elif excedeu_saldo: 
        print("\n@@@ Operação falhou! Você não tem saldo suficiente. @@@")
    elif excedeu_limite:
        print("f\n@@@ Operação falhou! O valor do saque excede o limite. @@@")
    elif valor_saque > 0:
        saldo -= valor_saque 
        numero_saque += 1 # ADD saque efetuado

        #inclui saque no extrato
        transacoes.append({"tipo": "SAQUE", "valor": valor_saque, "data": hora_atual})
        print("\n=== Saque realizado com sucesso! ===")
    else:
        print("\n@@@ Operação falhou! O valor informado é inválido. @@@")

    return saldo, transacoes 

# Função exibir extrato
def exibir_extrato(saldo, transacoes):

    print("\n================ EXTRATO ================")
    if not transacoes:
        extrato = "Não foram realizadas movimentações."
    else:
        for t in transacoes:
            print(f"{t['tipo']}: R$ {t['valor']:.2f} / {t['data']}")
        
    print(f"\nSALDO: R$ {saldo:.2f}")
    print("\n=========================================")

def gerar_relatorio(transacoes, tipo=None):
    for transacao in transacoes:
        if tipo is None or transacao["tipo"] == tipo.upper():
            yield transacao
# Função criar usuario e filtrar usuarios
def criar_usuario(usuarios):

    cpf = input("Digite o CPF (apenas números): ")
    usuario = filtro_usuarios(cpf, usuarios) # Verifica se o usuário já existe
    if usuario: # Se o usuário já existe, não cria outro
        print("Usuário já cadastrado.")
        return
    
    nome = input("Digite seu nome completo: ")
    data_nascimento = input("Digite sua data de nascimento (dd-mm-aaaa): ")
    endereco = input("Digite seu endereço (Logradouro, número - bairro - cidadde/UF): ")

    # Adiciona o novo usuário na lista de usuários
    usuarios.append({
        "cpf" : cpf,
        "nome" : nome,
        "data_nascimento" : data_nascimento,
        "endereco" : endereco
    })

    print("=== Usuário criado com sucesso! ===")

def filtro_usuarios(cpf, usuarios):
    usuario_filtrado = [usuario for usuario in usuarios if usuario["cpf"] == cpf]
    return usuario_filtrado[0] if usuario_filtrado else None

# criar conta
def criar_conta(AGENCIA, numero_conta, usuarios):
    cpf = input("Digite o CPF do usuário: ")
    usuario = filtro_usuarios(cpf, usuarios)

    if usuario:
        print("=== Conta criada com sucesso! ===")
        return {"agencia": AGENCIA, "conta" : numero_conta, "usuario": usuario}
    
    print("\n@@@ Usuário não encontrado, fluxo de criação de conta encerrado! @@@")

# Função listar contas
def listar_contas(contas):
    for conta in contas:
        linha_agencia = f'''
            Agência:\t{conta['agencia']}
            C/C:\t\t{conta['conta']}
            Titular:\t{conta['usuario']['nome']}
        '''
        print("=" * 50)
        print(textwrap.dedent(linha_agencia))

def listar_usuarios(usuarios):
    for usuario in usuarios:
        linha_usuario = f'''
            Nome:\t\t{usuario['nome']}
            CPF:\t\t{usuario['cpf']}
            Data Nascimento:\t{usuario['data_nascimento']}
        '''
        print("=" * 50)
        print(textwrap.dedent(linha_usuario))

def main(): # Main function

    # VARIAVEIS ESTATICAS
    LIMITE_SAQUE_DINEHIRO = 500
    LIMITE_SAQUE_DIARIO = 3
    AGENCIA = "0001"

    # VARIAVEIS 
    saldo = 0
    extrato = ""
    numero_saque = 0

    # LISTAS/DICIONARIOS
    usuarios = []
    contas = []
    transacoes = []


    while True:

        option = menu()

        if option == 0: # DEPOSITAR

            print("DEPOSITO")
            valor_user = float(input("Digite o valor para depositar: "))

            saldo, transacoes = depositar(saldo, transacoes, valor_user)

        elif option == 1: # SACAR

            print("SACAR")
            valor_user = float(input("Digite o valor para sacar: "))

            saldo, transacoes = sacar(
                saldo=saldo,
                valor_saque=valor_user,
                transacoes=transacoes,
                numero_saque=numero_saque,
                limite_saque=LIMITE_SAQUE_DIARIO,
                limite_saldo=LIMITE_SAQUE_DINEHIRO
            )

        elif option == 2: # Extrato

            exibir_extrato(saldo, transacoes)

        elif option == 3: # NOVA CONTA

            print("CRIAR CONTA")

            numero_conta = len(contas) + 1
            conta = criar_conta(AGENCIA, numero_conta, usuarios)

            if conta:
                contas.append(conta)

        elif option == 4: # LISTAR CONTAS

            print("LISTAS DE CONTAS")
            listar_contas(contas)

        elif option == 5: # NOVO USUARIO

            print("CADASTRO DE USUÁRIO")
            criar_usuario(usuarios)

        elif option == 6: # LISTAR USUÁRIOS

            print("LISTAR USUÁRIOS")
            listar_usuarios(usuarios)

        elif option == 7: # Sair
        
            break

        else: # Opção inválida
            print("\n@@@ Operação falhou! Digite uma opção válida. @@@")
            
main() # Chama a função main
# Fim do código