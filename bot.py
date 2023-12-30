"""
Codice per il bot Pluto di AISF Pisa.
Le informazioni date dal comando  /info devo essere caricate sul seguente foglio google:
-----------------vostro link giusto per sapre dove stanno le cose----------------------

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

Inoltre è possibile da parte del presidente o da chi autorizzato inoltrare un messaggio a tutti gli utenti.
Per farlo basta mandare un messaggio normalissimo al bot e lui lo reindirizzerà a tutti gli altri utenti di
cui il bot conosce il chat_id (per farlo sapere al bot l'utente deve semplicemente avviare il bot).
Il messaggio deve avere però la seguente forma e.g:

passwd
Salve a tutti il bot rimarrà inattivo per qualche ora per manutenzione

Dove passwd è una password e il testo sottostante sarà quello inoltrato.

Per le risposte e il quiz vedere il file talk.py 
"""


import os
import random
import asyncio
import logging
import numpy as np
import pandas as pd
from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update, Poll
from telegram.ext import Application, CallbackQueryHandler, CommandHandler, ContextTypes, ConversationHandler, MessageHandler, filters, PollHandler
from talk import L, QUIZ, MSG_QUIZ

# Per verificare tutto vada bene
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')

#**************************************************************************************************

# Link del foglio google dove sono le informazioni per essere letto come csv
googleSheetId = # Id del foglio google
worksheetName = # nome del foglio google
URL = f'https://docs.google.com/spreadsheets/d/{googleSheetId}/gviz/tq?tqx=out:csv&sheet={worksheetName}'

# Leturra del file
df = pd.read_csv(URL)

# Dimensioni tipiche di come è pensato il foglio google
N = len(df["Eventi"])             # Numero di eventi nella colonna eventi
K = df.columns.get_loc("Eventi")  # Numero di cariche del comitato

#**************************************************************************************************

# File per conservare gli id di chiunque avvii il bot, in modo da mandare un messaggio a tutti gli utenti
file_all_id = "id.txt"

# Leggo il file con tutti gli id
all_id = np.loadtxt(file_all_id, unpack=True, dtype=int)

# Potrebbero esserci dei doppioni dato che l'id viene salvato ad ogni chiamata di /start
all_id = np.unique(all_id)

# Riaggiorno il file con solo gli id diversi
file_id = open(file_all_id, "w")
for c_id in all_id:
    file_id.write(f"{c_id} \n")
file_id.close()

#==================================================================================================
# Comando start del bot
#==================================================================================================

async def start(update:Update, context:ContextTypes.DEFAULT_TYPE):
    '''
    Stampa il messaggio di benvenuto del bot quando viene eseguito /start
    '''
    global all_id
    
    description = "Ciao sono Pluto il bot del comitato locale AISF di PISA. \
    \nMi chiamo Pluto per il semplice fatto che il Generale ha iniziato a scrivermi subito dopo aver visto l'anime Pluto (consigliatissimo a proposito). \
    \nSe lo conoscete saprete che quello in foto non è Pluto, ma è molto figo come personaggio però non mi piaceva il nome, quindi è stata fatta una crasi. \
    \nAttualmente il mio scopo è darvi informazioni sul comitato e sugli eventi. Posso anche rispondervi a caso o farvi delle domande di cultura generale. \
    \n \
    \nPer il resto ricordatevi di santificare le feste."
    chat_id = update.effective_chat.id
    await context.bot.send_message(chat_id=chat_id, text=description)
    
    # Conservo l'id della persona per avere la possibilità di mandare messaggi a tutti
    file_id = open(file_all_id, "a") # permesso di append per non perdere i precedenti
    file_id.write(f"{chat_id} \n")
    file_id.close()
    if not chat_id in all_id:
         all_id = np.append(all_id, chat_id)

#==================================================================================================
# Comando info: informazioni sugli eventi e sul comitato
#==================================================================================================

async def info(update:Update, context:ContextTypes.DEFAULT_TYPE):
    '''
    Comando /info che crea bottoni tra cui scegliere
    '''
    
    ep = "U0001F465" # emoji persone
    ev = "U0001F387" # emoji eventi (fuochi d'artificio)
    
    # Creazione dei bottoni
    # keyboard deve essere una lista di liste, se in ogni lista interna
    # c'è solo un bottone tutti i bottoni sono sono in colonna, se una
    # lista interna contiene più bottoni, essi saranno stampati affianco
    keyboard = [
        [
            InlineKeyboardButton(chr(int(ep[1:], 16))+" Persone", callback_data='pers'),
            InlineKeyboardButton(chr(int(ev[1:], 16))+" Eventi",  callback_data='even'),
        ]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)

    # Messaggio del bot
    await update.message.reply_text("Cosa ti interessa?", reply_markup=reply_markup)

    # Mi trovo nello stato zero
    return 0


