import telebot
import re
from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.cron import CronTrigger
from dotenv import load_dotenv
import os
from assistente import assistente_geral, formatar_dados
from formatar import formatar_cpf
from verificacao import (
    verificar_aniversario_filho,
    verificar_aniversario_cliente,
    verificar_cpf_usuario,
    verificar_aniversario_conjuge,
    verificar_data_revisao,
    verificar_ani_compra,
    verificar_ani_casamento,
)

load_dotenv()
API_TELEGRAM_KEY = os.getenv("API_TELEGRAM_KEY")
bot = telebot.TeleBot(API_TELEGRAM_KEY)
session = {}
scheduler = BackgroundScheduler()

# === Funções Auxiliares ===
def get_session(chat_id): 
    return session.get(chat_id)

def validar_cpf(message):
    chat_id = message.chat.id
    sessao = get_session(chat_id)
    cpf = formatar_cpf(message.text.strip())
    result = verificar_cpf_usuario(cpf)
    if result:
        sessao["Nome"] = result[0].strip()
        sessao["cpf"] = cpf
        input_data = f"1 // session = {sessao}"
        bot.send_message(chat_id, assistente_geral(input_data))
    else:
        bot.send_message(chat_id, assistente_geral(f"0 // session = {sessao}"))
        bot.register_next_step_handler(message, validar_cpf)

def enviar_mensagens(chat_id):
    sessao = get_session(chat_id)
    cpf = sessao.get('cpf')

    if not cpf:
        bot.send_message(chat_id, "Erro: CPF não configurado. Clique em /start e informe seu CPF.")
        return

    verificacoes = [
        ("Clientes aniversariantes", verificar_aniversario_cliente),
        ("Filhos aniversariantes", verificar_aniversario_filho),
        ("Cônjuges aniversariantes", verificar_aniversario_conjuge),
        ("Revisões para próxima semana", verificar_data_revisao),
        ("Aniversário de Compra", verificar_ani_compra),
        ("Aniversário de Casamento", verificar_ani_casamento),
    ]

    resultados = {titulo: func(cpf) for titulo, func in verificacoes if func(cpf)}
    bot.send_message(chat_id, formatar_dados(str(resultados)) if resultados else "Hoje não há alertas.")

def iniciar_scheduler(chat_id):
    sessao = get_session(chat_id)
    horario = sessao.get('horario')
    if horario:
        hora, minuto = map(int, horario.split(':'))
        job = scheduler.add_job(
            tarefa_diaria, 
            trigger=CronTrigger(hour=hora, minute=minuto), 
            args=[chat_id],
            id=f"lembrete-{chat_id}"
        )
        sessao['IDagendamentoAlerta'] = job.id

def tarefa_diaria(chat_id):
    bot.send_message(chat_id, enviar_mensagens(chat_id))

def recebe_horario(message):
    chat_id = message.chat.id
    sessao = get_session(chat_id)
    user_input = message.text.strip()

    if re.match(r"^(?:[01]\d|2[0-3]):[0-5]\d$", user_input):
        sessao['horario'] = user_input
        iniciar_scheduler(chat_id)
        bot.send_message(chat_id, f"Horário definido como {user_input}. Para trocar de usuário, clique em /start.")
    else:
        bot.send_message(chat_id, "Formato inválido! Informe o horário no formato XX:XX.")
        bot.register_next_step_handler(message, recebe_horario)

# === Handlers do Bot ===
@bot.message_handler(commands=['start'])
def start(message):
    chat_id = message.chat.id
    if chat_id in session:
        if session[chat_id].get('IDagendamentoAlerta'):
            scheduler.remove_job(session[chat_id].get('IDagendamentoAlerta'))
        del session[chat_id]

    session[chat_id] = {'cpf': None, 'Nome': None, 'horario': None, 'IDagendamentoAlerta': None}
    bot.send_message(chat_id, "Por favor, informe seu CPF para começar.")
    bot.register_next_step_handler(message, validar_cpf)

@bot.message_handler(commands=['definirHorario'])
def definir_horario(message):
    bot.send_message(message.chat.id, "Informe o horário no formato XX:XX. Exemplo: '09:30'.")
    bot.register_next_step_handler(message, recebe_horario)

@bot.message_handler(func=lambda message: True)
def assistente_virtual(message):
    chat_id = message.chat.id
    sessao = get_session(chat_id)

    if sessao and sessao.get('cpf'):
        input_data = f"{message.text.strip()} // session = {sessao}"
        bot.send_message(chat_id, assistente_geral(input_data))
    else:
        bot.send_message(chat_id, "CPF não configurado. Clique em /start e informe seu CPF.")

# === Inicialização ===
if __name__ == "__main__":
    try:
        scheduler.start()
        bot.polling(none_stop=True)
    except Exception as e:
        print(f"Erro no bot: {e}")
