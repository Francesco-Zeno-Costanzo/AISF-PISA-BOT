"""
Codice per il bot Pluto di AISF Pisa.
Le informazioni date dal comando  /info devo essere caricate su un foglio google:

********************************************** ATTENZIONE **********************************************

A meno di non voler modificare il codice il foglio google DEVE essere così compilato:
___________________________________________________________________________________________________________________________________
 Carica 1           | Carica 2           | .... | Carica k           | Eventi   | Descrizione Eventi   |  Corsi  | Link Materiale |
--------------------|--------------------|------|--------------------|----------|----------------------|---------|----------------|
 Infomazioni sulla  | Informazioni sulla |      | Informazioni sulla |          |                      |         |                |
 persona che occupa | persona che occupa | .... | persona che occupa | Evento 1 | Descrizione Evento 1 | Corso 1 | Link materiale |
 Carica 1           | Carica 2           |      | Carica k           |          |                      |         |  del corso 1   |
--------------------|--------------------|------|--------------------|----------|----------------------|---------|----------------|
                    |                    |      |                    | Evento 2 | Descrizione Evento 2 | Corso 2 | Link materiale |
                    |                    |      |                    |          |                      |         | del corso 2    |
--------------------|--------------------|------|--------------------|----------|----------------------|---------|----------------|
                    |                    |      |                    |    .     |           .          |    .    |        .       |
                    |                    |      |                    |    .     |           .          |---------|----------------|
                    |                    |      |                    |    .     |           .          | Corso m | Link materiale |
                    |                    |      |                    |          |                      |         | del corso m    |
--------------------|--------------------|------|--------------------|----------|----------------------|---------|----------------|
                    |                    |      |                    | Evento n | Descrizione Evento n |         |                |
-----------------------------------------------------------------------------------------------------------------------------------

########################################################################################################

Se un utente invia un messaggio al bot, il bot risponderà a caso con frasi scelte da un pool in talk.py.
Esistono però dei messaggi "con privilegi di amministratore"; ovvero messaggi che iniziano con una
password, che il bot riconosce e permettere di compiere un certo numero di azioni:

1) Il presidente o chi autorizzato può inoltrare un messaggio a tutti gli utenti.
   Per farlo basta mandare un messaggio normalissimo al bot e lui lo reindirizzerà a tutti gli altri utenti di
   cui il bot conosce il chat_id (per farlo sapere al bot l'utente deve semplicemente avviare il bot).
   Il messaggio deve avere però la seguente forma e.g:

   password_1
   Salve a tutti il bot rimarrà inattivo per qualche ora per manutenzione

   Dove password_1 è una password e il testo sottostante sarà quello inoltrato.

2) Spegnere e riaccendere il bot. Per far si che il bot si accorga dei cambiamenti del google sheet è
   necessario che il bot lo legga di nuovo. Esiste quindi una password che spegne il bot scrivendo su
   un file. Appena il bot termina parte un secondo codice che legge il file per vedere se effettivamente
   il bot è spento e lo riaccende. Per far funzionare tutto vanno lanciati i due codici insieme:

   ~$ python3 bot.py && python3 run.py

3) Aprire le prenotazioni per un evento. La prenotazzione consiste in un codice di 4 cifre composto da
   un carattere speciale iniziale e un numero a tre cifre. Per aprire le prenotazioni è necessario 
   mandare un messaggio del tipo:

   passwd_prenotazioni
   numero posti disponibili
   carattere speciale
   
   Per stoppare o chiudere le prenotazioni si usa un altra password e i messagi sono del tipo:
   
   passwd
   stop
   
   oppure:
   
   passwd
   chiuso

4) In caso sia il google sheet contenete le mail a cambiare (aggiunta o rimozione di mail), bisogna
   anche sta volta riavviare il bot facendo però partire il codice che calcola gli hash delle mail
   aggiornate. Questo si fa con un signolo messaggio contenete unicamente la password assocciata.

########################################################################################################

Per le risposte e il quiz vedere il file talk.py 
"""

# stdlib
import os
import re
import hashlib
import logging
import datetime
from subprocess import call

# pacchetti
import random
import numpy as np
import pandas as pd
import wikipediaapi
from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update, Poll
from telegram.ext import Application, CallbackQueryHandler, CommandHandler, ContextTypes, ConversationHandler, MessageHandler, filters

