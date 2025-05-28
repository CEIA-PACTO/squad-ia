def classificar_abdominais(abd):
    if abd < 15:
        return 'Fraco'
    elif abd <= 30:
        return 'Moderado'
    else:
        return 'Bom'

def classificar_imc(imc):
    if imc < 18.5:
        return 'Abaixo do peso'
    elif imc < 25:
        return 'Normal'
    elif imc < 30:
        return 'Sobrepeso'
    else:
        return 'Obesidade'


def atribuir_persona(row):
    if row['nivel_fisico'] == 'Bom' and row['faixa_imc'] == 'Normal':
        return 'Executor'
    elif row['nivel_fisico'] == 'Moderado' and row['faixa_imc'] == 'Sobrepeso':
        return 'Planejador'
    elif row['nivel_fisico'] == 'Fraco' and row['faixa_imc'] == 'Obesidade':
        return 'Analista'
    elif row['nivel_fisico'] == 'Fraco' and row['faixa_imc'] == 'Abaixo do peso':
        return 'Comunicador'
    elif row['nivel_fisico'] == 'Moderado' and row['faixa_imc'] == 'Normal':
        return 'Comunicador'
    else:
        return 'Executor'