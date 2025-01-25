import pygame
from genetic_algorithm_functions import *
from level_editor import *

pygame.init()
screen = pygame.display.set_mode((1080,720))


#USER-CODE-BEGIN

trainer = Trainer(screen, "stereo_madness", "./temporary_saves",None,1, 30000)
trainer.run()

# tester = Tester(screen, "stereo_madness" , "./trained_models/stereo_madness_model.txt")
# tester.run()

# level_editor = LevelEditor(screen, "stereo_madness")
# level_editor.run()

#USER-CODE-END

pygame.quit()