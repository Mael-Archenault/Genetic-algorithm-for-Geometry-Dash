import pygame
import random
from math import *
class Floor:
    def __init__(self, y_init):
        self.y = y_init
        self.x = 0
        self.floor_img = pygame.image.load("./img/floor.png")
        self.floor_rect = pygame.Rect(self.x,self.y, 1080,5) # floor hitbox

    def update(self):
        self.floor_rect.update(self.x, self.y, 1080,10)

    def display(self, screen, collisions):
        screen.blit(self.floor_img, (self.x, self.y))
        if collisions:
            pygame.draw.rect(screen, (0,255,0), self.floor_rect)



class Block:
    def __init__(self, x,y, speed):
        self.speed = speed
        self.x = x
        self.y = y
        self.near_player = False
        self.block_img = pygame.image.load("./img/block.png")
        
    def update(self, player_position, window_size):
        self.x -= self.speed

        if abs(player_position[0]-self.x)<(window_size[0]/2)+50 and abs(player_position[1]-self.y)<(window_size[1]/2)+50:
            if not self.near_player:
                self.near_player = True
                self.block_rect = self.block_img.get_rect()
            self.block_rect.update(self.x, self.y, 50,50)

        else:
            if self.near_player:
                self.near_player = False

    def display(self, screen, collision_box):
        screen.blit(self.block_img, (self.x, self.y))

        if self.near_player and collision_box:
            pygame.draw.rect(screen, (255,0,0), self.block_rect)


class Spike:
    def __init__(self, x,y, speed, little_spike, angle):
        self.little_spike = little_spike
        self.angle = angle
        self.speed = speed
        self.near_player = False
        self.x = x
        self.y = y
        if not self.little_spike:
            self.spike_img = pygame.image.load("./img/spike.png")
        else:
            self.spike_img = pygame.image.load("./img/little_spike.png")

        self.spike_img = pygame.transform.rotate(self.spike_img, self.angle)
        self.spike_rect = self.spike_img.get_rect(center = (self.x, self.y))


    def update(self, player_position, window_size):
        self.x -= self.speed

        if self.little_spike:
            size = (20,15)
        else:
            size = (20,25)

        if self.angle == 180:
            position = (self.x + (50-size[0])/2, self.y+50-size[1])
        else:
            position = (self.x + (50-size[0])/2, self.y+50-size[1])
        if abs(player_position[0]-self.x)<(window_size[0]/2)+50 and abs(player_position[1]-self.y)<(window_size[1]/2)+50:
            if not self.near_player:
                self.near_player = True
                self.spike_rect = self.spike_img.get_rect()
            self.spike_rect.update(self.x, self.y, 50,50)
        else:
            if self.near_player:
                self.near_player = False
        self.spike_rect.update(position, size)

    def display(self, screen, collision_box):
        screen.blit(self.spike_img, (self.x, self.y))

        if self.near_player and collision_box:
            pygame.draw.rect(screen, (255,0,0), self.spike_rect)

class Particle:
    def __init__(self,x_init, y_init, time, speed,range_min, range_max, size, shape, colors, max_life_expectancy):
        self.x = x_init
        self.y= y_init

        self.y0 = y_init
        self.x0 = x_init

        self.shape = shape


        self.v = speed*100

        self.angle = random.randrange(range_min, range_max)

        self.vx0 = self.v*cos(self.angle*3.14/180)
        self.vy0 = -1*self.v*sin(self.angle*3.14/180)

        self.start_time = time

        self.init_size = size*(1+random.random()/2)
        self.size = self.init_size
        self.color = random.choice(colors)
        self.life_count = 0

        self.life_expectancy = random.randrange(20,max_life_expectancy)

        self.active = True

    def display(self, screen):

        if self.active:
            if self.shape == "circle":
                pygame.draw.circle(screen, self.color, (self.x, self.y), self.size*10)
            if self.shape == "square":
                pygame.draw.rect(screen, self.color, (self.x-25, self.y-25 ,self.size*10, self.size*10))


    def update(self, time, death, framerate):
        self.life_count += 1

        self.size = self.init_size*(1-self.life_count/self.life_expectancy)


        if self.life_count >= self.life_expectancy*framerate/120:
            self.active = False

        if self.active and not death:

            self.y += self.vy0/framerate
            self.x -= 50*10.38/framerate
