import os
import json
import subprocess
import time
from datetime import datetime as dt
from getpass import getpass
from termcolor import colored as col


def start():

    print(col("\n*****************************","green"))
    print(col("**   COMPRESSORE STARTED   **","green"))
    print(col("*****************************\n","green"))

    try:
        read_params()
    except FileNotFoundError:
        print(col("Error file params.json not found. Abort", "red"))
        return -1
    except ValueError:
        print(col("Error reading params. Abort", "red"))
        return -1

    getLogFile()

    if SSH_ENABLED:
        if check_conn_ssh() == -1: return -1
        PASSW = read_psw()

    cart = select_folders()
    if len(cart) < 1:
        print(col("No file/folder selected. Quit","yellow"))
        return 1
    shut = get_shutdown()

    print(col("\nSummary:", "cyan"))
    print(col("* Backup:", "cyan"))
    for c in cart:
        subprocess.call(["/bin/du","-sh", c], shell=False)
        subprocess.call(["/bin/du","-sh", c], stdout=f_log, shell=False) #brutto ma non so come scrivere contemporaneamente su f e stdout

    print(col("* Backup saved temporarily in "+SAVEFOLDER+"", "cyan"))
    print(col(("* SCP to "+IP_SSH) if SSH_ENABLED else "* No SSH", "cyan"))
    print(col("* Shutdown at the end? " +("yes" if shut == 1 else "no")+ "\n", "cyan"))

    inp = input(col("Do you want to proced? [y/n] ", "cyan"))
    if inp != "y" and inp != "Y":
        print(col("Abort", "red"))
        return 1

    #COMPRESSIONE E INVIO
    err = 0
    for c in cart:
        nome_tar = SAVEFOLDER+"/"+c.split("/")[-1]+".tar"
        nome_tar_bz2 = nome_tar+".bz2"
        start_time = dt.now()
        printer("\nStarting compression: {}".format(start_time), "white")
        printer("Compression "+SAVEFOLDER+"/"+c.split("/")[-1]+"...", "white")
        res = subprocess.call(["/bin/tar", "-cvf", nome_tar, c], stdout=f_log, stderr=f_log ,shell=False)
        res = subprocess.call(["/bin/pbzip2", "-v","-f", "-p4", nome_tar], stdout=f_log, stderr=f_log, shell=False)
        # res = os.system("tar -I \"pbzip2 -p4\" -cvf "+nome_tar+" "+c)
        if res != 0:
            print(col("\nERROR compression "+nome_tar+" failed. Abort","red"))
            err = 1
            break
        printer("**** COMPRESSION COMPLETED ****","green")
        printer("Duration: {}\n".format(dt.now()-start_time),"white")

        if SSH_ENABLED:
            start_time = dt.now()
            printer("Starting scp: {}".format(start_time), "white")
            printer("Sending "+nome_tar_bz2+" to "+IP_SSH+":"+FOLDER_SSH+"...", "white")
            res = subprocess.call(["/bin/sshpass","-p", PASSW, "scp", "-v", nome_tar_bz2, USER_SSH+"@"+IP_SSH+":"+FOLDER_SSH], shell=False)
            if res != 0:
                print(col("\nERROR send file "+c.split("/")[-1]+".tar.bz2 via ssh failed. Abort","red"))
                err=1
                break
            print(col("\n***** SEND SSH COMPLETED *****\n","green"))
            printer("Duration: {}\n".format(dt.now()-start_time),"white")
            subprocess.call(["/bin/rm", nome_tar_bz2], shell=False)
        
    if(err == 0):
        print(col("\n*******************************", "green"))
        print(col("***  COMPRESSORE TERMINATED ***", "green"))
        print(col("*******************************\n", "green"))
        if shut == 1:
            print("Shutting down...")
            time.sleep(5)
            subprocess.call(["/usr/sbin/shutdown", "now"], shell=False) 
    else:
        print(col("\n*******************************", "red"))
        print(col("!!!!     ERROR DETECTED    !!!!", "red"))
        print(col("*******************************\n", "red"))
        return -1


#TODO renderlo più parlabile. Per ora dice solo "Errore lettura parametri"
def read_params(): #throw Exception

    global SSH_ENABLED
    global IP_SSH
    global USER_SSH
    global FOLDER_SSH
    global SAVEFOLDER
    global FOLDERS
    global LOG_ENABLED
    global LOG_FOLDER

    f = open('params.json')

    data = json.load(f)

    for d in data["params"]:
        # if d == s:
        if d == "folder_to_backup":
            FOLDERS = data["params"]["folder_to_backup"]
        if d == "tmp_store_folder":
            SAVEFOLDER = data["params"]["tmp_store_folder"]
        if d == "ssh":
            SSH_ENABLED = data["params"]["ssh"]["enable"]
            if SSH_ENABLED :
                IP_SSH = data["params"]["ssh"]["ip"]
                USER_SSH = data["params"]["ssh"]["user"]
                FOLDER_SSH = data["params"]["ssh"]["folder"]
        if d == "log_folder":
            LOG_ENABLED = data["params"]["log_folder"]["enable"]
            if LOG_ENABLED:
                LOG_FOLDER  = data["params"]["log_folder"]["path"]

def getLogFile():

    if not LOG_ENABLED:
        return None

    global LOG_FILE_PATH
    global f_log
    e=dt.now()
    LOG_FILE_PATH = LOG_FOLDER+"/compressore_%s_%s_%s" % (e.year, e.month, e.day)

    try:
        #if the file with this date exists, it will append
        f_log = open(LOG_FILE_PATH, "w" if not os.path.isfile(LOG_FILE_PATH) else "a")
    except FileExistsError:
        print("ERRORE")


def read_psw():
    return getpass("Insert ssh password for user "+USER_SSH+": ")


def check_conn_ssh():
    print("Checking ssh connection...")
    ping = subprocess.call(["/bin/ping","-c 1", IP_SSH], stdout=subprocess.DEVNULL, shell=False)
    if ping == 0:
        print(col("Connection ok\n","green"))
        return 0
    else:
        print(col("SSh host seems offline. Abort","red"))
        return -1


def get_shutdown():
    inp = input("Shutdown pc at the end? [Y/n] ")
    if inp != "n" and inp != "N":
        return 1
    else:
        return 0 


def select_folders():
    cart = []
    print("Select folders/files:")
    for x in FOLDERS:
        while True:
            inp = input("Backup " + x +"? [y/n] ")
            if inp == "y" or inp == "Y":
                cart.append(x)
                break
            else :
                if inp == "n" or inp == "N":
                    break
    return cart


def printer(msg, color):
    print(col(msg, color))
    f_log.write(msg)

if __name__ == "__main__":
    start()
