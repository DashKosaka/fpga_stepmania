'''
LICENSE:

    Copyright (c) 2016 Jeremy DeJournett

    Permission is hereby granted, free of charge, to any person obtaining a copy of this software and associated documentation files
    (the "Software"), to deal in the Software without restriction, including without limitation the rights to use, copy, modify, 
    merge, publish, distribute, sublicense, and/or sell copies of the Software, and to permit persons to whom the Software is furnished 
    to do so, subject to the following conditions:

    The above copyright notice and this permission notice shall be included in all copies or substantial portions of the Software.

    THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES 
    OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE 
    LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN 
    CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.
    
On to the good stuff.
    
Written by Jeremy DeJournett for our ECE385 final project in Fall 2016.
This script assumes the directory structure given by https://github.com/Atrifex/ECE385-HelperTools
This script will change the text files generated by png_to_3_txt.py to valid SystemVerilog code for a sprite table.

Usage (continued)
In lab 8, things like DistX and ObjectOn are calculated in the color mapper, which is okay when you only have one object,
but is a huge mess when you have many many objects. A better strategy is to give DrawX and DrawY to every object,
and let them determine whether or not they are meant to be on at that time. Additionally, you can calculate the SpriteX
and SpriteY indexes inside the object's module itself, and just wire those as inputs to the color mapper. This way,
the color mapper does not need to know where every object is, and instead cand just map the colors according to what it's told to do.

If you have any more questions, be sure to ask one of the 385 TAs.

I also apologize in advance for how messy this is. Feel free to submit a PR if you want to try cleaning it up a bit.

'''
import math # needed ceiling and log functions.
from itertools import product # needed for finding maximally distant color palettes
from PIL import Image # can be obtained with a simple `pip install pillow`
import locale # for formatting large numbers with commas
import numpy as np

locale.setlocale(locale.LC_ALL, '')

github = "https://github.com/Atrifex/ECE385-HelperTools"
image_extension = ".png"
image_viewer = "feh"
parent_dir = "../" # Atrifex, this is .. since you moved the scripts into ./scripts
bytes_dir = parent_dir + "sprite_bytes/"
sv_dir = bytes_dir
orig_dir = parent_dir + "sprite_originals/"
spritename = "GalagaLogo"
outfile = sv_dir + spritename + ".sv"

compression_level = 16
xwidth = 0
ywidth = 0
header = ''
footer = ''

def usage():
    msg = ""
    lines = []
    lines.append("/*")
    lines.append("    This sprite table was generated using 'conv_to_sv.py'. Find out more here: " + github)
    lines.append("    To use, instantiate this module in your color mapper. The SpriteX input should be connected to")
    lines.append("        'ObjectXSize - DistX', where ObjectXSize is the width of your object in pixels along the")
    lines.append("        x direction. DistX is the horizontal distance between the DrawX pxiel and the top left corner")
    lines.append("        of the object in question, so something like: 'DistX = DrawX - ObjectXPosition' is fine.")
    lines.append("        Similarly this goes for SpriteY. Warning: If you don't do this, your image will be flipped along")
    lines.append("        the axis you ignored. This is a handy way to flip an image if you need to, though.")
    lines.append(" ")
    lines.append("    In the color mapper, you can then simply do something like:")
    lines.append("    module ColorMapper(...)")
    lines.append("    ...")
    lines.append("    logic [7:0] ObjectR, ObjectG, ObjectB")
    lines.append("    parameter ObjectXSize = 10'd10;")
    lines.append("    parameter ObjectYSize = 10'd10;")
    lines.append("    ...")
    lines.append("    always_comb")
    lines.append("    ...")
    lines.append("         if(ObjectOn == 1'b1)")
    lines.append("         begin")
    lines.append("             Red = ObjectR")
    lines.append("             Green = ObjectG")
    lines.append("             Blue = ObjectB")
    lines.append("         end")
    lines.append("     ...")
    lines.append("     ObjectSpriteTable ost(")
    lines.append("                           .SpriteX(ObjectXSize - DistX), .SpriteY(ObjectYSize - DistY),")
    lines.append("                           .SpriteR(ObjectR), .SpriteG(ObjectG), .SpriteB(ObjectB)")
    lines.append("                           );")
    lines.append(" ")
    lines.append("     See the comment at the top of the generation script if you're still confused.")
    lines.append("*/")
    for line in lines:
        msg += line + "\n"
    return msg

