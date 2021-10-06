#!/bin/bash

if [ $# -eq 0 ]
  then
    echo "No arguments supplied"
    exit 1
fi

infile=$1
identifier=$2

echo -----------------------------------
echo ------- Supplied input file -------
echo -----------------------------------
echo $infile

echo -----------------------------------
echo ------- Supplied identifier -------
echo -----------------------------------
echo $identifier

# check dicom compliance
echo -------------------------------------------------------
echo ------- Checking DICOM compliance with DCIODVFY -------
echo -------------------------------------------------------
dciodvfy $infile

# load private dicom dictionary (later supplied by user?)
echo ------------------------------------------------
echo ------- Loading provate DICOM dictionary -------
echo ------------------------------------------------
export DCMDICTPATH=./hologic_private.dic:$DCMDICTPATH

echo ---------------------------------------------
echo ------- Getting private data elements -------
echo ---------------------------------------------
dcmdump +L +P "7e01,1012" --prepend +uc $infile \
| grep "(7e01,1010).(7e01,1012)" \
| sed 's/^.*OB //;s/ #.*$//' \
| split -d -l1

for i in x0*; do
    xxd -r -p $i $i.bin
    rm $i
done

cat x*.bin > ${identifier}_data.bin
rm x*.bin

dcmdump -Un $infile > ${identifier}_tagdump

echo ---------------------------------------------
echo ------- Getting sanity check figures --------
echo ---------------------------------------------
dcmdump -M $infile | grep 0028,001 > sanity.txt
dcmdump -M $infile | grep 0028,0101 >> sanity.txt


