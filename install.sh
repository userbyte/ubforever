#!/usr/bin/env bash

# install script for ubforever

# echo "installing python dependencies"
# python3 -m pip install -r requirements.txt

# where the source files will live
INSTALLDIR="/home/$USER/.local/src/ubf"

echo "creating src dir"
mkdir -p $INSTALLDIR

echo "copying py files to src dir"
install -D -m 755 "ubf.py" "$INSTALLDIR/ubf.py"
install -D -m 755 "ubfm.py" "$INSTALLDIR/ubfm.py"

echo "creating symlinks for PATH (ubf and ubfm)"
ln -s "$INSTALLDIR/ubf.py" "/home/$USER/.local/bin/ubf"
ln -s "$INSTALLDIR/ubfm.py" "/home/$USER/.local/bin/ubfm"