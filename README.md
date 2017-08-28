#A maze generator in Python 3.6 

Depends on Pillow 4.2 https://pillow.readthedocs.io/en/4.2.x/index.html

This project provides a class called Maze. It can be of arbitary (two dimensional) size. 
After initilizing the class with the desired size, it can be formed into a maze by different algorithms. The default function 
implements the growing tree algorithm http://weblog.jamisbuck.org/2011/1/27/maze-generation-growing-tree-algorithm.


##Usage:
    
        import Maze
    
    First create a new maze object. The arugments decide the size in X and Y in **floor tiles**.
    The **finale amount** of tiles in a maze in one direction is size * 2 + 1:
        
        newMaze = Maze(100,100)
    
    A maze can also be named:
        
        newMaze = Maze(100,100, mazeName = "MyMaze")
        

    A maze object starts unformed. It then has to be formed by a chosen algorithm.
    This can be done only once per maze. After it was formed only the brading function can 
    change the maze.
    The default algorithm is the GrowTree algorithm:
    
        newMaze.makeMazeGrowTree()
    
    This function can be called with weights (0 - 100). These define the behavior of the the maze.
    Roughly speaking, the higher both weights are, the harder the maze is to solve.
    
        newMaze.makeMazeGrowTree(89,32)
    
    
    After a maze is formed it can be braided. This either removes all dead ends:
        
        newMaze.makeMazeBraided(-1)
        
    or introduces random loops, by give a percentage of tiles that will have additional connections:
        
        newMaze.makeMazeBraided(7)
    
    
    After a maze is finished, it can be made into a picture by using Pillow:
    
        mazeImageBW = newMaze.makePP()
        
    It defaults two a black and white picture (walls balck, floors white) with a edge length of 
    one tile square of 10 pixels
    This can be changed:
        
        mazeImageColor = newMaze.makePP(mode = "RGB",colorWall = "blue", colorFloor = (100,0,255),pixelSizeOfTile = 3)
    
    
    This class also provides a way to write these images to disk.
    It defaults to a png file with a name constructed out of the name and pixel size of the maze.
    
        newMaze.saveImage(mazeImageBW)
        
    The name and format can be choosen in differnt ways;
    (see https://pillow.readthedocs.io/en/4.2.x/reference/Image.html#PIL.Image.Image.save)
    
        newMaze.saveImage(mazeImageColor, name = "ColorImage.png")
        
        newMaze.saveImage(mazeImageColor, name = fileObject, format = "PNG")
        
        newMaze.saveImage(mazeImageColor, name = "ColorImage", format = "PNG")
        
    The last option results in a file without extension. Not practical on Windows.
        
        
    
    
