import os, sys, math
import pygame
from pygame.locals import *
from time import sleep
#enable double buffering for better performance
flags = DOUBLEBUF
from twisted.internet.protocol import ClientFactory
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

enemy_x = 150
enemy_y = 150
stations = []
c_made = False
rec_stations = False
received_play = False
received_quit = False
lost_display = False
########## COMMAND CONNECTION ##################
class MyCommandConnection(Protocol):
    def connectionMade(self):
        global connection
        global c_made
        c_made = True
        connection = self.transport
        self.transport.write("blahblah!\n".encode('utf-8'))

    def dataReceived(self, datam):
        #print("got data:".encode('utf-8'))
        global enemy_x
        global enemy_y
        datam = datam.split(b"#")
        #print(datam[0])
        for data in datam:
            data = data.split(b":")
            if data[0] == b"xy":
                enemy_x = int(data[1])
                enemy_y = int(data[2].strip(b'xy').strip(b's'))
            elif data[0] == b"s":
                global rec_stations
                global stations
                rec_stations = True
                station_x = []
                station_y = []
                st_rect = Rect(int(data[1]), int(data[2]), 70, 70)
                stations.append(st_rect)
            elif data[0] == b"W":
                global lost_display = True
                print("YOU LOST")
            elif data[0] == b"Q":
                global received_quit
                global received_play
                if data[1] == b"q":
                    received_quit = True
                else:
                    received_play = True

class MyCommandConnectionFactory(ClientFactory):
    def __init__(self):
        self.myconn = MyCommandConnection()

    def buildProtocol(self, addr):
        return self.myconn

########## COMMAND CONNECTION ##################





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
    def sendXY(self, x, y):
        global connection
        connection.write("XY:{}:{}".format(x, y).encode('utf-8'))

    def sendSize(self, size):
        global connection
        connection.write("S:{}".format(size).encode('utf-8'))
    
    def sendWon(self):
        global connection
        connection.write("W".encode('utf-8'))

    def sendStatus(self, status):
        global connection
        connection.write("Q:{}".format(status).encode('utf-8'))

    def main(self):
        while (1):
            again = self.game()
            if not again:
                break

    def game(self):
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
        self.clock = pygame.time.Clock()
        self.screen.set_alpha(None) # speed up performance
        pygame.event.set_allowed([QUIT, KEYDOWN, KEYUP]) # better performance
        self.mouse_down = False
        old_light = self.light.light_rect
        Thread(target=reactor.run, args=(False, )).start()
        win_display = False
        global received_play
        global received_quit
        while 1:
            self.clock.tick(60)
            global enemy_x
            global enemy_y
            self.star.star_rect.x = enemy_x
            self.star.star_rect.y = enemy_y
            for event in pygame.event.get():
                if event.type == pygame.MOUSEBUTTONDOWN:
                    light_size -= 70
                    if light_size < 10:
                        light_size = 10
                    self.mouse_down = True
                    if rect.colliderect(self.light.light_rect) and c_made:
                        self.sendWon()
                        print("WINNER WINNER CHICKEN DINNER!!!!!")
                        win_display = True
                if event.type == pygame.MOUSEBUTTONUP:
                    self.mouse_down = False
            pressed = pygame.key.get_pressed()
            if win_display and pressed[pygame.K_q]:
                self.sendStatus("q")
                return 0
            if win_display and pressed[pygame.K_p]:
                self.sendStatus("p")
                return 1
            pos = pygame.mouse.get_pos()
            self.light.light_rect.x = pos[0]
            self.light.light_rect.y = pos[1]
            rot_star = self.star.star
            rect = rot_star.get_rect(center=(self.star.star_rect.x, self.star.star_rect.y))
            self.screen.fill(self.black)

            self.light.light = pygame.transform.scale(self.light0.light, (light_size, light_size))
            s = pygame.display.get_surface()
            self.light.light_rect = self.light.light.get_rect(center=(self.light.light_rect.x, self.light.light_rect.y))
            active_rects = []
            active_rects.append(rect)
            s.fill(self.black, old_light)
            self.screen.blit(self.light.light, self.light.light_rect)
            self.screen.blit(rot_star, rect)
            if c_made:
                self.sendSize(light_size)

            # red value of character will change if spotlight shined
            if not rect.colliderect(self.light.light_rect):
                s.fill(self.character, rect)
                if r_val < 0:
                    r_val = 0
                if r_val > 255:
                    r_val = 255
                self.character = r_val, 0, 0
                r_val -= 50
            else:
                r_val += 5
                if r_val > 255:
                    r_val = 255
                if r_val < 0:
                    r_val = 0
                self.character = r_val, 0, 0
                s.fill(self.character, rect)
            active_rects.append(self.light.light_rect)

            # spotlight diamerter decreases as player moves mouse, then goes back to full size when player stops moving mouse
            if old_pos[0] != pos[0] or old_pos[1] != pos[1]:
                global c_made
                if c_made:
                    print("changin x and y")
                    self.sendXY(pos[0], pos[1])
                else:
                    print("connection not made")
                light_size -= 1
            else:
                light_size += 2
            if light_size > max_light:
                light_size = max_light

            if light_size < 10:
                light_size = 10
        
            global rec_stations
            global stations
       

            for st in stations:
                self.square = 0, 250, 250
                s.fill(self.square, st)
                active_rects.append(st)
                rec_stations = False

            active_rects.append(old_light)
            for ac_rect in active_rects:
                pygame.display.update(ac_rect)
            old_rects = active_rects[:] 
            old_pos = pos
            old_light = self.light.light.get_rect(center=(self.light.light_rect.x+light_size/2+1, self.light.light_rect.y+light_size/2+1))
            global lost_display
            if lost_display:
                pygame.font.init()
                myfont2 = pygame.font.SysFont('Comic Sans MS', 50)
                textsurface = myfont.render("Sorry. You've Lost!", True, (0,250,250))
                self.screen.blit(textsurface, (250,250))
                pygame.display.flip() 
            elif win_display:
                pygame.font.init()
                myfont = pygame.font.SysFont('Comic Sans MS', 30)
                textsurface = myfont.render("Congratulations. You've won!", True, (0,250,250))
                myfont2 = pygame.font.SysFont('Comic Sans MS', 50)
                textsurface2 = myfont.render("Press q to quit. Press p to play again.", True, (0,250,250))
                self.screen.blit(textsurface, (250,250))
                self.screen.blit(textsurface2, (250,350))
                pygame.display.flip()
                

if __name__=='__main__':
    global connection
    reactor.connectTCP("ash.campus.nd.edu", 10132, MyCommandConnectionFactory())
    gs = GameSpace()
    gs.main()
    pygame.quit()

