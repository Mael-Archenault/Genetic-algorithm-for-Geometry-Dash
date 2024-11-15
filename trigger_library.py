import pygame
from math import *

class Trigger:
    def __init__(self, relative_x,relative_y, trigger_type): #x,y coordinates of the trigger with the cube as origin (0,0)
        self.negative = False
        self.trigger_type = trigger_type
        self.relative_x = relative_x
        self.relative_y = relative_y
        self.x, self.y = 0,0
        self.activation = False
        self.used = False

        if self.trigger_type == "spike":
            self.negative = False
            self.trigger_img = pygame.image.load("./img/spike_trigger.png")
            self.activated_trigger_img = pygame.image.load("./img/activated_spike_trigger.png")

        elif self.trigger_type == "spikeNegative":
            self.negative = True
            self.trigger_img = pygame.image.load("./img/spike_trigger_negative.png")
            self.activated_trigger_img = pygame.image.load("./img/activated_spike_trigger_negative.png")

        elif self.trigger_type == "block":
            self.negative = False
            self.trigger_img = pygame.image.load("./img/block_trigger.png")
            self.activated_trigger_img = pygame.image.load("./img/activated_block_trigger.png")


        elif self.trigger_type == "blockNegative":
            self.negative = True
            self.trigger_img = pygame.image.load("./img/block_trigger_negative.png")
            self.activated_trigger_img = pygame.image.load("./img/activated_block_trigger_negative.png")

        self.trigger_rect = self.trigger_img.get_rect()





    def display(self, collision_box, screen):
        if self.activation:
            screen.blit(self.activated_trigger_img, (self.x, self.y))
        else:
            screen.blit(self.trigger_img, (self.x, self.y))
        if collision_box:
            pygame.draw.rect(screen, (255,0,0), self.trigger_rect)




class Node:
    def __init__(self, trigger_list,cube):

        self.node_img = pygame.image.load("./img/node.png")
        self.activated_node_img = pygame.image.load("./img/activated_node.png")
        
        
        self.used = False
        
        self.activation = False

        self.cube = cube

        self.trigger_list = trigger_list

        # Placing the node sprite in the middle of all triggers #
        self.relative_x, self.relative_y = 0,0
        self.x, self.y = 0,0
        total_x = 0
        total_y = 0
        for trigger in self.trigger_list:
            total_x += trigger.relative_x
            total_y += trigger.relative_y
        self.relative_x = total_x/(len(self.trigger_list)+1)
        self.relative_y = total_y/(len(self.trigger_list)+1)


    def update(self):

        #----Updating position------

        self.x = self.cube.x+ self.relative_x
        self.y = self.cube.y-self.relative_y
        for trigger in self.trigger_list:
            trigger.x = self.cube.x + trigger.relative_x
            trigger.y = self.cube.y - trigger.relative_y
            trigger.trigger_rect.update((trigger.x, trigger.y), (50,50))

        #----Updating state-------
        self.activation = True
        for trigger in self.trigger_list:
            if not trigger.activation:
                self.activation = False
        if self.activation and not self.cube.jump:
            self.used = True
            self.cube.jump = True

    def display(self, screen, collision_box):
        if self.activation:
            screen.blit(self.activated_node_img, (self.x, self.y))
        else:
            screen.blit(self.node_img, (self.x, self.y))

        for trigger in self.trigger_list:
            trigger.display(collision_box, screen)
            if trigger.x>self.x:
                if trigger.y < self.y:
                    pygame.draw.line(screen,(255,255,255), (self.x+25, self.y+25), (trigger.x, trigger.y+50))
                if trigger.y >= self.y:
                    pygame.draw.line(screen,(255,255,255), (self.x+25, self.y+25), (trigger.x, trigger.y))
            if trigger.x <=self.x:
                if trigger.y < self.y:
                    pygame.draw.line(screen,(255,255,255), (self.x+25, self.y+25), (trigger.x+50, trigger.y+50))
                if trigger.y >= self.y:
                    pygame.draw.line(screen,(255,255,255), (self.x+25, self.y+25), (trigger.x+50, trigger.y))




class Beam:
    def __init__(self, ship, angle, precision):
        self.ship = ship
        self.angle = angle*3.14/180
        self.length = 500
        self.precision = precision
        self.end_point = (self.ship.x + cos(self.angle)*self.length,self.ship.y - sin(self.angle)*self.length)
        self.collide_point = self.end_point
        self.point_color = (155,155,155)
        self.values_to_test = self.get_values_to_test(self.precision)
    
    def get_values_to_test(self, step):
        lengths = [i for i in range(0, self.length, step)]
        res = []
        for length in lengths:
            res.append((self.ship.x + cos(self.angle)*length,self.ship.y - sin(self.angle)*length))
        return res

    def update(self):
        self.end_point = (self.ship.x + cos(self.angle)*self.length,self.ship.y - sin(self.angle)*self.length)
    
    def display(self, screen):
        pygame.draw.line(screen, (255,255,255), (self.ship.x, self.ship.y), self.end_point)
        pygame.draw.circle(screen, self.point_color, self.collide_point, 10)

class Trigger_Window:
    def __init__(self, cube, size):
        self.cube = cube
        self.width = size[0]
        self.height = size[1]
        self.relative_cube_position = (self.width/2, self.height/2)
        self.window_rect = pygame.Rect(self.cube.x-self.relative_cube_position[0], self.cube.y - self.relative_cube_position[1], self.width, self.height)

    def getRelativeXmin(self):
        return int(-self.width/2)
    def getRelativeXmax(self):
        return int(self.width/2 -50)
    
    def getRelativeYmin(self):
        return int(-self.height/2)
    
    def getRelativeYmax(self):
        return int(self.height/2 -50)

    def update(self):
        self.window_rect = pygame.Rect(self.cube.x-self.relative_cube_position[0], self.cube.y - self.relative_cube_position[1], self.width, self.height)

    def display(self, screen):
        pygame.draw.rect(screen, (255,255,255), self.window_rect,  2)
    
