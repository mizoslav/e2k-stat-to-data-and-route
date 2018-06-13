##############################################################################
# prevod.py     prevod súborov STAT
##############################################################################

import re
import sys
import datetime 

##############################################################################
# Definicia funkcie ROZBI, zabezpeci vratenie
# potrebnych poloziek pre jeden let ako pole
##############################################################################
def rozbi(pole):
    let = re.split(" ", pole[0])                            #STAT, ID, OPER/STANDBY, CAS
    c = pole[1].find("/")
    let.append(pole[1][:c])                                 #CALLSIGN
    let.append(pole[1][c+1:c+2])                            #mod odpovedaca
    let.append(pole[1][c+2:c+6])                            #kod odpovedaca
    c = pole[1][-2:]
    
    let.append(c[:1])                                       #pravidla letu 
    let.append(c[-1:])                                      #typ letu
    let.append(pole[2][0])                                  #pocet lietadiel
    c = pole[2].find("/")
    let.append(pole[2][1:c])                                 #Typ lietadla
    let.append(pole[2][-1:])                                #Turbulencia v uplave
    c = pole[3].find("/")
    let.append(pole[3][:c])                                 #vybavenie
    let.append(pole[3][c+1:])                                #vybavenie na sledovanie
    let.append(pole[4][4:])                                 #REG
    let.append(pole[5][4:])                                 #OPR
    let.append(pole[6][4:])                                 #STS
    let.append(pole[7][4:])                                 #RMK
    let.append(pole[8][:4])                                 #ADEP
    let.append(pole[8][4:6]+":"+pole[8][6:8])               #DEP time
    if pole[8][-4:] == " ???":
        let.append("")
    else:
        let.append(pole[8][-2:])                            #ADEP RWY
    let = let + re.split(" ", pole[9])                      #ENTRY POINT
    c = let[22]
    del let[22]
    let.append(c[:2]+":"+c[2:])                             #dopln dvojbodku do casu
    let.append(pole[10][1:5])                               #RQ SPEED
    let. append(pole[10][6:])                               #RFL
    let.append(pole[11][:4])                                #ADES
    let.append(pole[11][4:6]+":"+pole[11][6:8])             #ARR time
    if pole[11][-4:] == " ???":
        let.append("")
    else:
        let.append(pole[11][-3:].strip())                   #ARR RWY

    let = let + re.split(" ", pole[12])                     #Exit POINT a Exit TIME
    c = let[29]
    del let[29]
    let.append(c[:2]+":"+c[2:])                             # dopln dvojbodku do casu

    let = let + re.split(" ", pole[13])                     # rozbi route na jednotlive polozky
    
    let.append(pole[14][:len(pole[14])-1])                  # dopln pocet preletenych km
                                               
    
    del let[0]                                              # vymaze "STAT"

    for i in range(0,29):                                   # v tomto cykle
        if len(let[i]) > 0:                                 # sa vsetky polozky
            if let[i][0] == "?":                            # ktore obsahuju znak ?
                let[i] = ""                                 # nahradia prazdnym retazcom
            
    return let


##############################################################################
# Definicia funkcie SPRACUJ_SUBOR, zabezpeci nacitanie dat zo suboru
# do pola vety. 
##############################################################################

