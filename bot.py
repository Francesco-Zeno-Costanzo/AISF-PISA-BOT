"""
Codice per il bot Pluto di AISF Pisa.
Le informazioni date dal comando /info devo essere caricate sul seguente foglio google:
........................................................................................

********************************************** ATTENZIONE **********************************************

A meno di non voler modificare il codice il foglio google DEVE essere così compilato:
________________________________________________________________________________________________________
 Carica 1           | Carica 2           | .... | Carica n           | Eventi   | Descrizione Eventi   |
--------------------|--------------------|------|--------------------|----------|----------------------|
 Infomazioni sulla  | Informazioni sulla |      | Informazioni sulla |          |                      |
 persona che occupa | persona che occupa | .... | persona che occupa | Evento 1 | Descrizione Evento 1 |
 Carica 1           | Carica 2           |      | Carica n           |          |                      |
--------------------|--------------------|------|--------------------|----------|----------------------|
                    |                    |      |                    | Evento 2 | Descrizione Evento 2 |
--------------------|--------------------|------|--------------------|----------|----------------------|
                    |                    |      |                    |    .     |           .          |
                    |                    |      |                    |    .     |           .          |
                    |                    |      |                    |    .     |           .          |
--------------------|--------------------|------|--------------------|----------|----------------------|
                    |                    |      |                    | Evento n | Descrizione Evento n |
--------------------------------------------------------------------------------------------------------

Per le risposte e il quiz vedere il file talk.py 
"""


import os
import random
import asyncio
import pandas as pd
from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update, Poll
from telegram.ext import Application, CallbackQueryHandler, CommandHandler, ContextTypes, ConversationHandler, MessageHandler, filters, PollHandler

import logging # Per verificare tutto vada bene
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')

from talk import L, QUIZ

# Link del foglio google dove sono le informazioni per essere letto come csv
googleSheetId = # id del google sheet
worksheetName = # nonme del google sheet
URL = f'https://docs.google.com/spreadsheets/d/{googleSheetId}/gviz/tq?tqx=out:csv&sheet={worksheetName}'

# Leturra del file
df = pd.read_csv(URL)

# Dimensioni tipiche di come è pensato il foglio google
N = len(df["Eventi"])             # Numero di eventi nella colonna eventi
K = df.columns.get_loc("Eventi")  # Numero di cariche del comitato

#==================================================================================================
# Comando start del bot
#==================================================================================================

async def start(update:Update, context:ContextTypes.DEFAULT_TYPE):
    '''
    Stampa il messaggio di benvenuto del bot quando viene eseguito /start
    '''
    description = "Ciao sono Pluto il bot del comitato locale AISF di PISA. \
    \nMi chiamo Pluto per il semplice fatto che il Generale ha iniziato a scrivermi subito dopo aver visto l'anime Pluto (consigliatissimo a proposito). \
    \nSe lo conoscete saprete che quello in foto non è Pluto, ma è molto figo come personaggio però non mi piaceva il nome, quindi è stata fatta una crasi. \
    \nAttualmente il mio scopo è darvi informazioni sul comitato e sugli eventi. Posso anche rispondervi a caso o farvi delle domande di cultura generale. \
    \n \
    \nPer il resto ricordatevi di santificare le feste."
    await context.bot.send_message(chat_id=update.effective_chat.id, text=description)

#==================================================================================================
# Comando info: informazioni sugli eventi e sul comitato
#==================================================================================================

async def info(update: Update, context: ContextTypes.DEFAULT_TYPE):
    '''
    Comando /info che crea bottoni tra cui scegliere
    '''
    # Creazione dei bottoni
    # keyboard deve essere una lista di liste, se in ogni lista interna
    # c'è solo un bottone tutti i bottoni sono sono in colonna, se una
    # lista interna contiene più bottoni, essi saranno stampati affianco
    keyboard = [
        [
            InlineKeyboardButton("Persone", callback_data='pers'),
            InlineKeyboardButton("Eventi",  callback_data='even'),
        ]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)

    # Messaggio del bot
    await update.message.reply_text("Cosa ti interessa?", reply_markup=reply_markup)

    # Mi trovo nello stato zero
    return 0


