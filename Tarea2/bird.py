import glfw
from OpenGL.GL import *
import OpenGL.GL.shaders
import numpy as np
import sys

import scene_graph as sg
import transformations as tr
import basic_shapes as bs
import easy_shaders as es
import lighting_shaders as ls
import local_shapes as lsh



# A class to store camera parameters.
class PolarCamera:

    # Initializing a Camera which moves with polar coordinates 
    def __init__(self):
        self.theta_angle = 0.0
        self.eyeX = 0.0
        self.eyeY = 0.0
        self.viewPos = 0.0
        self.view = 0.0
        self.radius = 5
        
    
    def change_theta_angle(self, dt):
        self.theta_angle += dt

    def change_zoom(self, dr):
        self.radius += dr

    def update_view(self):
        self.eyeX = self.radius * np.sin(self.theta_angle)
        self.eyeY = self.radius * np.cos(self.theta_angle)

        self.viewPos = np.array([self.eyeX, self.eyeY, 10])
        
        self.view = tr.lookAt(
            self.viewPos,
            np.array([0,0,4]),
            np.array([0,0,1])
        )   
        
        return self.view

    def view_pos(self):
        return self.viewPos

def cursor_pos_callback(window, x, y):
    global controller
    controller.mousePos = (x,y)

    
# A class to store the application control
class Controller:
    def __init__(self):
        self.fillPolygon = True
        self.polar_camera = PolarCamera()
        self.mousePos = (0.0, 0.0)


    def camera(self):
        """ Get a camera reference from the controller object. """
        return self.polar_camera

# We will use the global controller as communication with the callback function
controller = Controller()
controller.polar_camera = PolarCamera()


def on_key(window, key, scancode, action, mods):

    if action != glfw.PRESS:
        return
    
    global controller

    if key == glfw.KEY_SPACE:
        controller.fillPolygon = not controller.fillPolygon

    if key == glfw.KEY_ESCAPE:
        glfw.set_window_should_close(window, True)