# nostri codici
import secret
from talk import L, QUIZ, MSG_QUIZ


# Per verificare tutto vada bene
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')

#**************************************************************************************************
# Funzione per calcolare il secure hash della mail
SHA = lambda m: hashlib.sha256(m.encode('utf-8')).hexdigest()

#**************************************************************************************************

# Link del foglio google dove sono le informazioni per essere letto come csv
GoogleSheetId = secret.GoogleSheetId_info
WorkSheetName = secret.WorkSheetName_info
URL = f'https://docs.google.com/spreadsheets/d/{GoogleSheetId}/gviz/tq?tqx=out:csv&sheet={WorkSheetName}'

# Leturra del file
df = pd.read_csv(URL)

# Dimensioni tipiche di come è pensato il foglio google
N = len(df["Eventi"])             # Numero di eventi nella colonna eventi
K = df.columns.get_loc("Eventi")  # Numero di cariche del comitato
M = len(df["Corsi"])              # Numero di corsi nella colonna corsi

#**************************************************************************************************

absolut_Path = secret.Path

# File per conservare gli id di chiunque avvii il bot, in modo da mandare un messaggio a tutti gli utenti
file_all_id = absolut_Path + "id.txt"
# File per sapere se il bot si è spento
file_start  = absolut_Path + "start.txt"
# File per le prenotazioni agli eventi
file_prenot = absolut_Path + "prenotazioni.txt"
# File con le mail
file_mail   = absolut_Path + "mail.txt"
with open(file_mail, "r", encoding="utf-8") as file_mail:
    mail = file_mail.read().split()

# Leggo il file con tutti gli id
all_id = np.loadtxt(file_all_id, unpack=True, dtype=int)

# Potrebbero esserci dei doppioni dato che l'id viene salvato ad ogni chiamata di /start
all_id = np.unique(all_id)

# Riaggiorno il file con solo gli id diversi
with open(file_all_id, "w", encoding="utf-8") as file_id:
    for c_id in all_id:
        file_id.write(f"{c_id} \n")


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
    with open(file_all_id, "a", encoding="utf-8") as file_id: # permesso di append per non perdere i precedenti
        file_id.write(f"{chat_id} \n")
    
    if not chat_id in all_id:
        all_id = np.append(all_id, chat_id)

#==================================================================================================
# Comando info: informazioni sugli eventi e sul comitato
#==================================================================================================

async def info(update:Update, context:ContextTypes.DEFAULT_TYPE):
    '''
    Comando /info che crea bottoni tra cui scegliere
    '''

    ep = "U0001F465"
    ev = "U0001F387"

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
 
    query = update.callback_query
    await query.answer()

    ep = "U0001F465"
    ev = "U0001F387"

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
    e = "U0002B05"
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
    e = "U0002B05"
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

    ep = "U0001F9EE"
    el = "U0001F4DC"
    ev = [ep, el] # emoji prima python poi latex

    # Creazione dei bottoni
    # keyboard deve essere una lista di liste, se in ogni lista interna
    # c'è solo un bottone tutti i bottoni sono sono in colonna, se una
    # lista interna contiene più bottoni, essi saranno stampati affianco
    keyboard = []
    # Bottoni eventi
    for i, emoji in zip(range(M), ev):
        keyboard.append([InlineKeyboardButton(chr(int(emoji[1:], 16)) + " " + df["Corsi"][i], callback_data=f'{i}')])

    reply_markup = InlineKeyboardMarkup(keyboard)

    # Messaggio del bot
    await update.message.reply_text("A quale corso sei interessato:", reply_markup=reply_markup)


async def button_c(update:Update, context:ContextTypes.DEFAULT_TYPE):
    '''
    Funzione per le informazioni sui corsi
    '''
    query = update.callback_query
    await query.answer()

    # Messaggio del bot
    await query.edit_message_text(text="Il materiale è disponibile qui:\n" + df['Link Materiale'][int(query.data)])

#==================================================================================================
# Quiz 
#==================================================================================================

