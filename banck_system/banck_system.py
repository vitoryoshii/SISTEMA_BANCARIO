# menu estatico do sistema bancario

MENU = '''
    MENU

[0] SACAR
[1] DEPOSITAR
[2] EXTRATO
[3] SAIR

'''

# VARIAVEIS GLOBAIS ESTATICAS

LIMITE_SAQUE_DINEHIRO = 500
LIMITE_SAQUE_DIARIO = 3

# VARIAVEIS GLOBAIS

saldo = 1000
extrato = ""
numero_saque = 0

# Exibe menu e captura a opção desejada

while True:
    option = int(input(MENU))

    if option == 0: # Sacar
        print("SACAR")

        if numero_saque < LIMITE_SAQUE_DIARIO: # Verifica limite diário de saque.
            valor_saque = float(input("Informe o valor a SACAR: "))

            if valor_saque > saldo: # Saldo sulficiente.
                print("Não será possível sacar o valor. Falta de saldo.")
            else:  

                if valor_saque <= LIMITE_SAQUE_DINEHIRO: # Verifica limite por saque.
                    saldo -= valor_saque 

                    #inclui saque no extrato
                    extrato += f""" 

                        Saque
                        -R$ {valor_saque:.2f}

                    """
                    print(f"Saque efetuado com sucesso!. Saldo: {saldo}")

                    numero_saque += 1 # ADD saque efetuado   
                else:
                    print(f"Não realizado o saque. Valor: R$ {valor_saque:.2f} maior que o límite diário R$ {LIMITE_SAQUE_DINEHIRO:.2f}.")
        else:
            print("Excedeu o números de saque diário!")
            
 #   elif option == 1: # Depositar

 #   elif option == 2: # Extrato 

    elif option == 3: # Sair
       break

    else:
        print("Opção inválida! Digite novamente a opção desejada.")
    
