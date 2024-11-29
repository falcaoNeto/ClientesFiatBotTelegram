from bd import bd_pool
from datetime import date, timedelta
from dateutil.relativedelta import relativedelta
data = date.today()
data_hoje = data.strftime('%m-%d')


def verificar_aniversario_cliente(cpf):
    try:
        connect = bd_pool.getconn()
        cursor = connect.cursor()
        query = """
            SELECT cliente.nome, cliente.cpf, cliente.telefone 
            FROM cliente
            JOIN funcionario on cliente.id_funcionario = funcionario.id_func
            WHERE TO_CHAR(data_nascimento, 'MM-DD') = %s AND funcionario.cpf = %s
        """
        cursor.execute(query, (data_hoje, cpf))
        clientes = cursor.fetchall()
        return clientes
    
    except Exception as e:
        print(f"Erro ao acessar o banco de dados: {str(e)}")
    finally:
        if cursor:
            cursor.close()
        if connect:
            bd_pool.putconn(connect)
            
            
            
def verificar_aniversario_filho(cpf):
    try:
        connect = bd_pool.getconn()
        cursor = connect.cursor()
        query = """
            SELECT filho.nome, cliente.nome, cliente.telefone
            FROM filho
            JOIN cliente ON cliente.id_clien = filho.id_cliente
            JOIN funcionario on cliente.id_funcionario = funcionario.id_func
            WHERE TO_CHAR(filho.data_nascimento, 'MM-DD') = %s AND funcionario.cpf = %s
        """
        cursor.execute(query, (data_hoje, cpf))
        filhos = cursor.fetchall()
        return filhos
    
    except Exception as e:
        print(f"Erro ao acessar o banco de dados: {str(e)}")
    finally:
        if cursor:
            cursor.close()
        if connect:
            bd_pool.putconn(connect)
            
            
def verificar_cpf_usuario(cpf):
    try:
        connect = bd_pool.getconn()
        cursor = connect.cursor()
        query = "SELECT * FROM funcionario WHERE cpf = %s"
        cursor.execute(query, (cpf,))
        cpfF = cursor.fetchone()
        return bool(cpfF)
    except Exception as e:
        print(f"Erro ao acessar o banco de dados: {str(e)}")
        return False
    finally:
        if cursor:
            cursor.close()
        if connect:
            bd_pool.putconn(connect)
            
            
def verificar_aniversario_conjuge(cpf):
    try:
        connect = bd_pool.getconn()
        cursor = connect.cursor()

        query = """
            SELECT cliente.nome, cliente.cpf, cliente.nome_conjuge, cliente.telefone 
            FROM cliente 
            JOIN funcionario on cliente.id_funcionario = funcionario.id_func
            WHERE TO_CHAR(data_aniver_conjuge, 'MM-DD') = %s AND funcionario.cpf = %s
        """
        cursor.execute(query, (data_hoje, cpf))
        clientes = cursor.fetchall()
        return clientes
    
    except Exception as e:
        print(f"Erro ao acessar o banco de dados: {str(e)}")
    finally:
        if cursor:
            cursor.close()
        if connect:
            bd_pool.putconn(connect)
            
            
def verificar_data_revisao(cpf):
    semana_depois = data + timedelta(weeks=1)
    semana_depoiss = semana_depois.strftime('%m-%d')
    try:
        connect = bd_pool.getconn()
        cursor = connect.cursor()
        query = """
            SELECT cliente.nome, cliente.cpf, cliente.revisoes_pendentes, cliente.data_ultima_revisao, cliente.telefone 
            FROM cliente 
            JOIN funcionario on cliente.id_funcionario = funcionario.id_func
            WHERE TO_CHAR(data_ultima_revisao, 'MM-DD') = %s AND revisoes_pendentes != 0 AND funcionario.cpf = %s
        """
        cursor.execute(query, (semana_depoiss, cpf))
        clientes = cursor.fetchall()
        return clientes
    
    except Exception as e:
        print(f"Erro ao acessar o banco de dados: {str(e)}")
    finally:
        if cursor:
            cursor.close()
        if connect:
            bd_pool.putconn(connect)
         
            
def verificar_ani_compra(cpf):
    data_ate3anos = data - relativedelta(years=3) 

    try:
        connect = bd_pool.getconn()
        cursor = connect.cursor()

        query = """
            SELECT cliente.nome, cliente.cpf, cliente.telefone, cliente.data_compra
            FROM cliente 
            JOIN funcionario ON cliente.id_funcionario = funcionario.id_func
            WHERE TO_CHAR(data_compra, 'MM-DD') = %s AND funcionario.cpf = %s
        """
        cursor.execute(query, (data_hoje, cpf))
        clientes = cursor.fetchall()

        clientes_filtrados = [
            cliente for cliente in clientes
            if cliente[3] >= data_ate3anos  
        ]
        return clientes_filtrados
    
    except Exception as e:
        print(f"Erro ao acessar o banco de dados: {str(e)}")
    finally:
        if cursor:
            cursor.close()
        if connect:
            bd_pool.putconn(connect)
            
def verificar_ani_casamento(cpf):
    try:
        connect = bd_pool.getconn()
        cursor = connect.cursor()

        query = """
            SELECT cliente.nome, cliente.cpf, cliente.telefone 
            FROM cliente 
            JOIN funcionario on cliente.id_funcionario = funcionario.id_func
            WHERE TO_CHAR(data_casamento, 'MM-DD') = %s AND funcionario.cpf = %s
        """
        cursor.execute(query, (data_hoje, cpf))
        clientes = cursor.fetchall()
        return clientes
    
    except Exception as e:
        print(f"Erro ao acessar o banco de dados: {str(e)}")
    finally:
        if cursor:
            cursor.close()
        if connect:
            bd_pool.putconn(connect)
    
    
if __name__ == "__main__":
    
    n1 = verificar_aniversario_cliente('714.134.802-68')
    n2 = verificar_aniversario_conjuge('714.134.802-68')
    n3 = verificar_ani_casamento('714.134.802-68')
    n4 = verificar_ani_compra('714.134.802-68')
    print(n1)
    print(n2)
    print(n3)
    print(n4)
