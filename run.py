"""
Codice per gestire il riavvio del bot
"""
import numpy as np
from subprocess import call

while True:
    
    # Leggo il messaggio lasciato dal bot
    n = np.loadtxt("start.txt", unpack=True)
    n = int(n)
    
    # Se è zero il bot è spento e va riaccesso
    if n == 0:
        
        # Cambio il testo per sapere che il bot è acceso
        f = open("start.txt", "w")
        f.write("1 \n")
        f.close()
        
        # Avvio il bot
        call("python3 bot.py", shell=True)
        # IL ciclo non riparte finchè il bot non viene nuovamente killato
    
    # Se è due il bot si deve spegnere totalmente
    if n == 2:
        print("Spegnimento")
        exit()
