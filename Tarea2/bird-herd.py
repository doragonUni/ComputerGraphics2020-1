import glfw
from OpenGL.GL import *
import OpenGL.GL.shaders
import numpy as np
import sys

import gpu_creations as cr
import transformations as tr
import basic_shapes as bs
import easy_shaders as es
import lighting_shaders as ls
import scene_graph as sg
import catmullrom as cmr 
from bird import createBird

path = str(sys.argv[1])


def cursor_pos_callback(window, x, y):
    global controller
    controller.mousePos = (x,y)

def on_key(window, key, scancode, action, mods):

    if action != glfw.PRESS:
        return
    
    global controller

    if key == glfw.KEY_SPACE:
        controller.fillPolygon = not controller.fillPolygon

    if key == glfw.KEY_ESCAPE:
        glfw.set_window_should_close(window, True)

    
# A class to store the application control
class Controller:
    def __init__(self):
        self.fillPolygon = True
        self.mousePos = (0.0, 0.0)

# We will use the global controller as communication with the callback function
controller = Controller()

#TESTEO CON PUNTOS
#P1 = np.array([[0, 1, 0]]).T
#P2 = np.array([[0, 1, 1]]).T
#P3 = np.array([[0, 3, 3]]).T
#P4 = np.array([[0, 2, 1]]).T
#P5 = np.array([[5, 5, 0]]).T
    
#Puntos = [P1,P2,P3,P4,P5]

#trayectoria = cmr.catmullRom(Puntos)
#x,y,z = cmr.separacion(trayectoria)

#ARCHIVOS CSV
puntos = cmr.csvToPArray(path)

trayectoriaEx = cmr.catmullRom(puntos)
x,y,z = cmr.separacion(trayectoriaEx)
count = 0 