def spracuj_subor(meno_suboru):

    try:
        with open(meno_suboru, "r") as subor:                   # Ak existuje subor
            subor = open(meno_suboru, "r")                      # otvor  subor
            
    except FileNotFoundError:
        print("*** Neda sa otvorit subor : ", meno_suboru)      # Ak sa subor neda otvorit vypis chybu
        return
    
    j = 0
    pocet_viet = 0                                              # pocet_viet je pocet extrahovanych viet
    zaznam = []
    pocet_chyb = 0

    for riadok in subor:                                        # pre kazdy riadok suboru
        if ")" in riadok:
            if len(zaznam) == 14:                               # ak bol extrahovany spravny pocet riadkov
                zaznam.append(riadok.strip())                   # pridaj riadok do pola 
                lety.append(rozbi(zaznam))                      # zapis polozky letu do pola lety
                pocet_viet += 1
            else:
                print("Neuplny zaznam letu cislo ", pocet_viet," riadok ", zaznam)
                pocet_chyb += 1
                
            j = 0
            zaznam = []
            continue

        if "(STAT" in riadok:                                   # Ak obsahuje riadok uvedeny retazec
            if len(zaznam) > 0:                                 # zisti, ci predchazajuci let bol kompletny
                print("Neuplny zaznam letu cislo ", pocet_viet," riadok ", zaznam)
                pocet_chyb += 1                                 # Ak nebol, vypis chybu
                j = 1                                           # a zacni spracovavat novy let
                zaznam = []
                zaznam.append(riadok.strip())
                continue
            if riadok[0] != "(":                                # Ak sa riadok nezacina znakov "("
                pomst = riadok[riadok.find("("):]               # najdi ho v retazci
                zaznam.append(pomst.strip())                    # a vloz ako prvy zaznam
                continue
                
            
        if len(riadok.strip()) != "":                           # Ak riadok nie je prazdny
            zaznam.append(riadok.strip())                       # zapis si ho
            j += 1
                

    if len(zaznam) > 0 and len(zaznam[0]) > 0:                                        # Ak posledny zaznam nie je prazdny
        print("Neuplny zaznam letu cislo ", pocet_viet," riadok ", zaznam)
        pocet_chyb += 1
   
    subor.close()                                               #zatvor subor
    print("Pocet letov v subore ", meno_suboru," je ", pocet_viet)
    print("Pocet chybnych zaznamov v subore je ", pocet_chyb)
    
##############################################################################
# Definicia funkcie ZAPIS_VETU, zabezpeci zapis zaznamu o jednom lete
# do exportneho suboru data
##############################################################################

def zapis_let(datum, cislo, veta, subor_d, subor_r):

    zaznam = datum+"|"                                   #zapis datum spracovavaneho dna
    zaznam += str(cislo)+"|"                              #zapis poradove cislo exportovaneho letu

    for i in range(3, 29):                                #zapis udaje o lete do suboru dataddmmrr
        try:
            zaznam += veta[i]+"|"
        except ValueError:
            print("\n!!!  Chyba pri zapise vety", cislo, "do suboru", subor_d.name)
            return

    try:
        zaznam += " "+veta[len(veta)-1]+"|"
    except ValueError:
        print("\n!!!  Chyba pri zapise vety", cislo, "do suboru", subor_d.name)
        return
        
    zaznam += "\n"

    subor_d.write(zaznam)
    
    el = 0
    
    for i in range(29, len(veta)-1):
        try:
            zaznam = str(cislo)+"|"                           #zapis poradove cislo exportovaneho letu
            zaznam += str(el)+"|"                             #zapis poradove cislo route elementu       
            a,b,c = re.split("/", veta[i])
        except ValueError:
            print("\n!!!  Chyba pri zapise vety", cislo, "do suboru", subor_r.name)
            continue
        
        zaznam += a+"|"                                   # zapis bod
        zaznam += b[-3:]+"|"                               # zapis FL
        zaznam += c[:2]+":"+c[2:]+"|"+"\n"                # zapis cas

        subor_r.write(zaznam)

        el += 1                                           # inkrementuj element trate
        
        
        

##############################################################################
# Definicia funkcie VYTLAC_HELP, zabezpeci vypis pomoci
##############################################################################

def vytlac_help():
    print("Program PREVOD.PY\n")
    print("Spustenie bez argumentu znamena spracovanie dat predchadzajuceho dna.")
    print("Spustenie s argumentom YYMMDD   znamena spracovanie dat za den DD.MM.20YY")
    print("Vstupny subor musi mat meno \"STATDDMMYY.brfdp_a\" alebo \"STATDDMMYY.brfdp_b\"")
    exit(0)


##############################################################################
# Vlastne telo programu
##############################################################################

print("Spustenie ",sys.argv)