async def n_info(update: Update, context: ContextTypes.DEFAULT_TYPE):
    '''
    Funzione per tornare indietro da persone o eventi (i.e. tasto indietro)
    Così non c'è bisogno di creare un nuovo messaggio.
    '''
    # 
    query = update.callback_query
    await query.answer()

    # Creazione dei bottoni
    # keyboard deve essere una lista di liste, se in ogni lista interna
    # c'è solo un bottone tutti i bottoni sono sono in colonna, se una
    # lista interna contiene più bottoni, essi saranno stampati affianco
    keyboard = [
        [
            InlineKeyboardButton("Persone", callback_data='pers'),
            InlineKeyboardButton("Eventi",  callback_data='even'),
        ]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)

    # Messaggio del bot
    await query.edit_message_text("Cosa ti interessa?", reply_markup=reply_markup)

    # Mi trovo nello stato zero
    return 0

#*************************************************************************************************
#-------------------------------------------- PERSONE --------------------------------------------
#*************************************************************************************************

async def persone(update: Update, context: ContextTypes.DEFAULT_TYPE):
    '''
    Stampa come bottoni la lista delle cariche più il tatso indietro
    '''    
    query = update.callback_query
    await query.answer()

    # keyboard deve essere una lista di liste, se in ogni lista interna
    # c'è solo un bottone tutti i bottoni sono sono in colonna, se una
    # lista interna contiene più bottoni, essi saranno stampati affianco
    keyboard = []
    # Bottoni cariche
    for i in range(K):
        keyboard.append([InlineKeyboardButton(df.columns[i], callback_data=f'{i}')])
    # Bottone indietro
    keyboard.append([InlineKeyboardButton("Indietro", callback_data='indietro_p')])

    reply_markup = InlineKeyboardMarkup(keyboard)

    # Messaggio del bot
    await query.edit_message_text("Chi ti interesssa?", reply_markup=reply_markup)

    # Ora sono nello stato 1
    return 1


async def button_p(update: Update, context: ContextTypes.DEFAULT_TYPE):
    '''
    Dopo aver premuto un tasto generato dalla funzione persone, questa
    funzione stampa l'informazione desiderata e interrompe l'esecuzione del comando /info
    '''
    query = update.callback_query
    await query.answer()

    # Messaggio del bot
    await query.edit_message_text(text=df.columns[int(query.data)]+f": {df[df.columns[int(query.data)]][0]}")

    # Termino comando
    return ConversationHandler.END

#*************************************************************************************************
#-------------------------------------------- Eventi ---------------------------------------------
#*************************************************************************************************

async def eventi(update: Update, context: ContextTypes.DEFAULT_TYPE):
    '''
    Stampa come bottoni la lista degli eventi più il tatso indietro
    '''
    query = update.callback_query
    await query.answer()

    # keyboard deve essere una lista di liste, se in ogni lista interna
    # c'è solo un bottone tutti i bottoni sono sono in colonna, se una
    # lista interna contiene più bottoni, essi saranno stampati affianco
    keyboard = []
    # Bottoni eventi
    for i, j in zip(range(K,K+N), range(N)):
        keyboard.append([InlineKeyboardButton(df["Eventi"][j], callback_data=f'{i}')])
    # Bottone indietro
    keyboard.append([InlineKeyboardButton("Indietro", callback_data='indietro_e')])

    reply_markup = InlineKeyboardMarkup(keyboard)

    # Messaggio del bot
    await query.edit_message_text("A quale sei interessato?", reply_markup=reply_markup)

    # Ora sono nello stato 1
    return 1

  
async def button_e(update: Update, context: ContextTypes.DEFAULT_TYPE):
    '''
    Dopo aver premuto un tasto generato dalla funzione eventi, questa
    funzione stampa l'informazione desiderata e interrompe l'esecuzione del comando /info
    '''
    query = update.callback_query
    await query.answer()

    # Messaggio del bot
    await query.edit_message_text(text=df['Descrizione eventi'][int(query.data)-K])

    # Termino comando
    return ConversationHandler.END

#==================================================================================================
# Link dei matriali dei corsi
#==================================================================================================

