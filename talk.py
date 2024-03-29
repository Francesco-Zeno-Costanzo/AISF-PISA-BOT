"""
=============================================================================================================
Codice di supporto per il bot, contiene le risposte casuali e le domande dei quiz.
ATTENZIONE: La spiegazione dei quiz non deve superare la lunghezza di una riga altrimenti il codice da errore
e la domanda non viene visualizzata. Il codice è case sensitive quindi rispettare lo stile del quiz
=============================================================================================================
"""

#========================= SERIE DI RISPOSTE CASUALI, PRATICAMENTE TUTTE CIT =========================

L = ["Senti fra, anche meno", "A volte dorme più lo sveglio che il dormiente", "Prego prendi pure una cadrega",
     "Questa è una tua opinione e benchè comprovata da fatti rimane una tua opinione",
     "Non credi anche tu che ogni colore sia monocromatico a se stesso?", "Adoro l'odore del napalm al mattino",
     "Questo non creto", "Amico, te lo dico da amico, fatti li cazzi tua", "Impara a distaccarti da chi temi di perdere",
     "Danzi mai con il diavolo nel pallido plenilunio?", "Fare o non fare, non c'è provare", "No maria io esco",
     "La paura è la via per il Lato Oscuro. \nLa paura conduce all'ira, l'ira all'odio, l'odio conduce alla sofferenza. \nAh... Io sento in te molta paura",
     "Tu l'amore preferisci farlo sopra o sotto Trieste?", "Recuperati monster", "Sei in pari con One Piece?", "Te lo sei visto Pluto?",
     "Chi siete? cosa portate? Ma quanti siete? Un fiorino!", "Mio figlio poteva morire", "Potevo rimanere offeso",
     "E questo balletto racchiude in sè, diciamo tutti i quesiti che l'uomo si è fatto... \nC'è Dio? E se c'è, dov'è? E se dov'è, chi è? E se chi è, perchè? ... Eh?",
     "Nescio Rick mi videtur falso", "Queste rocce sono rocce", "Turnica e vieni giù ..., turnica e vieni giù ..., girati \nE DÌ GIRATI",
     "Mi hai fatto ridere ora torna nel gulag", "Perchè è questo che fano gli eroi", "The show must Honkong", "Piuttosto che perdere tempo a scrivere usa i comandi",
     "Senti mai quell'istinto mascolino di recitare poesie davanti alla corte d'assise?", "Quando ti laurei?", "Lui mi ha detto deh e allora io boia deh, capito?",
     "Lunga vita e prosperità", "Sarebbe bello vivere una favola", "Tu devi essere quello intelligente", "Forse siamo in ritardo, oggi è il 34 dicembre e il primo dell'anno non è ancora arrivato"
]

#========================= DOMANDE PER IL QUIZ =========================

