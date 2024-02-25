f = open("AISF.txt", "r")
text = f.read().split()
f.close()
g = open("mail.txt", "w")
for m in text:
    mail = m[:-2]
    g.write(f"{mail.lower()}\n")
g.close()