async def quiz(update:Update, context:ContextTypes.DEFAULT_TYPE):
    '''
    Funzione per creare il quiz
    '''
    extract     = random.randint(1, len(QUIZ.keys()))               # Estrazione causale di una domanda
    question, _ = QUIZ[extract].keys()                              # Domanda da porre
    answers     = list(QUIZ[extract][question].values())            # Lista delle possibili risposte
    correct     = list(QUIZ[extract][question].keys()).index("si")  # Indice della risposta giusta
    
    # Frase che il bot dice prima di porre la domanda
    await context.bot.send_message(chat_id=update.effective_chat.id, text=MSG_QUIZ[extract])

    # Domanda del quiz
    await update.effective_message.reply_poll(question, answers, type=Poll.QUIZ,
          correct_option_id=correct, explanation=QUIZ[extract]["spiegazione"])

#==================================================================================================
# Prenotazioni 
#==================================================================================================

async def prenotazioni(update:Update, context:ContextTypes.DEFAULT_TYPE):
    '''
    Funzione che spiega come funzionano le prenotazioni
    '''

    with open(file_prenot, "r", encoding="utf-8") as file_p:
        All = file_p.read().split()

    if All[0] == "nope":
        info = "Attualmente comunque non ci sono eventi per cui preonotarsi"
    else :
        NP = int(All[0])          # numero posti totali
        NO = (len(All) - 2) // 2  # numero posti prenotati
        info = f"Di {NP} posti totali ne rimangono {int(NP-NO)} disponibili"

    description = f"Vuoi prenotarti eh? Dammi la mail con cui ti sei iscritto ad AISF, grazie. \
                   \nPer piacere scrivi solo la mail e fai attenzione agli spazi prima e dopo. \
                   \nSe la sbagli mi indispongo e ti risponderò a caso. \
                   \n{info}"

    chat_id = update.effective_chat.id
    await context.bot.send_message(chat_id=chat_id, text=description)

#==================================================================================================
# Eventi storici a caso da wikipedia
#==================================================================================================

async def eventi_storici(update:Update, context:ContextTypes.DEFAULT_TYPE):
    '''
    Funzione che restituisce un evento storico avvenuto nello stesso giorno
    '''

    def read_page(date):
        '''
        Funzione per leggere una pagina di wikipedia

        Parameter
        ---------
        date : string
            titolo della pagina, per i nostri scopi sarà una data

        Return
        ------
        string
            contenuto della pagina
        '''
        wiki = wikipediaapi.Wikipedia(
            user_agent='https://meta.wikimedia.org/wiki/User-Agent_policy',
            language='it')
        page = wiki.page(date)

        if page.exists():
            # Controlla se la pagina esiste
            return page.text

        else:
            return "Nessuna pagina trovata"


    def parse_wikipedia_page(wikipedia_text):
        '''
        Funzione per riorganizzare il testo di wikipedia
        in modo da selezionare un solo evento

        Parameter
        ---------
        wikipedia_text : string
            contenuto della pagina di wikipedia

        Return
        ------
        events : list
            lista degli eventi
        '''

        # Pattern per estrarre eventi, nati, morti e feste e ricorrenze,
        # a noi interessano solo gli eventi ma per generalità si fa così

        event_pattern       = r'Eventi\n(.*?)\n\nNati'
        #born_pattern        = r'Nati\n(.*?)\n\nMorti'
        #death_pattern       = r'Morti\n(.*?)\n\nFeste e ricorrenze'
        #celebration_pattern = r'Feste e ricorrenze\n(.*?)\n\nNote'

        # Voglio tutto quello tra Eventi e Nati,
        # poi tutto quello tra Nati e Morti, et cetera

        # Estraggo e riodino le informazioni
        events       = re.findall(event_pattern,       wikipedia_text, re.DOTALL)[0].strip().split('\n')
        #born         = re.findall(born_pattern,        wikipedia_text, re.DOTALL)[0].strip().split('\n')
        #deaths       = re.findall(death_pattern,       wikipedia_text, re.DOTALL)[0].strip().split('\n')
        #celebrations = re.findall(celebration_pattern, wikipedia_text, re.DOTALL)[0].strip().split('\n')


        return events

    months = {1:'gennaio', 2:'febbraio', 3:'marzo', 4:'aprile',
              5:'maggio', 6:'giugno', 7:'luglio', 8:'agosto',
              9:'settembre', 10:'ottobre', 11:'novembre', 12:'dicembre'}

    date = datetime.date.today().strftime("%d/%m/%y")
    mth  = int(date[3:5])
    day  = int(date[0:2])

    chat_id = update.effective_chat.id

    event_info = read_page(f'{day}_{months[mth]}')

    if event_info == "Nessuna pagina trovata":

        description = "Non trovo niente, sembra sia stata una gionata tranquilla"
        await context.bot.send_message(chat_id=chat_id, text=description)

    else:

        parsed_data = parse_wikipedia_page(event_info)

        description = f"Ooh... ecco qua: {parsed_data[random.randint(0, len(parsed_data)-1)]}"
        await context.bot.send_message(chat_id=chat_id, text=description)

