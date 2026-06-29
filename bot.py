#Nathan e Gus: criem um outro arquivo pro desktop. Deixem este aqui apenas para o bot.
#Helen: Ajusta este código para que a localização seja armazenada em um arquivo conforme a Bagatini informou. Acho que a melhor forma seria CSV.
# VOU TERMINAR DE COMENTA EM PUTRO MOMENTO, ESTOU ENVIANDO ASSIM PARA QUE POSSAM AGILIZAR NO RESTO.

import logging # Registra eventos 
import csv # Biblioteca usada para criar e manipular csv
import os #Para manipular os arquivos
import subprocess # Usado para abrir o programa desktop como um processo separado
import sys # Para pegar o caminho do interpretador python em uso

# Update - atualiza o bot
# KeyboardButton - Criação do botão
# ReplyKeyboardMarkup - organiza os botões em um teclado personalizado
from telegram import Update, KeyboardButton, ReplyKeyboardMarkup 

# ApplicationBuilder - constrói/configura a aplicação principal do bot
# ContextTypes - define os tipos de contexto usados pelos handlers
# CommandHandler - associa um comando a uma função 
from telegram.ext import ApplicationBuilder, ContextTypes, CommandHandler, MessageHandler, filters

logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO) 

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    # Cria o botão que, quando tocado, pede ao Telegram a localização do usuário
    botao_localizacao = KeyboardButton(text = "Pedir uma pizza", request_location = True)
    
    # Monta o teclado personalizado com o botão acima.
    # resize_keyboard ajusta o tamanho do teclado pra ficar mais compacto
    # one_time_keyboard faz o teclado desaparecer depois de usado uma vez
    teclado = ReplyKeyboardMarkup([[botao_localizacao]], resize_keyboard = True, one_time_keyboard = True)

    # Envia a mensagem de boas-vindas pro usuário, junto com o teclado/botão criado acima   
    await context.bot.send_message(chat_id=update.effective_chat.id, text="Para localizar a entrega mais próxima, toque no botão abaixo e envie sua localização atual.", reply_markup = teclado)

#Essa função recebe e salva a localização enviada
async def receber_localizacoes(update:Update, context: ContextTypes. DEFAULT_TYPE):
    latitude = update.message.location.latitude #pega a latitude
    longitude = update.message.location.longitude #pega a longitude
    print(latitude)
    print(longitude)

    arquivo_existe = os.path.exists("dados.csv")#verificar

#abre ou cria o arquivo csv para salvar os dados dos usuários
    with open("dados.csv", "a", newline="", encoding="utf-8") as arquivo: 
        escreve = csv.writer(arquivo)#vai criar o escritor csv

        if not arquivo_existe: #evitar que o cabeçalho repita toda vez que salva
            escreve.writerow(["Nome","Sobrenome","Latitude", "Longitude"])
        escreve.writerow([update.effective_user.first_name, update.effective_user.last_name, latitude, longitude]) #salva dados: nome,sobrenome,latitude e longitude
    
    # envia uma mensagem enviando a confirmação do recebimento das informações
    await context.bot.send_message(
        chat_id= update.effective_chat.id,
        text="Localização recebida! Já estamos calculando a entrega mais próxima 🍕"
    )
if __name__ == '__main__':
    # Abre o painel desktop em outro processo, antes de iniciar o bot.
    # Usamos subprocess (e não thread) porque o tkinter precisa rodar
    # na sua própria thread principal — assim ele não trava nem é
    # travado pelo loop assíncrono do bot.
    pasta_atual = os.path.dirname(os.path.abspath(__file__))
    caminho_desktop = os.path.join(pasta_atual, 'desktop.py')
    subprocess.Popen([sys.executable, caminho_desktop])

    aplicacao_bot = ApplicationBuilder().token('8988223495:AAEgC4U3o9HHoGkDVBRK9k-BtBP_UAsQw0g').build() #TOKEN
    
    start_handler = CommandHandler('start', start)

    localizacao_handler = MessageHandler( filters.LOCATION, receber_localizacoes)#resgistra o handler para mensagens de localização
    aplicacao_bot.add_handler(start_handler)
    aplicacao_bot.add_handler(localizacao_handler)
    aplicacao_bot.run_polling()
