"""
Codice per associare un secure hash ad ogni mail per maggiore sicurezza
Il bot farà il confronto con l'hash piuttosto che con le mail stesse
"""
import hashlib
import pandas as pd
import secret


# Link del foglio google dove sono le informazioni per essere letto come csv
GoogleSheetId = secret.GoogleSheetId_mail
absolut_Path = secret.Path
WorkSheetName = secret.WorkSheetName_mail
URL = f'https://docs.google.com/spreadsheets/d/{GoogleSheetId}/gviz/tq?tqx=out:csv&sheet={WorkSheetName}'

# Leturra del file
df   = pd.read_csv(URL)
mail = df["MAIL"]
file_mail   = absolut_Path + "mail.txt"

# Calcolo sha256 e salvo sul file
with open(file_mail, "w") as f:
    for m in mail:
        ms = m.split()[0].lower()
        m_sha = hashlib.sha256(ms.encode('utf-8')).hexdigest()
        f.write(m_sha + "\n")
