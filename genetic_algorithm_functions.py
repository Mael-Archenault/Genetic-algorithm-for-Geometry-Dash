import os
import pygame
import keyboard
import random
from math import*
from map import Map
from trigger_library import Node, Trigger, Beam, Trigger_Window
from object_library import Floor, Spike, Block, Particle
from gamemodes import Cube
import time

os.getcwd()



class Trainer:
    def __init__(self, screen, map_name, save_folder_path, base_model_path, starting_generation, batch_size):

        
        self.save_floder_path = save_folder_path
        self.screen = screen
        self.map_name = map_name
        self.base_model_path = base_model_path
        self.batch_size = batch_size

        self.running = False
        self.activate_display = True

        self.bg_color = (0,0,40)
        self.font = pygame.font.Font('arial.ttf', 25)

        
        self.framerate = 120
        self.speed = 50*10.38/self.framerate

        self.cube = Cube(self.screen,300,568)

        self.floor = Floor(592)
        self.map = Map(self.map_name)

        self.collision_box = False


        self.particle_list = []

        self.drift_particles_last_spawn = 0

        self.block_list = []
        self.spike_list = []

        self.iteration = 1
        self.generation = starting_generation

        self.generation_best ={"death_time" : 0, "model" : [], "jump_count":0, "trigger_number":0}
        self.trigger_window_size = (500,500)
        
        self.trigger_window = Trigger_Window(self.cube,self.trigger_window_size) 
        
        self.epsilon = 30
        
        if self.base_model_path is None:
            self.original_node_list = self.random_configuration()
            
        else:
            self.original_node_list = self.load_player_configuration(self.base_model_path)

        self.node_list = self.original_node_list.copy()
        self.node_list_to_display = self.node_list

        self.time = 0
        self.last_row_spawn_time = 0



        self.last_change_overall_display = 0
        self.last_change_node_display = 0
        self.last_change_collision_display = 0
        self.last_change_epsilon = 0
        

        self.clock = pygame.time.Clock()

    def save_player_configuration(self, best_player, name):
        f = open(self.save_floder_path + "/"+name +".txt", "w")

        line = ""
        
        node_list = best_player["model"]

        for node in node_list:
            node_description = ""
            for trigger in node.trigger_list:
                node_description += trigger.trigger_type + "_"
                node_description += str(trigger.relative_x)+"_"+str(trigger.relative_y)+ " "
            node_description = node_description[:-1]
            line += node_description
            line += "/"
        line+= "("+str(best_player["death_time"])+")\n"
        f.write(line)
        

    def load_player_configuration(self, name):
        f = open(name, "r")
        text = ""
        for line in f:
            text += line
        print(text)
        configuration = []
        nodes = text.split("/")
        nodes = nodes[:-1]

        triggers = []
        for node in nodes:
            triggers.append(node.split(" "))

        for node in triggers:
            

            trigger_list = []
            flag = False            
            for trigger in node:
                description = trigger.split("_")


                if len(description)!=1:
                    flag = True
                    trigger_list.append(Trigger(int(description[1]), int(description[2]),description[0]))
            if flag:
                configuration.append(Node(trigger_list, self.cube))


        return configuration

    def random_configuration(self):
        node_number = random.randrange(1,4)
        node_list = []
        for i in range(node_number):
            trigger_number = random.randrange(1,3)
            trigger_list = []
            for j in range(trigger_number):
                trigger_type = random.choice(["spike", "block", "spikeNegative", "blockNegative"])
                trigger = Trigger(random.randrange(self.trigger_window.getRelativeXmin(), self.trigger_window.getRelativeXmax()),random.randrange(self.trigger_window.getRelativeYmin(), self.trigger_window.getRelativeYmax()), trigger_type)
                trigger_list.append(trigger)

            flag = False
            for trigger in trigger_list:
                if not trigger.negative:
                    flag = False
            if not flag:
                trigger_type = random.choice(["spike", "block"])
                trigger = Trigger(random.randrange(self.trigger_window.getRelativeXmin(), self.trigger_window.getRelativeXmax()),random.randrange(self.trigger_window.getRelativeYmin(), self.trigger_window.getRelativeYmax()), trigger_type)
                trigger_list.append(trigger)

            node_list.append(Node(trigger_list, self.cube))

        return node_list

    def semi_random_configuration(self, old_configuration, epsilon):
        #epsilon is a coefficient of modification, the higher it is, the more change there will be
        result = configuration_copy(old_configuration, self.cube)
        for node in result:
            node.cube = self.cube
        modified_parameters = random.randrange(0,epsilon+1)

        for _ in range(modified_parameters):
            possibilities = ["nodes_number", "trigger_number", "trigger_number","trigger_position", "trigger_position", "trigger_position"]
            choice = random.choice(possibilities)


            if choice == "nodes_number":
                if random.random()>0.5:
                    if len(result)<5:
                        trigger_number = random.randrange(1,3)
                        trigger_list = []
                        for j in range(trigger_number):
                            trigger_type = random.choice(["spike", "block", "spikeNegative", "blockNegative"])
                            trigger = Trigger(random.randrange(self.trigger_window.getRelativeXmin(), self.trigger_window.getRelativeXmax()),random.randrange(self.trigger_window.getRelativeYmin(), self.trigger_window.getRelativeYmax()), trigger_type)
                            trigger_list.append(trigger)

                        result.append(Node(trigger_list, self.cube))
                else:
                    if len(result) >1:
                        result.pop(random.randrange(0,len(result)))


            elif choice == "trigger_number":
                if random.random()>0.7:
                    trigger_type = random.choice(["spike", "block", "spikeNegative", "blockNegative"])
                    trigger = Trigger(random.randrange(self.trigger_window.getRelativeXmin(), self.trigger_window.getRelativeXmax()),random.randrange(self.trigger_window.getRelativeYmin(), self.trigger_window.getRelativeYmax()), trigger_type)
                    random.choice(result).trigger_list.append(trigger)
                else:
                    random_index_node = random.randrange(0, len(result))
                    if len(result[random_index_node].trigger_list)>1:
                        result[random_index_node].trigger_list.pop()


            elif choice == "trigger_position":
                random_index_node = random.randrange(0, len(result))
                random_index_trigger = random.randrange(0, len(result[random_index_node].trigger_list))
                result[random_index_node].trigger_list[random_index_trigger].x += epsilon*random.randrange(-20,20)
                result[random_index_node].trigger_list[random_index_trigger].y += epsilon*random.randrange(-20,20)

        for node in result:
            flag = False
            for trigger in node.trigger_list:
                if not trigger.negative:
                    flag = True

            if not flag:
                trigger_type = random.choice(["spike", "block"])
                trigger = Trigger(random.randrange(self.trigger_window.getRelativeXmin(), self.trigger_window.getRelativeXmax()),random.randrange(self.trigger_window.getRelativeYmin(), self.trigger_window.getRelativeYmax()), trigger_type)
                node.trigger_list.append(trigger)
        return result

    def setup_block_row(self):
        
        if len(self.map.map_list[0])!=0:
            for i in range(len(self.map.map_list)):
                #--Block--
                item = self.map.map_list[i][0]
                if item ==1:
                    self.block_list.append(Block(1180, self.floor.y + 50*(i-len(self.map.map_list)), self.speed))
                #--Spike up
                if item==2:
                    self.spike_list.append(Spike(1180, self.floor.y + 50*(i-len(self.map.map_list)), self.speed, False, 0))
                #--Little_spike up
                if item==3:
                    self.spike_list.append(Spike(1180, self.floor.y + 50*(i-len(self.map.map_list)), self.speed, True, 0))
                #--Spike down
                if item==4:
                    self.spike_list.append(Spike(1180, self.floor.y + 50*(i-len(self.map.map_list)), self.speed, False, 180))
                #--Little_spike down
                if item==5:
                    self.spike_list.append(Spike(1180, self.floor.y + 50*(i-len(self.map.map_list)), self.speed, True, 180))

                self.map.map_list[i].pop(0)
    def remove_items(self):
        if len(self.block_list) != 0 :
            force_out = False
            while not force_out:
                if self.block_list[0].x<-50:
                    self.block_list.pop(0)
                else :
                    force_out = True
                if self.block_list == []:
                    force_out = True
        if len(self.spike_list) != 0 :
            force_out = False
            while not force_out:
                if self.spike_list[0].x<-50:
                    self.spike_list.pop(0)
                else :
                    force_out = True
                if self.spike_list == []:
                    force_out = True
            

            
    def change_node_display(self, reset):
        if reset:
            self.node_list_to_display = self.node_list
            
        else:
            if len(self.node_list_to_display) != 1:
                self.node_list_to_display = [self.node_list[0]]
            else:
                if self.node_list.index(self.node_list_to_display[0])==len(self.node_list)-1:
                    self.node_list_to_display = self.node_list
                else:
                    self.node_list_to_display = [self.node_list[self.node_list.index(self.node_list_to_display[0])+1]]

    def clean_configuration(self,node_list):
        res = []
        for node in node_list:
            if node.used:
                res.append(node)
        if res == []:
            res = node_list
        return res

    def camera_up(self, speed):
        self.cube.y += speed*2
        self.floor.y += speed*2

        for particle in self.particle_list:
            particle.y += speed*2

        for block in self.block_list:
            block.y += speed*2

        for spike in self.spike_list:
            spike.y += speed*2

    def camera_down(self, speed):
        self.cube.y -=speed*2
        self.floor.y -= speed*2
        for particle in self.particle_list:
            particle.y -= speed*2
        for block in self.block_list:
            block.y -= speed*2

        for spike in self.spike_list:
            spike.y -= speed*2

    def reset(self):
        death_time = self.cube.death_time
        jump_count = self.cube.jump_count

        trigger_number = 0
        for node in self.node_list:
            trigger_number+= len(node.trigger_list)

        self.node_list = self.clean_configuration(self.node_list)
        

        # Managing the best player

        flag = False
        if self.iteration == 1:
            flag = True
        
        else:
            if death_time == self.generation_best["death_time"]:
                if jump_count+trigger_number <= self.generation_best["jump_count"] + self.generation_best["trigger_number"]:
                    flag = True
            elif death_time > self.generation_best["death_time"]:
                flag = True

        if (flag):
            self.generation_best = {"death_time" : death_time, "model" : self.node_list, "jump_count":jump_count, "trigger_number":trigger_number}
            self.save_player_configuration(self.generation_best, "generation_"+str(self.generation)+"_best")
            print("best player for generation "+str(self.generation)+": "+ str(death_time), self.cube.jump_count, trigger_number)

        
        # Reseting all variables #
        self.cube = Cube(self.screen, 300,568)
        self.floor = Floor(592)
        self.map = Map(self.map_name)
        self.drift_particles_last_spawn = 0
        self.block_list = []
        self.spike_list = []
        self.time = 0
        self.last_row_spawn_time = 0
        self.speed = 50*10.38/self.framerate
        
        
        
        if self.generation == 1 :
            self.node_list = self.random_configuration()
        
        else :
            self.node_list = self.semi_random_configuration(self.original_node_list, self.epsilon)
            
        
        self.change_node_display(True)
        
        self.trigger_window = Trigger_Window(self.cube,(500, 500))

        if self.iteration == self.batch_size:

            self.original_node_list = self.load_player_configuration(self.save_floder_path +"/generation_"+str(self.generation)+"_best.txt")

            self.node_list = configuration_copy(self.original_node_list, self.cube)
            self.generation += 1
            self.generation_best = 0
            self.iteration = 1

            self.epsilon = max(3, self.epsilon-1)

            print(" ")
            print("Generation : "+ str(self.generation))
            print(" ")


        else:
            self.iteration += 1

    def handling_events(self):

        
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False
        if keyboard.is_pressed("c"):
            if (time.time() - self.last_change_collision_display) > 0.5:
                self.collision_box = not(self.collision_box)
                self.last_change_collision_display = time.time()

        if keyboard.is_pressed("d"):
            if (time.time() - self.last_change_overall_display) > 0.5:
                self.activate_display= not(self.activate_display)
                self.last_change_overall_display = time.time()
                


        if keyboard.is_pressed("right"):
            if (time.time()-self.last_change_node_display)>0.5:
                self.change_node_display(False)
                self.last_change_node_display = time.time()

        if keyboard.is_pressed("r"):
            if (time.time()-self.last_change_epsilon>0.1):
                self.epsilon += 1
                print("Epsilon : " + str(self.epsilon))
                self.last_change_epsilon = time.time()

        if keyboard.is_pressed("e"):
            if (time.time()-self.last_change_epsilon>0.1):
                self.epsilon = max(3, self.epsilon-1)
                print("Epsilon : " + str(self.epsilon))
                self.last_change_epsilon = time.time()

    
    def update(self):
        
            if not self.cube.dead :

                if self.time > 150:
                    self.cube.dead = True
                    self.speed = 0

                self.cube.update(self.time, self.framerate)
                #//////////////// Block row spawn

                if (self.time-self.last_row_spawn_time)*self.speed*self.framerate>=50:

                    self.setup_block_row()
                    self.remove_items()
                    self.last_row_spawn_time = self.time


                #//////////////////////////////////////////////////



                #//////////////// Camera move to follow the player
                if self.cube.y < 70:
                    self.camera_up(2)
                elif self.cube.y<120:
                    self.camera_up(1)

                if self.cube.y > 650 :
                    self.camera_down(2)
                elif self.cube.y >600:
                    self.camera_down(1)
                #////////////////////////////////////////////////////////


                #//////////////////////// Particles due to the bloc drifting on a surface
                if self.cube.collisions[0] and self.time -self.drift_particles_last_spawn > 1/15:
                    self.particle_list.append(Particle(self.cube.x, self.cube.y+45, self.time, self.speed/2, 175,180, 0.4, "square", [(255,255,255)], 90))
                    self.drift_particles_last_spawn = self.time


                for particle in self.particle_list:
                    particle.update(self.time, False, self.framerate)
                    if not particle.active:
                        self.particle_list.remove(particle)
                #//////////////////////////////////////////////////////////////////

                #///////////////////// updating the position of every block (and spikes)
                cube_position = (self.cube.x, self.cube.y)
                for block in self.block_list:
                    block.update(cube_position, self.trigger_window_size)
                for spike in self.spike_list:
                    spike.update(cube_position, self.trigger_window_size)
                for node in self.node_list:
                    node.update()
                self.floor.update()
                self.trigger_window.update()

                #///////////////////////////////////////////////////////

                #////////////////////// Trigger collision detection with spike and blocks

                for node in self.node_list:
                    for trigger in node.trigger_list:

                        if not trigger.negative:
                            trigger.activation = False
                        else:
                            trigger.activation = True

                        if trigger.trigger_type == "spike" or trigger.trigger_type == "spikeNegative":
                            for spike in self.spike_list:

                                if spike.x<trigger.x+50 and spike.x>trigger.x-50:

                                    if pygame.Rect.colliderect(trigger.trigger_rect,spike.spike_rect ):
                                        if not trigger.negative:
                                            trigger.activation = True
                                            
                                        else:
                                            trigger.activation = False
                                        trigger.used = True



                        elif trigger.trigger_type == "block" or trigger.trigger_type == "blockNegative":
                            for block in self.block_list:

                                if block.near_player:

                                    if pygame.Rect.colliderect(trigger.trigger_rect,block.block_rect ):

                                        if not trigger.negative:
                                            trigger.activation = True
                                        else:
                                            trigger.activation = False


                #/////////////////////////// Collision detection with a spike (instant death)
                for spike in self.spike_list:
                    if spike.near_player:
                        if pygame.Rect.colliderect(spike.spike_rect, self.cube.cube_rect):
                            self.cube.dead = True
                            self.speed = 0
                #//////////////////////////////////////////

                #//////////////////////////// Collision detection with a block
                self.is_block_collisions = False
                for block in self.block_list:
                    if block.near_player:
                        if pygame.Rect.colliderect(self.cube.cube_rect, block.block_rect):

                            self.is_block_collisions = True
                            if self.cube.y+10 > block.y:
                                self.cube.dead = True
                                self.speed = 0
                            else:
                                if not self.cube.collisions[0] and self.cube.vy>0:
                                    self.cube.collisions[0] = True
                                    self.cube.vy = 0
                                    self.cube.y = block.y-24
                                    self.cube.nearest_angle = find_nearest_angle(self.cube.angle)

                if self.cube.collisions[0] and not self.is_block_collisions and not self.cube.y+26>self.floor.y:
                    self.cube.collisions[0] = False
                    self.cube.fall_setup(self.time)


                #/////////////////////////// Collision detection with the floor
                
                if pygame.Rect.colliderect(self.cube.cube_rect, self.floor.floor_rect) and not self.cube.collisions[0]:
    
                    
                    self.cube.y = self.floor.y-25
                    self.cube.collisions[0] = True
                    self.cube.vy = 0
                    self.cube.nearest_angle = find_nearest_angle(self.cube.angle)
                    self.cube.angle = self.cube.angle%360
                    

                #///////////////////////////////
            
            else :
                for particle in self.particle_list:
                    particle.update(self.time, True, self.framerate)
                    if not particle.active:
                        self.particle_list.remove(particle)

                self.cube.death_animation(self.time, self.framerate)
                if self.cube.death_particles == []:
                    self.reset()      



    def display(self):

        self.screen.fill(self.bg_color)

        for particle in self.particle_list:
            particle.display(self.screen)


        for block in self.block_list:
            block.display(self.screen, self.collision_box)
        for spike in self.spike_list:
            spike.display(self.screen, self.collision_box)
        
        for node in self.node_list_to_display:
            node.display(self.screen, self.collision_box)
        
        self.trigger_window.display(self.screen)
        

        
        self.cube.display(self.collision_box)

        self.floor.display(self.screen, self.collision_box)

        generation = self.font.render("generation: " + str(self.generation), True, (255,255,255))
        iteration = self.font.render("iteration: " + str(self.iteration), True, (255,255,255))
        time = self.font.render("time: " + str(round(self.time, 3)), True, (255,255,255))
        self.screen.blit(generation, [0, 0])
        self.screen.blit(iteration, [0, 40])
        self.screen.blit(time, [0,80])

        pygame.display.flip()


    def run(self):
        self.running  = True
        while self.running :
            self.handling_events()
            self.update()
            if self.activate_display:
                self.display()
            self.time += 1/self.framerate
            if self.activate_display:
                self.clock.tick(self.framerate)


