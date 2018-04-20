# -*- coding: utf-8 -*-
"""
Created on Wed Mar 28 14:32:11 2018

@author: NSing
"""

import json
import logging
from multiprocessing.dummy import Pool as ThreadPool

import numpy as np
import pytesseract  # need to install using pip
from PIL import Image  # need to install Pillow using pip

'''
******************************
***** USER INPUT SECTION *****
******************************
'''
# input and output are json files
input_file_name = 'reddit_memes_data_top_month_5_4_2'
output_file_name = 'reddit_memes_data_top_month_5_4_2_fixed'

# must have a folder in dir named: 'fixed_images'  
'''
******************************
******* END USER INPUT *******
******************************
'''

logging.basicConfig(
    format='%(thread)d:%(levelname)s:%(message)s',
    level=logging.INFO
)


class ImageFix:
    '''
    Class for reading words off of images and covering words with boxes
    After initializing class, call the 'run()' function to skim through input json file
    '''

    def __init__(self, in_file_name, out_file_name='out.json', save_json=True):
        self.json = {}
        self.file_name = in_file_name
        self.save = save_json
        self.output_name = out_file_name
        self.data = {}

        with open(self.file_name + '.json', 'r') as fp:
            self.data = json.load(fp)

    def fix(self, meme, save_image=False, show_image=False):

        # read in meme data and create image instance
        save_as = meme['image_file_name'] + '_fix'
        image_loc = meme['image_loc']
        image = Image.open(image_loc)

        # get text from image and box coords
        text = pytesseract.image_to_string(image)
        box = pytesseract.image_to_boxes(image)

        # make something useful out of shitty return format for box
        spl = box.split('\n')
        coords = []
        lowercase = 'abcdefghijklmnopqrstuvwxyz'
        uppercase = 'ABCDEFGHIJKLMNOPQRSTUVWXYZ'
        numbers = '1234567890'
        symbols = "!@#$%&:;<>,.?`/\[]{}()^'" + '"'
        allowable_chars = lowercase + uppercase + numbers + symbols

        # create list of dictionaries with characters and their coordinates
        if len(box) > 1:
            for line in spl:
                chars = line.split(' ')
                char = chars[0]
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
            # if fixed_image.pyaccess:
            color = (255, 255, 255)  # white boxes
            width, height = fixed_image.size
            for dic in coords:
                if int(dic['x_start']) - 2 > 1 and int(dic['x_end']) + 3 < width:
                    x_list = np.arange(int(dic['x_start']) - 2, int(dic['x_end']) + 2)
                else:
                    x_list = np.arange(int(dic['x_start']) + 1, int(dic['x_end']) - 1)

                if int(dic['y_start']) - 2 > 1 and int(dic['y_end']) + 3 < height:
                    y_list = np.arange(int(dic['y_start']) - 2, int(dic['y_end']) + 2)
                else:
                    y_list = np.arange(int(dic['y_start']) + 1, int(dic['y_end']) - 1)

                for x in x_list:
                    for y in y_list:  # write over pixel with color
                        xy = (x, (height - y))
                        fixed_image.putpixel(xy, color)

            # show image
            if show_image:
                fixed_image.show()

            # save image
            save_name = None
            if save_image:
                save_name = 'fixed_images/' + save_as + '.png'
                fixed_image.save(save_name, 'PNG')

            # add new file location and text data to dictionary
            meme['fixed_image_loc'] = save_name
            meme['text'] = text
            meme['error'] = False
            return meme
        # else:
        #                meme['text'] = 'No access'
        #                meme['error'] = True
        #                if verbose: print('Invalid access. Skipping')
        #                return meme
        else:

            logging.warning('No text found. Skipping')
            meme['text'] = 'None'
            meme['error'] = True
            return meme

    def run(self):
        logging.info('Fixing images...')
        pool = ThreadPool()
        fixed_items = pool.map(self.fix, self.data)
        # fixed_items = [self.fix(item) for item in self.data]
        logging.info('Finished and saving!')
        # save json file output
        if self.save:
            with open(self.output_name + '.json', 'w') as fp:
                json.dump(fixed_items, fp)


if __name__ == '__main__':

    im_fix = ImageFix(input_file_name, output_file_name)
    im_fix.run()

    ''' Troubleshoot specific errors  '''
    troubleshooting = False

    if troubleshooting:
        # open file
        with open(input_file_name + '.json', 'r') as fp:
            data = json.load(fp)

        # read in meme data and create image instance
        meme = data[0]
        image_loc = meme['image_loc']
        image = Image.open(image_loc)

        image.show()

        # get text from image and box coords
        text = pytesseract.image_to_string(image)
        box = pytesseract.image_to_boxes(image)

        # make something useful out of shitty return format for box
        spl = box.split('\n')
        coords = []
        lowercase = 'abcdefghijklmnopqrstuvwxyz'
        uppercase = 'ABCDEFGHIJKLMNOPQRSTUVWXYZ'
        numbers = '1234567890'
        symbols = "!@#$%&:;<>,.?`/\[]{}()^'" + '"'
        allowable_chars = lowercase + uppercase + numbers + symbols

        # create list of dictionaries with characters and their coordinates
        if len(box) > 1:
            for line in spl:
                chars = line.split(' ')
                char = chars[0]
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
            color = (255, 255, 255)  # white boxes
            width, height = fixed_image.size
            erase_error = False
            for dic in coords:
                if int(dic['x_start']) - 2 > 1 and int(dic['x_end']) + 3 < width:
                    x_list = np.arange(int(dic['x_start']) - 2, int(dic['x_end']) + 2)
                else:
                    x_list = np.arange(int(dic['x_start']) + 1, int(dic['x_end']) - 1)

                if int(dic['y_start']) - 2 > 1 and int(dic['y_end']) + 3 < height:
                    y_list = np.arange(int(dic['y_start']) - 2, int(dic['y_end']) + 2)
                else:
                    y_list = np.arange(int(dic['y_start']) + 1, int(dic['y_end']) - 1)

                for x in x_list:
                    for y in y_list:  # write over pixel with color
                        try:
                            fixed_image.putpixel((x, height - y), color)
                        except:
                            erase_error = True
            if erase_error:
                print('Error erasing text in image.')

            # show image
            fixed_image.show()
