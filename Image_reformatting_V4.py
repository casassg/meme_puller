# -*- coding: utf-8 -*-
"""
Created on Wed Mar 28 14:32:11 2018

@author: NSing
"""

import pytesseract # need to install using pip
import json
from PIL import Image # need to install Pillow using pip
import numpy as np

'''
******************************
***** USER INPUT SECTION *****
******************************
'''
# input and output are json files
input_file_name = 'reddit_memes_data_hot_100_4_5'
output_file_name = 'reddit_memes_data_hot_100_4_5_fixed'
# must have a folder in dir named: 'fixed_images'  

maximum_text_on_image = 140        # set to 'None' if not wanting to filter these
maximum_text_size_on_image = 0.4   # maximum fraction of the image covered by overall text size
remove_errors = True               # bool, determines whether to keep error images in json

'''
******************************
******* END USER INPUT *******
******************************
'''


class image_fix():
    '''
    Class for reading words off of images and covering words with boxes
    After initializing class, call the 'run()' function to skim through input json file
    '''
    def __init__(self, in_file_name, out_file_name = 'out.json', save_json = True):
        self.json = {}
        self.file_name = in_file_name
        self.save = save_json
        self.output_name = out_file_name
        
        self.read()
        
        self.data_len = len(self.data)
        
    def read(self):
        with open(self.file_name + '.json', 'r') as fp:
            self.data = json.load(fp)

    def fix(self, name, index, save_image = True, show_image = False, verbose = True, max_text = 'None', max_size = 'None'):
        
        # read in meme data and create image instance
        meme = self.data[index]
        save_as = meme['image_name']+'_fix'
        image_loc = meme['image_loc']
        image = Image.open(image_loc)
        
        # get text from image and box coords
        text = pytesseract.image_to_string(image)
        box = pytesseract.image_to_boxes(image)
        text_amount = len(text)
        
        # return error if too much text on image
        if max_text != 'None' and text_amount > max_text:
            meme['text'] = text
            meme['error'] = True
            if verbose: print(' (Too much text on image: '+str(text_amount)+')')
            return meme
        
        # make something useful out of shitty return format for box
        spl = box.split('\n')
        coords = []
        lowercase = 'abcdefghijklmnopqrstuvwxyz'
        uppercase = 'ABCDEFGHIJKLMNOPQRSTUVWXYZ'
        numbers = '1234567890'
        symbols = "!@#$%&:;<>,.?`/\[]{}()^'"+'"'
        allowable_chars = lowercase + uppercase + numbers + symbols
        
        # create list of dictionaries with characters and their coordinates
        if len(box) > 1:
            for line in spl:
                chars = line.split(' '); char = chars[0]
                if char in allowable_chars:
                    coord = {'char': char, 
                             'x_start': chars[1],
                             'x_end': chars[3],
                             'y_start': chars[2],
                             'y_end': chars[4]}
                    coords.append(coord)
            
            # create boxes over characters in image
            fixed_image = image.copy()
            
            # confirm image access
            #if fixed_image.pyaccess:   
            color = (255,255,255) # white boxes
            width, height = fixed_image.size
            erase_error = False
            max_x = 0; min_x = width; max_y = 0; min_y = height;
            for dic in coords:
                if int(dic['x_start']) - 2 > 1 and int(dic['x_end'])+3 < width:
                    x_list = np.arange(int(dic['x_start'])-2, int(dic['x_end'])+2)
                else:
                    x_list = np.arange(int(dic['x_start'])+1, int(dic['x_end'])-1)
                
                if int(dic['y_start']) - 2 > 1 and int(dic['y_end'])+3 < height:
                    y_list = np.arange(int(dic['y_start'])-2, int(dic['y_end'])+2)
                else:
                    y_list = np.arange(int(dic['y_start'])+1, int(dic['y_end'])-1)
                    
                for x in x_list:
                    for y in y_list: # write over pixel with color 
                        try:
                            fixed_image.putpixel( (x, height - y), color)
                        except: 
                            erase_error = True
                
                # get full box around text
                if len(x_list) > 0:
                    if max(x_list) > max_x: max_x = max(x_list)
                    if min(x_list) < min_x: min_x = min(x_list)
                if len(y_list) > 0:
                    if max(y_list) > max_y: max_y = max(y_list)
                    if min(y_list) < min_y: min_y = min(y_list)
            
            # how to handle if text size is too large
            total_area = height*width
            text_area = (max_x - min_x)*(max_y - min_y)
            if max_size != 'None' and (text_area/total_area) > max_size:
                meme['text'] = text
                meme['error'] = True
                meme['text_fraction'] = text_area/total_area
                if verbose: print(' (Text size over limit: %.2f)' % (text_area/total_area))
                return meme
            
            # how to handle problems erasing text
            if erase_error:
                meme['text'] = text
                meme['error'] = True
                if verbose: print(' (Error erasing text in image)')
            else:
                # show image            
                if show_image: fixed_image.show()
                
                # save image
                if save_image:
                    try:
                        save_name = 'fixed_images/'+save_as+'.jpg'
                        fixed_image.save(save_name, 'JPEG')
                    except:
                        meme['error'] = True
                        meme['text'] = text
                        if verbose: print(' (Error saving image as jpg)')
                        return meme
                
                # add new file location and text data to dictionary
                meme['fixed_image_loc'] = save_name
                meme['text'] = text
                meme['error'] = False
                meme['amount_chars'] = text_amount
                meme['text_fraction'] = text_area/total_area

            return meme