class Tester:
    def __init__(self, screen, map_name, model_path):
        self.screen = screen
        self.map_name = map_name
        self.model_path = model_path
        self.running = False

        self.bg_color = (0,0,40)
        self.font = pygame.font.Font('arial.ttf', 25)

        self.framerate = 120
        self.speed = 50*10.38/self.framerate

        self.cube = Cube(self.screen, 300,568)

        self.floor = Floor(592)
        self.map = Map(self.map_name)

        self.collision_box = False

        self.particle_list = []
        self.drift_particles_last_spawn = 0

        self.block_list = []
        self.spike_list = []

        self.trigger_window_size = (500,500)
        self.trigger_window = Trigger_Window(self.cube,self.trigger_window_size)
        
        if (self.model_path is not None):
            self.node_list = self.load_player_configuration(self.model_path)

        else:
            self.node_list = []
        self.node_list_to_display = self.node_list

        self.time = 0
        self.last_row_spawn_time = 0

        self.last_change_node_display = 0
        self.last_change_collision_display = 0

        self.clock = pygame.time.Clock()
        

    def load_player_configuration(self, configuration_path):
        f = open(configuration_path, "r")
        text = ""
        for line in f:
            text += line
        print(text)
        configuration = []
        nodes = text.split("/")
        nodes = nodes[:-1]

        triggers = []
        for node in nodes:
            triggers.append(node.split(" "))

        for node in triggers:
            

            trigger_list = []
            flag = False            
            for trigger in node:
                description = trigger.split("_")


                if len(description)!=1:
                    flag = True
                    trigger_list.append(Trigger(int(description[1]), int(description[2]),description[0]))
            if flag:
                configuration.append(Node(trigger_list, self.cube))

        return configuration

    def setup_block_row(self):
        
        if len(self.map.map_list[0])!=0:
            for i in range(len(self.map.map_list)):
                #--Block--
                item = self.map.map_list[i][0]
                if item ==1:
                    self.block_list.append(Block(1180, self.floor.y + 50*(i-len(self.map.map_list)), self.speed))
                #--Spike up
                if item==2:
                    self.spike_list.append(Spike(1180, self.floor.y + 50*(i-len(self.map.map_list)), self.speed, False, 0))
                #--Little_spike up
                if item==3:
                    self.spike_list.append(Spike(1180, self.floor.y + 50*(i-len(self.map.map_list)), self.speed, True, 0))
                #--Spike down
                if item==4:
                    self.spike_list.append(Spike(1180, self.floor.y + 50*(i-len(self.map.map_list)), self.speed, False, 180))
                #--Little_spike down
                if item==5:
                    self.spike_list.append(Spike(1180, self.floor.y + 50*(i-len(self.map.map_list)), self.speed, True, 180))

                self.map.map_list[i].pop(0)

    def remove_items(self):
        if len(self.block_list) != 0 :
            force_out = False
            while not force_out:
                if self.block_list[0].x<-50:
                    self.block_list.pop(0)
                else :
                    force_out = True
                if self.block_list == []:
                    force_out = True
        if len(self.spike_list) != 0 :
            force_out = False
            while not force_out:
                if self.spike_list[0].x<-50:
                    self.spike_list.pop(0)
                else :
                    force_out = True
                if self.spike_list == []:
                    force_out = True
            

            
    def change_node_display(self, reset):
        if reset:
            self.node_list_to_display = self.node_list
        else:
            if len(self.node_list_to_display) != 1:
                self.node_list_to_display = [self.node_list[0]]
            else:
                if self.node_list.index(self.node_list_to_display[0])==len(self.node_list)-1:
                    self.node_list_to_display = self.node_list
                else:
                    self.node_list_to_display = [self.node_list[self.node_list.index(self.node_list_to_display[0])+1]]

    def camera_up(self, speed):
        self.cube.y += speed*2
        self.floor.y += speed*2

        for particle in self.particle_list:
            particle.y += speed*2

        for block in self.block_list:
            block.y += speed*2

        for spike in self.spike_list:
            spike.y += speed*2

    def camera_down(self, speed):
        self.cube.y -=speed*2
        self.floor.y -= speed*2
        for particle in self.particle_list:
            particle.y -= speed*2
        for block in self.block_list:
            block.y -= speed*2

        for spike in self.spike_list:
            spike.y -= speed*2

    def reset(self):
        self.cube = Cube(self.screen, 300,568)
        self.node_list = configuration_copy(self.node_list, self.cube)
        self.floor = Floor(592)
        self.map = Map(self.map_name)
        self.drift_particles_last_spawn = 0
        self.block_list = []
        self.spike_list = []
        self.time = 0
        self.last_row_spawn_time = 0
        
        self.speed = 50*10.38/self.framerate
        self.change_node_display(True)
        self.trigger_window = Trigger_Window(self.cube,(500, 500))

    def handling_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False
        if keyboard.is_pressed("c"):
            if (time.time() - self.last_change_collision_display) > 0.5:
                self.collision_box = not(self.collision_box)
                self.last_change_collision_display = time.time()
                
        if keyboard.is_pressed("up") or keyboard.is_pressed("space"):
            self.cube.jump = True

        if keyboard.is_pressed("right"):
            if (time.time()-self.last_change_node_display)>0.5:
                self.change_node_display(False)
                self.last_change_node_display = time.time()


    def update(self):
        if not self.cube.dead :

            self.cube.update(self.time, self.framerate)
            #//////////////// Block row spawn

            if (self.time-self.last_row_spawn_time)*self.speed*self.framerate>=50:

                self.setup_block_row()
                self.remove_items()
                self.last_row_spawn_time = self.time


            #//////////////////////////////////////////////////



            #//////////////// Camera move to follow the player
            if self.cube.y < 70:
                self.camera_up(2)
            elif self.cube.y<120:
                self.camera_up(1)

            if self.cube.y > 650 :
                self.camera_down(2)
            elif self.cube.y >600:
                self.camera_down(1)
            #////////////////////////////////////////////////////////


            #//////////////////////// Particles due to the bloc drifting on a surface
            if self.cube.collisions[0] and self.time -self.drift_particles_last_spawn > 1/15:
                self.particle_list.append(Particle(self.cube.x, self.cube.y+45, self.time, self.speed/2, 175,180, 0.4, "square", [(255,255,255)], 90))
                self.drift_particles_last_spawn = self.time


            for particle in self.particle_list:
                particle.update(self.time, False, self.framerate)
                if not particle.active:
                    self.particle_list.remove(particle)
            #//////////////////////////////////////////////////////////////////

            #///////////////////// updating the position of every block (and spikes)
            cube_position = (self.cube.x, self.cube.y)
            for block in self.block_list:
                block.update(cube_position, self.trigger_window_size)
            for spike in self.spike_list:
                spike.update(cube_position, self.trigger_window_size)
            for node in self.node_list:
                node.update()
            self.floor.update()
           
            self.trigger_window.update()

            #///////////////////////////////////////////////////////

            #////////////////////// Trigger collision detection with spike and blocks

            for node in self.node_list:
                for trigger in node.trigger_list:

                    if not trigger.negative:
                        trigger.activation = False
                    else:
                        trigger.activation = True

                    if trigger.trigger_type == "spike" or trigger.trigger_type == "spikeNegative":
                        for spike in self.spike_list:

                            if spike.x<trigger.x+50 and spike.x>trigger.x-50:

                                if pygame.Rect.colliderect(trigger.trigger_rect,spike.spike_rect ):
                                    if not trigger.negative:
                                        trigger.activation = True
                                        
                                    else:
                                        trigger.activation = False
                                    trigger.used = True



                    elif trigger.trigger_type == "block" or trigger.trigger_type == "blockNegative":
                        for block in self.block_list:

                            if block.near_player:

                                if pygame.Rect.colliderect(trigger.trigger_rect,block.block_rect ):

                                    if not trigger.negative:
                                        trigger.activation = True
                                    else:
                                        trigger.activation = False


            #/////////////////////////// Collision detection with a spike (instant death)
            for spike in self.spike_list:
                if spike.near_player:
                    if pygame.Rect.colliderect(spike.spike_rect, self.cube.cube_rect):
                        self.cube.dead = True
                        self.speed = 0
            #//////////////////////////////////////////

            #//////////////////////////// Collision detection with a block
            self.is_block_collisions = False
            for block in self.block_list:
                if block.near_player:
                    if pygame.Rect.colliderect(self.cube.cube_rect, block.block_rect):

                        self.is_block_collisions = True
                        if self.cube.y+10 > block.y:
                            self.cube.dead = True
                            self.speed = 0
                        else:
                            if not self.cube.collisions[0] and self.cube.vy>0:
                                self.cube.collisions[0] = True
                                self.cube.vy = 0
                                self.cube.y = block.y-24
                                self.cube.nearest_angle = find_nearest_angle(self.cube.angle)

            if self.cube.collisions[0] and not self.is_block_collisions and not self.cube.y+26>self.floor.y:
                self.cube.collisions[0] = False
                self.cube.fall_setup(self.time)


            #/////////////////////////// Collision detection with the floor
            
            if pygame.Rect.colliderect(self.cube.cube_rect, self.floor.floor_rect) and not self.cube.collisions[0]:

                
                self.cube.y = self.floor.y-25
                self.cube.collisions[0] = True
                self.cube.vy = 0
                self.cube.nearest_angle = find_nearest_angle(self.cube.angle)
                self.cube.angle = self.cube.angle%360
                

            #///////////////////////////////
        
        else :
            for particle in self.particle_list:
                particle.update(self.time, True, self.framerate)
                if not particle.active:
                    self.particle_list.remove(particle)

            self.cube.death_animation(self.time, self.framerate)
            if self.cube.death_particles == []:
                self.reset()


    def display(self):

        self.screen.fill(self.bg_color)

        for particle in self.particle_list:
            particle.display(self.screen)


        for block in self.block_list:
            block.display(self.screen, self.collision_box)
        for spike in self.spike_list:
            spike.display(self.screen, self.collision_box)
        
        for node in self.node_list_to_display:
            node.display(self.screen, self.collision_box)
        
        self.trigger_window.display(self.screen)

        self.cube.display(self.collision_box)

        self.floor.display(self.screen, self.collision_box)
        time = self.font.render("time: " + str(round(self.time, 3)), True, (255,255,255))
        self.screen.blit(time, [0,80])

        pygame.display.flip()


    def run(self):
        self.running  = True
        while self.running :
            self.handling_events()
            self.update()
            
            self.display()
            self.time += 1/self.framerate
            
            self.clock.tick(self.framerate)
            

def configuration_copy(node_list, cube):
    res = []
    for node in node_list:
        trigger_list = []
        for trigger in node.trigger_list:
            trigger_list.append(Trigger(trigger.relative_x, trigger.relative_y, trigger.trigger_type))
        res.append(Node(trigger_list, cube))
    return res

def find_nearest_angle(current_angle):
    angle = current_angle%360
    memory = 0
    min_distance = abs(angle)
    for i in range(0,450, 90):
        if abs(angle-i)<min_distance:
            memory = i
            min_distance = abs(angle-i)
    return memory