async def n_info(update:Update, context:ContextTypes.DEFAULT_TYPE):
    '''
    Funzione per tornare indietro da persone o eventi (i.e. tasto indietro)
    Così non c'è bisogno di creare un nuovo messaggio.
    '''
    # 
    query = update.callback_query
    await query.answer()
    
    ep = "U0001F465" # emoji persone
    ev = "U0001F387" # emoji eventi (fuochi d'artificio)
    
    # Creazione dei bottoni
    # keyboard deve essere una lista di liste, se in ogni lista interna
    # c'è solo un bottone tutti i bottoni sono sono in colonna, se una
    # lista interna contiene più bottoni, essi saranno stampati affianco
    keyboard = [
        [
            InlineKeyboardButton(chr(int(ep[1:], 16))+" Persone", callback_data='pers'),
            InlineKeyboardButton(chr(int(ev[1:], 16))+" Eventi",  callback_data='even'),
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

async def persone(update:Update, context:ContextTypes.DEFAULT_TYPE):
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
    e = "U0002B05" # emoji freccia indietro
    keyboard.append([InlineKeyboardButton(chr(int(e[1:], 16))+" Indietro", callback_data='indietro_p')])

    reply_markup = InlineKeyboardMarkup(keyboard)

    # Messaggio del bot
    await query.edit_message_text("Chi ti interesssa?", reply_markup=reply_markup)

    # Ora sono nello stato 1
    return 1


async def button_p(update:Update, context:ContextTypes.DEFAULT_TYPE):
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

async def eventi(update:Update, context:ContextTypes.DEFAULT_TYPE):
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
    e = "U0002B05" # emoji freccia indietro
    keyboard.append([InlineKeyboardButton(chr(int(e[1:], 16))+" Indietro", callback_data='indietro_p')])

    reply_markup = InlineKeyboardMarkup(keyboard)

    # Messaggio del bot
    await query.edit_message_text("A quale sei interessato?", reply_markup=reply_markup)

    # Ora sono nello stato 1
    return 1

  
async def button_e(update:Update, context:ContextTypes.DEFAULT_TYPE):
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

async def corsi(update:Update, context:ContextTypes.DEFAULT_TYPE):
    '''
    Funzione per creare il comando /corsi creando i due bottoni
    '''
    
    ep = "U0001F9EE" # emoji abaco
    el = "U0001F4DC" # emoji pergamena
    
    # Creazione dei bottoni
    # keyboard deve essere una lista di liste, se in ogni lista interna
    # c'è solo un bottone tutti i bottoni sono sono in colonna, se una
    # lista interna contiene più bottoni, essi saranno stampati affianco
    keyboard = [
        [
            InlineKeyboardButton(chr(int(ep[1:], 16))+" Python", callback_data="py"),
            InlineKeyboardButton(chr(int(el[1:], 16))+" Latex",  callback_data="tex"),
        ]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)

    # Messaggio del bot
    await update.message.reply_text("A quale corso sei interessato:", reply_markup=reply_markup)


async def button_c(update:Update, context:ContextTypes.DEFAULT_TYPE):
    '''
    Funzione per le informazioni sui corsi
    '''
    query = update.callback_query
    await query.answer()
    
    corso = {"py"  : "https://github.com/Francesco-Zeno-Costanzo/4BLP",
             "tex" : "Error 404"}

    # Messaggio del bot
    await query.edit_message_text(text=f"Il materiale è disponibile qui:\n{corso[query.data]}")

#==================================================================================================
# Quiz 
#==================================================================================================

async def quiz(update:Update, context:ContextTypes.DEFAULT_TYPE):
    '''
    Funzione per creare il quiz
    '''
    extract     = random.randint(1, len(QUIZ.keys()))                      # Estrazione causale di una domanda
    question, _ = QUIZ[extract].keys()                                     # Domanda da porre
    answers     = [a for a in QUIZ[extract][question].values()]            # Lista delle possibili risposte
    correct     = [r for r in QUIZ[extract][question].keys()].index("si")  # Indice della risposta giusta
    
    # Frase che il bot dice prima di porre la domanda
    await context.bot.send_message(chat_id=update.effective_chat.id, text=MSG_QUIZ[extract])

    # Domanda del quiz
    await update.effective_message.reply_poll(question, answers, type=Poll.QUIZ,
          correct_option_id=correct, explanation=QUIZ[extract]["spiegazione"] )

#==================================================================================================
# Risposte a caso a chi manda messaggi
#==================================================================================================

async def echo(update:Update, context:ContextTypes.DEFAULT_TYPE):
    '''
    Funzione per inoltrare messaggi a tutti gli utenti o per rispondere a caso
    '''
    # update.message.text è il messaggio iviato dall'utente

    # Se i primi caratteri di un messaggio sono quelli in passwd significa che chi manda il messaggio
    # vuole inviare un messaggio a tutti gli utenti del bot per mandare qualche avviso,
    # ad esempio magari chi mantiene il codice vuole avvisare che sarà offline per qualche tempo
    passwd  = "vostra password"
    n       = len(passwd)
    inviati = 0                      # numero di messaggi inviati
    non_inv = 0                      # numero di messaggi non inviati
    
    if update.message.text[:n] == passwd :
        
        root = update.effective_chat.id # id di chi manda il messaggio
        
        for c_id in all_id:
            # Ciclo su tutti fuorchè su chi vuole mandare il messaggio
            if c_id != root:
            
                try :
                    await context.bot.send_message(chat_id=str(c_id), text=update.message.text[n:])
                    inviati += 1 # Aggiorno numero di messaggi inviati
                    
                except :
                    non_inv += 1 # Aggiorno numero di messaggi non inviati
                    continue
        
        # Mando un messaggio di resoconto a chi ha inviato il messaggio 
        msg = f"messaggio inviato correttamente a {inviati} untenti, con {non_inv} eccezioni"
        await context.bot.send_message(chat_id=str(root), text=msg)
    
    else:
        # altrimenti rispondo a caso
        await update.message.reply_text(L[random.randint(0, len(L)-1)])

#==================================================================================================
# Main del bot
#==================================================================================================

def main():
    '''
    Main del bot, il bot viene creato e creati i commandi
    '''

    # Creo il bot vero e proprio
    application = Application.builder().token('vostro token').build()

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

    # Per le risposte ai messaggi o per l'inoltro
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, echo))

    # Eseguo il bot
    application.run_polling(allowed_updates=Update.ALL_TYPES)

if __name__ == "__main__":
    main()

