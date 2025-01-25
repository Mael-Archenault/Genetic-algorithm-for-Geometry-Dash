from time import sleep
import pygame



FRAMERATE = 120
SPEED = 20
class LevelEditor:
    def __init__(self, screen, name):

        self.name = name
        self.screen = screen
        self.running = True
        self.clock = pygame.time.Clock()
        self.bg_color = (0,0,50)
        self.grid = Grid()
        self.floor = Floor(700)
        self.cursor = Cursor()
        self.preview = Preview()
        self.item_list_for_matrix = []
        self.item_list = []
        self.map =[]

        
    def handling_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False

            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_n:
                    self.preview.next_mode()
        

        keys = pygame.key.get_pressed()

        if keys[pygame.K_s]:
            self.save_level()
            sleep(1)
            print("Level saved")

        if keys[pygame.K_UP]:
            self.grid.y+=SPEED
            for item in self.item_list:
                item.y+=SPEED
            self.floor.y+=SPEED
        if keys[pygame.K_DOWN]:
            self.grid.y-=SPEED
            for item in self.item_list:
                item.y-=SPEED
            self.floor.y-=SPEED
        if keys[pygame.K_RIGHT]:
            self.grid.x-=SPEED
            for item in self.item_list:
                    item.x-=SPEED
        if keys[pygame.K_LEFT]:
            self.grid.x+=SPEED
            for item in self.item_list:
                item.x+=SPEED

    def update(self):
        
        self.grid.update()
        self.cursor.update()

        if self.cursor.click:
            x = self.grid.first_visible_bloc_index_x + (self.cursor.x - (self.grid.x+self.grid.space))//self.grid.space
            y = self.grid.first_visible_bloc_index_y + (self.cursor.y - (self.grid.y+self.grid.space))//self.grid.space

            ### Normalization ###

            y = 13-y

            if x>=0 and y>=0:
                remove_test = remove_items(self.item_list_for_matrix, self.item_list, (x,y))
                if not remove_test :
                    self.item_list_for_matrix.append([int(self.preview.mode[0]), (x,y)])
                

                    a = (self.cursor.x - (self.grid.x+self.grid.space))//self.grid.space
                    b = (self.cursor.y - (self.grid.y+self.grid.space))//self.grid.space
                    
                    self.item_list.append(Item((a+1)*50+self.grid.x,(b+1)*50+self.grid.y,int(self.preview.mode[0]),(x,y)) )
                else:
                    self.item_list_for_matrix, self.item_list = remove_test
    def display(self):
        self.screen.fill(self.bg_color)
        self.grid.display(self.screen)
        self.floor.display(self.screen)
        self.preview.display(self.screen)
        for item in self.item_list:
            item.display(self.screen)
        pygame.display.flip()
    
    def build_map(self):
        max_x, max_y = 0,0
        
        for element in self.item_list_for_matrix:
            if element[1][0]>= max_x:
                max_x=element[1][0]
            if element[1][1]>= max_y:
                max_y=element[1][1]
        res = [[0 for j in range(max_x+1)] for i in range(max_y+1) ]
        for element in self.item_list_for_matrix:
            res[element[1][1]][element[1][0]] = element[0]
        
        copy = res.copy()
        for i in range(len(res)):
            res[i]=copy[len(copy)-i-1]
        return res
    
    def save_level(self):
        self.map = self.build_map()
        file = open("./maps/"+str(self.name)+".txt", "w")
        for i in range(len(self.map)):
            file.write(str(self.map[i])+"\n")

    def load_level(self):
        file = open("./maps/"+str(self.name)+".txt", "r")
        res = []
        for line in file:
            values = line[1:-2]
            values = values.split(",")
            for i in range(len(values)):
                values[i] = int(values[i])
            res.append(values)
        
        copy = res.copy()
        for i in range(len(res)):
            res[i]=copy[len(copy)-i-1]

        self.map = res
        for i in range(len(self.map)):
            for j in range(len(self.map[0])):
                if self.map[i][j]!=0:
                    self.item_list_for_matrix.append([self.map[i][j], (j,i)])   
                    self.item_list.append(Item(j*50,-(i-13)*50,self.map[i][j],(j,i)))



    def run(self):
        self.load_level()
        self.running = True
        while self.running:
            self.handling_events()
            self.update()
            self.display()
            self.clock.tick(FRAMERATE)
        self.save_level()


