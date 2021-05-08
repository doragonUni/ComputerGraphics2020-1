# coding=utf-8
"""
Daniel Calderon, CC3501, 2019-2
Textures and transformations in 2D
"""

import glfw
from OpenGL.GL import *
import OpenGL.GL.shaders
import numpy as np
import sys
import scene_graph as sg 
import transformations as tr
import basic_shapes as bs
import easy_shaders as es
import math

#CONTROLLER:

# A class to store the application control
class Controller:
    def __init__(self):
        self.x = 0.0
        self.y = 0.0

        self.backgroundPos = 0.0

        self.shotx = 0.0
        self.shoty = 0.0
        self.shotBool = False 

        self.eshotx = 0.0
        self.eshoty = 0.0
        self.shotBoolE = False
        
        self.ex = 0.0
        self.ey = 0.0

        self.useShader2 = False       
        self.fillPolygon = True

# global controller as communication with the callback function
controller = Controller()



def on_key(window, key, scancode, action, mods):
        global controller

        # Keep pressed buttons

        #WASD PARA MOVIMIENTO DEL JUGADOR DE LA NAVE
        if action == glfw.REPEAT or action == glfw.PRESS:
            if key == glfw.KEY_A:
                controller.x -= 0.1
            elif key == glfw.KEY_D:
                controller.x += 0.1
            elif key == glfw.KEY_W:
                controller.y += 0.1
            elif key == glfw.KEY_S:
                controller.y -= 0.1
            elif key == glfw.KEY_SPACE:
                controller.shotBool = not controller.shotBool
                controller.shotx = controller.x
            
            

        if action != glfw.PRESS:
            return
    
        elif key == glfw.KEY_1:
            controller.fillPolygon = not controller.fillPolygon

        elif key == glfw.KEY_ESCAPE:
            sys.exit()

        else:
            print('Unknown key')


def collisionBool (ex, ey, shotx, shoty):
    distance = math.sqrt( (math.pow(ex-shotx,2))+ (math.pow(ey-shoty,2)) )
    if distance < 0.3   :
        return True
    else: 
        return False


   


#MODEL

def gameBackground():
    # Enabling transparencies
    glEnable(GL_BLEND)
    glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA)

    background = es.toGPUShape(bs.createTextureQuad("background.jpg"),GL_REPEAT, GL_LINEAR)

    #El fondo debe moverse de abajo hacia arriba:
    upper_background = sg.SceneGraphNode("upper_background")
    upper_background.transform = tr.matmul([tr.translate(0.2, 0, 0), tr.scale(2.5, 2, 1)])
    upper_background.childs += [background]

    lower_background = sg.SceneGraphNode("lower_background")
    lower_background.transform = tr.matmul([tr.translate(0.2, -1.7, 0), tr.scale(2.5, 2, 1)])
    lower_background.childs += [background]

    gameBackground = sg.SceneGraphNode("gameBackground")
    gameBackground.transform = tr.identity()
    gameBackground.childs += [upper_background, lower_background]

    return gameBackground



def gameEnemy():
    # Enabling transparencies
    glEnable(GL_BLEND)
    glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA)

    enemy = es.toGPUShape(bs.createTextureQuad("enemy.png"), GL_REPEAT, GL_NEAREST)
    enemyShot = es.toGPUShape(bs.createTextureQuad("shot.png"), GL_REPEAT, GL_NEAREST)

    enemyShot1 = sg.SceneGraphNode("enemyShot")
    enemyShot1.transform =  tr.scale(0.05, 0.05, 1)
    enemyShot1.childs += [enemyShot]


    cpuEnemy = sg.SceneGraphNode("cpuEnemy")
    cpuEnemy.transform = tr.uniformScale(0.3)
    cpuEnemy.childs += [enemy]

    gameEnemy = sg.SceneGraphNode("gameEnemy")
    gameEnemy.transform = tr.identity()
    gameEnemy.childs += [cpuEnemy]
    gameEnemy.childs += [enemyShot1]
    

    return gameEnemy

def createEnemy(N):
    enemies = sg.SceneGraphNode('gameEnemy')
    enemies.transform = tr.identity()
    enemies.childs += [gameEnemy()]

    

    Nenemies = sg.SceneGraphNode("Nenemies")
    baseName = "enemies"

    for i in range(N):
        
        
        newNode = sg.SceneGraphNode(baseName + str(i))
        newNode.transform = tr.translate(0.3*i -1, 1  , 0)
        newNode.childs += [enemies]     
    
        Nenemies.childs+= [newNode]
        
    return Nenemies




def gameShip():
    # Enabling transparencies 
    glEnable(GL_BLEND)
    glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA)


    shot = es.toGPUShape(bs.createTextureQuad("shot.png"), GL_REPEAT, GL_NEAREST)
    ship = es.toGPUShape(bs.createTextureQuad("ship.png"), GL_REPEAT, GL_NEAREST)
    

    playerShot = sg.SceneGraphNode("playerShot")
    playerShot.transform = tr.matmul([tr.translate(0, 0.3, 0), tr.scale(0.1, 0.1, 1)])
    playerShot.childs += [shot]


    playerShip = sg.SceneGraphNode("playerShip")
    playerShip.transform = tr.matmul([tr.translate(0, -0.6, 0), tr.scale(1, 1, 1)])
    playerShip.childs += [ship]

    

    gameShip = sg.SceneGraphNode("gameShip")
    gameShip.transform = tr.identity()
    gameShip.childs += [playerShip]
    gameShip.childs += [playerShot]

    return gameShip


