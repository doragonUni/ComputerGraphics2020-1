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
import fish as fish
import random 
import json 

def jsonToDict(fileName):
    with open(fileName) as file:
        data = json.load(file)
        return data

setup = sys.argv[1]
setup_view = jsonToDict(setup)



t_a= setup_view["t_a"]
t_b= setup_view["t_b"]
t_c= setup_view["t_c"]
n_a= setup_view["n_a"]
n_b= setup_view["n_b"]
n_c= setup_view["n_c"]
filename = setup_view["filename"]

def createColorCube(i, j, k, X, Y, Z, color):
    l_x = X[i, j, k]
    r_x = X[i+1, j, k]
    b_y = Y[i, j, k]
    f_y = Y[i, j+1, k]
    b_z = Z[i, j, k]
    t_z = Z[i, j, k+1]
    c = np.random.rand
    #   positions    colors
    vertices = [
    # Z+: number 1
        l_x, b_y,  t_z, color[0],color[1],color[2],
         r_x, b_y,  t_z, color[0],color[1],color[2],
         r_x,  f_y,  t_z, color[0],color[1],color[2],
        l_x,  f_y,  t_z, color[0],color[1],color[2],
    # Z-: number 6
        l_x, b_y, b_z, color[0],color[1],color[2],
         r_x, b_y, b_z, color[0],color[1],color[2],
         r_x,  f_y, b_z, color[0],color[1],color[2],
        l_x,  f_y, b_z, color[0],color[1],color[2],
    # X+: number 5
         r_x, b_y, b_z, color[0],color[1],color[2],
         r_x,  f_y, b_z, color[0],color[1],color[2],
         r_x,  f_y,  t_z, color[0],color[1],color[2],
         r_x, b_y,  t_z, color[0],color[1],color[2],
    # X-: number 2
        l_x, b_y, b_z, color[0],color[1],color[2],
        l_x,  f_y, b_z, color[0],color[1],color[2],
        l_x,  f_y,  t_z, color[0],color[1],color[2],
        l_x, b_y,  t_z, color[0],color[1],color[2],
    # Y+: number 4
        l_x,  f_y, b_z, color[0],color[1],color[2],
        r_x,  f_y, b_z, color[0],color[1],color[2],
        r_x,  f_y, t_z, color[0],color[1],color[2],
        l_x,  f_y, t_z, color[0],color[1],color[2],
    # Y-: number 3
        l_x, b_y, b_z, color[0],color[1],color[2],
        r_x, b_y, b_z, color[0],color[1],color[2],
        r_x, b_y, t_z, color[0],color[1],color[2],
        l_x, b_y, t_z, color[0],color[1],color[2],
        ]

    # Defining connections among vertices
    # We have a triangle every 3 indices specified
    indices = [
        0, 1, 2, 2, 3, 0,
        4, 5, 6, 6, 7, 4,
        4, 5, 1, 1, 0, 4,
        6, 7, 3, 3, 2, 6,
        5, 6, 2, 2, 1, 5,
        7, 4, 0, 0, 3, 7]

    return bs.Shape(vertices, indices)

def merge(destinationShape, strideSize, sourceShape):

    # current vertices are an offset for indices refering to vertices of the new shape
    offset = len(destinationShape.vertices)
    destinationShape.vertices += sourceShape.vertices
    destinationShape.indices += [(offset/strideSize) + index for index in sourceShape.indices]


PROJECTION_ORTHOGRAPHIC = 0
PROJECTION_FRUSTUM = 1
PROJECTION_PERSPECTIVE = 2





# A class to store the application control
class Controller:
    def __init__(self):
        self.fillPolygon = True
        self.projection = PROJECTION_ORTHOGRAPHIC
        self.voxel1=False
        self.voxel2=False
        self.voxel3=False


# We will use the global controller as communication with the callback function
controller = Controller()


