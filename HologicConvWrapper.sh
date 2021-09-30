#!/bin/bash

if [ $# -eq 0 ]
  then
    echo "No arguments supplied"
    exit 1
fi

# collect inputs
hol_image=$1
identifier=$2


echo -----------------------------------
echo ----- Retrieving private data -----
echo -----------------------------------

# run initial binary info generation
bash converto.sh $hol_image $identifier


echo -----------------------------------
echo ----- Constructing new image ------
echo -----------------------------------

# run python image reconstruction
python3 converto.py $hol_image ${identifier}_data.bin ${identifier}_tagdump ${identifier}.dcm



