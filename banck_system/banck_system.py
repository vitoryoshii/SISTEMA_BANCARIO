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

    [0] SACAR
    [1] DEPOSITAR
    [2] EXTRATO
    [3] SAIR

    ====================
    '''

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

# Função Depositar
def depositar():

    global saldo, extrato

    print("DEPOSITO")
    valor_deposito = float(input("Digite o valor para depositar: "))

    # Verifica se o valor a depositar e maior que zero

    if valor_deposito > 0:
        saldo += valor_deposito
        extrato += f"DEPOSITO: R$ {valor_deposito:.2f}\n"
        print("Deposito efetuado com sucesso!")
    else:
        print("Opção falhou! Valor informado é inválido. ")

# Função exibir extrato
def exibir_extrato():

    global extrato, saldo

    print("\n================ EXTRATO ================")
    print("Não foram realizado movimentações." if not extrato else extrato)
    print(f"\nSALDO: R$ {saldo:.2f}")
    print("\n=========================================")

# Chama Função resposável por cada interação do user

while True:

    option = int(input(menu()))

    if option == 0: # Sacar

        print("SACAR")
        valor_saque = float(input("Digite o valor para sacar: "))

        saldo, extrato = sacar(
            saldo=saldo,
            valor_saque=valor_saque,
            extrato=extrato,
            numero_saque=numero_saque,
            limite_saque=LIMITE_SAQUE_DIARIO,
            limite_saldo=LIMITE_SAQUE_DINEHIRO
        )

    elif option == 1: # Depositar
        
        depositar()
        
    elif option == 2: # Extrato 
        
        exibir_extrato() 

    elif option == 3: # Sair
       
       break

    else:
        print("Opção inválida! Digite novamente a opção desejada.")
    
