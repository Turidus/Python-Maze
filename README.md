A maze generator in Python 3.6 Depends on Pillow https://pillow.readthedocs.io/en/4.2.x/index.html

This project provides a class called Maze. It can be of arbitary (two dimensional) size. 
After initilizing the class with the desired size, it can be formed into a maze by different algorithms. The default function 
implements the growing tree algorithm http://weblog.jamisbuck.org/2011/1/27/maze-generation-growing-tree-algorithm.

The formed maze can be parsed into an image which can be saved as picture file (default format is .png). The size of the 
picture will be (sizeOfMaze * 2 + 1)pixel.
