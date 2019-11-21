# import the pygame module, so you can use it
import pygame
import random
from colorama import init,Back
import csv
from random import choice
from os import path


#TB1 Modules
from tb1util.Constants import *
from tb1util.Enums import GridItemType,Direction
from tb1util.Spritesheet import SpriteSheet
from Astar import astar,Node

class Pasajero:
    def __init__(self,end,distance):
        self.end = end
        self.distance=distance


class GridItem:
    def __init__(self,x,y,width,height):
        self.x=x
        self.y=y
        self.width=width
        self.height=height

class spritesheethouse:
    def __init__(self, filename, cols, rows,screen):
        self.sheet = pygame.image.load(filename).convert_alpha()
        self.screen = screen
        self.cols = cols
        self.rows = rows
        self.totalCellCount = cols * rows

        self.rect = self.sheet.get_rect()
        w = self.cellWidth = int(self.rect.width / cols)
        h = self.cellHeight = int(self.rect.height / rows)
        hw, hh = self.cellCenter = (int(w / 2), int(h / 2))

        self.cells = list([(index % cols * w, int(index / cols) * h, 32, 32) for index in range(self.totalCellCount)])
        self.handle = list([
            (0, 0), (-hw, 0), (-w, 0),
            (0, -hh), (-hw, -hh), (-w, -hh),
            (0, -h), (-hw, -h), (-w, -h),])

    def draw(self,cellIndex, x, y):
        self.screen.blit(self.sheet,(x,y), self.cells[cellIndex])
                #self.screen.blit(self.ss_house.sheet,(rect.x,rect.y))

class Player(GridItem):
    def __init__(self,x,y,width,height,vel,spritesheet = None,direction = Direction.RIGHT, frameIndex = 0):
        super().__init__(x,y,width,height)
        self.vel=vel
        self.direction = direction
        self.frameIndex = frameIndex
        self.spritesheet = spritesheet

        if self.spritesheet is not None:
            frames = []
            for i in range(17):
                frames.append((i*FRAME_SIZE,0,FRAME_SIZE,FRAME_SIZE))

            self.images = [None] * 4
            for dir in [Direction.LEFT,Direction.RIGHT,Direction.DOWN,Direction.UP]:
                a = dir * 4
                b = a + 4
                self.images[dir] = self.spritesheet.images_at(frames[a:b],PLAYER_COLORKEY)

    def move(self):
        if self.direction == Direction.UP:
            self.y -= self.vel
        elif self.direction == Direction.DOWN:
            self.y += self.vel
        elif self.direction == Direction.LEFT:
            self.x -= self.vel
        elif self.direction == Direction.RIGHT:
            self.x += self.vel

        if self.frameIndex < 3:
            self.frameIndex += 1
        else:
            self.frameIndex = 0

    def stop(self):
        self.frameIndex = 0

    def blit_on(self,screen,debug = False):
        if self.images is not None:
            screen.blit(self.images[self.direction][self.frameIndex],(self.x, self.y))
        if debug:
            pygame.draw.rect(screen,COLOR_BLUE,(self.x,self.y,FRAME_SIZE,FRAME_SIZE),1)


def printPath(scenario):
    init(convert=True)
    n = len(scenario)
    for i in range(n):
        k = len(scenario[i])
        for j in range(k):
            value = scenario[i][j]
            background = Back.BLACK
            if value == 10:
                background = Back.MAGENTA
            elif value == 11:
                background = Back.CYAN
            elif value == 2:
                background = Back.BLUE
            elif value == 3:
                background = Back.GREEN
            elif value == 4:
                background = Back.RED
            print(background + '  ', end = '')
        print('')



