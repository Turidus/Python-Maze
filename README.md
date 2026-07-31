from Maze import maze_image_bw from Maze import maze_image_bw

# A maze generator in Python 3.6 

**Depends on Pillow 4.2** https://pillow.readthedocs.io/en/4.2.x/index.html

This project provides a class called Maze. It can be of arbitrary (two-dimensional) size. 
After initializing the class with the desired size, it can be formed into a maze by different algorithms. 
The default function implements the growing tree algorithm:
http://weblog.jamisbuck.org/2011/1/27/maze-generation-growing-tree-algorithm.


### Usage:

#### 0. Provide Pillow
This generator uses Pillow, a fork of the Python Image Library. See the link on how to install Pillow.
https://pillow.readthedocs.io/en/4.2.x/installation.html

#### 1. Optional Import
Import the Maze class into your project if you want to use the maze inside a project. If you 
just want nice picture of a maze, you can simply uncomment and modify the examples and run this file directly. 
The examples are provided on the bottom of Maze.py.
```python    
import Maze
```
#### 2. Create a maze object
Create a new maze object. The arguments decide the size in X and Y in **floor tiles**.
The **finale amount** of tiles in a maze in one direction is size * 2 + 1:
```python      
new_maze = Maze(100,100)
```      
A maze can also be named:
```python      
new_maze = Maze(100,100, maze_name = "MyMaze")
```    

#### 3. Form the maze
A maze object starts unformed. It has to be formed by a chosen maze algorith, which can be
only done **once** per maze. After it was formed only the braiding function can change the maze.
The default algorithm is the GrowTree algorithm:

```python  
new_maze.make_maze_grow_tree()
``` 
This function can be called with weights (0 - 100). These define the behavior of the maze.
Roughly speaking, the higher both weights are, the harder the maze is to solve.

```python
new_maze.make_maze_grow_tree(weight_high=89, weight_low=32)
```

#### 4. Braid it when needed
After a maze is formed it can be braided, multiple time if necessary.
This either removes all dead ends:

```python    
new_maze.make_maze_braided(-1)
```    
or introduces random loops, by taking a percentage of tiles that will have additional connections:

```python    
new_maze.make_maze_braided(7)
```

#### 5. Make a picture
After a maze is finished, it can be made into a picture, which uses Pillow:

```python
maze_image_bw = new_maze.make_pp()
```    
It defaults two a black and white picture (walls black, floors white) with a tile size of 
10 by 10 pixels
This can be changed into colored picture:

```python    
maze_image_color = new_maze.make_pp(mode="RGB", color_wall="blue", color_floor=(100, 0, 255), pixel_size_of_tile=3)
```

#### 6. Save the picture
This class also provides a way to write these images to disk.
It defaults to a png file with a name constructed out of the name and pixel size of the maze.

```python
new_maze.save_image(maze_image_bw)
```   
The name and format can be chosen in different ways;
(see https://pillow.readthedocs.io/en/4.2.x/reference/Image.html#PIL.Image.Image.save)

```python
new_maze.save_image(maze_image_color, name="ColorImage.png")

new_maze.save_image(maze_image_color, name=path_object, save_format="PNG")

new_maze.save_image(maze_image_color, name="ColorImage", save_format="PNG")
```
The last option results in a file without extension. Not practical on Windows.
        
        
    
    
