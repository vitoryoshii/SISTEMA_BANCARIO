# VARIAVEIS ESTATICAS

LIMITE_SAQUE_DINEHIRO = 500
LIMITE_SAQUE_DIARIO = 3

# VARIAVEIS GLOBAIS

saldo = 0
extrato = ""
numero_saque = 0

# Função exibe menu
def menu():
    
    return '''
    ========MENU========

    [0] DEPOSITAR
    [1] SACAR
    [2] EXTRATO
    [3] SAIR

    ====================
    '''

# Função Depositar
def depositar(saldo, extrato, valor_user, /):

    # Verifica se o valor a depositar e maior que zero
    if valor_user > 0:
        saldo += valor_user
        extrato += f"DEPOSITO: R$ {valor_user:.2f}\n"
        print("\n=== Depósito realizado com sucesso! ===")
    else:
        print("\n@@@ Operação falhou! O valor informado é inválido. @@@")
    
    return saldo, extrato

# Função Sacar 
def sacar(*, saldo, valor_saque, extrato, numero_saque, limite_saque, limite_saldo):

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
        extrato += f"SAQUE: {valor_saque:.2f}\n"

        print("\n=== Saque realizado com sucesso! ===")
    else:
        print("\n@@@ Operação falhou! O valor informado é inválido. @@@")

    return saldo, extrato 

# Função exibir extrato
def exibir_extrato(saldo, /, *, extrato):

    print("\n================ EXTRATO ================")
    print("Não foram realizado movimentações." if not extrato else extrato)
    print(f"\nSALDO: R$ {saldo:.2f}")
    print("\n=========================================")

# Chama Função resposável por cada interação do user

while True:

    option = int(input(menu()))

    if option == 0: # DEPOSITAR

        print("DEPOSITO")
        valor_user = float(input("Digite o valor para depositar: "))

        saldo, extrato = depositar(saldo, extrato, valor_user)

    elif option == 1: # SACAR

        print("SACAR")
        valor_user = float(input("Digite o valor para sacar: "))

        saldo, extrato = sacar(
            saldo=saldo,
            valor_saque=valor_user,
            extrato=extrato,
            numero_saque=numero_saque,
            limite_saque=LIMITE_SAQUE_DIARIO,
            limite_saldo=LIMITE_SAQUE_DINEHIRO
        )

    elif option == 2: # Extrato 
        
        exibir_extrato(saldo, extrato=extrato) 

    elif option == 3: # Sair
       
       break

    else:
        print("Operação inválida, por favor selecione novamente a operação desejada.")
    