def pad_phrase(phrase, char, len):
    return len * char + phrase
    
def print_pad(phrase, char, len):
    print(pad_phrase(phrase, char, len))

def show_section_msg(phrase):
    indentation = 5
    if(phrase[-1] != '\n'):
        phrase += '\n'
    dash_width = 1
    for line in phrase.split('\n'):
        dash_width = max(len(line), dash_width)
    print("\n" + indentation* " " + dash_width * "-" + "\n" + indentation*" " + phrase + indentation * " " + dash_width*"-" + "\n")
    
def tuple_distance(X):
    dist = 0
    Y = sorted(X)
    N = len(X)
    for i in range(N + 1):
        new_dist = 0
        if(i == 0):
            new_dist = (Y[i] - 0)^2
        elif(i == N):
            new_dist = (255 - Y[i - 1])^2
        else:
            new_dist = (Y[i] - Y[i - 1])^2
        dist += new_dist
    return dist
    
def percentile(X, p):
    # Returns the p'th percentile of X.
    # Has an intermediate value pctile instead of returns
    # for debugging purposes.
    pctile = X[0]
    N = len(X)
    if(N == 1):
        pass
    elif(N == 2):
        pctile = X[0] if p < .5 else X[1]
    else:
        n = min(int(round(p * N + 0.5)), N)
        #print (len(X), n)
        pctile = X[n - 1] if p > 1.0/N else X[0]
    # print(100*p, "'th percentile of: ", X, " is: ", pctile)
    return pctile

def min_dist(replacements):
    palette = []
    current_list = []
    old_keys = []
    rep_colors = []
    
    print("Attempting to find palette with the minimum least squared distance...")
    for key, val in replacements.items():
        current_list = val[:]
        old_keys.append(key)
        current_list.append(key)
        palette.append(current_list)
    
    current_min = len(old_keys) * (256)^2
    min_tuple = tuple()
    
    prod = 1
    
    # Attempt at reducing the number of permutations by selecting a representative
    # sample (min, 25th, med, 75th, max) and iterating over them.
    # problem lies in tracking the other colors that get discarded from this
    # representative sample.
    
    # Just realized we are only using this to produce a minimal palette tuple, so we can
    # just use these to make a new representative palette to take the cartesian product.
    # Then use that tuple as normal.
    rep_palette = []
    for i, el in enumerate(palette):
        N = len(el)
        prod *= N
        # We use a set here to ensure uniqueness.
        el[:] = sorted(el)
        rep_colors = set(el)
        if(N > 5):
            rep_colors = set([])
            rep_colors.add(percentile(el, 0.00))
            rep_colors.add(percentile(el, 0.25))
            rep_colors.add(percentile(el, 0.50))
            rep_colors.add(percentile(el, 0.75))
            rep_colors.add(percentile(el, 1.00))
        rep_palette.append(list(rep_colors))
    # print(rep_palette)        
        
    
    #print("Number of palette tuples: ", locale.format("%d", prod, grouping=True))
    
    max_tries = 3000000
    
    for i, palette_tuple in enumerate(product(*rep_palette)):
        dist = tuple_distance(palette_tuple)
        if(dist < current_min):
            current_min = dist
            min_tuple = palette_tuple
     #       print("Iteration: ", i, "\t\tNew minimum tuple found: ", min_tuple)
        if(i + 1 > max_tries):
      #      print("Exceeded maximum number of tries (", locale.format("%d", max_tries, grouping=True), "). Continuing with last found minimum tuple.")
            break
    
    filtered_replacements = dict()
    
    for i, old_key in enumerate(old_keys):
        if(min_tuple[i] != old_key):
            colors = palette[i][:]
            colors.remove(min_tuple[i])
            filtered_replacements[min_tuple[i]] = colors
        else:
            filtered_replacements[min_tuple[i]] = replacements[old_key]
    '''
    print("Old Replacements:")
    for key, val in replacements.items():
        print(key, " : ", val)
    print("New Replacements:")
    for key, val in filtered_replacements.items():
        print(key, " : ", val)
    '''
    return filtered_replacements