def on_key(window, key, scancode, action, mods):

    if action != glfw.PRESS:
        return
    
    global controller

    if key == glfw.KEY_SPACE:
        controller.fillPolygon = not controller.fillPolygon

    elif key == glfw.KEY_1:
        print('Orthographic projection')
        controller.projection = PROJECTION_ORTHOGRAPHIC

    elif key == glfw.KEY_2:
        print('Frustum projection')
        controller.projection = PROJECTION_FRUSTUM

    elif key == glfw.KEY_3:
        print('Perspective projection')
        controller.projection = PROJECTION_PERSPECTIVE
    elif key == glfw.KEY_A:
                controller.voxel1 = not controller.voxel1
    elif key == glfw.KEY_B:
                controller.voxel2 = not controller.voxel2
    elif key == glfw.KEY_C:
                controller.voxel3 = not controller.voxel3
                
     

    elif key == glfw.KEY_ESCAPE:
        glfw.set_window_should_close(window, True)



if __name__ == "__main__":

    # Initialize glfw
    if not glfw.init():
        sys.exit()

    width = 1200
    height = 600

    window = glfw.create_window(width, height, "Aquarium-viewer", None, None)

    if not window:
        glfw.terminate()
        sys.exit()

    glfw.make_context_current(window)

    # Connecting the callback function 'on_key' to handle keyboard events
    glfw.set_key_callback(window, on_key)

    # Assembling the shader program
    pipeline = es.SimpleModelViewProjectionShaderProgram1()
    lightingPipeline = ls.SimplePhongShaderProgram()

    # Telling OpenGL to use our shader program
    glUseProgram(pipeline.shaderProgram)

    # Setting up the clear screen color
    glClearColor(0.15, 0.15, 0.15, 1.0)

    # As we work in 3D, we need to check which part is in front,
    # and which one is at the back
    glEnable(GL_DEPTH_TEST)
    glEnable(GL_BLEND)
    glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA)

    # Creating shapes on GPU memory
    gpuAxis = es.toGPUShape(bs.createAxis(7))
    
    # Load potentials and grid
    load_voxels = np.load(filename)
    X, Y, Z = np.mgrid[0:3:16j, 0:6:31j, 0:4:21j]

    
    isosurface1 = bs.Shape([], [])
    isosurface2 = bs.Shape([], [])
    isosurface3 = bs.Shape([], [])
    # Now let's draw voxels!
    for i in range(X.shape[0]-1):
        for j in range(X.shape[1]-1):
            for k in range(X.shape[2]-1):
                # print(X[i,j,k])
                if load_voxels[i,j,k]>=t_a-2 and load_voxels[i,j,k]<=t_a+2:
                    temp_shape = createColorCube(i,j,k, X,Y,Z, [0,0,1]) 
                    merge(destinationShape=isosurface1, strideSize=7, sourceShape=temp_shape) #temperatura
                if load_voxels[i,j,k]>=t_b-2 and load_voxels[i,j,k]<=t_b+2:
                    temp_shape = createColorCube(i,j,k, X,Y,Z, [1,0,0])
                    merge(destinationShape=isosurface2, strideSize=7, sourceShape=temp_shape)
                if load_voxels[i,j,k]>=t_c-2 and load_voxels[i,j,k]<=t_c+2:
                    temp_shape = createColorCube(i,j,k, X,Y,Z, [0,1,0])
                    merge(destinationShape=isosurface3, strideSize=7, sourceShape=temp_shape)

    gpu_surface1 = es.toGPUShape(isosurface1)
    gpu_surface2 = es.toGPUShape(isosurface2)
    gpu_surface3 = es.toGPUShape(isosurface3)

    
    gpu_aquarium = es.toGPUShape(bs.createColorCube(0.1,0.6 ,1))
    gpu_borders = es.toGPUShape(bs.createColorCube(0,0,0))


    #FISH TIPO 1
    A = isosurface1.vertices
    location= []
    position= []
    
    fishes1 = []

    for i in range(0, len(A), 6):
        pos1 = (A[i], A[i+1], A[i+2])
        location.append(pos1)
    
    for i in range(n_a):
        fish1 = fish.createFISHA()  
        fishes1.append(fish1)
        position.append(random.choice(location))
        

    
    #FISH TIPO 2 
    B = isosurface2.vertices
    location2= []
    position2= []
    
    fishes2 = []

    for i in range(0, len(B), 6):
        pos2 = (B[i], B[i+1], B[i+2])
        location2.append(pos2)
    
    for i in range(n_b):
        fish2 = fish.createFISHB()  
        fishes2.append(fish2)
        position2.append(random.choice(location2))
        
      
   
    


    #FISH TIPO C
    C = isosurface3.vertices
    location3= []
    position3= []
    
    fishes3 = []

    for i in range(0, len(C), 6):
        pos3 = (C[i], C[i+1], C[i+2])
        location3.append(pos3)
    
    for i in range(n_c):
        fish3 = fish.createFISHC()  
        fishes3.append(fish3)
        position3.append(random.choice(location3))
        
    t0 = glfw.get_time()
    camera_theta = np.pi/4
    change_zoom= 5
    rand = random.uniform(0,1)
   

    while not glfw.window_should_close(window):
        # Using GLFW to check for input events
        glfw.poll_events()

        # Getting the time difference from the previous iteration
        t1 = glfw.get_time()
        dt = t1 - t0
        t0 = t1


        if (glfw.get_key(window, glfw.KEY_LEFT) == glfw.PRESS):
            camera_theta -= 2 * dt

        if (glfw.get_key(window, glfw.KEY_RIGHT) == glfw.PRESS):
            camera_theta += 2* dt

        if (glfw.get_key(window, glfw.KEY_DOWN) == glfw.PRESS):
                change_zoom += 2*dt

        if (glfw.get_key(window, glfw.KEY_UP) == glfw.PRESS):
                change_zoom -=  2*dt
            

        projection = tr.perspective(45, float(width)/float(height), 0.1, 100)

        camX = -15 * change_zoom* np.sin(camera_theta)
        camY = -15 * change_zoom* np.cos(camera_theta)
        camZ = 1

        viewPos = np.array([camX,camY,10])

        view = tr.lookAt(
            viewPos,
            np.array([0,0,3]),
            np.array([0,0,1])
        )

        rotation_theta = glfw.get_time()

        glUniformMatrix4fv(glGetUniformLocation(pipeline.shaderProgram, "view"), 1, GL_TRUE, view)

        # Setting up the projection transform

        if controller.projection == PROJECTION_ORTHOGRAPHIC:
            projection = tr.ortho(-8, 8, -8, 8, 0.1, 100)

        elif controller.projection == PROJECTION_FRUSTUM:
            projection = tr.frustum(-5, 5, -5, 5, 9, 100)

        elif controller.projection == PROJECTION_PERSPECTIVE:
            projection = tr.perspective(60, float(width)/float(height), 0.1, 100)
        
        else:
            raise Exception()

        glUniformMatrix4fv(glGetUniformLocation(pipeline.shaderProgram, "projection"), 1, GL_TRUE, projection)


        # Clearing the screen in both, color and depth
        glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)

        # Filling or not the shapes depending on the controller state
        if (controller.fillPolygon):
            glPolygonMode(GL_FRONT_AND_BACK, GL_FILL)
        else:
            glPolygonMode(GL_FRONT_AND_BACK, GL_LINE)
        
        
        
        
        #glUniformMatrix4fv(glGetUniformLocation(pipeline.shaderProgram, "model"), 1, GL_TRUE, tr.matmul([tr.translate(6,12,8),tr.scale(3*2,6*2,4*2)]))
        #pipeline.drawShape(gpu_aquarium)
        
