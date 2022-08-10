import os
import json
from getpass import getpass
from termcolor import colored as col


def start():

    print(col("\n*****************************","green"))
    print(col("** INIZIO PROGRAMMA BACKUP **","green"))
    print(col("*****************************\n","green"))

    try:
        leggiParams()
    except:
        print(col("Errore lettura parametri. Abort", "red"))
        return -1

    if checkConnPI() == -1: return -1
    PASSW = readPsw()

    cart = selezioneCartelle()
    if len(cart) < 1:
        print(col("Nessuna cartella selezionata per il backup. Fine","yellow"))
        return 1
    shut = getShutdown()

    print(col("\nRiepilogo:", "cyan"))
    print(col("* Backup di:", "cyan"))
    for c in cart:
        os.system("du -sh "+c)

    print(col("* Backup salvato in "+SAVEFOLDER+"", "cyan"))
    print(col("* SCP to "+IP_SSH+"", "cyan"))
    print(col("* Spegnimento al termine? " +("yes" if shut == 1 else "no")+ "\n", "cyan"))

    inp = input(col("Procedere? [y/n] ", "cyan"))
    if inp != "y" and inp != "Y":
        print(col("Abort", "orange"))
        return 1

    #COMPRESSIONE E INVIO
    err = 0
    for c in cart:
        nomeCompr = SAVEFOLDER+"/"+c.split("/")[-1]+".tar.bz2"
        res = os.system("tar -I \"pbzip2 -p4\" -cvf "+nomeCompr+" "+c)
        if res != 0:
            print(col("\nERRORE compressione "+nomeCompr+" non riuscita. Abort","red"))
            err = 1
            break
        print("\n*** COMPRESSIONE COMPLETATA ***\n\n")

        res = os.system("sshpass -p '"+PASSW+"' scp -v "+nomeCompr+" "+USER_SSH+"@"+IP_SSH+":"+FOLDER_SSH)
        if res != 0:
            print(col("\nERRORE invio file "+c.split("/")[-1]+".tar.bz2 via ssh. Abort","red"))
            err=1
            break
        os.system("rm "+nomeCompr)

    if(err == 0):
        print(col("\n\n******************************", "green"))
        print(col("***    BACKUP TERMINATO    ***", "green"))
        print(col("******************************\n", "green"))
        if shut == 1:
            print("Procedo con lo spegnimento...")
            os.system("sleep 5")
            os.system("shutdown now")
    else:
        print(col("\n\n*******************************", "red"))
        print(col("!!!!    ERRORI RILEVATI    !!!!", "red"))
        print(col("*******************************\n", "red"))
        return 1


#TODO renderlo più parlabile. Per ora dice solo "Errore lettura parametri"
def leggiParams(): #throw Exception

    global IP_SSH
    global USER_SSH
    global FOLDER_SSH
    global SAVEFOLDER
    global FOLDERS
    global LOG_FOLDER

    f = open('params.json')

    data = json.load(f)

    for d in data["params"]:
        # if d == s:
        if d == "folder_to_backup":
            FOLDERS     = data["params"]["folder_to_backup"]
        if d == "tmp_store_folder":
            SAVEFOLDER  = data["params"]["tmp_store_folder"]
        if d == "ssh":
            IP_SSH      = data["params"]["ssh"]["ip"]
            USER_SSH    = data["params"]["ssh"]["user"]
            FOLDER_SSH  = data["params"]["ssh"]["folder"]
        if d == "log_folder":
            LOG_FOLDER  = data["params"]["log_folder"]

def readPsw():
    return getpass("Inserire password ssh: ")


def checkConnPI():
    print("Controllo connessione con PI...")
    ping = os.system("ping -c 1 "+IP_SSH+" > /dev/null 2>&1")
    if ping == 0:
        print("PI acceso\n")
        return 0
    else:
        print("PI NON RAGGIUNGIBILE. Impossibile continuare.")
        return -1


def getShutdown():
    inp = input("Spegnere il pc al termine? [Y/n] ")
    if inp != "n" and inp != "N":
        return 1
    else:
        return 0 


def selezioneCartelle():
    cart = []
    print("Selezionare cartelle:")
    for x in FOLDERS:
        while True:
            inp = input("Backup di " + x +"? [y/n] ")
            if inp == "y" or inp == "Y":
                cart.append(x)
                break
            else :
                if inp == "n" or inp == "N":
                    break
    return cart


if __name__ == "__main__":
    start()
