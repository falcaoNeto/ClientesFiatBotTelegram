def formatar_cpf(cpf):
    Fcpf = f"{cpf[:3]}.{cpf[3:6]}.{cpf[6:9]}-{cpf[9:]}"
    return Fcpf
    
def formatar_clientes(clientes):
    return "\n".join([
        f'Cliente: {cliente[0]} (CPF: {cliente[1]})\n'
        f'Clique para enviar uma mensagem:\n'
        f'https://wa.me/55{cliente[2]}\n'
        for cliente in clientes
        ])
                   
def formatar_filhos(filhos):
    return "\n".join([
        f'Filho: {filho[0]} - Responsável: {filho[1]}\n'
        f'Clique para enviar uma mensagem:\n'
        f'https://wa.me/55{filho[2]}\n'
        for filho in filhos
        ])

def formatar_conjuge(clientes):
    return "\n".join([
        f'Conjuge: {cliente[2]} - Cliente: {cliente[0]} (CPF: {cliente[1]})\n'
        f'Clique para enviar uma mensagem:\n'
        f'https://wa.me/55{cliente[3]}\n'
        for cliente in clientes
    ])
    
def format_revisoes(clientes):
    return "\n".join([
        f'Cliente: {cliente[0]} (CPF: {cliente[1]})\n'
        f'Proxima revisão prevista para {format_data(cliente[3])}\n'
        f'O Cliente possui {cliente[2]} revisões pendentes\n'
        f'Clique para enviar uma mensagem:\n'
        f'https://wa.me/55{cliente[4]}\n'
        for cliente in clientes
        ])
    
def format_data_compra(clientes):
    return "\n".join([
        f'Cliente: {cliente[0]} (CPF: {cliente[1]})\n'
        f'Clique para enviar uma mensagem:\n'
        f'https://wa.me/55{cliente[2]}\n'
        for cliente in clientes
        ])
    
def format_data_casamento(clientes):
    return "\n".join([
        f'Cliente: {cliente[0]} (CPF: {cliente[1]})\n'
        f'Clique para enviar uma mensagem:\n'
        f'https://wa.me/55{cliente[2]}\n'
        for cliente in clientes
        ])

def format_data(data):
    if data:
        data_formatada = data.strftime("%d-%m-%Y")
        return data_formatada
    
