import os, sys, math
import pygame
from pygame.locals import *
from time import sleep
#enable double buffering for better performance
flags = DOUBLEBUF
from twisted.internet.protocol import ClientFactory
from twisted.internet.protocol import Factory
from twisted.internet.protocol import Protocol
from twisted.application.internet import ClientService
from twisted.internet import reactor
from twisted.internet.defer import DeferredQueue
from time import sleep
import os
import sys
from twisted.python import log
from threading import Thread
log.startLogging(sys.stdout)

c_made = False

enemy_x = 10
enemy_y = 10

########## COMMAND CONNECTION ##################
class MyCommandConnection(Protocol):
    def connectionMade(self):
        self.transport.write("W: message: hi!\n".encode('utf-8'))
        print("connectionmade")
        global c_made
        c_made = True
        global connection
        connection = self.transport
        
    def dataReceived(self, data):
        global enemy_x
        global enemy_y
        data = data.split(b":")
        if data[0] == b"XY":
            print("changing x and y...")
            enemy_x = int(data[1])
            enemy_y = int(data[2].strip(b'XY').strip(b'S'))
            print(enemy_x)
            print(enemy_y)
        elif data[0] == b"S":
            global light_size
            light_size = int(data[1].strip(b'S').strip(b'XY'))
        print("got data:")

class MyCommandConnectionFactory(Factory):
    def __init__(self):
        self.myconn = MyCommandConnection()

    def buildProtocol(self, addr):
        return self.myconn
########### COMMAND CONNECTION ##################





class DeathStar:
    def __init__(self):
        self.src = "/home/scratch/paradigms/deathstar/deathstar.png"
        self.star = pygame.image.load(self.src).convert()
        self.star = pygame.transform.scale(self.star, (50, 50))
        self.star.set_colorkey(-1, RLEACCEL)
        self.star_rect = self.star.get_rect()
        self.star_rect.x = 0
        self.star_rect.y = 0

class SpotLight:
    def __init__(self):
        self.src = "./spotlight2.png"
        self.light = pygame.image.load(self.src).convert()
        self.light = pygame.transform.scale(self.light, (100, 100))
        self.light_rect = self.light.get_rect()

class GameSpace:
    def sendSelfXY(self, x, y):
        global connection
        connection.write("xy:{}:{}".format(x, y).encode('utf-8'))
        
    def main(self):
        global light_size
        r_val = 100 # red value of player
        max_light = 125 # maximum diameter of spotlight
        light_size = max_light # light_size changes when light shined on player
        old_pos = [0, 0] # to detect change in mouse position
        old_rects = [] # to track rects that need to be black filled

        pygame.init()
        self.width = 1280
        self.height = 840
        self.black = 0,0,0
        self.character = r_val, 0, 0 # character is square plain color
        self.size = self.width, self.height
        self.screen = pygame.display.set_mode(self.size, flags)
        self.star = DeathStar()
        self.light = SpotLight()
        self.light0 = SpotLight()
        self.star.star_rect.x = 150
        self.star.star_rect.y = 150
        global c_made
        if c_made:
            self.sendSelfXY(150, 150)
        self.clock = pygame.time.Clock()
        self.screen.set_alpha(None) # speed up performance
        pygame.event.set_allowed([QUIT, KEYDOWN, KEYUP]) # better performance
        self.mouse_down = False
        old_light = self.light.light_rect
        Thread(target=reactor.run, args=(False, )).start()
        while 1:
            self.clock.tick(60)
            for event in pygame.event.get():
                if event.type == KEYDOWN:
                    if event.key == K_LEFT:
                        self.star.star_rect.x -= 50
                        if self.star.star_rect.x < 20:
                            self.star.star_rect.x = 20
                    if event.key == K_RIGHT:
                        self.star.star_rect.x += 50
                        if self.star.star_rect.x > self.width-20:
                            self.star.star_rect.x = self.width-20
                    if event.key == K_UP:
                        self.star.star_rect.y -= 50
                        if self.star.star_rect.y < 20:
                            self.star.star_rect.y = 20
                    if event.key == K_DOWN:
                        self.star.star_rect.y += 50
                        if self.star.star_rect.y > self.height-20:
                            self.star.star_rect.y = self.height-20
                    global c_made
                    if c_made:
                        self.sendSelfXY(self.star.star_rect.x, self.star.star_rect.y)
                        print("sending {}, {}".format(self.star.star_rect.x, self.star.star_rect.y))
                    else:
                        print("not connection")
                if event.type == pygame.MOUSEBUTTONDOWN:
                    light_size -= 70
                    if light_size < 10:
                        light_size = 10
                    self.mouse_down = True
                    if rect.colliderect(self.light.light_rect):
                        print("WINNER WINNER CHICKEN DINNER!!!!!")
                if event.type == pygame.MOUSEBUTTONUP:
                    self.mouse_down = False
            pos = pygame.mouse.get_pos()
            global enemy_x
            global enemy_y
            self.light.light_rect.x = enemy_x
            self.light.light_rect.y = enemy_y
            rot_star = self.star.star
            rect = rot_star.get_rect(center=(self.star.star_rect.x, self.star.star_rect.y))
            self.screen.fill(self.black)

            self.light.light = pygame.transform.scale(self.light0.light, (light_size, light_size))
            s = pygame.display.get_surface()
            self.light.light_rect = self.light.light.get_rect(center=(self.light.light_rect.x, self.light.light_rect.y))
            active_rects = []
            s.fill(self.black, old_light)
            self.screen.blit(self.light.light, self.light.light_rect)
            self.screen.blit(rot_star, rect)

            # red value of character will change if spotlight shined
            self.character = 0, 250, 250
            s.fill(self.character, rect)
            active_rects.append(rect)
            active_rects.append(self.light.light_rect)

            # spotlight diamerter decreases as player moves mouse, then goes back to full size when player stops moving mouse
            if old_pos[0] != pos[0] or old_pos[1] != pos[1]:
                light_size -= 1
            else:
                light_size += 2
            if light_size > max_light:
                light_size = max_light

            if light_size < 10:
                light_size = 10

            active_rects.append(old_light)
            for ac_rect in active_rects:
                pygame.display.update(ac_rect)
            old_rects = active_rects[:] 
            old_pos = pos
            old_light = self.light.light.get_rect(center=(self.light.light_rect.x+light_size/2+1, self.light.light_rect.y+light_size/2+1))

if __name__=='__main__':
    reactor.listenTCP(10130, MyCommandConnectionFactory())
    gs = GameSpace()
    gs.main()