def combine_channels_core(channels, dist):
    # Thanks to niemmi on SO for making a more efficient and
    # correct version of this! Link: http://stackoverflow.com/a/41082911/2289030
    
    # What happens here is we find just group a bunch of colors together
    # by their distance from each other. This way, we can build a
    # dictionary that is used to replace similar colors with a color
    # from a much smaller palette. This will cause some loss of detail,
    # but if you set the dist low enough (I think 16 is perfect), 
    # you will not be able to tell the difference.
    
    result = {}
    replacements = {}
    groups = []
    group = []
    key = None
    
    print("Before combining channels, " + str(len(channels)) + " different colors are needed.")

    # Iterate through channels in ascending numerical order
    for channel, count in sorted((int(k), v) for k, v in channels.items()):
        # Add new group in case that channel doesn't fit to current group
        if group and channel - key > dist:
            groups.append((key, group))
            group = []
            key = None

        # Add channel to group
        group.append((channel, count))

        # Pick a new key in case there's none or current channel is within
        # dist from first channel in the group
        if key is None or channel - group[0][0] <= dist:
            key = channel

    # Add last group in case it exists
    if group:
        groups.append((key, group))

    for key, group in groups:
        result[key] = sum(x[1] for x in group)
        replacements[key] = [x[0] for x in group if x[0] != key]

    print("After combining channels, " + str(len(replacements)) + " different colors are needed.")
    
    return result, replacements#min_dist(replacements)#replacements

def combine_channels(lst, max_dist):
    counts = dict()
    replacements = dict()

    for el in lst:
        counts[el] = counts.get(el, 0) + 1
    _, replacements = combine_channels_core(counts, max_dist) 

    for i, el in enumerate(lst):
        for key, val in replacements.items():
            if(el in val):
                lst[i] = key
    return lst
    
def construct_sprite_table(sprite_table_lines, num_digits, num_bits, lst, width):
    clen = len(lst) - 1
    i = 0
    for el in lst:
        entry = str(num_bits) + "'d" + str(int(el)).zfill(num_digits)
        if(i % width == 0):
            sprite_table_lines += "'{"
        if(i == clen):
            sprite_table_lines += entry + "}};\n"
        else:
            if(i % width == width - 1):
                sprite_table_lines += entry + "},\n"
            else:
                sprite_table_lines += entry + ","
        i += 1
    return sprite_table_lines