#            else: 
#                meme['text'] = 'No access'
#                meme['error'] = True
#                if verbose: print('Invalid access. Skipping')
#                return meme
        else:
            if verbose: print(' (No text found. Skipping)')
            meme['text'] = 'None'
            meme['error'] = True
            return meme
        
    def name_generator(self):
        # generate names for dictionary tags
        length = len(self.data)
        zeros = len(str(length))
        
        # create names
        self.name_list = []
        name_num = np.arange(1, length+1).tolist()
        for num in name_num:
            zero = '0' * (zeros - len(str(num)))
            name = 'meme_'+zero+str(num)
            self.name_list.append(name)
            
    def run(self, exclude_errors = True, verbose = True, troubleshoot_mode = False, max_text = 'None', max_size = 'None'):
        # get name tags
        self.name_generator()
        
        # get image text and fix images
        itt = 1
        name_count = len(self.name_list)
        if verbose: print('Fixing images...')
        if troubleshoot_mode: div = 1
        else: div = 10
        
        for name in self.name_list:
            if verbose and itt % div == 0: print("\r", 'Fixing images: '+str(itt)+' of '+str(name_count), end="")
            meme_dict = self.fix(name, itt-1, verbose = verbose, max_text = max_text, max_size = max_size)
            if exclude_errors and not meme_dict['error']: self.json[name] = meme_dict
            elif not exclude_errors:self.json[name] = meme_dict
            itt += 1
            
        if verbose: print('\nFinished and saving!')
        #save json file output
        if self.save:
            with open(self.output_name+'.json', 'w') as fp:
                json.dump(self.json, fp)
        

im_fix = image_fix(input_file_name, output_file_name)
im_fix.run(exclude_errors = remove_errors, troubleshoot_mode = True, 
           max_text = maximum_text_on_image, max_size = maximum_text_size_on_image)
dictionary = im_fix.__dict__
output = im_fix.json

# double check it's not overprinting 
with open(output_file_name + '.json', 'r') as fp:
    re_data = json.load(fp)








''' Troubleshoot specific errors  '''
troubleshooting = False
name = 'meme_067'

if troubleshooting:
    # open file
    with open(input_file_name + '.json', 'r') as fp:
        data = json.load(fp)
    
    # read in meme data and create image instance
    meme = data[name]
    image_loc = meme['image_loc']
    image = Image.open(image_loc)
    title = meme['title']
    
    image.show()
    
    # get text from image and box coords
    text = pytesseract.image_to_string(image)
    box = pytesseract.image_to_boxes(image)
    
    # is there text? if not add key to specify (screen later) ---- already done above using Error
    if len(text.split(' ')) < 2: no_text = True
    else: no_text = False
    
    # make something useful out of shitty return format for box
    spl = box.split('\n')
    coords = []
    lowercase = 'abcdefghijklmnopqrstuvwxyz'
    uppercase = 'ABCDEFGHIJKLMNOPQRSTUVWXYZ'
    numbers = '1234567890'
    symbols = "!@#$%&:;<>,.?`/\[]{}()^'"+'"'
    allowable_chars = lowercase + uppercase + numbers + symbols
    
    # create list of dictionaries with characters and their coordinates
    if len(box) > 1:
        for line in spl:
            chars = line.split(' '); char = chars[0]
            if char in allowable_chars:
                coord = {'char': char, 
                         'x_start': chars[1],
                         'x_end': chars[3],
                         'y_start': chars[2],
                         'y_end': chars[4]}
                coords.append(coord)
    
        # create boxes over characters in image
        fixed_image = image.copy()
        
        # confirm image access   
        color = (255,255,255) # white boxes
        width, height = fixed_image.size
        erase_error = False
        for dic in coords:
            if int(dic['x_start']) - 2 > 1 and int(dic['x_end'])+3 < width:
                x_list = np.arange(int(dic['x_start'])-2, int(dic['x_end'])+2)
            else:
                x_list = np.arange(int(dic['x_start'])+1, int(dic['x_end'])-1)
            
            if int(dic['y_start']) - 2 > 1 and int(dic['y_end'])+3 < height:
                y_list = np.arange(int(dic['y_start'])-2, int(dic['y_end'])+2)
            else:
                y_list = np.arange(int(dic['y_start'])+1, int(dic['y_end'])-1)
            
            for x in x_list:
                for y in y_list: # write over pixel with color 
                    try:
                        fixed_image.putpixel( (x, height - y), color)
                    except: 
                        erase_error = True
        if erase_error:
            print('Error erasing text in image.')

        
        # show image            
        fixed_image.show()


