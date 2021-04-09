#!/bin/bash

if [ $# -eq 0 ]
  then
    echo "No arguments supplied"
    exit 1
fi

infile=$1

# check dicom compliance
echo -------------------------------------------------------
echo ------- Checking DICOM compliance with DCIODVFY -------
echo -------------------------------------------------------
dciodvfy $infile

# load private dicom dictionary (later supplied by user?)
echo ------------------------------------------------
echo ------- Loading provate DICOM dictionary -------
echo ------------------------------------------------
export DCMDICTPATH=./hologic_private.dic

echo ---------------------------------------------
echo ------- Getting private data elements -------
echo ---------------------------------------------
dcmdump +L +P "7e01,1012" --prepend +uc $infile | grep "(7e01,1010).(7e01,1012)" | sed 's/^.*OB //;s/ #.*$//' | split -d -l1

for i in ls x0*; do
    xxd -r -p $i $i.bin
done

cat x*.bin > data.bin
rm x*.bin