#==================================================================================================
# Risposte a caso a chi manda messaggi
#==================================================================================================

async def echo(update:Update, context:ContextTypes.DEFAULT_TYPE):
    '''
    Funzione che gesitisce i messagi dell'utente e alcune funzioni
    '''
    # update.message.text è il messaggio iviato dall'utente

    # Se i primi caratteri di un messaggio sono quelli in passwd_msg significa che chi manda il messaggio
    # vuole inviare un messaggio a tutti gli utenti del bot per mandare qualche avviso,
    # ad esempio magari chi mantiene il codice vuole avvisare che sarà offline per qualche tempo.
    # Se invece il meaaggio è solamente passwd_on_off il bot si spegnerà e riaccenderà.
    # Se invece il meaaggio è solamente passwd_off il bot si spegnerà.
    # Le altre due aprono e chiudono/cancellano le prenotazioni per gli eventi.
    # Se invece si usa passwd_update il codice che calcola l'hash di tutte le mail viene chiamato e il bot riavviato'
    
    passwd_msg    = secret.passwd_msg
    passwd_on_off = secret.passwd_on_off
    passwd_off    = secret.passwd_off
    passwd_prenot = secret.passwd_prenot
    passwd_nopre  = secret.passwd_nopre
    passwd_update = secret.passwd_update

    n             = len(passwd_msg)
    inviati       = 0               # numero di messaggi inviati
    non_inv       = 0               # numero di messaggi non inviati

    root = update.effective_chat.id # id di chi manda il messaggio

    #######################################################################################################

    if update.message.text[:n] == passwd_msg:

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

    #######################################################################################################

    # Per riavviare il bot
    elif update.message.text == passwd_on_off:
        # Scrivo su file un messaggio di spegnimento
        with open(file_start, "w", encoding="utf-8") as file_off:
            file_off.write(f"{0} \n")
        
        # uccido questo specifico processo grazie al suo id
        call(f"kill {os.getpid()}", shell=True)

    #######################################################################################################

    # Per Spegnere il bot
    elif update.message.text == passwd_off:
        # Scrivo su file un messaggio di spegnimento
        with open(file_start, "w", encoding="utf-8") as file_off:
            file_off.write(f"{2} \n")

        # uccido questo specifico processo grazie al suo id
        call(f"kill {os.getpid()}", shell=True)

    #######################################################################################################

    # Per creare i codici che aprono le prenotazioni
    elif update.message.text[:n] == passwd_prenot:
        # numero di posti da prenotare e carattere speciale
        n_posti, sc =  update.message.text[n:].split()
        n_posti = int(n_posti)

        # Scrivo su file le informazioni di apertura
        with open(file_prenot, "w", encoding="utf-8") as file_p:
            file_p.write(f"{n_posti}\n{sc}\n")

        msg = "Prenotazioni aperte correttamente"
        await context.bot.send_message(chat_id=str(root), text=msg)

    #######################################################################################################

    # Per stoppare le prenotazioni dopo un evento, per evitare che chi si può penotrare
    # non si trovi bloccato dalle prenotazioni dell'evento precedente
    elif update.message.text[:n] == passwd_nopre:

        # Calcellare le prenotazioni
        if update.message.text[n+1:].lower() == "cancella":
            # Scrivo su file un messaggio di stop
            with open(file_prenot, "w", encoding="utf-8") as file_p:
                file_p.write("nope\n")

            msg = "Prenotazioni cancellate correttamente"
            await context.bot.send_message(chat_id=str(root), text=msg)

        # Stoppare le prenotazioni
        if update.message.text[n+1:].lower() == "chiuso":

            with open(file_prenot, "a", encoding="utf-8") as file_p:
                file_p.write("chiuso")

            msg = "Prenotazioni chiuse correttamente"
            await context.bot.send_message(chat_id=str(root), text=msg)

    #######################################################################################################

    # Bisogna fornire al bot le nuove mail, cioè i nuovi hash
    elif update.message.text[:n] == passwd_update:

        old_n_mail = len(mail) # numero attuale di mail

        # Aggiungo le hash nuove al file
        call("python3 /home/BOT/AISF-PISA-BOT/SHA.py", shell=True)

        with open(file_mail, "r", encoding="utf-8") as file_mail:
            mail_N = file_mail.read().split()
        
            new_n_mail = len(mail_N)

            msg = f"Prima il numero di mail era {old_n_mail}, adesso è {new_n_mail}"
            await context.bot.send_message(chat_id=str(root), text=msg)

        # Poi devo riavviare il bot
        with open(file_start, "w", encoding="utf-8") as file_off:
            file_off.write(f"{0} \n")

        # uccido questo specifico processo grazie al suo id
        call(f"kill {os.getpid()}", shell=True)

    #######################################################################################################

    # Gestione vera e propria delle prenotazioni
    elif SHA(update.message.text.lower()) in mail:
        # Apro il file per controllare che si possa ancora prenotare
        with open(file_prenot, "r", encoding="utf-8") as file_p:
            All = file_p.read().split()

        chat_id = update.effective_chat.id

        # Se sul file ci sta scritto "nope" non è ancora possibile prenotarsi
        if All[0] == "nope":
            description = "Ciao teso mi spiace ma non è ancora possibile prenotarsi"
            await context.bot.send_message(chat_id=chat_id, text=description)
        
        # Se l'id è gia memorizzato vuol dire che ti sei già prenotato
        elif str(chat_id) in All:
            description = "Ciao teso ma ti sei già prenotato"
            await context.bot.send_message(chat_id=chat_id, text=description)
        
        elif All[-1] == "chiuso":
            description = "Ciao teso ma le prenotazioni sono chiuse"
            await context.bot.send_message(chat_id=chat_id, text=description)

        else :

            NP  = int(All[0])          # numero posti totali
            SC  = All[1]               # carattere speciale
            NO  = (len(All) - 2) // 2  # numero posti prenotati

            # Se il numero è arrivato al massimo le iscrizioni si chiudono
            if NO == NP:
                description = "Ciao teso mi spiace ma non è più possibile prenotarsi. I posti sono esauriti"
                await context.bot.send_message(chat_id=chat_id, text=description)

            # Creazione del codice di prenotazione
            else :
                tmp = random.randint(100, 999) # estarggo numero casuale

                while SC+str(tmp) in All:
                    tmp = random.randint(100, 999)

                with open(file_prenot, "a", encoding="utf-8") as file_p:
                    file_p.write(f"{SC}{tmp}\n{chat_id}\n")

                description = f"Ciao teso ecco il tuo codice di prenotazione: {SC}{tmp} \
                                \nmi raccomando non dirlo a nessunno potresti incorrere nell'ira di Achille."
                await context.bot.send_message(chat_id=chat_id, text=description)

    #######################################################################################################

    # Se il messaggio è lungo 4 potrebbe essere un codice di prenotazione
    elif len(update.message.text) == 4:
        
        chat_id = update.effective_chat.id
        # leggo tutti i codici
        with open(file_prenot, "r", encoding="utf-8") as file_p:
            All = file_p.read().split()
        
        # Se è dentro tutto bene
        if update.message.text in All:
            description = "Il codice corrisponde c'è una prenotazione"
            await context.bot.send_message(chat_id=chat_id, text=description)
        
        # Se il primo carattere corrisponde ma il resto no
        elif not update.message.text in All and not update.message.text.isalpha():
            description = "Non trovo una corrispondenza, attento in caso a scrivere bene il codice"
            await context.bot.send_message(chat_id=chat_id, text=description)
        
        # In caso non fosse un codice di prenotazione
        else :
            # rispondo a caso
            await update.message.reply_text(L[random.randint(0, len(L)-1)])

    #######################################################################################################

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
    application = Application.builder().token(secret.TOKEN).build()

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

    # Creo il comando per le prenotazioni
    application.add_handler(CommandHandler("prenotami", prenotazioni))

    # Creo il comando per le ricorrenze storiche
    application.add_handler(CommandHandler("eventi_storici", eventi_storici))

    # Eseguo il bot
    application.run_polling(allowed_updates=Update.ALL_TYPES)

if __name__ == "__main__":
    main()