def split_to_palette(lst, color):
    '''
    
    lst is assumed to be a list of integers corresponding to R, G, or B values.
    
    Create SV module with this structure:
    
    logic [NB - 1:0] palette_index;
    parameter bit [7:0] SpritePaletteR [NB - 1:0] = '{8'h$colors[0], ... , 8'hcolors[NB - 1]};
    parameter bit [NB - 1:0] SpriteTableR [W-1:0,H-1:0] = '{idx(color[0,0]), ...}
    
    '''
    
    global xwidth, ywidth, spritename, footer, outfile
    
    counts = dict() # key is the actual color, value is the count of them
    palette = dict() # key is the hex string, value is the lookup index
    
    footer += "assign Sprite" + color + " = SpritePalette" + color + "[SpriteTable" + color + "[SpriteY][SpriteX]];\n"
    
    for el in lst:
        # el = int(el.strip('\n'), 16)
        # el.strip('\n')
        counts[el] = counts.get(el, 0) + 1
    print("\nColors, with occurences, for the " + color + " channel:\n", counts, "\n")
    
    i = 0
    colors = []
    
    # Replace elements of list with their corresponding lookup values
    for key in counts:
        for idx, item in enumerate(lst):
            if item == key:
                lst[idx] = i # str(i)
        # Fill the palette dictionary (unused)
        palette[key] = i
        # Fill the list of colors
        colors.append("8'd" + str(key))
        i += 1
    num_colors = len(counts)
    
    # Calculate the number of bits needed to represent the number of colors in our palette
    num_bits = math.ceil(math.log2(num_colors))
    num_digits = math.ceil(math.log10(2**num_bits - 1))
    # print("NB, ND:", num_bits, num_digits)
    
    sprite_palette_lines = "parameter bit [7:0] SpritePalette" + color + "[" + str(num_colors - 1) + ":0] = '{"
    
    for swatch in colors:
        sprite_palette_lines += swatch + ", "
    sprite_palette_lines = sprite_palette_lines[:-2] # Strip the last ", "
    sprite_palette_lines += "};\n\n" # End the declaration
    
    # print(sprite_palette_lines)
    
    sprite_table_lines = "parameter bit [" + str(num_bits - 1) + ":0] SpriteTable" + color + "[" + str(ywidth - 1) + ":0][" + str(xwidth - 1) + ":0] = '{"

    # Generate SV code for the sprite table, now with lookup values instead of
    # actual colors.
    clen = len(lst) - 1
    i = 0
    for el in lst:
        entry = str(num_bits) + "'d" + str(el).zfill(num_digits)
        if(i % xwidth == 0):
            sprite_table_lines += "'{"
        if(i == clen):
            sprite_table_lines += entry + "}};\n\n"
        else:
            if(i % xwidth == xwidth - 1):
                sprite_table_lines += entry + "},\n"
            else:
                sprite_table_lines += entry + ","
        i += 1
    # print(sprite_table_lines)
    
    # Write the SV code to the output file
    with open(outfile, 'a+') as f:
       f.write(sprite_palette_lines)
       f.write(sprite_table_lines)

def sprite_table_name(color):
    return "SpriteTable" + color
def sprite_subtable_name(color, i, j):
    return sprite_table_name(color) + "_" + str(i) + "_" + str(j)
def upper_pixel(idx, N, W):
    return min((idx + 1)* N, W)
def conditional_line(table_index, table, NC, NR, color):
    # Create the if/then statement used to index into the proper sprite table.
    # Used only if you're splitting a large sprite table into many smaller sprite tables
    global xwidth, ywidth
    
    i = table_index[0]
    j = table_index[1]
    MinX = i * NC
    MinY = j * NR
    MaxX = upper_pixel(i, NC, xwidth)
    MaxY = upper_pixel(j, NR, ywidth)
    line = "\nif(SpriteX >= 10'd{} && SpriteX < 10'd{} && SpriteY >= 10'd{} && SpriteY < 10'd{})".format(MinX, MaxX, MinY, MaxY)
    line += "\nbegin\n"
    line += " "*4
    line += sprite_table_name(color) + " = " + sprite_subtable_name(color, i, j) + "[Y_Index][X_Index];\n"
    line += "end\nelse"
    return line
