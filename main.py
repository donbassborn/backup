import os
import datetime
import winsound
import shutil
import subprocess
import hashlib
import psutil

p = psutil.Process(os.getpid())
p.nice(psutil.IDLE_PRIORITY_CLASS)


dirlistfile = "list.txt"
logfile = "logfile.txt"

log_types = ("[FATAL] ", "[ERR] ", "[WARN] ", "[OK] ")

try:
    log_handle = open(logfile, 'a')
except Exception as e: 
    _fatal("Unknown i/o exception " + str(e.__class__) + " while opening log file!") 
    winsound.Beep(1000, 100)
    exit(1)

def _fatal(_str):
    _log(log_types[0] + _str)

def _err(_str):
    _log(log_types[1] + _str)

def _warn(_str):
    _log(log_types[2] + _str)

def _ok(_str):
    _log(log_types[3] + _str)

def _log(_str):
    print(str(datetime.datetime.now()) + ": " + _str)
    log_handle.write(str(datetime.datetime.now()) + ": " + _str)
    
def md5(fname):
    hash_md5 = hashlib.md5()
    with open(fname, "rb") as f:
        for chunk in iter(lambda: f.read(4096), b""):
            hash_md5.update(chunk)
    return hash_md5.hexdigest()



try:
    dirlist = {}
    with open(dirlistfile, 'r') as list_handle:
        while list_handle.readable:
            path = list_handle.readline().strip()
            key = list_handle.readline().strip()
            if len(key) > 0 and len(path) > 0:
                if key in dirlist:
                    _warn("Key " + key + " duplicates in list, updated")
                dirlist.update({key: path})
            else:
                break
    _ok("Read " + str(len(dirlist)) + " dirs from list")

except FileNotFoundError as ex:
    _fatal("File " + os.curdir + os.sep + dirlistfile + " not found. Programm will exit!") 
    winsound.Beep(750, 100)
    exit(1)

for key in dirlist:
    target_dir = dirlist[key]
    backup_dir = key

    if(os.path.exists(target_dir)):
        if(os.path.isdir(target_dir)):
            for (dirpath, dirnames, filenames) in os.walk(target_dir):
                for dirname in dirnames:
                    fulldir = os.path.normpath(backup_dir + os.sep + dirpath.replace(target_dir, "") + os.sep + dirname)
                    if(not os.path.exists(fulldir) or (os.path.exists(fulldir) and os.path.isfile(fulldir))):
                        try:
                            os.makedirs(fulldir)
                            _ok("Dir " + fulldir + " created") 
                        except Exception as ex:
                            _err("During dir creation of " + fulldir + " an exception occured: " + str(ex.__class__))
                    
                for filename in filenames:
                    targetpath = os.path.normpath(backup_dir + os.sep + dirpath.replace(target_dir, "") + os.sep + filename)
                    filepath = dirpath + os.sep + filename
                    if(os.path.exists(targetpath)):
                        if(md5(targetpath) != md5(filepath)):
                            try:
                                shutil.copy2(filepath, targetpath)
                                _ok("Replaced " + filepath)
                            except Exception as ex:
                                _err("During replace of " + filepath + " an exception occured: " + str(ex.__class__)) 
                    else:
                        try:
                            shutil.copy2(filepath, targetpath)
                            _ok("Created " + filepath)
                        except Exception as ex:
                            _err("During creation of " + filepath + " an exception occured: " + str(ex.__class__))
        elif(os.path.isfile(target_dir) and os.path.isfile(backup_dir)):
            if(os.path.exists(backup_dir)):
                if(md5(backup_dir) != md5(target_dir)):
                    try:
                        shutil.copy2(target_dir, backup_dir)
                        _ok("Replaced " + target_dir)
                    except Exception as ex:
                         _err("During replace of " + target_dir + " an exception occured: " + str(ex.__class__)) 
            else:
                try:
                    shutil.copy2(target_dir, backup_dir)
                    _ok("Created " + target_dir)
                except Exception as ex:
                    _err("During creation of " + target_dir + " an exception occured: " + str(ex.__class__))
    else:
        _err("Dir " + target_dir + " doesnt exist!")