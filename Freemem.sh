#!/bin/bash
# Title 		Freemem
# Date			2024-03-26(v1.0)

#
# Written by	Jean Paul BERES
##
# v2.0          2025-06-04 : Using external source for colours

# Colors
source ~/bin/bash_colours
# Screen handling characters
Cr='\c'			# Carriage Return
#

ClearMem () {

clear
echo -e $L_Yellow$Bold; sudo free -h
sudo sysctl -w vm.drop_caches=3 && sync && echo 3 | sudo tee /proc/sys/vm/drop_caches
echo -e $Reset$Bold$Cr; sudo free -h

}

#
# MAIN
#
ClearMem
