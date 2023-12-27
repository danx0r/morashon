import sys, os

filename = sys.argv[1]

adjust = float(sys.argv[2])

j = filename.rfind(".")

gz = filename[:j] + ".gz"

cmd = f"cp {filename} {gz}"
print (cmd)
os.system(cmd)

cmd = f"gzip -c -d {gz} > __temp__.xml"
print (cmd)
os.system(cmd)

f = open("__temp__.xml")
fout = open(filename, 'w')

for row in f.readlines():
    if row.strip()[:6] == "<tempo":
        parts = (row.split())
        bph = float(parts[2].split("=")[1].replace('"', "")) * adjust
        tempo = float(parts[3].split("=")[1].replace("/>", "").replace('"', "")) * adjust
#        print (bph, tempo)
        parts[2] = f'bph="{int(bph)}"'
        parts[3] = f'tempo="{int(tempo)}"'
        if len(parts)==4:
            parts[3] += "/>"
        recon = "  " + " ".join(parts)
        print(recon)
        fout.write(recon+"\n")
    else:
        fout.write(row)
fout.close()
f.close()
