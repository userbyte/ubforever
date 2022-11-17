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
subparsers = parser.add_subparsers(dest="subcommand")

def argument(*name_or_flags, **kwargs):
    return (list(name_or_flags), kwargs)

def subcommand(name, args=[], parent=subparsers):
    def decorator(func):
        parser = parent.add_parser(name, description=func.__doc__)
        for arg in args:
            parser.add_argument(*arg[0], **arg[1])
        parser.set_defaults(func=func)
    return decorator

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

# -- commands --

@subcommand("list")
def c_list(args):
    """list running ubforever instances"""
    print(f'searching for ubf instances...')
    fi = {}
    for fn in os.listdir('/tmp/ubf'):
        with open(f'/tmp/ubf/{fn}') as f:
            ipid = f.read()
        iname = fn.replace('ubf-','').replace('.pid','') # carve out instance name from its pid file
        fi.update({iname:ipid})
    for i in fi:
        print(f'found: {i} ({fi[i]})')

@subcommand("start", [argument("instance", help="name of target ubforever instance")])
def c_start(args):
    """tell a ubf instance to start it's thing (if its not already running)"""
    print(f'sending start signal to ubf[{args.instance}]')
    ubfsendsig(args.instance, signal.SIGUSR1)

@subcommand("stop", [argument("instance", help="name of target ubforever instance")])
def c_stop(args):
    """tell a ubf instance to stop it's thing"""
    print(f'sending stop signal to ubf[{args.instance}]')
    ubfsendsig(args.instance, signal.SIGUSR2)

@subcommand("restart", [argument("instance", help="name of target ubforever instance")])
def c_restart(args):
    """tell a ubf instance to restart it's thing"""
    print(f'sending restart signal to ubf[{args.instance}]')
    ubfsendsig(args.instance, signal.SIGTSTP)

@subcommand("terminate", [argument("-y", "--yes", help="assume yes", required=False, action="store_true"), argument("instance", help="name of target ubforever instance")])
def c_terminate(args):
    """tell a ubf instance to kill itself"""
    if args.yes:
        print(f'sending terminate signal to ubf[{args.instance}]')
        ubfsendsig(args.instance, signal.SIGTERM)
    else:
        yn = input('are you sure you want to terminate this instance of ubforever (it will need to be restart manually)? [y/n]: ')
        if yn.lower() in ['y','yes']:
            print(f'sending terminate signal to ubf[{args.instance}]')
            ubfsendsig(args.instance, signal.SIGTERM)
        else:
            print('aight, not doing anything')

# -- commands --

if __name__ == "__main__":
    args = parser.parse_args()
    if args.subcommand is None:
        parser.print_help()
    else:
        args.func(args)