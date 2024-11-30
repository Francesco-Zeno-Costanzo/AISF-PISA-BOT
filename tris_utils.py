"""
Codice che contiene alcune funzioni ausiliari
per consentire al bot di giocare a tris
"""
from math import inf as infinity

# Variabili globali per gestire il gioco
Utente = -1
Engine = +1

CROSS_UNICODE  = "U0000274C"  # ❌
CIRCLE_UNICODE = "U00002B55"  # ⭕

CROSS  = chr(int(CROSS_UNICODE[1:], 16))
CIRCLE = chr(int(CIRCLE_UNICODE[1:], 16))



def computer_move(context):
    '''
    Gestisce la mossa del computer
    '''
    grid = context.user_data["grid"]  # Recupera la griglia dallo user_data
    if len(libero(grid)) == 0 or game_over(grid):
        return

    depth = len(libero(grid)) if context.user_data.get("difficulty") == "hard" else 1
    move  = minimax(grid, depth, Engine)

    x, y = move[0], move[1]
    grid[x][y] = Engine               # Aggiorna la griglia nello user_data
    context.user_data["grid"] = grid  # Salva la griglia aggiornata


def libero(stato):
    '''
    controlla le caselle libere

    Parametri
    ---------
    stato : list
        matrice del campo da gioco

    Return
    ---------
    celle : list
        lista delle coordinate delle celle vuote
    '''
    celle = []
    for x, riga in enumerate(stato):
        for y, cella in enumerate(riga):
            if cella == 0:
                celle.append([x, y])
    return celle


def game_over(stato):
    '''
    ritorna True se la partita è finita

    Parametri
    ---------
    stato : list
        matrice del campo da gioco

    Return
    ---------
    Bolean True se uno dei giocatori ha vinto False altrimenti
    '''
    return vittoria(stato, Utente) or vittoria(stato, Engine)


def minimax(stato, depth, giocatore, alpha=-infinity, beta=infinity):
    '''
    Algoritmo Minimax con Alpha-Beta Pruning

    Parametri
    ---------
    stato : list
        Matrice del campo da gioco
    depth : int
        Profondità, ovvero quante caselle libere ci sono
    giocatore : int
        Assume valori +1 (Engine) o -1 (Utente)
    alpha : float
        Il valore alpha per il pruning (miglior valore per il Max)
    beta : float
        Il valore beta per il pruning (miglior valore per il Min)

    Return
    ---------
    best : list
        Lista contenente [x, y, punteggio migliore]
    '''

    # Funzione massimizzante (Engine)
    def maxplayer(stato, depth, alpha, beta):
        best = [-1, -1, -infinity]

        # Controllo fine gioco
        if depth == 0 or game_over(stato):
            punteggio = punti(stato)
            return [-1, -1, punteggio]

        for cella in libero(stato):
            x, y = cella[0], cella[1]
            stato[x][y] = Engine
            punteggio = minplayer(stato, depth-1, alpha, beta)
            stato[x][y] = 0
            punteggio[0], punteggio[1] = x, y

            if punteggio[2] > best[2]:
                best = punteggio

            alpha = max(alpha, best[2])
            if beta <= alpha:
                break  # Pruning

        return best

    # Funzione minimizzante (Utente)
    def minplayer(stato, depth, alpha, beta):
        best = [-1, -1, +infinity]

        # Controllo fine gioco
        if depth == 0 or game_over(stato):
            punteggio = punti(stato)
            return [-1, -1, punteggio]

        for cella in libero(stato):
            x, y = cella[0], cella[1]
            stato[x][y] = Utente
            punteggio = maxplayer(stato, depth-1, alpha, beta)
            stato[x][y] = 0
            punteggio[0], punteggio[1] = x, y

            if punteggio[2] < best[2]:
                best = punteggio

            beta = min(beta, best[2])
            if beta <= alpha:
                break  # Pruning

        return best

    # Inizia con il giocatore corrente
    if giocatore == Engine:
        return maxplayer(stato, depth, alpha, beta)
    else:
        return minplayer(stato, depth, alpha, beta)


def vittoria(stato, giocatore):
    '''
    funzione che controlla chi ha vinto

    Parametri
    ---------
    stato : list
        matrice del campo da gioco
    giocatore : int
        assume valori +-1 a seconda di chi gioca

    Return
    ---------
    Bolean True se giocatore ha vinto False altrimenti
    '''
    #casistiche possibili
    stato_vincente = [
        [stato[0][0], stato[0][1], stato[0][2]],  #righe
        [stato[1][0], stato[1][1], stato[1][2]],
        [stato[2][0], stato[2][1], stato[2][2]],
        [stato[0][0], stato[1][0], stato[2][0]],  #colonne
        [stato[0][1], stato[1][1], stato[2][1]],
        [stato[0][2], stato[1][2], stato[2][2]],
        [stato[0][0], stato[1][1], stato[2][2]],  #diagonali
        [stato[2][0], stato[1][1], stato[0][2]],
    ]
    #controllo
    if [giocatore]*3 in stato_vincente:
        return True
    else:
        return False


def punti(stato):
    '''
    conteggio punti, necessario per minimax
    per vedre se le mosse del computer sono vincenti

    Parametri
    ---------
    stato : list
        matrice del campo da gioco

    Return
    ---------
    punteggio : int
        1 se il computer vinche, -1 se perde, 0 per pareggio
    '''
    if vittoria(stato, Engine):
        punteggio = +1
    elif vittoria(stato, Utente):
        punteggio = -1
    else:
        punteggio = 0

    return punteggio
