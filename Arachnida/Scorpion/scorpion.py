#!/usr/bin/env python3

import imageio.v2 as imageio
import exifread
from PIL import Image, ExifTags
from PIL.ExifTags import TAGS
from PIL.PngImagePlugin import PngImageFile, PngInfo
import re
import os
from prettytable import PrettyTable
import argparse


def options():
    parser = argparse.ArgumentParser(description="Read image metadata")
    parser.add_argument("-i", "--image", help="Input image file.", required=True)
    args = parser.parse_args()
    return args

def gen_metadata(image):
    
    # Read image into imageio for data type
    pic = imageio.imread(image)
    Summary_table = PrettyTable()
    Metadata_table = PrettyTable()
    Summary_table.field_names = ["MetaTags", "Values"]
    Metadata_table.field_names = ["MetaTags", "Values"]
    # Read image into PIL to extract basic metadata
    my_image = Image.open(image)

    # Calculations
    megapixels = (my_image.size[0]*my_image.size[1]/1000000) # Megapixels
    d = re.sub(r'[a-z]', '', str(pic.dtype)) # Dtype
    t = len(Image.Image.getbands(my_image)) # Number of channels

    Summary_table.add_row(["Filename: ",my_image.filename])
    Summary_table.add_row(["Format: ", my_image.format])
    Summary_table.add_row(["Data Type:", pic.dtype])
    Summary_table.add_row(["Bit Depth (per Channel):", d])
    Summary_table.add_row(["Bit Depth (per Pixel): ", int(d)*int(t)])
    Summary_table.add_row(["Number of Channels: ", t])
    Summary_table.add_row(["Mode: ",my_image.mode])
    Summary_table.add_row(["Palette: ",my_image.palette])
    Summary_table.add_row(["Width: ", my_image.size[0]])
    Summary_table.add_row(["Height: ", my_image.size[1]])
    Summary_table.add_row(["Megapixels: ",megapixels])
    print("\n--Summary--\n")
    print(Summary_table)
    # Open image with ExifMode to collect EXIF data
    exif_tags = open(image, 'rb')
    tags = exifread.process_file(exif_tags)

    # Create an empty array
    exif_array = []
    flag=1
    tagss=[]
    values=[]
    # Print header
    print("\n--Metadata--\n")

    # For non-PNGs
    if my_image.format != "PNG":
        # Compile array from tags dict
        for i in tags:
            c= i, str(tags[i])
            exif_array.append(c)
            for properties in exif_array:
                if properties[0] != 'JPEGThumbnail':
                    for x in properties:
                        if flag==1:
                            if x not in tagss:
                                tagss+=[str(x)]
                                flag=0
                            else:flag=2
                        elif flag==2:flag=1
                        else:
                            values+=[str(x)]
                            flag = 1
        for i in range(len(tagss)):
            Metadata_table.add_row([tagss[i], values[i]])
        print(Metadata_table)
    if my_image.format == "PNG":
        image = PngImageFile(image) #via https://stackoverflow.com/a/58399815
        metadata = PngInfo()
        
        # Compile array from tags dict
        for i in image.text:
            compile = i, str(image.text[i])
            exif_array.append(compile)
        
        # If XML metadata, pull out data by idenifying data type and gathering useful meta
        if len(exif_array) > 0:
            header = exif_array[0][0]
        else:
            header = ""
            print("No available metadata")
            return
        
        xml_output = []
        flag=1
        tagss=[]
        values=[]
        if header.startswith("XML"):
            xml = exif_array[0][1]
            xml_output.extend(xml.splitlines()) # Use splitlines so that you have a list containing each line
            # Remove useless meta tags
            for line in xml.splitlines():
                if "<" not in line:
                    if "xmlns" not in line:
                        # Remove equal signs, quotation marks, /> characters and leading spaces
                        xml_line = re.sub(r'[a-z]*:', '', line).replace('="', ': ')
                        xml_line = xml_line.rstrip(' />')
                        xml_line = xml_line.rstrip('\"')
                        xml_line = xml_line.lstrip(' ')
                        print(xml_line)
        
        elif header.startswith("Software"):
            print("No available metadata")
       
        # If no XML, print available metadata
        else:
            for properties in exif_array:
                if properties[0] != 'JPEGThumbnail':
                    if flag==1:
                        if x not in tagss:
                            tagss+=[str(x)]
                            flag=0
                        else:flag=2
                    elif flag==2:flag=1
                    else:
                        values+=[str(x)]
                        flag = 1
            for i in range(len(tagss)):
                Metadata_table.add_row([tagss[i], values[i]])
            print(Metadata_table)


    # Explanation for GIF or BMP
    if my_image.format == "GIF" or my_image.format == "BMP":
        print("No available metadata")

def main():

    # Get options
    args = options()
    image = args.image

    # Check for RAW images

    name, extension = os.path.splitext(image)

    # List valid extensions
    ext = [".png", ".jpg", ".jpeg", ".gif", ".bmp"]
    if extension not in ext:
        print("File format ",extension," not supported.")
        exit()

    gen_metadata(image)

if __name__ == '__main__':
    main()