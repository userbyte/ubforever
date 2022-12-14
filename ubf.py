#!/usr/bin/python3

import subprocess as sbp
import sys, asyncio, time, toml, signal, os

version = '0.0.3.3'

mypid = os.getpid()
iname = 'untitled' # default iname

def printubf(s):
    """simple function that adds [UBF] to the beginning of print statements to make it easier to differentiate program output and ubf output"""
    print('[UBF] '+s)

def cleanup():
    try: cfg
    except NameError: return False
    run_stopcmd()
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
    try: cfg
    except NameError: return False
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
    # printubf('A config file is required. Exiting...')
    yn = input('Create one? [Y/N]: ')
    if yn.lower() in ['y','yes']:
        cfg = {
            "iname": input('instance name: '),
            "startcmd": input('start command: '),
            "stopcmd": input('stop command: '),
            "wait": int(input('wait interval: '))
        }
        printubf(f'Saving config to {os.getcwd()}/ubf_cfg.toml...')
        with open('./ubf_cfg.toml', 'w') as f:
            toml.dump(cfg, f, encoder=None)
        printubf('Starting UBForever')
    else:
        printubf('Exiting...')
        sys.exit(2)

try:
    iname = cfg['iname']
    startcmd = cfg['startcmd']
    stopcmd = cfg['stopcmd']
    wait = cfg['wait']
except KeyError as e:
    printubf(f'Config is missing required value: {e}')
else: 
    printubf(f'Config loaded: {cfg}')

# i should probably use /run but that requires root permissions i think... so ill just use tmp instead
if not os.path.exists('/tmp/ubf'):
    os.mkdir('/tmp/ubf')
    # printubf('Created /tmp/ubf')

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
    printubf('caught KeyboardInterrupt. cleaning up...')
    cleanup()
    printubf('UBForever exiting...')
    exit()
except Exception as e:
    printubf(f'unexpected error: {e}')