def split_sprite_table(lst, color, NC, NR):

    print("\nSplitting image into smaller chunks and generating tables to save fitter resources.")

    global xwidth, ywidth, spritename, footer, outfile
    sprite_tables = dict()
    counts = dict() # key is the actual color, value is the count of them
    palette = dict() # key is the hex string, value is the lookup index
    chunk_sizes = dict()

    footer += "assign Sprite" + color + " = SpritePalette" + color + "[" + sprite_table_name(color) + "];\n"
    
    for el in lst:
        # el = int(el.strip('\n'), 16)
        # el.strip('\n')
        counts[el] = counts.get(el, 0) + 1
    print("\nColors, with occurences, for the " + color + " channel:\n", counts, "\n")
    num_colors = len(counts)
    
    # Calculate the number of bits and digits needed to represent the number of colors in our palette
    num_bits = math.ceil(math.log2(num_colors))
    num_digits = math.ceil(math.log10(2**num_bits - 1))

    # Begin sprite table and palette generation
    
    # Replace elements of list with their corresponding lookup values, populate palette list
    i = 0
    colors = []
    for key in counts:
        for idx, item in enumerate(lst):
            if item == key:
                lst[idx] = i # str(i)
        # Fill the palette dictionary (unused)
        palette[key] = i
        # Fill the list of colors
        colors.append("8'd" + str(key))
        i += 1
    
    # Create entries in sprite table dictionary, loop over tables
    # If the image is divided evenly by the chunk width, loop exactly that number of times.
    # Otherwise loop once more to grab partial chunks.
    # In the dictionary, place a bunch of 0's in the tables, to allow for easy indexing later.
    for i in range(xwidth // NC + (1 if xwidth % NC != 0 else 0)):
        for j in range(ywidth // NR + (1 if ywidth % NR != 0 else 0)):
            if(i == xwidth // NC):
                xdim = xwidth - i * NC
            else:
                xdim = NC
            if(j == ywidth // NR):
                ydim = ywidth - j * NR
            else:
                ydim = NR
            xname = NC * i
            yname = NR * j
            if(xdim != 0 and ydim != 0):
                sprite_tables[(i, j)] = [[0 for m in range(xdim)] for n in range(ydim)]
    # Fill sprite tables dictionary from the list, loop over pixels
    for j in range(ywidth):
        for i in range(xwidth):
            sprite_tables[(i // NC, j // NR)][j % NR][i % NC] = lst[j * xwidth + i]
    
    # Print some information about chunk sizes.
    for (i, j), table in sprite_tables.items():
        (hh, ww) = np.array(table).shape
        chunk_sizes[(hh, ww)] = chunk_sizes.get((hh, ww), 0) + 1
    print("Image chunks have the follow sizes and frequencies:")
    for key, val in chunk_sizes.items():
        print(key, ":", val)
    
    # Create conditional lines, loop over tables
    conditionals = ['\t\t'.join(conditional_line(key, val, NC, NR, color).splitlines(True)) for key, val in sprite_tables.items()]
    modulebody = '\talways_comb\n\tbegin'
    modulebody += '\n\t\t' + sprite_table_name(color) + " = 10'd0;"
    for c in conditionals:
        modulebody += c
    modulebody = modulebody[:modulebody.rfind('\n')]
    modulebody += '\n\tend\n\n'
    
    
    # Generate palette lookup table
    sprite_palette_lines = "parameter bit [7:0] SpritePalette" + color + "[" + str(num_colors - 1) + ":0] = '{"
    
    for swatch in colors:
        sprite_palette_lines += swatch + ", "
    sprite_palette_lines = sprite_palette_lines[:-2] # Strip the last ", "
    sprite_palette_lines += "};\n\n" # End the declaration
    
    # Loop over image chunks and build subtables
    for (i, j), subtable in sprite_tables.items():
        # Converting between Array and List after grabbing the dimensions
        subtable = np.array(subtable)
        subtable_width, subtable_height = subtable.shape
        subtable = list(subtable.reshape(subtable_height*subtable_width, 1))
        # Initializing the Sprite Table
        sprite_table_lines = "parameter bit [" + str(num_bits - 1) + ":0] " + sprite_subtable_name(color, i, j) + "[" + str(subtable_height - 1) + ":0][" + str(subtable_width - 1) + ":0] = '{"
        # Generate SV code for the sprite table, now with lookup values instead of
        # actual colors.
        sprite_table_lines = construct_sprite_table(sprite_table_lines, num_digits, num_bits, subtable, subtable_width)
        modulebody += sprite_table_lines + '\n'
    # Write new lines to the file
    with open(outfile, 'a+') as f:
       f.write("logic [9:0] " + sprite_table_name(color) + ";\n\n")
       f.write(sprite_palette_lines)
       f.write(modulebody)

def clean_raw_list(lst):
    for i, el in enumerate(lst):
        lst[i] = int(el.strip('\n'), 16)
    return lst
    
def generate_palette(color, max_dist, NC, NR):
    global spritename, bytes_dir
    print("\nGenerating palette SystemVerilog for the " + color + " channel:\n")
    fname = bytes_dir + spritename + color + ".txt"
    with open(fname) as f:
        rawlst = f.readlines()
    lst = clean_raw_list(rawlst)
    palette = combine_channels(lst, max_dist)
    # We're using chunking by default, as it's easier for the fitter to optimize chunks as
    # compared to one massive table.
    
    #split_to_palette(palette, color)
    split_sprite_table(palette, color, NC, NR)

def create_sprite_table_channel(color):
    # Use this function to generate a straightforward sprite table of 8 bits wide
    # for each entry. Not recommended anymore, as generate_palette() uses less 
    # hardware resources.
    
    global xwidth, ywidth, spritename, footer, outfile, bytes_dir
    # pretty dirty, but what else are you supposed to use Python for?
    fname = bytes_dir + spritename + color + ".txt"
    with open(fname) as f:
        content = f.readlines()
    footer += "assign Sprite" + color + " = SpriteTable" + color + "[SpriteY][SpriteX];\n"

    sprite_table_lines = "parameter bit [7:0] SpriteTable" + color + "[" + str(ywidth - 1) + ":0][" + str(xwidth - 1) + ":0] = '{"
    # note that in order to index into it normally, you need to put y first? I think. This has worked for us so far.

    i = 0
    # I wanted to increment over the content, so we need an extra variable for keeping track of location.
    clength = len(content) - 1
    for hexval in content:
        hv = "8'h" + str(hexval).strip('\n').zfill(2)
        # left-pad with 0's for consistent width
        if(i % xwidth == 0):
            # start a new row of the array with '{
            sprite_table_lines += "'{"
        if(i == clength):
            # special case for the last element
            sprite_table_lines += hv + "}};\n\n"
        else:
            if(i % xwidth == xwidth - 1):
                # at the end of a row, close it off and print newline
                sprite_table_lines += hv + "},\n"
            else:
                # in the middle of the row, print the hexval and a comma
                sprite_table_lines += hv + ","
        i += 1
    # print(sprite_table_lines)
    with open(outfile, 'a+') as f:
        f.write(sprite_table_lines)

def module_signals(NC, NR):
    sigs = "logic [9:0] X_Index, Y_Index;\n\n"
    sigs += "assign X_Index = SpriteX % 10'd{};\n".format(NC)
    sigs += "assign Y_Index = SpriteY % 10'd{};\n".format(NR)
    return sigs

def create_sv(NC, NR):
    # Generate valid systemverilog code.
    global outfile, header, footer, spritename, compression_level
    with open(outfile, 'w+') as f:
        # This script overwrites the file that currently exists.
        f.write(header)
        f.write(module_signals(NC, NR))
    show_section_msg("Generating SystemVerilog Code...")
    for color in ["R", "G", "B"]:
        generate_palette(color, compression_level, NC, NR)
        # create_sprite_table_channel
    footer += "\nendmodule\n"
    with open(outfile, 'a+') as f:
        f.write(footer)
    show_section_msg("SystemVerilog code generation complete! It's located at: " + outfile)

def test():
    global spritename, bytes_dir
    fname = bytes_dir + spritename + "R" + ".txt"
    with open(fname) as f:
        content = f.readlines()
        #split_to_palette("R", 0)
    lines = []
    for line in content:
        lines.append(int(line.strip('\n'), 16))
    combine_channels(lines, 15)

def create_image():
    # Used to compare the original image to the image
    # after palette generation
    global xwidth, ywidth, spritename, bytes_dir, orig_dir, image_extension, compression_level, image_viewer
    
    ans = input("Would you like to see a comparison of the image before and after compressing it with a palette? (y/N) ").lower()
    if(ans != 'y'):
        return
    show_section_msg("Displaying original and paletted images...")
    print("If nothing shows, try changing the image viewer command name at the top of this script.")
    im1 = Image.open(orig_dir + spritename + image_extension)
    im1.show(command=image_viewer)
    channels = []
    for color in ["R", "G", "B"]:
        print("\nProcessing " + color + " channel...")
        fname = bytes_dir + spritename + color + ".txt"
        with open(fname) as f:
            content = f.readlines()
            #split_to_palette("R", 0)
        lines = clean_raw_list(content)
        channels.append(combine_channels(lines, compression_level))
    #print(channels)
    imdata = list(zip(*channels))
    #print(imdata)
    im2 = Image.new("RGB", (xwidth, ywidth))
    im2.putdata(imdata)
    im2.show(command=image_viewer)
    im2path = orig_dir + spritename + "_filt" + image_extension
    print("Processed image has been saved under: ", im2path)
    im2.save(im2path)
    # input("Press any key to continue.")

def startup():

    global github, orig_dir, sv_dir, image_extension, spritename, outfile, header, footer, xwidth, ywidth, compression_level

    print_pad("="*80, " ", 5)
    print_pad("'conv_to_sv.py', written by Jeremy DeJournett in Fall of 2016 to help make using sprite tables less terrible.", " ", 5)
    print_pad("", " ", 5)
    print_pad("This script assumes you have the directory structure given by: " + github, " ", 5)
    print_pad("", " ", 5)
    print_pad("Script Usage: ", " ", 5)
    print_pad(" 1) Place the image you want to create a sprite table from in: " + orig_dir, " ", 5)
    print_pad(" 2) Run 'png_to_3_txt.py' to get three text files, one for each color channel.", " ", 5)
    print_pad(" 3) Run this script. Supply it with the same name you gave to 'png_to_3_txt.py.", " ", 5)
    print_pad(" 4) It will generate a .sv file with your sprite table in: " + sv_dir, " ", 5)
    print_pad(" 5) You can modify this and the directories at the top of this script if you need to.", " ", 5)
    print_pad("      Extension is currently assumed to be: " + image_extension, " ", 5)
    print_pad(" 6) Instructions for usage and example code will be included as a comment at the top of the output file.", " ", 5)
    print_pad("="*80, " ", 5)

    print("Hint: If you just ran 'png_to_3_txt.py', enter the same sprite name here.")
    spritename = str(input("What's the image name? Don't include the extension: "))
    outfile = sv_dir + spritename + ".sv"
    try:
        im = Image.open(orig_dir + spritename + image_extension)
        xwidth, ywidth = im.size
    except FileNotFoundError:
        print("Could not automatically find the image you're talking about.\nIf you have the output text files, enter the image dimensions manually.")
        xwidth = int(input("What's the sprite's x width in pixels? ")) # These two could be read from Image().size(), for now just set them manually.
        ywidth = int(input("What's the sprite's y width in pixels? "))

    try:
        cl = input("What compression level do you want? Typically the number of resulting colors in a palette is 256/compression_level. (" + str(compression_level) + "): ")
        if(cl != ""):
            cl = int(cl)
            if(cl > 0 and cl < 256):
                compression_level = cl
            else:
                print("Entered compression level is out of range of valid values (1-255). Using default.")
    except ValueError:
        print("What you entered was not a valid compression level. Using default.")
    ans = input("Do you want the usage details to included at the top of the output file? (Y/n) ").lower()
    if(ans == 'n'):
        header = ''
    else:
        header = usage()
    header += "module " + spritename + "(input [9:0] SpriteX, SpriteY,\n"
    header += ' ' * 12 + "output [7:0] SpriteR, SpriteG, SpriteB);\n\n"

    create_image()
    create_sv(8, 8)
startup()