class Cursor:
    def __init__(self):
        self.x, self.y = 0,0
        self.lately_pressed = False
        self.click = False

    def update(self):
        if pygame.mouse.get_pressed()[0] or pygame.K_SPACE in pygame.key.get_pressed():
            if not self.lately_pressed:
                self.lately_pressed = True
                self.click = True
                self.x, self.y = pygame.mouse.get_pos()
            else:
                self.click = False
            
                 
        else:
            self.lately_pressed = False

class Grid:
    def __init__(self):
        self.space = 50
        self.first_visible_bloc_index_x = 0
        self.first_visible_bloc_index_y = 0
        self.x, self.y = -self.space, -self.space
        self.lines = []
        self.horizontal_lines_number = 17
        self.vertical_lines_number = 24
        self.line_color = (50,50,50)
    def display(self, screen):
        for i in range(self.horizontal_lines_number):
            pygame.draw.line(screen, self.line_color, (self.x, self.y+i*self.space), (self.x+self.vertical_lines_number*self.space, self.y+i*self.space))
        for i in range(self.vertical_lines_number):
            pygame.draw.line(screen, self.line_color, (self.x +i*self.space, self.y), (self.x+i*self.space, self.y+self.horizontal_lines_number*self.space))
        

    def update(self):

        if self.x <= -2*self.space:
            self.x += self.space
            self.first_visible_bloc_index_x+=1
        if self.x > -self.space:
            self.x -= self.space
            self.first_visible_bloc_index_x-=1
        if self.y <= -2*self.space:
            self.y += self.space
            self.first_visible_bloc_index_y+=1
        if self.y > -self.space:
            self.y -= self.space
            self.first_visible_bloc_index_y-=1
    
class Floor:
    def __init__(self, y_init):
        self.y = y_init
        self.x = 0

        self.floor_img = pygame.image.load("./img/floor.png")
        
        

    def display(self, screen):
        screen.blit(self.floor_img, (self.x, self.y))

class Preview:
    def __init__(self):
        self.preview_list = [("1", block),("2", spike), ("3", little_spike), ("4", reversed_spike), ("5", reversed_little_spike)]
        self.mode = ("1",block)

        

    def next_mode(self):
        self.mode = self.preview_list[(self.preview_list.index(self.mode)+1)%5]

    def display(self, screen):
        screen.blit(self.mode[1], (1000, 30))      

class Item:
    def __init__(self, x,y, mode, matrix_position):
        self.matrix_position = matrix_position
        self.item_img = mode_list[mode]

        self.x = x
        self.y = y
        
    
    def display(self, screen):
        
        screen.blit(self.item_img, (self.x, self.y))

def remove_items(item_list_for_matrix, item_list, position):
    flag = False
    for i in range(len(item_list_for_matrix)):
        if item_list_for_matrix[i][1]==position:
            index_in_matrix = i
            flag = True
        if item_list[i].matrix_position == position:
            index = i
            flag = True

    if flag:
        item_list_for_matrix.pop(index_in_matrix)
        item_list.pop(index)
        return item_list_for_matrix, item_list
    else:
       return False





spike = pygame.image.load("./img/spike.png")
little_spike = pygame.image.load("./img/little_spike.png")
block = pygame.image.load("./img/block.png")
reversed_spike = pygame.transform.rotate(spike, 180)
reversed_little_spike = pygame.transform.rotate(little_spike, 180)
mode_list = [0,block, spike, little_spike, reversed_spike, reversed_little_spike]