#-------------------------------------------------------------------------- luz-----------------
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

        
        
        

    

        
        # Drawing shapes with different model transformations
        
        
        for i in range(n_a):
            fish = sg.findNode(fishes1[i], "fish")
            at = position[i]
            fish1.transform = tr.matmul([tr.translate(at[0]*2-2.98, at[1]*2-6, at[2]*2-1), tr.uniformScale(0.25)])
            fishTail = sg.findNode(fishes1[i], "fishTail")
            fishTail.transform = tr.matmul([tr.rotationZ(0.5*np.cos(-4*t0)),tr.rotationY(np.pi/2),tr.translate(0, 1.41, 0)])
            sg.drawSceneGraphNode(fish1, lightingPipeline, "model")
        
        #b
        for i in range(n_b):
            fish = sg.findNode(fishes2[i], "fish")
            at2 = position2[i]
            fish2.transform = tr.matmul([tr.translate(at2[0]*2-2.98, at2[1]*2-6, at2[2]*2-1) , tr.uniformScale(0.25)])
            fishTail = sg.findNode(fish2, "fishTail")
            fishTail.transform = tr.matmul([tr.rotationZ(((-1)**(i))*(rand**(i//2))*np.cos(-6*t0+i//10)),tr.translate(0, 1.41, 0)])
            fishTail2 = sg.findNode(fish2, "fishTail2")
            fishTail2.transform = tr.matmul([tr.rotationZ(((-1)**(i))*-(rand**(i//2))*np.cos(-7*t0+i//1)),tr.translate(0, 1.41, 0)])
            sg.drawSceneGraphNode(fish2, lightingPipeline, "model")

        #C
        for i in range(n_c):
            fish = sg.findNode(fishes3[i], "fish")
            at3 = position3[i]
            fishTail = sg.findNode(fish3, "fishTail")
            fishTail.transform = tr.matmul([tr.rotationZ(0.3*np.cos(-4*t0)),tr.translate(0, 1.41, 0)])

            fish3.transform = tr.matmul([tr.translate(at3[0]*2-2.98, at3[1]*2-6, at3[2]*2-1) , tr.uniformScale(0.25)])
            
            
            sg.drawSceneGraphNode(fish3, lightingPipeline, "model")



        #fish.movement3(fish3,t0, lightingPipeline)
        #fish.movement2(fish2,t0, lightingPipeline)
        #
        # sg.drawSceneGraphNode(fish3, lightingPipeline, "model")
       #------------------------------------------pipeline-------------
       # Drawing shapes with different model transformations
        glUseProgram(pipeline.shaderProgram)

                 
        if controller.voxel1 == True:
            glUniformMatrix4fv(glGetUniformLocation(pipeline.shaderProgram, "model"), 1, GL_TRUE, tr.matmul([tr.translate(-3,-6,-1),tr.uniformScale(2.1)]))
            
            pipeline.drawShape(gpu_surface1, GL_LINES)
            
        if controller.voxel2 == True:
            glUniformMatrix4fv(glGetUniformLocation(pipeline.shaderProgram, "model"), 1, GL_TRUE, tr.matmul([tr.translate(-3,-6,-1),tr.uniformScale(2.1)]))
            
            pipeline.drawShape(gpu_surface2, GL_LINES)
        if controller.voxel3 == True:
            glUniformMatrix4fv(glGetUniformLocation(pipeline.shaderProgram, "model"), 1, GL_TRUE, tr.matmul([tr.translate(-3,-6,-1),tr.uniformScale(2.1)]))
            
            pipeline.drawShape(gpu_surface3,  GL_LINES) 

        glUniformMatrix4fv(glGetUniformLocation(pipeline.shaderProgram, "model"), 1, GL_TRUE,tr.matmul([tr.translate(-0.6,0,3),tr.scale(8,14,9)]))
        pipeline.drawShape(gpu_aquarium)
        pipeline.drawShape(gpu_borders, GL_LINES)

        # Once the drawng is rendered, buffers are swap so an uncomplete drawing is never seen.
        glfw.swap_buffers(window)

    glfw.terminate()    