def gameGG():

    glEnable(GL_BLEND)
    glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA)

    GG = es.toGPUShape(bs.createTextureQuad("gg.png"), GL_REPEAT, GL_NEAREST)
    
    gameGG = sg.SceneGraphNode("gameGG")
    gameGG.transform = tr.identity()
    gameGG.childs += [GG]

    return gameGG






if __name__ == "__main__":

    
    N = int(sys.argv[1])

    # Initialize glfw
    if not glfw.init():
        sys.exit()

    width = 600
    height = 600

    window = glfw.create_window(width, height, "SpaceWars alpha", None, None)

    if not window:
        glfw.terminate()
        sys.exit()

    glfw.make_context_current(window)

    # Connecting the callback function 'on_key' to handle keyboard events
    glfw.set_key_callback(window, on_key)

    # Assembling the shader program (pipeline) with both shaders
    pipelineTexture = es.SimpleTextureTransformShaderProgram()

    pipelineNoTexture = es.SimpleTransformShaderProgram()
    
    # Telling OpenGL to use our shader program
    #glUseProgram(pipeline.shaderProgram)

    # Setting up the clear screen color
    glClearColor(0.25, 0.25, 0.25, 1.0)

    # Creating shapes on GPU memory

    gpuBackground = gameBackground()

    gpuEnemy = createEnemy(N)
    
    
    gpuShip = gameShip()

    gpuGG = gameGG()
    
    


    
    # Our shapes here are always fully painted
    glPolygonMode(GL_FRONT_AND_BACK, GL_FILL)
    controller.x = glfw.get_time()
    controller.y = glfw.get_time()
    controller.ey = glfw.get_time()
    controller.ex = glfw.get_time()

    controller.eshotx = glfw.get_time()
    controller.eshoty = glfw.get_time()
    

    controller.backgroundPos = glfw.get_time()
    
    t0 = glfw.get_time()


    

#VIEW:

    while not glfw.window_should_close(window):
        # Using GLFW to check for input events
        glfw.poll_events()


        
        #getting the time 
        
        t1= glfw.get_time()
        dt = t1-t0
        td = t0 -t1
        
        speed = 7  
        
        theta = glfw.get_time()
        time = glfw.get_time()
        
        ex = (0.4 * np.sin(0.4 * theta))*0.4 #enemy position x 
        ey = glfw.get_time()*0.05 #enemy position y
    
    
        #Player 
        #reseting the bullet
        if controller.shotBool == True:
            controller.shoty += 0.009
            if controller.shoty > 3 :
                controller.shotBool =False
        else: 
            controller.shotx = controller.x
            controller.shoty = controller.y

        #Cpu
        #reseting the bullet
        

        if controller.shotBoolE == True:
            controller.eshoty += 0.0020
            if controller.eshoty > 3:
                controller.shotBoolE = False
        else:
            controller.eshotx = ex
            controller.eshoty = ey 
            controller.shotBoolE = True

        
        

        

        # Filling or not the shapes depending on the controller state
        if (controller.fillPolygon):
            glPolygonMode(GL_FRONT_AND_BACK, GL_FILL)
        else:
            glPolygonMode(GL_FRONT_AND_BACK, GL_LINE)

        # Clearing the screen in both, color and depth
        glClear(GL_COLOR_BUFFER_BIT)

        # Create transform matrix
        glUseProgram(pipelineTexture.shaderProgram)

        #drawing the background:
        # This condition translates the sky so it can be seen as a loop
        controller.backgroundPos += (td * speed)
        if controller.backgroundPos < -1:
            controller.backgroundPos = 0

        



        lower_background = sg.findNode(gpuBackground, "lower_background")
        lower_background.transform = tr.matmul([tr.translate(0.2, 1 + controller.backgroundPos, 0), tr.scale(2.5, 2, 1)] )

        upper_background = sg.findNode(gpuBackground,"upper_background")
        upper_background.transform  = tr.matmul( [tr.translate(0.2, -1 + controller.backgroundPos, 0), tr.scale(2.5, 2, 1)] )



        playerShot = sg.findNode(gpuShip, "playerShot")
        playerShot.transform = tr.matmul([tr.translate( -0.98 + controller.shotx  ,  -1.40 + controller.shoty  , 0.0), tr.scale(0.1, 0.1, 0)])


        ship = sg.findNode(gpuShip, "playerShip")
        ship.transform = tr.matmul([tr.translate(-0.96 + controller.x, -1.58 + controller.y, 0.0), tr.scale(0.4, 0.4, 0)])

    
        enemy = sg.findNode(gpuEnemy, "cpuEnemy")
        enemy.transform = tr.matmul([tr.translate( ex  , -ey , 0 ), tr.scale(0.3, 0.3, 0) ]) 




        enemyShot = sg.findNode(gpuEnemy, "enemyShot")
        enemyShot.transform = tr.matmul([tr.translate( controller.eshotx , -controller.eshoty , 0.0), tr.scale(0.13, 0.13, 0)])


        finalGG = sg.findNode(gpuGG, "gameGG")
        finalGG.transform = tr.matmul([tr.translate( 0.7 , 0.5 , 0.0), tr.scale(0.2, 0.2, 0)])


        sg.drawSceneGraphNode(gpuBackground, pipelineTexture, "transform")

        sg.drawSceneGraphNode(gpuEnemy, pipelineTexture, "transform")

        sg.drawSceneGraphNode(gpuShip, pipelineTexture, "transform")   

        #sg.drawSceneGraphNode(gpuGG, pipelineTexture, "transform")   

        glUseProgram(pipelineNoTexture.shaderProgram)

       

        # Once the render is done, buffers are swapped, showing only the complete scene.
        glfw.swap_buffers(window)

        t0 = glfw.get_time()

    glfw.terminate()