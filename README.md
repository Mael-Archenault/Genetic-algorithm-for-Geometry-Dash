# Context

First I would like to give credit to who it is due. I did not have the idea for this project, I just watched a youtube video that I found amazing. I wanted to try the same concept to see if I could achieve different results.
The youtube video : https://www.youtube.com/watch?v=MTcXW94V838&ab_channel=CodeBH

# Content of the project
## General Overview
This project contains 3 differents modes :
- Training mode: to run a genetic algorithm on a specific map and save the best models
- Test mode: to test models that were found by the genetic algorithm
- Level editor : to have an easy access to level creation

## Detailled content

# User Manual

First you will need to install 2 pythons libraries (if not already installed). In a python console write:
- pip install pygame
- pip install keyboard

Download all files on the repository and place them in the same directory. The file you will use to launch each mode is called "main.py"

## Launch a training
To launch a training, you will need to create an instance of class "Trainer". Arguments are the following:
-screen: the display surface that will be used to render objects. **Use the instance that were created before : screen**
-map_name: the name of the map that will be used. The map should be located in the directory "/map".
-save_folder_path: the path to the folder where you want to store the models of the training. This path can be absolute or relative
-base_model_path: if you want to restart a training from a pre-existing model, place the path of the model in this argument. Otherwise type "None".
-batch_size: a number defining the number of individual for each generation

Once the instance of "Trainer" is created, you only need to call name of instance.run()
In "main.py", between the "user-code-begin" and "user-code-end", 
