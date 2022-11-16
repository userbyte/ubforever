#!/usr/bin/python3

import subprocess as sbp
import sys, asyncio, time, toml, signal, os

version = '0.0.3.1'

mypid = os.getpid()
iname = 'untitled' # default iname

def printubf(s):
    """simple function that adds [UBF] to the beginning of print statements to make it easier to differentiate program output and ubf output"""
    print('[UBF] '+s)

def cleanup():
    printubf('deleting pid file...')
    try:
        os.remove(f'/tmp/ubf/ubf-{iname}.pid')
        if len(os.listdir('/tmp/ubf')) == 0: # only delete the folder if it doesnt contain other UBF instance files
            os.rmdir('/tmp/ubf')
    except Exception as e:
        printubf(f'cleanup error: could not remove pid file ({e})')

def signal_handler(signum, frame):
    global autorestart
    signame = signal.Signals(signum).name
    if signame in ['SIGTERM','SIGINT']: # signals to stop ubforever
        printubf(f'{signame} has been caught. Exiting...')
        run_stopcmd()
        cleanup()
        time.sleep(2)
        exit()
    elif signame == 'SIGCHLD':
        # sigchld received when a child process exits i think?
        # printubf('child process has exited')
        pass
    elif signame == 'SIGTSTP': # Ctrl+Z can trigger this
        printubf(f'{signame} has been caught. Restarting child process...')
        autorestart = True
        run_stopcmd()
    elif signame == 'SIGUSR1':
        printubf(f"{signame} has been caught. Starting child process...")
        autorestart = True
    elif signame == 'SIGUSR2':
        printubf(f"{signame} has been caught. Stopping child process...")
        autorestart = False
        run_stopcmd()
    else:
        printubf(f'{signame} has been caught. idk what to do with this, ignoring it')

def run_stopcmd():
    printubf(f'Running stopcmd: {stopcmd}')
    p = sbp.Popen(f"{stopcmd}", shell=True)
    p.wait()
    printubf('stopcmd completed')

signal.signal(signal.SIGINT, signal_handler)
signal.signal(signal.SIGTERM, signal_handler)
signal.signal(signal.SIGCHLD, signal_handler)
signal.signal(signal.SIGTSTP, signal_handler)
signal.signal(signal.SIGUSR1, signal_handler)
signal.signal(signal.SIGUSR2, signal_handler)

printubf(f'UBForever v{version} started')
printubf('Starting program...')

try:
    with open('./ubf_cfg.toml', 'r') as f:
        cfg = toml.load(f)
except FileNotFoundError:
    printubf('Current directory is missing a config file! (ubf_cfg.toml)')
    printubf('A config file is required. Exiting...')
    sys.exit(2)

try:
    startcmd = cfg['startcmd']
    stopcmd = cfg['stopcmd']
    wait = cfg['wait']
    iname = cfg['iname']
except KeyError as e:
    printubf(f'Config is missing required value: {e}')
else: 
    printubf(f'Config loaded: {cfg}')

# i should probably use /run but that requires root permissions i think... so ill just use tmp instead
if not os.path.exists('/tmp/ubf'):
    os.mkdir('/tmp/ubf')
    printubf('created /tmp/ubf')

with open(f'/tmp/ubf/ubf-{iname}.pid', 'w') as f:
    f.write(str(mypid))

global autorestart
autorestart = True
restarts = 0
try:
    while True:
        if autorestart:
            if restarts != 0:
                printubf(f'Restarting program...\n[UBF] Total restarts occurred: {restarts}')
            p = sbp.Popen(f"{startcmd}", shell=True)
            p.wait()
            time.sleep(wait)
            restarts = restarts+1
        else:
            # printubf('autorestart is disabled')
            time.sleep(wait)
except KeyboardInterrupt:
    printubf('caught KeyboardInterrupt. running program stop command...')
    run_stopcmd()
    printubf('UBForever exiting...')
    cleanup()
    exit()
except Exception as e:
    printubf(f'unexpected error: {e}')