async def corsi(update: Update, context: ContextTypes.DEFAULT_TYPE):
    '''
    Funzione per creare il comando /corsi creando i due bottoni
    '''
    # Creazione dei bottoni
    # keyboard deve essere una lista di liste, se in ogni lista interna
    # c'è solo un bottone tutti i bottoni sono sono in colonna, se una
    # lista interna contiene più bottoni, essi saranno stampati affianco
    keyboard = [
        [
            InlineKeyboardButton("Python", callback_data="py"),
            InlineKeyboardButton("Latex",  callback_data="tex"),
        ]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)

    # Messaggio del bot
    await update.message.reply_text("A quale corso sei interessato:", reply_markup=reply_markup)


async def button_c(update: Update, context: ContextTypes.DEFAULT_TYPE):
    '''
    Funzione per le informazioni sui corsi
    '''
    query = update.callback_query
    await query.answer()
    
    corso = {"py"  : "https://github.com/Francesco-Zeno-Costanzo/4BLP",
             "tex" : "Error 404"}

    # Messaggio del bot
    await query.edit_message_text(text=f"Il materiale è disponibile quì:\n{corso[query.data]}")

#==================================================================================================
# Quiz 
#==================================================================================================

async def quiz(update: Update, context: ContextTypes.DEFAULT_TYPE):
    '''
    Funzione per creare il quiz
    '''
    extract     = random.randint(1, len(QUIZ.keys()))                      # Estrazione causale di una domanda
    question, _ = QUIZ[extract].keys()                                     # Domanda da porre
    answers     = [a for a in QUIZ[extract][question].values()]            # Lista delle possibili risposte
    correct     = [r for r in QUIZ[extract][question].keys()].index("si")  # Indice della risposta giusta

    await update.effective_message.reply_poll(question, answers, type=Poll.QUIZ,
          correct_option_id=correct, explanation=QUIZ[extract]["spiegazione"] )

#==================================================================================================
# Risposte a caso a chi manda messaggi
#==================================================================================================

async def echo(update: Update, context: ContextTypes.DEFAULT_TYPE):
    '''
    Risponde ai messaggi con messaggi a caso
    '''
    #print(update.message.text)
    await update.message.reply_text(L[random.randint(0, len(L)-1)])

#==================================================================================================
# Main del bot
#==================================================================================================

def main():
    '''
    Main del bot, il bot viene creato e creati i commandi
    '''

    # Creo il bot vero e proprio
    application = Application.builder().token('METTERE IL VOSTRO TOKEN').build()

    # Creo il comando start
    application.add_handler(CommandHandler("start", start))  
    
    # Creo il comando info e ora qui è un po' convoluto
    # I return delle funzioni danno lo stato in cui siamo e ciò ci permette di gestire
    # la creazione dei sotto bottoni delle rispettivi classi. La sintassi del pattern
    # l'ho copiata dalla documentazion di python-telegra-bot (il pacchetto usato),
    # non so di preciso a cosa serva so solo che la stringa in mezzo deve
    # essere uguale al callback_data usato quando il bottone è stato creato 
    conv_handler = ConversationHandler(entry_points=[CommandHandler("info", info)],
        states={
            0: [
                CallbackQueryHandler(persone, pattern="^" + 'pers' + "$"),
                CallbackQueryHandler(eventi,  pattern="^" + 'even' + "$"),
            ],
            1: [
                *[CallbackQueryHandler(button_p, pattern="^" + f'{i}' + "$") for i in range(K)],
                *[CallbackQueryHandler(button_e, pattern="^" + f'{i}' + "$") for i in range(K,K+N)],
                CallbackQueryHandler(n_info, pattern="^" + 'indietro_p' + "$"),
                CallbackQueryHandler(n_info, pattern="^" + 'indietro_e' + "$"),
            ],
        },
        fallbacks=[CommandHandler("info", info)],
    )
    # Il fallbacks permette di avviare nuovamente /info prima che il comando abbia finito facendolo ripartire da capo 
    application.add_handler(conv_handler)

    # Creo il comando /corsi
    application.add_handler(CommandHandler("corsi", corsi))
    application.add_handler(CallbackQueryHandler(button_c))

    # Creo comando /quiz
    application.add_handler(CommandHandler("quiz", quiz))

    # Per le risposte ai messaggi
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, echo))

    # Eseguo il bot
    application.run_polling(allowed_updates=Update.ALL_TYPES)

if __name__ == "__main__":
    main()

