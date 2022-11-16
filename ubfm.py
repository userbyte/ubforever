#!/usr/bin/env python3

# basically systemctl but for instances of ubforever
#### lol im basically making my own systemd at this point
# some ideas/examples for what this could do

## up/down management
# ubfm start dlapi              - starts dlapi using its ubforever instance
# ubfm stop dlapi              - stops dlapi using its ubforever instance, but leaves ubforever running
# ubfm restart dlapi              - restarts dlapi using its ubforever instance

# start a new instance of ubforever using the provided values, and system-provided ubforever code
# ubfm new \
# --iname="progname" \
# --startcmd="python3 /path/to/some/program.py" \
# --stopcmd="sh /path/to/some/stopscript.sh" \
# --wait="5"