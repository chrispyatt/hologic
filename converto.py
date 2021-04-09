import argparse
import pydicom
import os


infile = "/home/chris/Dev/PyDicom/images/Case1 [Case1]/20080408 023126 [ - BREAST IMAGING TOMOSYNTHESIS]/Series 73100000 [MG - L CC Tomosynthesis Reconstruction]/1.3.6.1.4.1.5962.99.1.2280943358.716200484.1363785608958.67.0.dcm"


def check_dcm_compliance(img):
    command1 = f"dciodvfy \"{img}\""
    result = os.system(command1)
    return result


check_dcm_compliance(infile)


print('reading input file')
ds = pydicom.read_file(infile)


# dump out data from file so we can find the embedded images
command2 = "dcmdump +P 7e01,1010 +L " + infile + "> temp.txt"
os.system(command2)

command3 = "grep -o '\\01\\7e\\12\\10' temp.txt | wc -l"


# make new dicom file
print('making new dataset')
ds2 = pydicom.Dataset()

# copy across existing attributes (but not private elements)
print('getting non-private elements')


# set frame count, columns etc in new dicom file (take from igh res sequence)
print('getting info')
data = ds[('7e01', '1010')]

print('frame count')
print(data[20])
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


