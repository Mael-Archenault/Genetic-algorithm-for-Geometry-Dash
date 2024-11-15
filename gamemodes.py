import pygame
from math import *
from object_library import Particle
import keyboard

class Cube:
    def __init__(self, screen, x_init, y_init):

        self.x = x_init
        self.y = y_init

        self.collisions = [False,False,False] #collisions : dans l'ordre bas/droite/haut
        self.jump = False
        self.jump_count = 0


        self.vy = 0
        self.ay = 9.18*500


        self.y0 = self.y
        self.vy0_jump = -1000
        self.vy0 = 0

        self.jump_stall_time = 0
        self.death_time = 0


        self.cube_color = (255,255,255)
        self.cube_img = pygame.image.load("./img/cube.png")
        self.cube_copy = self.cube_img

        self.cube_rect = self.cube_copy.get_rect(center = (self.x, self.y))



        self.angle = 0
        self.previous_angle = 0
        self.nearest_angle = 0
        self.dead = False

        self.death_particles = []

        self.screen = screen


    def display(self, collision_box):
        if not self.dead :
            if self.angle != self.previous_angle:
                self.previous_angle = self.angle
                self.cube_copy = pygame.transform.rotate(self.cube_img,-1*self.angle)


            x_copy = int(self.cube_copy.get_width()/2)
            y_copy = int(self.cube_copy.get_height()/2)
            self.screen.blit(self.cube_copy,(self.x - x_copy, self.y- y_copy))
            if collision_box:
                pygame.draw.rect(self.screen,(20,0,255),self.cube_rect)
        else :
            for particle in self.death_particles:
                particle.display(self.screen)






    def death(self, time):
        self.death_time = time
        for i in range(10):
            self.death_particles.append(Particle(self.x, self.y, time, 4, 0, 360, 5, "square", [(255,255,255), (160,160,160), (32,32,32)], 90))

    def fall_setup(self, time):
        self.y0 = self.y
        self.vy0 = 0
        self.jump_stall_time = time

    def jump_setup(self, time):
        self.y0 = self.y
        self.vy0 = self.vy0_jump
        self.vy = self.vy0
        self.jump_stall_time = time
        self.jump_count += 1




    def update(self, time, framerate):
        if self.angle > 360:
            self.angle = self.angle%360



        self.cube_rect.update(self.x-25, self.y-25, 50,50)


        if self.collisions[0] and self.angle!= self.nearest_angle:
            equalizer = 4*120/framerate
            if self.angle > self.nearest_angle:

                if self.angle-equalizer <= self.nearest_angle:
                    self.angle = self.nearest_angle
                else :
                    self.angle -= equalizer
            else :
                if self.angle+equalizer >= self.nearest_angle:
                    self.angle = self.nearest_angle
                else :
                    self.angle += equalizer

#/////////////////////////////////////////////////////////////////////////////////////////////
#       Initialization of the jump

        if self.jump and self.collisions[0] and time-self.jump_stall_time >0.2:


            self.jump = False
            self.y -= 1
            self.cube_rect.update(self.x-25, self.y-25, 50,50)
            self.jump_setup(time)
            self.collisions[0] = False

#/////////////////////////////////////////////////////////////////////////////////////////////

        if not self.collisions[0] :
            self.compute_position(time - self.jump_stall_time, framerate)
            if self.jump:
                self.jump = False
            self.cube_rect.update(self.x-25, self.y-25, 50,50)
        
    def compute_position(self, time, framerate):
        if self.vy < 1600:
            self.vy += self.ay/framerate

        self.added_px = self.vy/framerate

        self.y +=  self.added_px
        self.angle += 3*120/framerate

    def death_animation(self, time, framerate):
        if self.death_particles == []:
            self.death(time)
        for particle in self.death_particles:
            particle.update(time, False, framerate)
            if not particle.active:
                self.death_particles.remove(particle)
