import os
import json
import subprocess
import time
from datetime import datetime as dt
from getpass import getpass
from termcolor import colored as col


def start():
    try:
        read_params()
    except FileNotFoundError:
        printer("Error file params.json not found. Abort", "red")
        return -1
    except ValueError:
        printer("Error reading params. Abort", "red")
        return -1

    getLogFile()

    printer("\n*****************************","green")
    printer("**   COMPRESSORE STARTED   **","green")
    printer("*****************************\n","green")

    if SSH_ENABLED:
        if check_conn_ssh() == -1: return -1
        PASSW = read_psw()

    cart = select_folders()
    #TODO controllo che esistano le cartelle!!

    if len(cart) < 1:
        printer("No file/folder selected. Quit","yellow")
        return 1
    shut = get_shutdown()

    printer("\nSummary:", "cyan")
    printer("* Backup:", "cyan")
    for c in cart:
        subprocess.call(["/bin/du","-sh", c], shell=False)
        subprocess.call(["/bin/du","-sh", c], stdout=F_LOG, shell=False) #brutto ma non so come scrivere contemporaneamente su f e stdout

    printer("* Backup saved temporarily in "+SAVEFOLDER+"", "cyan")
    printer(("* SCP to "+IP_SSH) if SSH_ENABLED else "* No SSH", "cyan")
    printer("* Shutdown at the end? " +("yes" if shut == 1 else "no")+ "\n", "cyan")

    inp = input(col("Do you want to proced? [y/n] ", "cyan"))
    F_LOG.write("Do you want to proced? [y/n] " + inp)
    if inp != "y" and inp != "Y":
        printer("Abort", "red")
        return 1

    #COMPRESSIONE E INVIO
    err = 0
    for c in cart:
        nome_tar = SAVEFOLDER+"/"+c.split("/")[-1]+".tar"
        nome_tar_bz2 = nome_tar+".bz2"
        start_time = dt.now()
        printer("\nStarting compression: {}".format(start_time), "white")
        printer("Compressing "+SAVEFOLDER+"/"+c.split("/")[-1]+"...", "white")
        res = subprocess.call(["/bin/tar -I '/bin/pbzip2 -f -p4' -cvf "+nome_tar_bz2+" "+c], shell=True)
        # res = subprocess.call(["/bin/tar", "-cvf", nome_tar, c], stdout=F_LOG, stderr=F_LOG ,shell=False)
        # res = subprocess.call(["/bin/pbzip2", "-v","-f", "-p4", nome_tar], stdout=F_LOG, stderr=F_LOG, shell=False)
        if res != 0:
            printer("\nERROR compression "+nome_tar+" failed. Abort","red")
            err = 1
            break
        printer("**** COMPRESSION COMPLETED ****","green")
        printer("Duration: {}\n".format(dt.now()-start_time),"white")

        if SSH_ENABLED:
            start_time = dt.now()
            printer("Starting scp: {}".format(start_time), "white")
            printer("Sending "+nome_tar_bz2+" to "+IP_SSH+":"+FOLDER_SSH+"...", "white")
            res = subprocess.call(["/bin/sshpass","-p", PASSW, "/bin/scp", "-v", "-P", PORT_SSH, nome_tar_bz2, USER_SSH+"@"+IP_SSH+":"+FOLDER_SSH], shell=False)
            # res = subprocess.call(["/bin/sshpass","-p", PASSW, "/bin/scp", "-v", "-P", PORT_SSH, nome_tar_bz2, USER_SSH+"@"+IP_SSH+":"+FOLDER_SSH], stdout=F_LOG, stderr=F_LOG ,shell=False)
            if res != 0:
                printer("\nERROR send file "+c.split("/")[-1]+".tar.bz2 via ssh failed. Abort","red")
                err=1
                break
            printer("\n***** SEND SSH COMPLETED *****\n","green")
            printer("Duration: {}\n".format(dt.now()-start_time),"white")
            subprocess.call(["/bin/rm", nome_tar_bz2], stdout=F_LOG, stderr=F_LOG ,shell=False)
        
    if(err == 0):
        printer("\n*******************************", "green")
        printer("***  COMPRESSORE TERMINATED ***", "green")
        printer("*******************************\n", "green")
        if shut == 1:
            printer("Shutting down...", "white")
            time.sleep(5)
            subprocess.call(["/usr/sbin/shutdown", "now"], stdout=F_LOG, stderr=F_LOG ,shell=False) 
    else:
        printer("\n*******************************", "red")
        printer("!!!!     ERROR DETECTED    !!!!", "red")
        printer("*******************************\n", "red")
        return -1


#TODO renderlo più parlabile. Per ora dice solo "Errore lettura parametri"
def read_params(): #throw Exception

    global SSH_ENABLED
    global IP_SSH
    global PORT_SSH
    global USER_SSH
    global FOLDER_SSH
    global SAVEFOLDER
    global FOLDERS
    global LOG_ENABLED
    global LOG_FOLDER

    f = open('../params.json')

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
                PORT_SSH = data["params"]["ssh"]["port"]
                if PORT_SSH == "": PORT_SSH = 22
                USER_SSH = data["params"]["ssh"]["user"]
                FOLDER_SSH = data["params"]["ssh"]["folder"]
        if d == "log":
            LOG_ENABLED = data["params"]["log"]["enable"]
            if LOG_ENABLED:
                LOG_FOLDER  = data["params"]["log"]["folder"]


def getLogFile():
    if not LOG_ENABLED:
        return None

    global LOG_FILE_PATH
    global F_LOG
    e=dt.now()
    LOG_FILE_PATH = LOG_FOLDER+"/compressore_%s_%s_%s.log" % (e.year, e.month, e.day)

    try:
        #if the file with this date exists, it will append
        F_LOG = open(LOG_FILE_PATH, "w" if not os.path.isfile(LOG_FILE_PATH) else "a")
    except FileExistsError:
        printer("ERROR log file","red")


def read_psw():
    return getpass("Insert ssh password for user "+USER_SSH+": ")


def check_conn_ssh():
    printer("Checking ssh connection...","white")
    ping = subprocess.call(["/bin/ping","-c 1", IP_SSH], stdout=subprocess.DEVNULL, shell=False)
    if ping == 0:
        printer("Connection ok\n","green")
        return 0
    else:
        printer("SSh host seems offline. Abort","red")
        return -1


def get_shutdown():
    inp = input("Shutdown pc at the end? [Y/n] ")
    F_LOG.write("Shutdown pc at the end? [Y/n] " + inp)
    if inp != "n" and inp != "N":
        return 1
    else:
        return 0 


def select_folders():
    cart = []
    printer("Select folders/files:", "white")
    for x in FOLDERS:
        while True:
            inp = input("Backup " + x +"? [y/n] ")
            F_LOG.write("Backup " + x +"? [y/n] "+inp)
            if inp == "y" or inp == "Y":
                cart.append(x)
                break
            else :
                if inp == "n" or inp == "N":
                    break
    return cart


def printer(msg, color):
    print(col(msg, color))
    F_LOG.write(msg+"\n")

if __name__ == "__main__":
    start()
