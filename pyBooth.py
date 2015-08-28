#! /usr/bin/env python

import sys
import time
import pygame
import os
import argparse
import math
from watchdog.observers import Observer
from watchdog.events import PatternMatchingEventHandler
from subprocess import Popen
from pygame.locals import *

last_image = None
new_image = False

startimg = None
countdownimgs = []
flashimg = None

photo_event = pygame.USEREVENT + 1

class Button:
    """ a simple button class to hold all the attributes together and draw itself """    
    
    def __init__(self, rect=pygame.Rect(0,0,0,0), color=pygame.Color('WHITE'), caption='Button'):
        self.rect = rect
        self.color = color
        self.caption = caption
        self.fsize = 36
        
    def draw(self, surface):
        surface.fill(self.color, rect=self.rect)
        if (pygame.font):
            font = pygame.font.Font(None, self.fsize)
            text = font.render(self.caption,0,pygame.Color('BLACK'))
            textpos = text.get_rect(center=self.rect.center)
            surface.blit(text,textpos)
        
def load_resources():
    base_path = './gfx/'
    startimg = pygame.image.load(base_path + 'start.png')
    countdownimgs.append(pygame.image.load(base_path + '10.png'))
    countdownimgs.append(pygame.image.load(base_path + '9.png'))
    countdownimgs.append(pygame.image.load(base_path + '8.png'))
    countdownimgs.append(pygame.image.load(base_path + '7.png'))
    countdownimgs.append(pygame.image.load(base_path + '6.png'))
    countdownimgs.append(pygame.image.load(base_path + '5.png'))
    countdownimgs.append(pygame.image.load(base_path + '4.png'))
    countdownimgs.append(pygame.image.load(base_path + '3.png'))
    countdownimgs.append(pygame.image.load(base_path + '2.png'))
    countdownimgs.append(pygame.image.load(base_path + '1.png'))
    flashimg = pygame.image.load(base_path + 'flash.png')

def draw_buttons(surface, sw, sh):
    color = pygame.Color('#ee4000')
    btnwidth = 250
    btnheight = 50
    margin = (sw - (2 * btnwidth)) / 3
    btnleft = Button(pygame.Rect(margin, sh-btnheight, btnwidth, btnheight), color, 'Start')
    btnright = Button(btnleft.rect.move(btnwidth + margin,0), color, 'Print')
    btnleft.draw(surface)
    btnright.draw(surface)
    

def get_image(path):
    
    canonicalized_path = path.replace('/', os.sep).replace('\\', os.sep)
    image = pygame.image.load(canonicalized_path)
            
    return image

def aspect_scale(img,(bx,by)):
    """ Scales 'img' to fit into box bx/by.
     This method will retain the original image's aspect ratio """
    ix,iy = img.get_size()
    if ix > iy:
        # fit to width
        scale_factor = bx/float(ix)
        sy = scale_factor * iy
        if sy > by:
            scale_factor = by/float(iy)
            sx = scale_factor * ix
            sy = by
        else:
            sx = bx
    else:
        # fit to height
        scale_factor = by/float(iy)
        sx = scale_factor * ix
        if sx > bx:
            scale_factor = bx/float(ix)
            sx = bx
            sy = scale_factor * iy
        else:
            sy = by
            
    sx = int(sx)
    sy = int(sy)

    return pygame.transform.scale(img, (sx,sy))
    


class MyHandler(PatternMatchingEventHandler):
    patterns=["*.jpg", "*.JPG"]

    def process(self, event):
        """
        event.event_type
            'modified' | 'created' | 'moved' | 'deleted'
        event.is_directory
            True | False
        event.src_path
            path/to/observed/file
        """

        print "got something"
        print event.src_path, event.event_type
        global last_image
        global new_image
        print "loading image"
        last_image = aspect_scale(get_image(event.src_path), (x,y)).convert()
        new_image = True
        print "done loading"

    
    def on_created(self, event):
        self.process(event)

    def on_modified(self, event):
        self.process(event)



if __name__ == '__main__':
    args = sys.argv[1:]

    parser = argparse.ArgumentParser()
    parser.add_argument("--width", type=int, help="screen width", default=1024)
    parser.add_argument("--height", type=int, help="screen height", default=768)
    parser.add_argument("--path", help="path to observe", default=".")
    parser.add_argument("--fullscreen", "-f", action='store_true', help="run in fullscreen")
    args = parser.parse_args()
    x = args.width
    y = args.height
    path = args.path
    fullscreen = args.fullscreen
    
    load_resources()    
    
    observer = Observer()
    observer.schedule(MyHandler(), path)
    observer.start()   

    pygame.init()
    if(fullscreen):
        screen = pygame.display.set_mode((x, y), FULLSCREEN)
    else:
        screen = pygame.display.set_mode((x, y))
        
    pygame.mouse.set_visible(False)
    done = False
    clock = pygame.time.Clock()

    def end_script():
        print "exit"
        global done        
        done = True
        observer.stop()
        observer.join()
   
   
   
    
    first_run=True
    cnt_id = 0
    #global photo_event
    #global countdownimgs
    #global startimg
    #global flashimg

    while not done:
        for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    end_script()
                if event.type == KEYDOWN and event.key == K_ESCAPE: 
                    end_script()
                if event.type == KEYDOWN and event.key == K_SPACE:
                    screen.blit(countdownimgs[cnt_id], (0, 0))
                    cnt_id = cnt_id + 1
                    pygame.time.set_timer(photo_event, 1000)
                    pygame.display.flip()
                    #sub = Popen(['gphoto2','--capture-image-and-download'])
            
                if event.type == photo_event:
                    screen.blit(countdownimgs[cnt_id], (0, 0))                    
                    if (cnt_id >=10):
                        screen.blit(flashimg, (0, 0))
                        cnt_id = 0
                        pygame.time.set_timer(photo_event, 0)
                    cnt_id = cnt_id + 1
                    pygame.display.flip()
                    
        
        
        if(last_image and new_image):
            print "blitting image"
            screen.blit(last_image, (0, 0))
            new_image = False
            print "done blitting"
            draw_buttons(screen, x, y)
            
            pygame.display.flip()
           
        if(not last_image and first_run):            
            screen.blit(startimg, (0, 0))
            first_run=False
            draw_buttons(screen, x, y)
            pygame.display.flip()
        
        clock.tick(60)   


    
