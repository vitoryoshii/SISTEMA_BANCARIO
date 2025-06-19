from pathlib import Path
from datetime import datetime

PASTA_RAIZ = Path(__file__).resolve().parent.parent
DADOS_PATH = PASTA_RAIZ / 'dados'

def getDataHora():
    return datetime.now().strftime("%d/%m/%Y %H:%M:%S")

def getValidaCPF(cpf) -> bool:
    cpf = ''.join(filter(str.isdigit, cpf))

    if len(cpf) != 11 or cpf == cpf[0] * 11:
        return False

    for i in [9, 10]:
        soma = sum(int(cpf[num]) * (i + 1 - num) for num in range(i))
        digito = (soma * 10) % 11
        if digito == 10:
            digito = 0
        if digito != int(cpf[i]):
            return False

    return True

def log_transacao(func):
    def envelope(*args, **kwargs):
        resultado = func(*args, **kwargs)
        data_hora = getDataHora()

        with open(DADOS_PATH / 'logTransacao.txt', 'a', encoding='utf-8') as arquivo:
            arquivo.write(
                f"[{data_hora}] Função '{func.__name__}' executada com argumentos {args}, e {kwargs}. Retornou {resultado}\n"
            )

        return resultado
    return envelope

def filtro_usuarios(cpf, usuarios):
    usuario_filtrado = [usuario for usuario in usuarios if usuario.cpf == cpf]
    return usuario_filtrado[0] if usuario_filtrado else None

def recuperar_conta_usuario(usuario):
    if not usuario.contas:
        print("\n@@@ Cliente não possui conta! @@@")
        return
    
    return usuario.contas[0]