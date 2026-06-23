#Nathan e Gus: criem um outro arquivo pro desktop. Deixem este aqui apenas para o bot.
#Helen: Ajusta este código para que a localização seja armazenada em um arquivo conforme a Bagatini informou. Acho que a melhor forma seria CSV.
# VOU TERMINAR DE COMENTA EM PUTRO MOMENTO, ESTOU ENVIANDO ASSIM PARA QUE POSSAM AGILIZAR NO RESTO.

import logging # Registra eventos 

# Update - atualiza o bot
# KeyboardButton - Criação do botão
# ReplyKeyboardMarkup - organiza os botões em um teclado personalizado
from telegram import Update, KeyboardButton, ReplyKeyboardMarkup 

# ApplicationBuilder - constrói/configura a aplicação principal do bot
# ContextTypes - define os tipos de contexto usados pelos handlers
# CommandHandler - associa um comando (ex: /start) a uma função 
from telegram.ext import ApplicationBuilder, ContextTypes, CommandHandler

logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO) 

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    botao_localizacao = KeyboardButton(text = "Pedir uma pizza", request_location = True)

    teclado = ReplyKeyboardMarkup([[botao_localizacao]], resize_keyboard = True, one_time_keyboard = True)
    await context.bot.send_message(chat_id=update.effective_chat.id, text="Para localizar a entrega mais próxima, toque no botão abaixo e envie sua localização atual.", reply_markup = teclado)

if __name__ == '__main__':
    aplicacao_bot = ApplicationBuilder().token('8988223495:AAEgC4U3o9HHoGkDVBRK9k-BtBP_UAsQw0g').build() #TOKEN
    
    start_handler = CommandHandler('start', start)
    aplicacao_bot.add_handler(start_handler)
    aplicacao_bot.run_polling()
