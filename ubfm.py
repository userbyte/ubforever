#!/usr/bin/env python3

# ubfm - UBForever Manager

# basically systemctl but for instances of ubforever
#### lol im basically making my own systemd at this point
# some ideas/examples for what this could do

## up/down management
# ubfm start dlapi              - starts dlapi using its ubforever instance
# ubfm stop dlapi              - stops dlapi using its ubforever instance, but leaves ubforever running
# ubfm restart dlapi              - restarts dlapi using its ubforever instance

# start a new instance of ubforever using the provided values, and system-provided ubforever code
# ubfm new \
# --iname "progname" \
# --startcmd "python3 /path/to/some/program.py" \
# --stopcmd "sh /path/to/some/stopscript.sh" \
# --wait 5
# ^ i realized this is kinda dumb to implement so im putting my current work in a seperate git branch


import argparse, sys, signal, os

class ap(argparse.ArgumentParser):
    def error(self, message):
        sys.stderr.write(f'error: {message}\n')
        self.print_help()
        sys.exit(2)

parser = ap()
parser.add_argument("action", help="action to perform", choices=['start', 'stop', 'restart', 'terminate'])
parser.add_argument("instance", help="name of target ubforever instance")
args = parser.parse_args()

def ubfsendsig(iname, signum):
    """send a signal to a given ubf instance name"""
    # print(f'sending {signal.Signals(signum).name} to {iname}')
    try:
        with open(f'/tmp/ubf/ubf-{iname}.pid') as f:
            target_pid = f.read()
        os.kill(int(target_pid), signum)
    except ProcessLookupError as e:
        print(f'ubfsendsig failed to find process {target_pid}')
    except FileNotFoundError as e:
        print(f'ubfsendsig failed to find pid file "ubf-{iname}.pid"')
    except Exception as e:
        print(f'ubfsendsig unknown error: {e}')

if __name__ == "__main__":
    if len(sys.argv) == 1:
        parser.print_help(sys.stderr)
        sys.exit(1)
    if args.action == 'start':
        print(f'sending start signal to ubf[{args.instance}]')
        ubfsendsig(args.instance, signal.SIGUSR1)
    elif args.action == 'stop':
        print(f'sending stop signal to ubf[{args.instance}]')
        ubfsendsig(args.instance, signal.SIGUSR2)
    elif args.action == 'restart':
        print(f'sending restart signal to ubf[{args.instance}]')
        ubfsendsig(args.instance, signal.SIGCONT)
    elif args.action == 'terminate':
        yn = input('are you sure you want to terminate this instance of ubforever (it will need to be restart manually)? [y/n]: ')
        if yn.lower() in ['y','yes']:
            print(f'sending terminate signal to ubf[{args.instance}]')
            ubfsendsig(args.instance, signal.SIGTERM)
        else:
            print('aight, not doing anything')
    else:
        print(f'unknown action: {args.action}')