pocet_viet = 0                                              # "pocet_viet" je pocet extrahovanych viet
lety = []                                                   # inicializacia pola "lety", ktora bude obsahovat zaznamy o letoch
cislo_vety = 0

if len(sys.argv) > 2:                                       # Ak pocet argumentov je viac ako 1
    vytlac_help()                                           # daj napovedu a skonci

if len(sys.argv) == 2:                                      # Ak pocet argumentov je 1
    ret = sys.argv[1].strip()
    if len(ret) != 6:                                       # ak pocet jeho znakov je iny ako 6
        vytlac_help()                                       # daj napovedu a skonci
                                                            # inak vytvor nazvy suborov
    in_subor_a = "STAT"+ret[-2:]+ret[2:4]+ret[:2]+".brfdp_a-B"
    in_subor_b = "STAT"+ret[-2:]+ret[2:4]+ret[:2]+".brfdp_b-B"
    report_date = ret[4:7] + ret[2:4] + ret[:2]             # datum reportu urob do tvaru DDMMYY

if len(sys.argv) == 1:                                      # Ak nebol ziadny argument urci vcerajsi den
    yesterday = datetime.date.fromordinal(datetime.date.today().toordinal()-1)
    report_date = ('' if len(str(yesterday.day)) == 2 else '0') + str(yesterday.day)+ \
                  ('' if len(str(yesterday.month)) == 2 else '0') + str(yesterday.month) + \
                  str(yesterday.year)[-2:]
    in_subor_a = "STAT"+report_date+".brfdp_a-B"              # vytvor nazvy suborov
    in_subor_b = "STAT"+report_date+".brfdp_b-B"

"""
report_date = "100418"
ret = report_date[4:7] + report_date[2:4] + report_date[:2]
in_subor_a = "STAT"+report_date+".brfdp_a-B"
in_subor_b = "STAT"+report_date+".brfdp_b-B"
"""

ret = report_date[4:7] + report_date[2:4] + report_date[:2]
datum = report_date[:2]+ "." + report_date[2:4] + ".20" + report_date[4:7]

print("Spracovavany den:  ", datum)

spracuj_subor(in_subor_a)
spracuj_subor(in_subor_b)

if len(lety) == 0:
    print("Nulovy pocet zaznamov !!! Koniec programu")
    exit()

i = 0

out_subor_data  = "data"  + ret + "N"
out_subor_route = "route" + ret + "N"

try:
    with open(out_subor_data, "w") as subor_data:           # Skus otvorit subor dataddmmyy na zapis
        subor_data = open(out_subor_data, "w")              # otvor  subor dataddmmyy

except (OSError, FileNotFoundError, TypeError) :
    print("*** Neda sa otvorit subor : ", out_subor_data)   # Ak sa subor neda otvorit vypis chybu
    exit()
    
try:
    with open(out_subor_route, "w") as subor_route:         # Skus otvorit subor routeddmmyy na zapis
        subor_route = open(out_subor_route, "w")            # otvor  subor routeddmmyy

except (OSError, FileNotFoundError, TypeError) :
    print("*** Neda sa otvorit subor : ", out_subor_route)  # Ak sa subor neda otvorit vypis chybu
    exit()

z_callsign = []
z_id = []

for veta in lety:                                           # urob export zaznamov OPERATIONAL
    if lety[i][1] == "OPERATIONAL":
        zapis_let(datum, cislo_vety, lety[i], subor_data, subor_route)
        cislo_vety += 1
        z_callsign.append(lety[i][3])
        z_id.append( int(lety[i][0] ))
#        print(vety[i][3], end=" ")
    i += 1

i = 0
for veta in lety:                                           # urobi export z chybajucich zaznamov v STAND_BY
    if lety[i][1] == "STAND_BY":
        if lety[i][3] in z_callsign:
            if lety[i][0] in z_id:
                pass
        else:
            zapis_let(datum, cislo_vety, lety[i], subor_data, subor_route)
            cislo_vety += 1
    i += 1

print("Celkovy pocet exportovanych letov je ", cislo_vety)
            
subor_data.close()
subor_route.close()











          
