from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.cron import CronTrigger
import telebot
from dotenv import load_dotenv
import os

from verificacao import (
    verificar_aniversario_filho,
    verificar_aniversario_cliente,
    verificar_cpf_usuario,
    verificar_aniversario_conjuge,
    verificar_data_revisao,
    verificar_ani_compra,
    verificar_ani_casamento,
)
from formatar import (
    formatar_clientes,
    formatar_cpf,
    formatar_filhos,
    formatar_conjuge,
    format_revisoes,
    format_data_compra,
    format_data_casamento,
)

load_dotenv()
API_TELEGRAM_KEY = os.getenv("API_TELEGRAM_KEY")
bot = telebot.TeleBot(API_TELEGRAM_KEY)
sessoes = {} 
scheduler = BackgroundScheduler()


# === Funções Auxiliares ===
def obter_sessao(chat_id): 
    return sessoes[chat_id]


def enviar_mensagens(chat_id):
    sessao = obter_sessao(chat_id)
    cpf = sessao['cpf']

    if not cpf:
        bot.send_message(chat_id, "Erro: CPF não configurado. Clique em /start e informe seu CPF.")
        return

    verificacoes = [
        ("Clientes aniversariantes", verificar_aniversario_cliente, formatar_clientes),
        ("Filhos aniversariantes", verificar_aniversario_filho, formatar_filhos),
        ("Cônjuges aniversariantes", verificar_aniversario_conjuge, formatar_conjuge),
        ("Revisões para próxima semana", verificar_data_revisao, format_revisoes),
        ("Aniversário de Compra", verificar_ani_compra, format_data_compra),
        ("Aniversário de Casamento", verificar_ani_casamento, format_data_casamento),
    ]
    alertas = []

    for titulo, func_verificar, func_formatar in verificacoes:
        resultados = func_verificar(cpf)
        if resultados:
            alertas.append(f"{titulo}:\n{func_formatar(resultados)}")

    if alertas:
        instrucoes = """
            Para interromper a verificação:
/finishVerificacao 
Para redefinir o horário:
/definirHorario
Para trocar de usuário:
/start
"""
        
        for alerta in alertas:
            bot.send_message(chat_id, alerta)
        bot.send_message(chat_id, instrucoes)
    else:
        bot.send_message(chat_id, "Nenhuma alerta para enviar no momento.")


# === Handlers do Bot ===
@bot.message_handler(commands=['start'])
def start(message):
    chat_id = message.chat.id
    if chat_id in sessoes:
        sessao = obter_sessao(chat_id)
        id = sessao['agendamento']
        scheduler.remove_job(id)
        del sessoes[chat_id]
    
    sessoes[chat_id] = {'cpf': None, 'horario': None, 'esperandoHorario': False, 'agendamento': None}  
    bot.send_message(chat_id, "Por favor, informe seu CPF para começar.")


@bot.message_handler(commands=['startVerificacao'])
def start_verificacao(message):
    chat_id = message.chat.id
    sessao = obter_sessao(chat_id)
    horario = sessao['horario'] 

    if not sessao['cpf']:
        bot.send_message(chat_id, "Por favor, informe seu CPF com /start antes de começar.")
        return

    if horario:
        hora, minuto = map(int, horario.split(':'))
        agendamento = scheduler.add_job(
            tarefa_diaria, 
            trigger=CronTrigger(hour=hora, minute=minuto), 
            args=[chat_id],
            id=f"lembrete-{chat_id}" 
        )
        sessao['agendamento'] = agendamento.id
        bot.send_message(chat_id, "Verificação iniciada!")
    else:
        bot.send_message(chat_id, "Defina o horário primeiro com /definirHorario.")


@bot.message_handler(commands=['finishVerificacao'])
def finish_verificacao(message):
    chat_id = message.chat.id
    if chat_id not in sessoes:
        bot.send_message(chat_id, "Clique em /start para começar uma nova sessão.")
    sessao = obter_sessao(chat_id)
    id = sessao['agendamento']
    if id:
        scheduler.remove_job(id)
        sessao['agendamento'] = None
        bot.send_message(chat_id, """
                Verificação interrompida. 
Para reiniciar a verificação:
/startVerificacao
Para redefinir o horário:
/definirHorario
Para trocar de usuário:
/start
    """)
    else:
        bot.send_message(chat_id, "Não há verificação em andamento.")

@bot.message_handler(commands=['definirHorario'])
def definir_Horario(message):
    chat_id = message.chat.id
    sessao = obter_sessao(chat_id)
    sessao['esperandoHorario'] = True
    bot.send_message(chat_id, "Informe no formato XX:XX. Exemplo '09:30'")

@bot.message_handler(func=lambda message: obter_sessao(message.chat.id).get('esperandoHorario', False))
def recebe_Horario(message):
    chat_id = message.chat.id
    sessao = obter_sessao(chat_id)
    user_input = message.text.strip()

    import re
    if re.match(r"^(?:[01]\d|2[0-3]):[0-5]\d$", user_input):
        sessao['horario'] = user_input
        sessao['esperandoHorario'] = False  
        bot.send_message(chat_id, f"Horário definido como {user_input}.")
        bot.send_message(chat_id, """
            Para começar a verificação:
/startVerificacao
Para interromper a verificação:
/finishVerificacao
Para redefinir o horário:
/definirHorario
Para trocar de usuário:
/start
        """)
    else:
        bot.send_message(chat_id, "Formato inválido! Por favor, informe o horário no formato XX:XX.")   

@bot.message_handler(func=lambda message: True)
def validar_cpf(message):
    chat_id = message.chat.id
    sessao = obter_sessao(chat_id)
    cpf = message.text.strip()
    if len(cpf) == 11:
        cpf = formatar_cpf(cpf)
    if verificar_cpf_usuario(cpf):
        sessao['cpf'] = cpf
        bot.send_message(chat_id, f"Bem-vindo, CPF {cpf} validado!")
        bot.send_message(chat_id, "Defina o horário que deseja receber os alertas /definirHorario")
    else:
        bot.reply_to(message, "CPF não encontrado. Por favor, tente novamente.")

def tarefa_diaria(chat_id):
    sessao = obter_sessao(chat_id)
    id = sessao['agendamento']
    if id:
        enviar_mensagens(chat_id)


if __name__ == "__main__":
    try:
        scheduler.start()
        bot.polling(none_stop=True, interval=1, timeout=20, long_polling_timeout=20)
    except Exception as e:
        print(f"Erro no bot.polling: {e}")