def createBird():
        #gpu
        gpuBirdbody = es.toGPUShape(bs.createColorNormalsCube(0.8,0.4,0.3))
        gpuBirdWingLeft = es.toGPUShape(bs.createColorRectangleWingNormal(0.8 ,0.8 , 0))
        gpuBirdWingRight = es.toGPUShape(bs.createColorRectangleWingNormal(0.8,0.8,0))
        gpuBirdTail = es.toGPUShape(bs.createColorRectangleTailNormal(0.8,0.8,0))
        gpuBirdHead = es.toGPUShape(bs.createColorNormalsCube(0.8,0.4,1))

        birdBody = sg.SceneGraphNode('birdBody')
        birdBody.transform = tr.uniformScale(1.4)
        birdBody.childs = [gpuBirdbody]

        birdWingLeft = sg.SceneGraphNode('birdWingLeft')
        birdWingLeft.transform = tr.matmul([tr.translate(-1, 0, 0), tr.rotationZ(np.pi/2), tr.rotationX(np.pi/6)])
        birdWingLeft.childs = [gpuBirdWingLeft]

        birdWingRight = sg.SceneGraphNode('birdWingRight')
        birdWingRight.transform = tr.matmul([tr.translate(1, 0, 0),tr.rotationZ(-1*np.pi/2), tr.rotationX(np.pi/6)])
        birdWingRight.childs = [gpuBirdWingRight]

        birdTail = sg.SceneGraphNode('birdTail')
        birdTail.transform = tr.matmul([tr.translate(0, 1, 0), tr.rotationX(np.pi/3)])
        birdTail.childs = [gpuBirdTail]

        birdHead = sg.SceneGraphNode('birdHead')
        birdHead.transform = tr.translate(0, -1, 1)
        birdHead.childs = [gpuBirdHead]

        bird = sg.SceneGraphNode('bird')
        bird.childs = [birdBody, birdHead, birdTail, birdWingLeft, birdWingRight]

        return bird   

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
    lightingPipeline = ls.SimplePhongShaderProgram()
    # Telling OpenGL to use our shader program
    glUseProgram(pipeline.shaderProgram)

    # Setting up the clear screen color
    glClearColor(0.85, 0.85, 0.85, 1.0)

    bird = createBird()

    # Our shapes here are always fully painted
    glPolygonMode(GL_FRONT_AND_BACK, GL_FILL)
    

    # As we work in 3D, we need to check which part is in front,
    # and which one is at the back
    glEnable(GL_DEPTH_TEST)

    # Creating shapes on GPU memory
    gpuAxis = es.toGPUShape(bs.createAxis(7))

    

    


    t0 = glfw.get_time()

    while not glfw.window_should_close(window):
        # Using GLFW to check for input events
        glfw.poll_events()

        # Getting the time difference from the previous iteration
        t1 = glfw.get_time()
        dt = t1 - t0
        t0 = t1

        camera = controller.camera()

        if (glfw.get_key(window, glfw.KEY_LEFT) == glfw.PRESS):
            camera.change_theta_angle(2 * dt)

        if (glfw.get_key(window, glfw.KEY_RIGHT) == glfw.PRESS):
            camera.change_theta_angle(-2 * dt)
        
        if (glfw.get_key(window, glfw.KEY_UP) == glfw.PRESS):
            camera.change_zoom(5 * dt)

        if (glfw.get_key(window, glfw.KEY_DOWN) == glfw.PRESS):
            camera.change_zoom(-5 * dt)

        view = controller.camera().update_view()
        viewPos = controller.camera().view_pos()

        # Getting the mouse location in opengl coordinates
        mousePosX = 2 * (controller.mousePos[0] - width/2) / width
        mousePosY = 2 * (height/2 - controller.mousePos[1]) / height

        glUniformMatrix4fv(glGetUniformLocation(pipeline.shaderProgram, "view"), 1, GL_TRUE, view)

        # Setting up the projection transform
        projection = tr.perspective(60, float(width)/float(height), 0.1, 100)
        glUniformMatrix4fv(glGetUniformLocation(pipeline.shaderProgram, "projection"), 1, GL_TRUE, projection)

        # Clearing the screen in both, color and depth
        glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)

        glUseProgram(pipeline.shaderProgram)
        glUniformMatrix4fv(glGetUniformLocation(pipeline.shaderProgram, "model"), 1, GL_TRUE, tr.identity())
        pipeline.drawShape(gpuAxis, GL_LINES)

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

        
        
        

        # Filling or not the shapes depending on the controller state
        if (controller.fillPolygon):
            glPolygonMode(GL_FRONT_AND_BACK, GL_FILL)
        else:
            glPolygonMode(GL_FRONT_AND_BACK, GL_LINE)

        theta = camera.theta_angle
        # Drawing shapes with different model transformations
        
        

        #gpuwingleft and gpuwingright
        birdWingLeft = sg.findNode(bird, "birdWingLeft")
        birdWingLeft.transform = tr.matmul([tr.rotationY(mousePosY/1.5), tr.translate(-1, 0, 0), tr.rotationZ(np.pi/2)])
        

        birdWingRight = sg.findNode(bird, "birdWingRight")
        birdWingRight.transform = tr.matmul([tr.rotationY(-mousePosY/1.5), tr.translate(1, 0, 0), tr.rotationZ(-1*np.pi/2)])
        

        #GpuTAIL
        birdTail = sg.findNode(bird, "birdTail")
        birdTail.transform = tr.matmul([ tr.rotationX(mousePosY/3), tr.translate(0, 1, 0)])
        

        
        

        sg.drawSceneGraphNode(bird, lightingPipeline, "model")
        

        

        # Once the drawing is rendered, buffers are swap so an uncomplete drawing is never seen.
        glfw.swap_buffers(window)

    glfw.terminate()
