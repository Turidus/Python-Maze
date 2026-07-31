"""
    Written by turidus (github.com/turidus) in python 3.6.0
    Dependend on Pillow 4.2, a fork of PIL (https://pillow.readthedocs.io/en/4.2.x/index.html)
"""
from PIL import Image,ImageDraw, ImageColor
import random as rnd
import re

from lxml.doctestcompare import temp_install
from websockets.legacy.server import remove_path_argument


class Maze:
    """ This Class represents a Maze. After init, it consists of an unformed maze made out of a nested list (grid) of
            untouched floor tiles. It sizes in X and Y are dependent on input.
            It depends on Pillow, a PIL fork (https://pillow.readthedocs.io/en/4.2.x/index.html).
            
            The finale internal representation of the maze is a nested list of touched floor tiles that are connected to at 
            least one neighbour. Walls will be added by the graphic representation. 
            
            The maze can be formed by two different algorithms, modified Prim's and Growing Tree. A short 
            explanation of the used algorithms (and many more) can be found at http://www.astrolog.org/labyrnth/algrithm.htm
            A more in depth explanation can be found in this article series:
            Prims Algorithm: http://weblog.jamisbuck.org/2011/1/10/maze-generation-prim-s-algorithm
            Growing Tree Algorithm: http://weblog.jamisbuck.org/2011/1/27/maze-generation-growing-tree-algorithm
            
            This classes raises Maze Error on invalid input; when a maze get the command to change after it was formed or
            if the maze gets the command to make a graphical representation of an unformed maze.
            
            Content:
            
            private subclass    Maze Tile:  Structure representing a single tile.
            private subclass    Maze Error: Custom Error
            
            private function    __init_(int,int,string):    this function takes two integers for size(X,Y)
                                                            and an optional string for the name of the Maze.
            private function    __str__:    Returns a formated string with as many columns and lines as sizeX and sizeY respectively.
                                            The cells are filled with the status of the tile (workedOn, True or False)
            private function    __repr()__ :    Returns a string with the size of the Maze as description 
            private function    __getNextTiles(int,int):  returns a list of available tiles to the specified coordinates
            private function    __connectTiles(tileA,tileB): connects specified tiles to make a way
            private function    __connectTilesWithString(tile,string): connects two tiles dependent on one tile and a given connection string.
            private function    __makeEntryandExit(): creates an entry and an exit into the maze
            
            public function     makeMazeSimple():  returns True
                                                    This function takes the unformed maze and forms it with the modified Prim's
                                                    algorithm. This results in a simple to solve maze. These algorithms are less
                                                    efficient than the Growing Tree algorithm.
            public function     makeMazeGrowingTree(int,int): returns True
                                                              This algorithm forms the maze with the Growing Tree algorithms
                                                              takes two integer values between 0 and 100, with the first 
                                                              integer bigger than the second one. These are weights defining the
                                                              behavior of the algorithm. (see link above)
            public function     makeMazeBraiding(int): This function works as braider on a formed maze. Can either work as dead end remover (-1)
                                                        or produce random loops (0-100), decided by the weight.
                                                        
            public function     makePP(var,int,int,int):    Takes an optional string for color mode and two optional argument 
                                                            defining the color of wall and floor.
                                                            
                                                            Returns an image object.
                                                            
                                                            This function takes a formed maze and creates a picture with the help of Pillow.
                                                            The size of the picture depends on the chosen pixelSizePerTiles and the amount of tiles
                                            
            public function     saveImage(image,string): Specialized implementation of Pillow's Save function. Takes an image and
                                                                saves it with an (optional) given name/path object and format. 
                                                                If no name is given, a name will be constructed.
    """

    class __MazeTile:
        """ This subclass is a structure representing a single tile inside the Maze. This tile has a X and Y coordinate which are specified on generation.
            It can also be specified if the tile is a wall or a floor.
        """
        
        def __init__(self, x, y, is_wall = True):
            """Generator for the __MazeTile class
            """
            
            
            self.workedOn = False   # Needed for certain generation algorithm to define if a tile as already be touched
            self.wall = is_wall      # Is the tile a wall (True) or a floor (False). Mostly for future proving
            self.coordinateX = x    # Defining the X coordinate
            self.coordinateY = y    # Defining the Y coordinate
            self.connectTo = []     # A list of strings that describe the tiles this tile is connected to (North, South, West, East)

            
        def __str__(self):
            return "X: " + str(self.coordinateX)+" "+ "Y: " + str(self.coordinateY) + " " + str(self.connectTo)
            
        
        def __repr__(self):
            
            return "__MazeTile, wall = {}, worked on = {} ,x = {}, y = {} ---".format(self.wall , self.workedOn, self.coordinateX, self.coordinateY)
            
    class __MazeError(Exception):
        """ Custom Maze Error, containing a string describing the error that occurred
                and an error code:
                
                errorcode       meaning
                1               A wrong value was passed
                2               Out of bounds of list
                3               A maze algorithm tried to change a already changed maze
                4               A function that assumed a formed maze found an unformed maze
        """
        def __init__(self, string, error_code):
            self.string = string
            self.error_code = error_code
        def __str__(self):
            return str(self.string) + " |Error code: {}".format(self.error_code)
            
    
    
    
    
    def __init__(self, dimension_x, dimension_y, maze_name ="A_Maze"):
        """Generator for the Maze class.
           It takes two integer to decide the size of the maze (X and Y). It also takes an optional string to determine the name of the maze.
        
        """
        
        if not isinstance(dimension_x, int) or not isinstance(dimension_y, int):      #Checking input errors
            raise self.__MazeError("Maze dimensions have to be an integer > 0",1)
            
        
        if dimension_x < 1 or dimension_y < 1:
            raise self.__MazeError("Maze dimensions have to be an integer > 0",1)
        
            
        if not isinstance(maze_name, str):
            raise self.__MazeError("The name of the Maze has to be a string",1)
        
        
            
        self.sizeX = dimension_x     #The size of the Maze in the X direction (from left to right)
        self.sizeY = dimension_y     #The size of the Maze in the Y direction (from up to down)
        
        self.name = maze_name    #The name of the Maze. Can be any string
        self.__mazeIsDone = False     #When this flag is False, no picture can be made. When this flag is True, the maze can not be changed
        
        self.mazeList = []          #A nested List of maze Tiles. The internal representation of the maze
        
        self.wallList = []          #A list of all lists that are walls (needed for certain algorithm)
        self.tileList = []          #A single list of all tiles (needed of certain algorithm)
        
        self.mazeString = ""        #A string describing the Maze in a pseudo graphical manner, gets generated everytime __str__() gets called
        
        
        
        
    def __str__(self): 
        """ Generates the mazeString which is a string with as many columns as sizeX and as many lines as sizeY.
            The cells are filled with the connection of the tile at these coordinates.
        """
        
        self.mazeString = ""
        
        for row in self.mazeList:
            
            for tile in row:
                
                self.mazeString += "{:^20}".format(str(tile.connectTo))
        
            self.mazeString += "\n"
        
        
        return self.mazeString
        
            
        
    def __repr__(self): 
        """ Generates a representing string
        """
            
            
        return "This is a Maze with width of {} and height of {}".format(self.sizeX , self.sizeY)
    
    def __get_next_tiles(self, X, Y):
        """ 
            This function collects all nearest neighbour of a tile. Important for tiles that lay on a border.
            
        """
        
        if X < 0 or Y < 0:  #Checks input error (this should never happen)
            
            raise self.__MazeError("Inputs have to be an integer > 0",1)
        
        temp_list = []
        
        try:
            if Y == 0:
                pass
            else:
                temp_list.append(self.mazeList[Y-1][X])
        
        except IndexError:
            pass

        try:
            temp_list.append(self.mazeList[Y+1][X])
        except IndexError:
            pass
            
        try:
            if X == 0:
                pass
            else:
                temp_list.append(self.mazeList[Y][X-1])
        except IndexError:
            pass
            
        try:
            temp_list.append(self.mazeList[Y][X+1])
        except IndexError:
            pass
        
        return temp_list

    @staticmethod
    def __connect_tiles(tile_a, tile_b):
        """   Takes two tiles and returns True if successful.
              Connect the two given tiles to make a way. This is used to decide where walls shouldn't be in the final picture.
              The Tile connectTo field is appended by the compass direction of the tile it connects to (N,S,E,W).
        """
        x1 = tile_a.coordinateX
        y1 = tile_a.coordinateY

        x2 = tile_b.coordinateX
        y2 = tile_b.coordinateY

        if x1 == x2:

            if y1 < y2:

                tile_a.connectTo.append("S")
                tile_b.connectTo.append("N")

            elif y1 > y2:
                tile_a.connectTo.append("N")
                tile_b.connectTo.append("S")

        else:
            if x1 < x2:

                tile_a.connectTo.append("E")
                tile_b.connectTo.append("W")

            else:
                tile_a.connectTo.append("W")
                tile_b.connectTo.append("E")

        return True

    def __connect_tiles_with_string(self, tile, direction):
        """Takes one tile and a direction string (N,S,W,E) to connect two tiles. Returns True.
                Raises __MazeError if a tile wants to connect out of the maze.
                Make sure that this only connects unconnected tiles
        """

        if direction == "N":

            try:

                if tile.coordinateY == 0:   #This prevents list[-1] situations and two holes in the border wall
                    raise IndexError
                    
                self.mazeList[tile.coordinateY -1][tile.coordinateX].connectTo.append("S")
                tile.connectTo.append("N")
                
            except IndexError:
                raise self.__MazeError("This tile can not connect in this direction",2)
        
        elif direction == "S":

            try:
                self.mazeList[tile.coordinateY + 1][tile.coordinateX].connectTo.append("N")
                tile.connectTo.append("S")
                
            except IndexError:
                raise self.__MazeError("This tile can not connect in this direction",2)     
               
        elif direction == "W":
            
            try:
                if tile.coordinateX == 0:
                    raise IndexError
                self.mazeList[tile.coordinateY][tile.coordinateX - 1].connectTo.append("E")
                tile.connectTo.append("W")   
                             
            except IndexError:
                raise self.__MazeError("This tile can not connect in this direction",2)
                
        elif direction == "E":
            
            try:
                self.mazeList[tile.coordinateY][tile.coordinateX + 1].connectTo.append("W")
                tile.connectTo.append("E")
                
            except IndexError:
                raise self.__MazeError("This tile can not connect in this direction",2)
                
        else:
            raise self.__MazeError("This was not a direction string",1)
            
        return True
        
    
    def __make_entry_and_exit(self, random = False):
        """ Takes an optional boolean
            If random is set to True, it chooses the entry and exit field randomly.
            It set to False, it chooses the left uppermost and right lowermost corner as entry.
        """
        if random:
            
            tile = rnd.choice(self.mazeList[0])
            tile.connectTo.append("N")
                    
            tile = rnd.choice(self.mazeList[-1])
            tile.connectTo.append("S")
        else:
            self.mazeList[0][0].connectTo.append("N")
            self.mazeList[-1][-1].connectTo.append("S")
            
        return True
                
            
        
    
    def make_maze_simple(self):
        """Algorithm to form the final maze. It works like the modified Prim's algorithm
            (http://weblog.jamisbuck.org/2011/1/10/maze-generation-prim-s-algorithm)
            
            It works on the initial mazeList. The finale mazeList consist of touched floor tiles that are connect
            with each other.
            The end result is a easy to solve perfect 2D maze.
            
            This runs much slower than GrowTreeAlgorithm.
             
             
            A short description of what happens:
            At first a untouched (tile.workedOn = False) tile is randomly chosen, it is transformed to a
            touched tile and all neighbour are put into a frontier list.
             
            From this list comes the next tile which is again transformed into a touched tile
            and removed from the frontier list.
            Then this touched tile is connected to a randomly neighbor that was also touched.
            All neighbours that are untouched tiles are added into the frontier list.
             
            This will run until the frontier list is empty.
        """
        
        if self.__mazeIsDone:     #Can only run if the maze is not already formed
            raise self.__MazeError("Maze is already done",3)
            
        for indexY in range (0,self.sizeY):     #This loops generates the mazeList and populates it with new untouched floor tiles
            temp_list = []
            
            for indexX in range(0,self.sizeX):
                new_tile = self.__MazeTile(indexX, indexY, is_wall= False)
                temp_list.append(new_tile)
                
            self.mazeList.append(temp_list)
        
        front_list = []          #A list of all untouched tiles that border a touched tile
        starting_tile = rnd.choice(rnd.choice(self.mazeList))    #A randomly chosen tile that acts as starting tile
        
        starting_tile.workedOn = True    #This flag always gets set when a tile has between worked on.
        front_list += self.__get_next_tiles(starting_tile.coordinateX, starting_tile.coordinateY)  #populates the frontier
                                                                                                #list with the first 2-4 tiles 
        

        while len(front_list) > 0 : #When the frontier list is empty the maze is finished because all tiles have been connected
            
            

            new_front_tiles = []
            worked_on_list = []
            
            rnd.shuffle(front_list)
            next_tile = front_list.pop()
            next_tile.workedOn = True
            
            temp_list = self.__get_next_tiles(next_tile.coordinateX, next_tile.coordinateY)
            

            for tile in temp_list: #Finds all neighbours who are touched and all that are a untouched
                if tile.workedOn:
                    
                    worked_on_list.append(tile)
                    
                else:
                    
                    if not tile in front_list:
                        new_front_tiles.append(tile)
                    
            front_list += new_front_tiles
            

            
            if len(worked_on_list) > 1:   #Chooses the neighbor the tile should connect to
                connect_tile = rnd.choice(worked_on_list)
            
            else:
                connect_tile = worked_on_list[0]
            
            self.__connect_tiles(next_tile, connect_tile)
            
        self.__make_entry_and_exit()     #Finally produces a Entry and an Exit
        self.__mazeIsDone = True
        return True
            
   
    def make_maze_grow_tree(self, weight_high = 99, weight_low = 97):
        
        """Algorithm to form the final maze. It works like the Growth Tree algorithm
            http://weblog.jamisbuck.org/2011/1/27/maze-generation-growing-tree-algorithm
            
            It works on the initial mazeList. The finale mazeList consist of touched floor tiles that are connect
            with each other.
            The end result is a perfect 2D maze that has a variable hardness in solution
            
            This runs much faster than makeMazeSimple and should be used as default.
            
            This algorithm can be modified with two weights between 0 and 100. 
            weightHigh should always be higher or equal to weightLow.
            
            Three extremes:
                      
            weightHigh == 100, weightLow == 100:
                
                The algorithm always takes the newest tile out of the choice list and behaves
                like a reversed backtrace. Very hard to solve
                http://weblog.jamisbuck.org/2010/12/27/maze-generation-recursive-backtracking
            
            weightHigh == 100, weightLow == 0
                
                The algorithm always chooses the next tile randomly
                and behaves like Prim's algorithm, but runs much faster.
                Solving is less hard than 100/100

                
            weightHigh == weightLow == 0:
                
                The algorithm always chooses the oldest tile in the list
                The resulting maze will have a lot of long passageways (high river factor) and
                will be trivial to solve.
                
                
            I personally like a 99/97 distribution but feel free to experiment yourself.
             
            A short description of what happens:
            At first one untouched tile is randomly chosen, it is transformed to a
            touched tile, and it is put into a list of available tiles.
            
            From this list is a tile chosen, how depends on the weights.
            If this tile has no untouched neighbours it is removed from the list of available tiles.
            Else a neighbour is chosen, marked as touched, put into the available tile list and
            connected to the current tile.
            This loops until the list of available tiles is empty.
        """
        
        if self.__mazeIsDone: #This function only runs of the Maze is not already formed.
            raise self.__MazeError("Maze is already done",3)
            
        for indexY in range (0,self.sizeY):     #This loops generates the mazeList and populates it with new untouched floor tiles
            temp_list = []
            
            for indexX in range(0,self.sizeX):
                new_tile = self.__MazeTile(indexX, indexY, is_wall= False)
                temp_list.append(new_tile)
                
            self.mazeList.append(temp_list)
        
        
        starting_tile = rnd.choice(rnd.choice(self.mazeList))    #First tile is randomly chosen
        starting_tile.workedOn = True
        
        choice_list = [starting_tile] #The list of available tiles
        
        while len(choice_list) > 0:  #Runs until choiceList is empty
            
            choice_ = rnd.random() * 100    #This random choice determines how the next tile is chosen
            
            if choice_ <= weight_low:
                next_tile = choice_list[-1]
            elif weight_low < choice_ < weight_high:
                next_tile=rnd.choice(choice_list)
            else:
                next_tile = choice_list[0]
            
            nei_list = []    #List of neighbours
            
            for tile in self.__get_next_tiles(next_tile.coordinateX, next_tile.coordinateY):
                
                if not tile.workedOn:
                    nei_list.append(tile)
            
            if len(nei_list) == 0:   #either removing this tile or choosing a neighbour to interact with
                choice_list.remove(next_tile)
            
            else:
                connect_tile = rnd.choice(nei_list)
                connect_tile.workedOn = True
                choice_list.append(connect_tile)
                self.__connect_tiles(next_tile, connect_tile)
                
        
            
        self.__make_entry_and_exit() #finally marking an Entry and an Exit
        self.__mazeIsDone = True
        return True
        
    def make_maze_braided(self, weight_braid = -1):
        """This function produces a braided maze by either removing dead ends or by producing
            random loops. It takes an Integer between -1 and 100.
            
            weightBraid decides how many percent of the tiles should create loops. (0-100)
            If set to -1, it will braid the maze by removing all and only dead ends
            
            Raises a __MazeError on wrong input or if the maze is unformed
        """
        if not self.__mazeIsDone:
            raise self.__MazeError("Maze needs to be formed first",4)

        if not isinstance(weight_braid, int) or weight_braid <  -1 or weight_braid > 100:
            raise self.__MazeError("weightBraid has to be >= -1",1)
        
        elif weight_braid == -1:
            for row in self.mazeList:
                for tile in row:
                    if len(tile.connectTo) == 1: #All tiles that are only connected to one other tile are dead ends
    
                        direction_list=["N","S","W","E"]
                        direction_list.remove(tile.connectTo[0])
                        
                        rnd.shuffle(direction_list) #Randomizing connections
                        for direction in direction_list:
                            
                            try:
                                self.__connect_tiles_with_string(tile, direction)
                                break
                                
                            except self.__MazeError as mazeExcept:
                                if mazeExcept.error_code == 2:
                                    pass
                                    
                                else:
                                    raise
        else:
            for row in self.mazeList:
                for tile in row:
                    if weight_braid >= (rnd.random() * 100): #Weight decides if this tiles gets an additional connection
                        
                        direction_list=["N","S","W","E"]
                        for connection in tile.connectTo:
                            direction_list.remove(connection)
                             
                        rnd.shuffle(direction_list) #Randomizing connections
                        for direction in direction_list:
                            
                            try:
                                self.__connect_tiles_with_string(tile, direction)
                                break
                                
                            except self.__MazeError as mazeExcept:
                                if mazeExcept.error_code == 2:
                                    pass
                                    
                                else:
                                    raise

        return True
        
    def make_pp(self, mode ="1", color_wall = 0, color_floor = 1, pixel_size_of_tile = 10, ):
        """
        This generates and returns a Pillow Image object. It takes into account the size of the maze and
            the size of the individual pixel defined with pixelSizeOfTile. Defaults to 10 pixel.
            
            It creates this picture by drawing a square with the defined size for every tile in
            the mazeList on a background. It then proceeds to draw in the connections this tile has by checking
            tile,connectTo.
            
            The default mode this picture is created is 1 bit per pixel and allows only for white (1) and black(0)
            pictures.
            
            The mode and colors can be changed to RGB, but this will increase the picture size massively (24 times).
            
            Allowed modes:
            "1":    1 bit per pixel, colors are 1-bit integers. 1 for white and 0 for black
            "RGB":  3x8 bit per pixels. colors can be given either as three 8 bit tuples (0,0,0)-(255,255,255)
                    or html color strings.
            
            The pixelSizeOfTile decides the edge length on of tile square in the picture.

            Raises __MazeError if the maze is not already finished and on wrong input.
        """
        if not self.__mazeIsDone:
            raise self.__MazeError("There is no Maze yet",4)
            
        if mode == "1":                                                         #Checking for input errors
            if color_wall in (1, 0) and color_floor in (1, 0):
                pass
            else:
                raise self.__MazeError("In mode \'1\' the color values have to be 0 for black or 1 for white",1)
                
        elif mode == "RGB":
            
            try:
                if isinstance(color_wall, str):
                    color_wall = ImageColor.getrgb(color_wall)
                
                elif isinstance(color_wall, tuple) and len(color_wall) == 3:
                    for i in color_wall:
                        if not isinstance(i,int) or (i < 0 or i > 255):
                            raise self.__MazeError("RGB mode excepts only 8-bit integers",1)
                
                else:
                    raise self.__MazeError("RGB Mode only excepts color strings or 3x8bit tuples",1)
                
                    
                if isinstance(color_floor, str):
                    color_floor = ImageColor.getrgb(color_floor)
                
                elif isinstance(color_floor, tuple) and len(color_floor) == 3:
                    for i in color_floor:
                        if not isinstance(i,int) or (i < 0 or i > 255):
                            raise self.__MazeError("RGB mode excepts only 8-bit integers",1)
                
                else:
                    raise self.__MazeError("RGB Mode only excepts color strings or 3x8bit tuples",1)
                    
            except ValueError:
                raise self.__MazeError("RGB mode excepts 140 common html color strings. This was not one of them",1)
                
            
                
        else: raise self.__MazeError("The mode was not recognized. Only \'1\' or \'RGB\' are allowed",1)  
        
        if not isinstance(pixel_size_of_tile, int) or pixel_size_of_tile <= 0:
            raise self.__MazeError("the size of the tiles has to be an integer > 0",1) #Finished looking for input errors.
                
        
        size = (pixel_size_of_tile * (self.sizeX * 2 + 1), pixel_size_of_tile * (self.sizeY * 2 + 1))
            #Determines the size of the picture. It does this by taking the number of tiles,
                # multiplying it with 2 to account for walls or connections and adds one for offset
        

        image = Image.new(mode, size, color_wall) #Generates a Pillow Image object
        draw_image = ImageDraw.Draw(image)
        
        for row in self.mazeList: #Iterates over all tiles
                
                for tile in row:
                    #There are floor tiles at position 1,3,5..., at position 0,2,4,6... are either wall tiles or connecting tiles.

                    x = ((tile.coordinateX  + 1) * 2 - 1) * pixel_size_of_tile
                    y = ((tile.coordinateY  + 1) * 2 - 1) * pixel_size_of_tile
                    draw_image.rectangle((x, y, x + pixel_size_of_tile - 1, y + pixel_size_of_tile - 1), fill = color_floor)

                    
                    if "N" in tile.connectTo:
                        draw_image.rectangle((x, y - pixel_size_of_tile, x + pixel_size_of_tile - 1, y - 1), fill = color_floor)
                        
                    if "S" in tile.connectTo:
                        draw_image.rectangle((x, y + pixel_size_of_tile, x + pixel_size_of_tile - 1, y + pixel_size_of_tile + pixel_size_of_tile - 1), fill = color_floor)
                        
                    if "W" in tile.connectTo:
                        draw_image.rectangle((x - pixel_size_of_tile, y, x - 1, y + pixel_size_of_tile - 1), fill = color_floor)
        
                    if "E" in tile.connectTo:
                        draw_image.rectangle((x + pixel_size_of_tile, y, x + pixel_size_of_tile + pixel_size_of_tile - 1, y + pixel_size_of_tile - 1), fill = color_floor)

        return image #returns an image object
        
                        
    def save_image(self, image, pixel_size_of_tile = 1, name = None, save_format = None):
        """Specialized implementation of Pillow's Save function. Takes an image and
            saves it with an (optional) given name or format. Either this name has contains a
            file extension that is known to Pillow or format has to be specified.
            
            This name has to fulfill all filename rules on the given system!
            
            The name can be a path object, then the format argument needs to be specified.
            
            Details here: https://pillow.readthedocs.io/en/4.2.x/reference/Image.html#PIL.Image.Image.save
            
            If no name is given, a name will be constructed and a png file created.
            The name is constructed out of the maze name and its pixel size in x and y direction.
            To make sure that the image can be saved, all chars that are not letters, numbers or underscores
            will be removed from the maze name and the length will be limited two 120 chars. 
            This will not be done on names that are passed as arguments!
        """
        if name is None:
            temp_name = re.sub(r'[^a-zA-Z0-9_]', '', self.name)  #Regular expression to make name filename safe
            if len(temp_name) > 120:                             #Limiting the length of the filename
                temp_name = temp_name[0:120]
            size = (pixel_size_of_tile * (self.sizeX * 2 + 1), pixel_size_of_tile * (self.sizeY * 2 + 1))
            name = temp_name +"-"+ str(size[0]) + "_" + str(size[1]) + ".png"

            
        image.save(name, save_format)
        
        return True

#Examples:
new_maze = Maze(64,64)
new_maze.make_maze_grow_tree(weight_high = 99, weight_low = 97)
maze_image_bw = new_maze.make_pp()
new_maze.save_image(maze_image_bw)

#newMaze = Maze(50,50,mazeName="ColorMaze")
#newMaze.makeMazeGrowTree(90.80)
#mazeImageColor = newMaze.makePP(mode="RGB",colorWall = "yellow",colorFloor = (250,0,20))
#newMaze.saveImage(mazeImageColor)

#newMaze = Maze(30,30,mazeName = "BraidedMaze")
#newMaze.makeMazeGrowTree(weightHigh = 100, weightLow = 95)
#newMaze.makeMazeBraided(-1)
#mazeImageBW.show()
#newMaze.saveImage(mazeImageBW)