class Game:
    def __init__(self):
        self.gameover = False
        self.player = None
        self.readScenario()
        self.nuevos = None
        self.pos_actual = None
        self.path = None
        self.house_print  = [[random.randint(0, 19)] * 25 for i in range(25)]

    def calcular_distancias_nuevos(self):
        if len(self.nuevos) >= 1:
            for pas in self.nuevos:
                _end =  Node(None, pas.end)
                _pa =  Node(None, self.pos_actual)
                pas.distance = Node.Manhattan(_pa,_end)
            self.nuevos.sort(key = lambda x: x.distance)

    #def obtener_destino(self):



    #obtener datos del csv
    def readScenario(self,level = 1):
        with open(path.join('resources','maps',f'map{level}.csv'),'r') as csvFile:
            reader = csv.reader(csvFile)
            self.scenario = [[0 for i in range(N_FRAMES)] for j in range(N_FRAMES)]
            for i,row in enumerate(reader):
                for j,gridValue in enumerate(row):
                    pos_x = i * FRAME_SIZE
                    pos_y = j * FRAME_SIZE
                    self.scenario[i][j] = (int(gridValue),pygame.Rect(pos_x,pos_y,FRAME_SIZE,FRAME_SIZE))
        csvFile.close()

    #
    def getScenarioRects(self):
        n = N_FRAMES ** 2
        num_columns = N_FRAMES
        rects = [None] * n
        for index in range(n):
            x = index % num_columns
            y = index // num_columns
            _,rects[index] = self.scenario[x][y]
        return rects


    def getCoordsFromScenarioRectsIndex(self,rectIndex):
        num_columns = N_FRAMES
        x = rectIndex % num_columns
        y = rectIndex // num_columns
        return (x,y)


    def getValueMatrix(self):
        matrix = [[0 for i in range(N_FRAMES)] for j in range(N_FRAMES)]
        for i in range(N_FRAMES):
            for j in range(N_FRAMES):
                matrix[i][j],_ = self.scenario[j][i]
        return matrix

    def printScenario(self,debug = False):
        for i in range(N_FRAMES):
            for j in range(N_FRAMES):
                value,rect = self.scenario[i][j]

                if value == GridItemType.ROAD:
                    pygame.draw.rect(self.screen,COLOR_ROAD,rect)
                elif value == GridItemType.GROUND:

                    pygame.draw.rect(self.screen,COLOR_GREEN,rect)
                    self.ss_house.draw(self.house_print[i][j],rect.x,rect.y)
                    #self.screen.blit(self.ss_house.sheet,(rect.x,rect.y))
                elif value == GridItemType.SEMAPH_GREEN:
                    self.screen.blit(self.semaph_green,(rect.x,rect.y))
                elif value == GridItemType.SEMAPH_RED:
                    self.screen.blit(self.semaph_red,(rect.x,rect.y))
                elif value == GridItemType.TARGET:
                    pygame.draw.rect(self.screen,COLOR_SKYBLUE,rect)
                if debug:
                    pygame.draw.rect(self.screen,COLOR_RED,rect,1)
    """
    def printScenario(self,debug = False):
        for i in range(N_FRAMES):
            for j in range(N_FRAMES):
                value,rect = self.scenario[i][j]
                if value == GridItemType.ROAD:
                    pygame.draw.rect(self.screen,COLOR_ROAD,rect)
                elif value == GridItemType.SEMAPH_GREEN:
                    self.screen.blit(self.semaph_green,(rect.x,rect.y))
                elif value == GridItemType.SEMAPH_RED:
                    self.screen.blit(self.semaph_red,(rect.x,rect.y))
                elif value == GridItemType.TARGET:
                    pygame.draw.rect(self.screen,COLOR_SKYBLUE,rect)
                if debug:
                    pygame.draw.rect(self.screen,COLOR_RED,rect,1)

    """
    def preload(self):
        #Init game
        pygame.init()
        self.screen = pygame.display.set_mode((GAME_WIDTH,GAME_HEIGHT))


        #Load resources
        self.logo = pygame.image.load(path.join('resources','logo.png'))
        self.semaph_red = pygame.image.load(path.join('resources','semaphore-red.png'))
        self.semaph_green = pygame.image.load(path.join('resources','semaphore-green.png'))
        self.ss_player = SpriteSheet(path.join('resources','player.png'))
        self.ss_house = spritesheethouse(path.join('resources','house2.png'), 5, 4,self.screen)

        #Create instances
        self.pos_actual = (0*FRAME_SIZE,0*FRAME_SIZE)

        self.player=Player(0*FRAME_SIZE,0*FRAME_SIZE,FRAME_SIZE,FRAME_SIZE,4,self.ss_player)

        self.nuevos = []
        self.path = []
        pygame.display.set_caption("Autonomous Car Route")

    def create(self):
        #First draw
        self.screen.fill(SCREEN_BACKGROUND_COLOR)
        self.printScenario(DEBUG)
        pygame.display.update()

    def calculatePath(self,x,y,p):

        print("Entro calculate Path")

        npath = len(p)
        #print(npath)
        #print(self.path)

        for i in range(npath - 1):
            y1,x1 = p[i]
            y2,x2 = p[i+1]
            difx = x2 - x1
            dify = y2 - y1
            #agregar mov del jugador
            if difx > 0:
                self.path.append(Direction.RIGHT)
            elif difx < 0:
                self.path.append(Direction.LEFT)
            elif dify > 0:
                self.path.append(Direction.DOWN)
            elif dify < 0:
                self.path.append(Direction.UP)


    def movimiento(self):
        print("Entro movimiento")
        currentTarget = None
        scenarioRects = self.getScenarioRects()
        mouseRect = pygame.Rect(int(self.nuevos[0].end[0]/32)*32,int(self.nuevos[0].end[1]/32)*32,FRAME_SIZE,FRAME_SIZE)
        collideIndex = mouseRect.collidelist(scenarioRects)
        self.pos_actual = self.getCoordsFromScenarioRectsIndex(collideIndex)
        #movimiento
        x,y = self.pos_actual
        #print(f'target: {x,y}')
        gridType,_ = self.scenario[x][y]
        #print(f'gridType: {gridType}')

        if gridType is GridItemType.ROAD:
            _,r = self.scenario[x][y]
            self.scenario[x][y] = (GridItemType.TARGET,r)
            if currentTarget is not None:
                a,b = currentTarget
                _,d = self.scenario[a][b]
                self.scenario[a][b] = (1,d)
            currentTarget = (x,y)


        scenario = self.getValueMatrix()
        start = (self.player.y // FRAME_SIZE,self.player.x // FRAME_SIZE)
        p,evaluated = astar(scenario,start,(self.pos_actual[1],self.pos_actual[0]),Node.Manhattan)
        self.calculatePath(self.pos_actual[0],self.pos_actual[1],p)


    def update(self):
        c = 1
        move = None
        ini = False
        while not self.gameover:
            pygame.time.delay(DELAY)
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.gameover = True
                # click event and get the position
                if event.type ==pygame.MOUSEBUTTONDOWN:

                    print("Entro click")
                    self.path = []
                    c = 1
                    move = None
                    ini = True
                    mx,my=pygame.mouse.get_pos()
                    mx=int(mx/32)*32
                    my=int(my/32)*32
                    final = (mx,my)
                    self.player.x = int(self.player.x/32)*32
                    self.player.y = int(self.player.y/32)*32;
                    self.pos_actual = (self.player.x ,self.player.y)
                    pasjeroNuevo = Pasajero(final,0)
                    self.nuevos.append(pasjeroNuevo)
                    self.calcular_distancias_nuevos()
                    #print([item.distance for item in self.nuevos])
                    #print(len(self.path))
                    self.movimiento()
                if  event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_w:
                        for i in range(N_FRAMES):
                            for j in range(N_FRAMES):
                                value,rect = self.scenario[i][j]
                                if value == GridItemType.SEMAPH_GREEN:
                                    self.scenario[i][j] = GridItemType.SEMAPH_RED,rect
                                elif value == GridItemType.SEMAPH_RED:
                                    self.scenario[i][j] = GridItemType.SEMAPH_GREEN,rect

                        if ini == True:
                            self.path = []
                            c = 1
                            move = None
                            self.player.x = int(self.player.x/32)*32
                            self.player.y = int(self.player.y/32)*32;
                            self.pos_actual = (self.player.x ,self.player.y)
                            self.calcular_distancias_nuevos()
                            self.movimiento()

            if ini == True:
                print("Entoro ini")
                if len(self.path) == 0:
                    ini = False
                    self.path=[]
                    self.nuevos.pop(0)
                    print("Pop")
                    if len(self.nuevos) >= 1:
                        print("Entro click")
                        self.path = []
                        c = 1
                        move = None
                        ini = True
                        self.calcular_distancias_nuevos()
                        self.movimiento()

            self.screen.fill(SCREEN_BACKGROUND_COLOR)
            self.printScenario(DEBUG)
            self.player.blit_on(self.screen,DEBUG)
            if c == 9:
                if len(self.path) > 0:
                    move = self.path.pop(0)
                else:
                    move = None

                c = 1
            if move is not None:
                self.player.direction = move
                self.player.move()
            c += 1
            pygame.display.update()


def main():
    game = Game()
    game.preload()
    game.create()
    game.update()


if __name__=="__main__":
    main()
