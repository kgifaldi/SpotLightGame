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
from random import randint
from twisted.python import log
from threading import Thread
log.startLogging(sys.stdout)

c_made = False
stations_sent = False
lost = False

enemy_x = 10
enemy_y = 10

stations = []
s_colors = [1, 1, 1, 1, 1, 1, 1, 1, 1, 1]
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
            print("chaning x_y")
            enemy_x = int(data[1])
            enemy_y = int(data[2].strip(b'XY').strip(b'S'))
        elif data[0] == b"S":
            global light_size
            light_size = int(data[1].strip(b'S').strip(b'XY'))
        elif data[0] == b"W":
            global lost
            lost = True
            print("YOU LOST!")

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
        connection.write("xy:{}:{}#".format(x, y).encode('utf-8'))
       
    def sendStation(self, x, y): #x2, y2, x3, y3, x4, y4, x5, y5, x6, y6, x7, y7, x8, y8):
        global connection
        connection.write("s:{}:{}#".format(x, y).encode('utf-8'))

    def sendColor(self, num, col):
        global connection
        connection.write("c:{}:{}#".format(num, col).encode('utf-8'))

    def sendWon():
        global connection
        connection.write("W".encode('utf-8'))

    def main(self):
        while (1):
            again = self.game()
            if not again:
                break #end game if winner does not want
            # to go again

    def game(self):
        global light_size
        r_val = 100 # red value of player
        max_light = 125 # maximum diameter of spotlight
        light_size = max_light # light_size changes when light shined on player
        old_pos = [0, 0] # to detect change in mouse position
        old_rects = [] # to track rects that need to be black filled
        num_stations = 10
        pygame.init()
        self.width = 1280
        self.height = 840
        global stations
        for s in range(0, num_stations):
            rand_x = randint(10, self.width-50)
            rand_y = randint(10, self.height-50)
            new_rect = Rect(rand_x - 35, rand_y - 35, 70, 70)
            collision = False
            for r in stations:
                if r.colliderect(new_rect):
                    collision = True
                    break
            if not collision:
                stations.append(new_rect)
            else:
                s -= 1 # if collision, generate new rect
        global s_colors
        global c_made
        index = 0
        if c_made:
            for c in s_colors:
                self.sendColor(index, c)
                index += 1
        self.black = 0,0,0
        self.character = r_val, 0, 0 # character is square plain color
        self.size = self.width, self.height
        self.screen = pygame.display.set_mode(self.size, flags)
        self.star = DeathStar()
        self.light = SpotLight()
        self.light0 = SpotLight()
        self.star.star_rect.x = 150
        self.star.star_rect.y = 150
        if c_made:
            self.sendSelfXY(150, 150)
        self.clock = pygame.time.Clock()
        self.screen.set_alpha(None) # speed up performance
        pygame.event.set_allowed([QUIT, KEYDOWN, KEYUP]) # better performance
        self.mouse_down = False
        old_light = self.light.light_rect
        old_char = self.star.star_rect
        Thread(target=reactor.run, args=(False, )).start()
        clear_old_char = False
        stations_won = 0
        global lost
        lost_display = lost
        win_display = False
        while 1:
            #global stations_sent
            #if c_made and not stations_sent:
                #print("send stations")
                #for i in range(0, 7):
                #stations_sent = True
            self.clock.tick(60)
            for event in pygame.event.get():
                if event.type == KEYDOWN:
                    clear_old_char = True
                    if event.key == K_LEFT:
                        self.star.star_rect.x -= 50
                        if self.star.star_rect.x < 20:
                            self.star.star_rect.x = 20
                    elif event.key == K_RIGHT:
                        self.star.star_rect.x += 50
                        if self.star.star_rect.x > self.width-20:
                            self.star.star_rect.x = self.width-20
                    elif event.key == K_UP:
                        self.star.star_rect.y -= 50
                        if self.star.star_rect.y < 20:
                            self.star.star_rect.y = 20
                    elif event.key == K_DOWN:
                        self.star.star_rect.y += 50
                        if self.star.star_rect.y > self.height-20:
                            self.star.star_rect.y = self.height-20
                    else:
                        clear_old_char = False  
                    global c_made
                    if c_made:
                        self.sendSelfXY(self.star.star_rect.x, self.star.star_rect.y)
                        print("sending {}, {}".format(self.star.star_rect.x, self.star.star_rect.y))
                    else:
                        print("not connection")
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

            if clear_old_char:
                s.fill(self.black, old_char)

            # red value of character will change if spotlight shined
            self.character = 0, 0, 250
            s.fill(self.character, rect)
            self.station = 0, 250, 0
            self.cyan = 40, 40, 5
            global s_colors
            global stations
            global c_made
            counter = 0
            global lost
            for st in stations:
                s.fill(self.station, st)
                if s_colors[counter]:
                    active_rects.append(st) 
                if st.colliderect(rect) and c_made and s_colors[counter] and not lost:
                    self.sendStation(st.x, st.y)# stations[1][0], stations[1][1], stations[2][0], stations[2][1], stations[3][0], stations[3][1], stations[4][0], stations[4][1], stations[5][0], stations[5][1], stations[6][0], stations[6][1], stations[7][0], stations[7][1]) 
                    s_colors[counter] = 0
                    self.sendColor(counter, 0)
                    stations_won += 1
                    if stations_won == len(stations):
                        self.sendWon()
                        win_display = True
                        print("YOU WON!") 
                if counter > num_stations-1:
                    break
                if not s_colors[counter]:
                    s.fill(self.cyan, st)
                counter += 1

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
            active_rects.append(old_char)
            active_rects.append(old_light)
            for ac_rect in active_rects:
                pygame.display.update(ac_rect)
            old_rects = active_rects[:] 
            old_pos = pos
            old_char = rect
            old_light = self.light.light.get_rect(center=(self.light.light_rect.x+light_size/2+1, self.light.light_rect.y+light_size/2+1))
            if lost_display:
                pygame.font.init()
                myfont = pygame.font.SysFont('Comic Sans MS', 50)
                textsurface = myfont.render("Sorry. You've lost!", True, (0,250,250))
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
    reactor.listenTCP(10130, MyCommandConnectionFactory())
    gs = GameSpace()
    gs.main()
