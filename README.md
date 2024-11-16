# Context

First I would like to give credit to who it is due. I did not have the idea for this project, I just watched a youtube video that I found amazing. I wanted to try the same concept to see if I could achieve different results.
The youtube video : https://www.youtube.com/watch?v=MTcXW94V838&ab_channel=CodeBH

The main objective of the project was to build a clone of the game Geometry Dash. In the aftermath, I implemented a genetic algorithm to create auto-players of the game.
# Principle used
This algorithm follows rules of a genetic algorithm:

- we run a game with generations of randomly generated "players"
- the best "player" of one given generation is used as a model to create the next generation
- we repeat until we get to a satisfying result

To generate the behaviour of the player I used two items:

- triggers: they are the sensors of the "player". A trigger is activated if it is positioned over its target object (Example : a spike trigger will activate if the hitbox of the trigger touches the hitbox of a spike). There is also negative triggers, that are always activated except when they touch their target object.
- nodes: they are used to group triggers. One node is activated if all of its associated triggers are activated. Once the node is activated, the cube jumps.

With this method, we can generate random behaviour by generating random node/trigger configurations (type, position, association, etc...). Each node is locked relatively to the cube (so are the triggers)


# Content of the project
## General Overview
This project contains 3 differents modes :
- Training mode: to run a genetic algorithm on a specific map and save the best models
- Test mode: to test models that were found by the genetic algorithm
- Level editor : to have an easy access to level creation

## Detailled content
-/img: contains all png used for the project
-/maps: contains all maps with a .txt extension
-/save: contains models that I have already trained
-arial.ttf: font used to display time on the screen
-trigger_library.py: contains all classes concerning triggers and nodes
-map.py: contains the map class, to convert .txt to a playable map in the game
-object_library.py: contains classes relative to spikes and blocks, the 2 obstacles implemented in the game
-gamemodes.py: contains class describing all gamemodes we can play (only cube for the moment)
-level_editor.py: contains the class able to open and run the level editor
-genetic_algorithm_functions.py: contains the main training and testing functions for the genetic algorithm
-main.py: the file to write into to train and test models, as well as editing maps.

# User Manual

First you will need to install 2 pythons libraries (if not already installed). In a python console write:
- pip install pygame
- pip install keyboard

Download all files on the repository and place them in the same directory. The file you will use to launch each mode is called "main.py".

## Launch a training
To launch a training, you will need to create an instance of class "Trainer" between the "user-code-begin" and "user-code-end". Arguments are the following:
-screen: the display surface that will be used to render objects. **Use the instance that were created before : screen**
-map_name: the name of the map that will be used. The map should be located in the directory "/maps".
-save_folder_path: the path to the folder where you want to store the models of the training. This path can be absolute or relative
-base_model_path: if you want to restart a training from a pre-existing model, place the path of the model in this argument. Otherwise type "None".
-batch_size: a number defining the number of individual for each generation

Once the instance of "Trainer" is created, you only need to call (name of instance).run()

Once the window has appeared you have various options :
- "c": stands for "collisions", toggle the display of the hitboxes of objects
- "d": stands for "display", once this mode is toggled, the screen stops to be rendered. That way the simulation is no longer limited by the screen refresh rate. **I strongly recommend to use this if you want to train models**
Each generation features a foundational model that serves as the basis for all other models within that generation. Epsilon is a factor that gives the amount of likelyhood between the generated model and the base model. A high value of Epsilonn will make the generation more likely to change its models from the base model. 
- "e": decrease the value of Epsilon
- "r": increase the value of Epsilon

Epsilon is already decreased between each generation, to make sure the algorithm converges to a fixed solution. However, it can sometimes be useful to re-direct the training when we see a dead-end, by modifying value of Epsilon during the training.

-"right arrow": used to display sequentially all nodes of the current model

## Test a model

In main.py, between the "user-code-begin" and "user-code-end", create an instance of "Tester" with arguments :
-screen: the display surface that will be used to render objects. **Use the instance that were created before : screen**
-map_name: the name of the map that will be used. The map should be located in the directory "/maps".
-model_path: the absolute or relative path to the model you want to test

Once the instance is created, just run (name of instance).run()

Once the window has appeared you have various options :
- "c": stands for "collisions", toggle the display of the hitboxes of objects
-"right arrow": used to display sequentially all nodes of the current model
- "up" or "space": only in this mode, you can jump with these keys

## Launch the editor

In main.py, between the "user-code-begin" and "user-code-end", create an instance of "LevelEditor" with arguments :
-screen: the display surface that will be used to render objects. **Use the instance that were created before : screen**
-name: the name of the map you are working on (necessarily inside /maps). If the map already exists, it is modified. Otherwise, it is created.

Once the instance is created, just run (name of instance).run()

Once the window has appeared you have various options :
- "n": stands for "next", it selects the next object as object to place. You can see a preview of the current object in the top-right corner.
-"s": to save the map
- Arrows : to move on the grid
- You can place an element by clicking on an empty place. If the place has an object, the click will delete it.

I hope you'll have fun with this algorithm. Don't hesitate to make your own modifications. Have fun.