QUIZ = {1:{"Quanto fa 1+1?":{"si":"0", "no1":"2"}, "spiegazione":"Salvetti spiega gli anelli"},
        2:{"Quanti cavalli ha un cavallo?":{"no1":"1", "no2":"42", "si":"12", "no3":"in che senso?"},
           "spiegazione":"Un cavalo può sviluppare circa 12 cavalli vapore di potenza"},
        3:{"Dove vive Dio?":{"no1":"paradiso", "si":"a Bruxelles", "no2":"certamente prima di Eboli", "no3":"vicino di casa di Colombini"},
           "spiegazione":"cit al film: Dio esiste e vive a Bruxelles"},
        4:{"Come hanno aggiustato uno dei giroscopi di Hubble?":{"si":"Spento e riacceso", "no1":"Sono andati lì con uno shuttle",
                                                                "no2":"Non ne hanno mai aggiustato nessuno", "no3":"Con la magia del natale"},
           "spiegazione":"Uno dei giroscopi di Hublle fu spento per via di malfunzionamenti, diverso tempo dopo fu riacesso e sorprendentemente funzionava"},
        5:{"Quale azienda collaborò alle missioni apollo sviluppando poi il primo telefonino?":{"no1":"Nokia", "no2":"Apple", "no3":"Samsung", "si":"Motorola"},
           "spiegazione":"Nel 1973 la Motorola creo il primo telefino e fece la prima chiamata intercontinentale, 4 anni prima Apollo 11 aveva appena allunato"},
        6:{"Di che colore era il cavallo bianco di napoleone?":{"si":"bianco", "no1":"giallo", "no2":"cachi", "no3":"magenta"},
           "spiegazione":"Bianco non era il nome del cavallo ma effettivamente il colore del suo manto"},
        7:{"Quale sistema operativo avete sul vostro computer?":{"si":"Linux based", "no1":"Windows", "no2":"MacOS"},
           "spiegazione":"https://wiki.archlinux.org/"},
        8:{"Quale ente inventò mouse e interfaccia desktop":{"no1":"Microsoft", "no2":"Apple", "si":"Xerox", "no3":"NASA"},
           "spiegazione":"I geni della Xerox non credettero che tali invenzioni fossero utili e quindi lasciano che Apple le copiasse"},
        9:{"Cosa porta alla nascita di GNU/Linux?":{"no1":"Per insegnare le basi degli OS", "si":"Una stampante Xerox", "no2":"La necessità di codice open source", "no3":"GNU: GNU is Not Unix"},
           "spiegazione":"Una piegazione la potete trovare qui: https://www.youtube.com/watch?v=VT4A4efdheo&ab_channel=morrolinux"},
       10:{"In fisica delle particelle che cos'è un campo":{"no1":"una particella", "no2":"dei numeri", "no3":"non lo so", "si":"una rappresentazione irriducibile del gruppo di Poincaré"},
           "spiegazione":"Il gruppo di Poincaré è il grupppo di simmetria della relatività ristretta e gli autovalori dell'operatore  di casimir sono legati a massa (m^2) e spin s(s+1)m^2"},
       11:{"Se un mattone pesa un kilo più mezzo mattone, quanto pesa il mattone?":{"si":"2 kg", "no1":"0.5 kg", "no2":"1.5 kg", "no3":"pi greco (numero puro)"},
           "spiegazione":"x = 1 + x/2"},
       12:{"Quanti pianeti ci sono nell'universo?":{"no1":"Circa uno a stella", "no2":"Troppo difficile da stimare", "si":"8", "no4":"4"},
           "spiegazione":"I pianeti sono solo quelli che orbitano intorno al sole, quindi solo 8. Siamo molto egocentrici"},
       13:{"Attorno a cosa orbitano i pianeti del sistema solare?":{"no1":"Terra", "no2":"Sole", "no3":"te", "si":"Nessuna delle precedenti"},
           "spiegazione":"Giustamente dipende dal sistema di riferimento. (P.S. Sole sarebbe comunque sbagliato, bisgna considerare il baricento, che grazie a Giove a volte è fuori dal Sole)"},
       14:{"Chi ha ideato inizialmente il meccanismo di Higgs":{"no1":"Landau", "si":"Philip W. Anderson", "no2":"Peter Higgs", "no3":"Alexander Polyakov"},
           "spiegazione":"Il primo articolo fu di Philip W. Anderson nel 1963 ma per una teoria non relativistica, l'anno dopo Higgs e altri in maniera indipendente lo generalizzarono"},
       15:{"Con quale sigla è più conosciuto il polivinilcloruro":{"si":"Cipolla", "no1":"pvc"},
           "spiegazione":"Questo non è un villaggio turistico e tu non fai ridere"},
       16:{"Cosa si intende con il termine cadrega":{"si":"Una sedia", "no1":"una mela", "no2":"delle posate", "no3":"la padania"},
           "spiegazione":"https://www.youtube.com/watch?v=SHEgE6cX4Vo"},
       17:{"Di che canzone si tratta?":{"no1":"Quale canzone?", "no2":"Non ho capito la domanda", "no3":"In che senso?", "si":"Dardue sandstorm"},
           "spiegazione":"Esiste sempre almeno un commento che alla risposta a tale domanda recita:Dardue sandstorm"},
       18:{"Chi è il dio cieco che gorgoglia e bestemmia al centro dell'Universo?":{"no1":"Cthulhu", "no2":"Andreotti", "si":"Azathoth", "no3":"Nyarlathotep"},
           "spiegazione":"Creatura creata da H.P. Lovecraft, signore di tutte le cose, demone sultano, il più antico e potente dgeli dei esterni"},
       19:{"Chi creo la bilancia con cui Anubi giudica i defunti?":{"no1":"Ra", "si":"Thot", "no2":"Anubi", "no3":"Osiride"},
           "spiegazione":"Thot, dio della luna, scriba di Ra, dio della conoscenza e delle scienze, per non avere problemi fecero costruire la bilancia la più capace, per un processo equo"},
       20:{"Giove stesso lo teme, treman di lui gli dei, orrore ne hanno i fiumi d'averno e i regni bui. Parliamo di:":{"si":"cupido", "no1":"Ade", "no2":"Crono", "no3":"Moire"},
           "spiegazione":"Sono le parole con cui l'oracolo parla di cupido (Amore) al padre di Psiche"},
       21:{"Chi è che: in mezzo a un fiume impetuoso bevendo patisce la sete?":{"si":"Un/una innamorato/a", "no1":"Un/una viandante", "no2":"I poeti", "no3":"Sisifo"},
           "spiegazione":"Andate a leggere: De rerum natura, IV, vv.1017-1103"},
       22:{"Come fanno i girasoli a seguire il sole?":{"no1":"Dei nani li spostano", "no2":"Non lo fanno", "si":"Grazie agli ormoni", "no3":"Con il vento"},
           "spiegazione":"https://www.science.org/doi/10.1126/science.aaf9793"}
}

#========================= FRASE DA DIRE PRIMA DELLA RISPETTIVA DOMANDA =========================

MSG_QUIZ = {1:"Questa è una cit, probabilmente non la saprete",
            2:"Te ne intendi di ippica?",
            3:"Testiamo un po' la tua cultura",
            4:"Vuoi una domanda eh? Vediamo se questa la sai",
            5:"Vediamo un po' di storia",
            6:"Non me ne vengono molte, proviamo questa, ma è facile",
            7:"Rifletti bene prima di rispondere",
            8:"Immagina il meme di Mr Bean che copia",
            9:"Cosa posso chiederti mhmm... proviamo questa",
           10:"Proviamo con qualcosa di difficile",
           11:"Dai un giochino matematico",
           12:"Ah voi umani..., siete esagerati",
           13:"Attenzione che sono bastardo e pignolo",
           14:"Oh guarda un fotono a preso massa",
           15:"Alti momenti della TV, devi saperla",
           16:"Prendi pure una cadrega...",
           17:"Spero che abbiate vissuto questi momenti",
           18:"Non è morto ciò che in eterno può attendere, e con il volgere di strani eoni anche la morte può morire",
           19:"Sei mai stato nella sala delle due Verità?",
           20:"Sapevate che Cratos è figlio della ninfa Stige?",
           21:"Un po' di letteratura fa sempre bene",
           22:"Vediamo se hai il pollice verde"
}
