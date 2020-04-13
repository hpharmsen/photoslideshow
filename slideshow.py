#!/usr/bin/env python
#
#  Naar de basis van Corey Goldberg https://github.com/cgoldberg/py-slideshow
#  License: GPLv3

import argparse
import random
import os
import sys
import time

from configparser import ConfigParser
from PIL import ExifTags, Image

import pyglet
from pyglet.window import key

FILETYPES = (
    '.bmp',
    '.dib',
    '.dcx',
    '.gif',
    '.im',
    '.jpg',
    '.jpe',
    '.jpeg',
    '.pcd',
    '.pcx',
    '.png',
    '.pbm',
    '.pgm',
    '.ppm',
    '.psd',
    '.tif',
    '.tiff',
    '.xbm',
    '.xpm',
)


def adjust_rotation(image_file):
    # Even kijken (met PIL) of img geroteerd moet worden.
    PILimg = Image.open(image_file)
    try:
        exif = dict((ExifTags.TAGS[k], v) for k, v in PILimg._getexif().items() if k in ExifTags.TAGS)
        orientation = exif.get('Orientation', 1)
    except (KeyError, AttributeError):
        orientation = 1
    if orientation in (3, 6, 8):
        if orientation == 3:
            PILimg = PILimg.rotate(180, expand=True)
        elif orientation == 6:
            PILimg = PILimg.rotate(270, expand=True)
        else:  # orientation == 8
            PILimg = PILimg.rotate(90, expand=True)
        try:
            PILimg.save(image_file)
        except:
            pass


class Photo:
    def __init__(self, window, image_file, animate, time_per_picture=None):
        self.window = window
        adjust_rotation(image_file)
        self.image_file = image_file
        pyglet_image = pyglet.image.load(image_file)

        self.width = pyglet_image.width
        self.height = pyglet_image.height
        self.sprite = pyglet.sprite.Sprite(pyglet_image)

        self.sprite.x = 0
        self.sprite.y = 0
        self.time_per_picture = time_per_picture

        self.direction = 'None'
        if self.width / self.height < window.width / window.height:
            self.direction = 'Vertical'
            if not animate:
                self.sprite.scale = window.height / self.height * 1.2 # 20% greater than window height
                self.sprite.y = (window.height - self.height * self.sprite.scale) / 2
                self.sprite.x = (window.width - self.width * self.sprite.scale) / 2
            else:
                self.sprite.scale = float(window.width) / self.width
                self.pan_dist = self.height * self.sprite.scale - window.height
                self.sprite.y = window.height - self.height * self.sprite.scale
        else:  # Landscape mode
            self.direction = 'Horizontal'
            if not animate:
                self.sprite.scale = window.width / self.width * 1.2
                self.sprite.x = (window.width - self.width * self.sprite.scale) / 2
                self.sprite.y = (window.height - self.height * self.sprite.scale) / 2
            else:
                self.sprite.scale = float(window.height) / self.height
                self.pan_dist = self.width * self.sprite.scale - window.width

        image_dir = image_file.split('/')[-2]
        try:
            year = int(image_dir[:4])
            name = image_dir[5:]
            if name.lower() == 'diversen':
                image_dir = str(year)
            else:
                image_dir = name + ', ' + str(year)
        except:
            pass
        self.label = pyglet.text.Label(image_dir,
                                  font_name='Times New Roman',
                                  font_size=24,
                                  x=window.width - 10, y= 30 ,
                                  anchor_x='right', anchor_y='center')

        self.start_time = time.time()

    def update_pan(self):
        if self.direction == 'None':
            return
        elapsed_time = time.time() - self.start_time
        fraction = min(1, elapsed_time / self.time_per_picture)
        if self.direction == 'Horizontal':
            self.sprite.x = -fraction * self.pan_dist
        else:
            self.sprite.y = fraction * self.pan_dist + window.height - self.height * self.sprite.scale

    def update_zoom(self):
        self.sprite.scale += 0.0002

    def draw(self):

        self.sprite.draw()
        elapsed_time = time.time() - self.start_time
        if self.time_per_picture - elapsed_time < 2:
            self.label.draw()

class Show:
    def __init__(self, config):
        self.images = self.load(config['imagedir'])
        self.paused = False
        self.config = config

    def load(self, mainpath):
        image_file = 'images.txt'
        if os.path.isfile(image_file):
            with open(image_file) as f:
                images = f.read().split('\n')
                if images and images[0] == mainpath:
                    return images[1:]
        # parse the files
        images = [
            os.path.abspath(os.path.join(path, name))
            for path, subdirs, files in os.walk(mainpath)
            for name in files
            if name.endswith(FILETYPES)
        ]
        with open(image_file, 'w') as f:
            f.write("\n".join([mainpath] + images))
        return images

    def new_image(self, img_path=None):
        if not img_path:
            if self.paused:
                return
            img_path = random.choice(self.images)
        photo = Photo(window, img_path, self.config['animate'], self.config['time_per_picture'])
        window.clear()
        return photo


# Initialize Pyglet here..
debugging = getattr(sys, 'gettrace', None)()
window = pyglet.window.Window(fullscreen=True and not debugging)


@window.event
def on_draw():
    cur_photo.draw()


@window.event
def on_key_press(symbol, modifiers):
    global paused
    if symbol == key.Q:
        sys.exit()
    if symbol == key.RIGHT:
        paused = True
        show.new_image()
    elif symbol == key.LEFT:
        # paused = True
        # update_image( )  # Hier iets met lijst van laatste getoonde imgs.
        pass
    elif symbol == key.SPACE:
        paused = not paused


def update_pan(dt):
    # dt is tijd sinds laatste update_pan
    global cur_photo
    cur_photo.update_pan()


def update_zoom(dt):
    global cur_photo
    cur_photo.update_zoom()


def new_image(time):
    global cur_photo
    cur_photo = show.new_image()


if __name__ == '__main__':
    parser = ConfigParser()
    parser.read(os.path.join(os.path.dirname(os.path.abspath(__file__)),'slideshow.ini'))
    ini = parser['slideshow']
    imagedir = ini.get('imagedir')

    if not imagedir:
        assert len(sys.argv) > 1, 'Spcify image directory in slideshow.ini or pass it as a parameter'
        parser = argparse.ArgumentParser()
        parser.add_argument('dir', help='directory of images', nargs='?', default=os.getcwd())
        args = parser.parse_args()
        imagedir = args.dir

    config = {'imagedir':imagedir,
              'time_per_picture': float(ini.get('time_per_picture',7)),
              'animate': int(ini.get('animate',1)),
              'framerate': float(ini.get('framerate',60))
    }

    show = Show(config)

    cur_photo = show.new_image()
    pyglet.clock.schedule_interval(new_image, config['time_per_picture'])
    if config['animate']:
        pyglet.clock.schedule_interval(update_pan, 1 / config['framerate'])
        pyglet.clock.schedule_interval(update_zoom, 1 / config['framerate'])

    pyglet.app.run()