if __name__ == "__main__":

    # Initialize glfw
    if not glfw.init():
        sys.exit()

    width = 600
    height = 600

    window = glfw.create_window(width, height, "BIRD", None, None)

    if not window:
        glfw.terminate()
        sys.exit()

    glfw.make_context_current(window)

    # Connecting the callback function 'on_key' to handle keyboard events
    glfw.set_key_callback(window, on_key)

    #mouse movement
    glfw.set_cursor_pos_callback(window, cursor_pos_callback)

    # Assembling the shader program
    pipeline = es.SimpleModelViewProjectionShaderProgram()
    texturePipeline = es.SimpleTextureModelViewProjectionShaderProgram()
    lightingPipeline = ls.SimplePhongShaderProgram()
    # Telling OpenGL to use our shader program
    glUseProgram(pipeline.shaderProgram)

    # Setting up the clear screen color
    glClearColor(0.85, 0.85, 0.85, 1.0)

    # As we work in 3D, we need to check which part is in front,
    # and which one is at the back
    glEnable(GL_DEPTH_TEST)

    # Creating shapes on GPU memory
    gpuAxis = es.toGPUShape(bs.createAxis(7))



    #FloorBkng
    gpuFloor = es.toGPUShape(bs.createTexturefloor("floor.jpg", 1, 1), GL_REPEAT, GL_LINEAR)
    
    

    #skycube
    background_img = cr.ImageObject("skybox.png")

    backgroundNode = sg.SceneGraphNode("background")
    backgroundNode.childs += [cr.createSkybox(background_img, 512, 30)]



    bird1 = createBird()
    bird2 = createBird()
    bird3 = createBird()
    bird4 = createBird()
    bird5 = createBird()

    camera_theta = np.pi/2
    t0 = glfw.get_time()
    
    count = 0


    while not glfw.window_should_close(window):
        # Using GLFW to check for input events
        glfw.poll_events()

        # Getting the time difference from the previous iteration
        t1 = glfw.get_time()
        dt = t1 - t0
        t0 = t1

        # Getting the mouse location in opengl coordinates
        mousePosX = 2 * (controller.mousePos[0] - width/2) / width
        mousePosY = 2 * (height/2 - controller.mousePos[1]) / height

        index = t0*10//1
        
        # Setting up the view transform

        camX = -7
        camY = 7
        camZ = 10

        at = [10*np.sin(np.pi*mousePosX)+ camX, 5*np.cos(np.pi*mousePosX)+ camY, 5*np.sin(mousePosY)+ camZ]

        viewPos = np.array([camX, camY, camZ])

        view = tr.lookAt(
            viewPos,
            at,
            np.array([0,0,1])
        )

        glUniformMatrix4fv(glGetUniformLocation(pipeline.shaderProgram, "view"), 1, GL_TRUE, view)

        glUniformMatrix4fv(glGetUniformLocation(pipeline.shaderProgram, "view"), 1, GL_TRUE, view)

        # Setting up the projection transform
        projection = tr.perspective(60, float(width)/float(height), 0.1, 100)
        glUniformMatrix4fv(glGetUniformLocation(pipeline.shaderProgram, "projection"), 1, GL_TRUE, projection)

        # Clearing the screen in both, color and depth
        glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)

        #Todo lo que sea no texture y no iluminado
            
        pipeline.drawShape(gpuAxis, GL_LINES)

        #Todo lo que use textura y no iluminado
        glUseProgram(texturePipeline.shaderProgram)
        glUniformMatrix4fv(glGetUniformLocation(texturePipeline.shaderProgram, "view"), 1, GL_TRUE, view)
        glUniformMatrix4fv(glGetUniformLocation(texturePipeline.shaderProgram, "projection"), 1, GL_TRUE, projection)
        glUniformMatrix4fv(glGetUniformLocation(texturePipeline.shaderProgram, "model"), 1, GL_TRUE, tr.uniformScale(30))
        texturePipeline.drawShape(gpuFloor)
        
        sg.drawSceneGraphNode(backgroundNode, texturePipeline, "model")


        

        

        

        #Aqui va todo lo iluminado
        glUseProgram(lightingPipeline.shaderProgram)

        # White light in all components: ambient, diffuse and specular.
        glUniform3f(glGetUniformLocation(lightingPipeline.shaderProgram, "La"), 0.2, 0.2, 0.2)
        glUniform3f(glGetUniformLocation(lightingPipeline.shaderProgram, "Ld"), 1.0, 1.0, 1.0)
        glUniform3f(glGetUniformLocation(lightingPipeline.shaderProgram, "Ls"), 1.0, 1.0, 1.0)

        glUniform3f(glGetUniformLocation(lightingPipeline.shaderProgram, "Ka"), 1.0, 1.0, 1.0)
        glUniform3f(glGetUniformLocation(lightingPipeline.shaderProgram, "Kd"), 1.0, 1.0, 1.0)
        glUniform3f(glGetUniformLocation(lightingPipeline.shaderProgram, "Ks"), 1.0, 1.0, 1.0)


        # TO DO: Explore different parameter combinations to understand their effect!

        glUniform3f(glGetUniformLocation(lightingPipeline.shaderProgram, "lightPosition"),-5, -5, 5)    
        glUniform3f(glGetUniformLocation(lightingPipeline.shaderProgram, "viewPosition"), viewPos[0], viewPos[1], viewPos[2])
        glUniform1ui(glGetUniformLocation(lightingPipeline.shaderProgram, "shininess"), 100)

        glUniform1f(glGetUniformLocation(lightingPipeline.shaderProgram, "constantAttenuation"), 0.0001)
        glUniform1f(glGetUniformLocation(lightingPipeline.shaderProgram, "linearAttenuation"), 0.09)
        glUniform1f(glGetUniformLocation(lightingPipeline.shaderProgram, "quadraticAttenuation"), 0.09)

        glUniformMatrix4fv(glGetUniformLocation(lightingPipeline.shaderProgram, "view"), 1, GL_TRUE, view)
        glUniformMatrix4fv(glGetUniformLocation(lightingPipeline.shaderProgram, "projection"), 1, GL_TRUE, projection)
        

        

        #WINGS

        #left
        bird1WingLeft = sg.findNode(bird1, "birdWingLeft")
        bird1WingLeft.transform = tr.matmul([tr.rotationY(0.4*np.sin(t0*4)), tr.translate(-1, 0, 0), tr.rotationZ(np.pi/2)])

        bird2WingLeft = sg.findNode(bird2, "birdWingLeft")
        bird2WingLeft.transform = tr.matmul([tr.rotationY(0.3*np.sin(t0*3)), tr.translate(-1, 0, 0), tr.rotationZ(np.pi/2)])

        bird3WingLeft = sg.findNode(bird3, "birdWingLeft")
        bird3WingLeft.transform = tr.matmul([tr.rotationY(0.4*np.sin(t0*2)), tr.translate(-1, 0, 0), tr.rotationZ(np.pi/2)])

        bird4WingLeft = sg.findNode(bird4, "birdWingLeft")
        bird4WingLeft.transform = tr.matmul([tr.rotationY(0.2*np.sin(t0*2.6)), tr.translate(-1, 0, 0), tr.rotationZ(np.pi/2)])

        bird5WingLeft = sg.findNode(bird5, "birdWingLeft")
        bird5WingLeft.transform = tr.matmul([tr.rotationY(0.5*np.sin(t0*1.3)), tr.translate(-1, 0, 0), tr.rotationZ(np.pi/2)])

        #right
        bird1WingRight = sg.findNode(bird1, "birdWingRight")
        bird1WingRight.transform = tr.matmul([tr.rotationY(-0.4*np.sin(t0*4)),tr.translate(1, 0, 0), tr.rotationZ(-1*np.pi/2)])

        bird2WingRight = sg.findNode(bird2, "birdWingRight")
        bird2WingRight.transform = tr.matmul([tr.rotationY(-0.3*np.sin(t0*3)),tr.translate(1, 0, 0), tr.rotationZ(-1*np.pi/2)])

        bird3WingRight = sg.findNode(bird3, "birdWingRight")
        bird3WingRight.transform = tr.matmul([tr.rotationY(-0.4*np.sin(t0*2)),tr.translate(1, 0, 0), tr.rotationZ(-1*np.pi/2)])

        bird4WingRight = sg.findNode(bird4, "birdWingRight")
        bird4WingRight.transform = tr.matmul([tr.rotationY(-0.2*np.sin(t0*2.6)),tr.translate(1, 0, 0), tr.rotationZ(-1*np.pi/2)])

        bird5WingRight = sg.findNode(bird5, "birdWingRight")
        bird5WingRight.transform = tr.matmul([tr.rotationY(-0.5*np.sin(t0*1.3)),tr.translate(1, 0, 0), tr.rotationZ(-1*np.pi/2)])
        

        #TAILS
        bird1Tail = sg.findNode(bird1, "birdTail")
        bird1Tail.transform = tr.matmul([tr.rotationX(0.4*np.sin(t0*4)), tr.translate(0, 1, 0)])
        
        bird2Tail = sg.findNode(bird2, "birdTail")
        bird2Tail.transform =tr.matmul([tr.rotationX(0.3*np.sin(t0*3)), tr.translate(0, 1, 0)])
        
        bird3Tail = sg.findNode(bird3, "birdTail")
        bird3Tail.transform =tr.matmul([tr.rotationX(0.4*np.sin(t0*2)), tr.translate(0, 1, 0)])
        
        bird4Tail = sg.findNode(bird4, "birdTail")
        bird4Tail.transform = tr.matmul([tr.rotationX(0.2*np.sin(t0*2.6)), tr.translate(0, 1, 0)])
        
        bird5Tail = sg.findNode(bird5, "birdTail")
        bird5Tail.transform = tr.matmul([tr.rotationX(0.5*np.sin(t0*1.3)), tr.translate(0, 1, 0)])


        
        



        
        bird1 = sg.findNode(bird1, "bird")
        bird1.transform=tr.translate(-1 +  x[count], -3 + y[count], 10 + z[count])

        bird2 = sg.findNode(bird2, "bird")
        bird2.transform= tr.translate(3 +  x[count] , -4+ y[count] , 2  + z[count])

        bird3 = sg.findNode(bird3, "bird")
        bird3.transform= tr.translate(5+  x[count] , 3+ y[count] , 4 + z[count])

        bird4 = sg.findNode(bird4, "bird")
        bird4.transform= tr.translate(1 +  x[count] , -2 +  y[count] , 6  + z[count] )

        bird5 = sg.findNode(bird5, "bird")
        bird5.transform= tr.translate(8 +  x[count], 1 + y[count], 8 + z[count] )

        count+=1    
        if count == len(x)-1:
            count = 0




        
        


        sg.drawSceneGraphNode(bird1, lightingPipeline, "model")
        sg.drawSceneGraphNode(bird2, lightingPipeline, "model")
        sg.drawSceneGraphNode(bird3, lightingPipeline, "model")
        sg.drawSceneGraphNode(bird4, lightingPipeline, "model")
        sg.drawSceneGraphNode(bird5, lightingPipeline, "model")


    

        # Filling or not the shapes depending on the controller state
        if (controller.fillPolygon):
            glPolygonMode(GL_FRONT_AND_BACK, GL_FILL)
        else:
            glPolygonMode(GL_FRONT_AND_BACK, GL_LINE)

        
       
        
        
        # Once the drawing is rendered, buffers are swap so an uncomplete drawing is never seen.
        glfw.swap_buffers(window)

    glfw.terminate()
