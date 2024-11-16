import pygame
from genetic_algorithm_functions import *
from level_editor import *

pygame.init()
screen = pygame.display.set_mode((720,620))


#USER-CODE-BEGIN

trainer = Trainer(screen, "stereo_madness", "./temporary_saves","./trained_models/stereo_madness_model.txt",6, 30000)
trainer.run()

# tester = Tester(screen, "stereo_madness" , "./trained_models/stereo_madness_model.txt")
# tester.run()

# level_editor = LevelEditor(screen, "stereo_madness")
# level_editor.run()

#USER-CODE-END

pygame.quit()