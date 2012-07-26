#!/bin/sh
# Runs rst2confluence.py on all .rst files in test/ and compares them
# to the expected output (.exp)
for i in test/*.rst
do
    echo -n Testing $i
    expFile="$i.exp"
    outFile="$i.out"
    diffFile="$i.diff"
    ./rst2confluence.py "$i" > "$outFile"

    diff -u "$expFile" "$outFile" > "$diffFile"
    if [ "$?" -ne "0" ]; then
        echo " \033[01;31merror\033[00m"
        cat "$diffFile" | colordiff
        break;
    else
        #all fine
        echo " \033[01;32mok\033[00m"
        rm "$outFile"
        rm "$diffFile"
    fi
done
