

import argparse
import pydicom
import os
import numpy

# this line assigns the arguments given at command line to variables that can be used within the script (the first is the name of the script itself)
parser = argparse.ArgumentParser(description='This script takes a Hologic image file and a binary dump of the private data from that image (generated by separate script). It then outputs a new image with the private data appropriately integrated.')
parser.add_argument('infile',
                    help='The Hologic image file to be processed.')
parser.add_argument('pvt_dump',
                    help='The private data dump.')
parser.add_argument('tagdump',
                    help='The dump of the image file tags.')
parser.add_argument('outfile',
                    help='Desired output filename.')


args = parser.parse_args()
infile = args.infile
pvt_dump = args.pvt_dump
tagdump = args.tagdump
outfile = args.outfile
#outputDirectory = args.outputDirectory


print('Reading input file')
ds = pydicom.read_file(infile)

'''
new_dict_entries = {
    0x7E011001 : ('LO', 'CodecVersion', '1', 'HologicTomoSc'),
    0x7E011002 : ('SH', 'CodecContentType', '1', 'HologicTomoSc'),
    0x7E011010 : ('SQ', 'HighResolutionDataSequence', '1', 'HologicTomoSc'),
    0x7E011011 : ('SQ', 'LowResolutionDataSequence', '1', 'HologicTomoSc'),
    0x7E011012 : ('OB', 'CodecContent', '1', 'HologicTomoSc'),
}
'''

# make new dicom file
print('Making new dataset')
ds2 = pydicom.Dataset()
ds2.file_meta = pydicom.Dataset()

# copy across existing attributes (but not private elements)
print('Getting non-private elements')
ds2.RelatedSeriesSequence = ds.RelatedSeriesSequence
ds2.StudyInstanceUID = ds.StudyInstanceUID
ds2.SeriesInstanceUID = ds.SeriesInstanceUID
avoid_tags = ['UN', 'SQ', 'na', 'OB', 'OW']
with open(tagdump,'r') as tags:
    for line in tags:
        if not line.startswith('#') and line != '\n':
            raw = (line.split('#')[0].strip())
            tag_group = raw[1:5]
            tag_element = raw[6:10]
            VR = raw[12:14]
            content = raw[15:].strip('[]()')
        else:
            continue
        if tag_group == '0002':
            continue
            if VR == 'UL':
                cont = int(content)
                content = bytearray.fromhex(format(cont,'x').zfill(8))
            ds2.file_meta[tag_group,tag_element] = pydicom.DataElement((tag_group,tag_element), VR, content)
        elif VR not in avoid_tags:
            if VR == 'US':
                content = int(content)
                #content = bytearray.fromhex(format(cont,'x').zfill(4))
            ds2[tag_group,tag_element] = pydicom.DataElement((tag_group,tag_element), VR, content)

# set frame count, columns etc in new dicom file (take from high res sequence)
print('Getting private info')
with open(pvt_dump, "rb") as fh:
    data = fh.read()

fcount = int.from_bytes(data[20:22],"little")
ds2[0x0028,0x0008] = pydicom.DataElement((0x0028,0x0008), 'IS', fcount)
print('Frame count: ', fcount)

cols = int.from_bytes(data[24:26],"little")
byte_col = bytearray.fromhex(format(cols,'x').zfill(4))
ds2[0x0028,0x0011] = pydicom.DataElement((0x0028,0x0011), 'US', cols)
print('No. columns: ', cols)
print(byte_col)

rows = int.from_bytes(data[28:30],"little")
byte_row = bytearray.fromhex(format(rows,'x').zfill(4))
ds2[0x0028,0x0010] = pydicom.DataElement((0x0028,0x0010), 'US', rows)
print('No. rows: ', rows)
print(byte_row)

bits = int.from_bytes(data[32:33],"little")
byte_bits = bytearray.fromhex(format(bits,'x').zfill(4))
byte_hibit = bytearray.fromhex(format(bits-1,'x').zfill(4))
ds2[0x0028,0x0101] = pydicom.DataElement((0x0028,0x0101), 'US', bits)
ds2[0x0028,0x0102] = pydicom.DataElement((0x0028,0x0102), 'US', bits-1)
print('Bits stored: ', bits)

#misc values
ds2[0x0028,0x0100] = pydicom.DataElement((0x0028,0x0100), 'US', 16)
ds2[0x0028,0x0004] = pydicom.DataElement((0x0028,0x0004), 'CS', 'MONOCHROME2')

# add transfer syntax meta-header (maybe same as endian stuff below)
print('Adding transfer syntax meta-header')
ds2.file_meta.TransferSyntaxUID = '1.2.840.10008.1.2.4.81'
#ds2.file_meta[0x0002,0x0001] = pydicom.DataElement((0x0002,0x0001), 'OB', b'00\01')
# set littleEndian & VR options
print('Setting little-endian & implicit VR options to false')
ds2.is_little_endian = True
ds2.is_implicit_VR = False

# make jpeg-ls header
print('Making JPEG-LS header')
header = "FF D8 FF F7 00 0B {} {} {} 01 01 11 00 FF DA 00 08 01 01 00 {} 00 00".format(format(bits,'x').zfill(4), format(rows,'x').zfill(4), format(cols,'x').zfill(4), format(data[36],'x').zfill(2))

# get frame positions from high res sequence
print('Getting frame positions')
frames = []
for i in range(-1024,0,4):
    frame_pos = int.from_bytes(data[i:i+4],"little")
    frames.append(frame_pos)

    
# Pixel Data tag is 7FE0,0010. Add offset table as first fragment.
pixel_data = []

# Insert data for each frame with jpeg-ls header
# save pixel data via array
print('Inserting pixel data')
for i in range(0,fcount):
    frame_data = ""
    frame_start = frames[i]
    frame_end = frames[i+1]-1
    # Append header
    frame_data = frame_data + header
    # Append pixel data
    for k in data[frame_start:frame_end]:
        l = format(k,'x').zfill(2)
        frame_data = frame_data + l
    # If frame length is odd - append 00 byte.
    if (frame_end-frame_start)%2>0:
        frame_data = frame_data + ' 00'
    # Append EOI marker
    frame_data = frame_data + ' FFD9'
    #pixel_data = pixel_data + frame_data
    frame_bytes = bytearray.fromhex(frame_data)
    pixel_data.append(frame_bytes)

# create basic offset table & prepend as first fragment
print('Making basic offset table (BOT)')
offsets = '00000000'
prev = 0
for i in range(0,fcount):
    offset = prev + len(pixel_data[i])
    prev = offset
    offsets = offsets + ' ' + format(offset,'x').zfill(8)
byte_offsets = bytearray.fromhex(offsets)
print('Inserting BOT as first fragment')
pixel_data.insert(0,byte_offsets)

print("Transfer Syntax Info")
print(ds2.file_meta.TransferSyntaxUID.name)
print(ds2.file_meta.TransferSyntaxUID.is_compressed)


print('Converting to array')
#pix_arr = bytearray.fromhex(pixel_data)
#print(type(pix_arr))
print('Converting new pixel array to bytes')
#pix_bytes = bytes(pix_arr)
print('Encapsulating')
ds2.PixelData = pydicom.encaps.encapsulate(pixel_data)
#ds2.PixelData = pix_arr
#ds2.PixelData = pix_bytes

print(ds2)


# write output to file
print('Saving to file: {}'.format(outfile))
#ds2.save_as(outfile)
pydicom.filewriter.dcmwrite(outfile, ds2, write_like_original=False)
#ds2.save()


# profit


