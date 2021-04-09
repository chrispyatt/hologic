import argparse
import pydicom
import os

# this line assigns the arguments given at command line to variables that can be used within the script (the first is the name of the script itself)
parser = argparse.ArgumentParser(description='This script takes a Hologic image file and a binary dump of the private data from that image (generated by separate script). It then outputs a new image with the private data appropriately integrated.')
parser.add_argument('infile',
                    help='The Hologic image file to be processed.')
parser.add_argument('pvt_dump',
                    help='The private data dump.')


args = parser.parse_args()
infile = args.infile
pvt_dump = args.pvt_dump
#outputDirectory = args.outputDirectory


print('reading input file')
ds = pydicom.read_file(infile)

new_dict_entries = {
    0x7E011001 : ('LO', 'CodecVersion', '1', 'HologicTomoSc'),
    0x7E011002 : ('SH', 'CodecContentType', '1', 'HologicTomoSc'),
    0x7E011010 : ('SQ', 'HighResolutionDataSequence', '1', 'HologicTomoSc'),
    0x7E011011 : ('SQ', 'LowResolutionDataSequence', '1', 'HologicTomoSc'),
    0x7E011012 : ('OB', 'CodecContent', '1', 'HologicTomoSc'),
}


# check values (sanity check)
# print rows/columns from x00 and from dcm dump of file
pass

# make new dicom file
print('making new dataset')
ds2 = pydicom.Dataset()

# copy across existing attributes (but not private elements)
print('getting non-private elements')


# set frame count, columns etc in new dicom file (take from igh res sequence)
print('getting info')
with open(pvt_dump, "rb") as fh:
    data = fh.read()

print(type(data))
h = hex(int(data))
print(type(h))

print('frame count')
print(data[20],data[21])
print(data[21])

print('columns')
print(data[24])
print(data[25])

print('rows')
print(data[28])
print(data[29])

print('bits stored')
print(data[32])

# make jpeg-ls header


# get frame positions from high res sequence
frames = []

for i in range(-1024,0,4):
    l = [data[i],data[i+1],data[i+2],data[i+3]]
    frames.append(l)


# get each frame, one by one & add jpeg header (to each frame??)
# also add end of image marker to each one


# save into new dicom file (with offset table??)


# meta header (1.2.840.10008.1.2.4.81)



# profit


