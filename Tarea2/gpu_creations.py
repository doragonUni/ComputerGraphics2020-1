import glfw
from OpenGL.GL import *
import OpenGL.GL.shaders
import numpy as np
import sys
from PIL import Image

import transformations as tr
import basic_shapes as bs
import easy_shaders as es
import scene_graph as sg
import math

SIZE_IN_BYTES = 4

class ImageObject:
    #Clase que sirve para contener la informacion de l imagen y asi cargarla solo una vez
    def __init__(self, fileName):
        image = Image.open(fileName)
        self.data = np.array(list(image.getdata()), np.uint8)
        self.width = image.size[0]
        self.height = image.size[1]
        if image.mode == "RGB":
            self.internalFormat = GL_RGB
            self.format = GL_RGB
        elif image.mode == "RGBA":
            self.internalFormat = GL_RGBA
            self.format = GL_RGBA
        else:
            print("Image mode not supported.")
            raise Exception()

def createShadowColorCube(r, g, b):

    shadow = 0.2

    # Defining the location and colors of each vertex  of the shape
    vertices = [
    #    positions        colors
        -0.5, -0.5,  0.5, r , g, b,
         0.5, -0.5,  0.5, r , g, b,
         0.5,  0.5,  0.5, r , g, b,
        -0.5,  0.5,  0.5, r , g, b,

        -0.5, -0.5, -0.5, shadow * r, shadow * g, shadow * b,
         0.5, -0.5, -0.5, shadow * r, shadow * g, shadow * b,
         0.5,  0.5, -0.5, shadow * r, shadow * g, shadow * b,
        -0.5,  0.5, -0.5, shadow * r, shadow * g, shadow * b,]

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


def createCar():

    gpuNeumatico = es.toGPUShape(createShadowColorCube(0,0,0))
    gpuLlanta = es.toGPUShape(createShadowColorCube(1,1,1))
    gpuChasisRojo = es.toGPUShape(createShadowColorCube(253 / 255, 21 / 255, 35 / 255))
    gpuChasisAzul = es.toGPUShape(createShadowColorCube(0, 98 / 255, 216 / 255))
    gpuChasisAmarillo = es.toGPUShape(createShadowColorCube( 254 / 255, 197 / 255, 45 / 255))
    gpuChasisNegro = es.toGPUShape(createShadowColorCube(0.2,0.2,0.2))

    neumatico = sg.SceneGraphNode("wheel")
    neumatico.transform = tr.scale(0.2, 0.8, 0.2)
    neumatico.childs += [gpuNeumatico]

    llanta = sg.SceneGraphNode("llanta")
    llanta.transform = tr.matmul([tr.scale(0.1, 0.85, 0.1),tr.rotationY(np.pi / 4)])
    llanta.childs += [gpuLlanta]

    rueda = sg.SceneGraphNode("rueda")
    rueda.childs += [neumatico]
    rueda.childs += [llanta]

    ruedaRotacion = sg.SceneGraphNode("ruedaRotacion")
    ruedaRotacion.childs += [rueda]

    ruedaDelantera = sg.SceneGraphNode("ruedaDelantera")
    ruedaDelantera.transform = tr.translate(0.3, 0, -0.3)
    ruedaDelantera.childs += [ruedaRotacion]

    ruedaTrasera = sg.SceneGraphNode("ruedaTrasera")
    ruedaTrasera.transform = tr.translate(-0.3, 0, -0.3)
    ruedaTrasera.childs += [ruedaRotacion]

    # Creating the chasis of the car
    cuerpo = sg.SceneGraphNode("cuerpo")
    cuerpo.transform = tr.matmul([tr.scale(1,0.7,0.25), tr.rotationZ(np.pi/4)])
    cuerpo.childs += [gpuChasisRojo]

    cabina = sg.SceneGraphNode("cabina")
    cabina.transform = tr.matmul([tr.rotationY(np.pi/16), tr.scale(0.7,0.4,0.15), tr.translate(0,0,1), tr.rotationZ(np.pi/4)])
    cabina.childs += [gpuChasisAzul]

    cohete = sg.SceneGraphNode("cohete")
    cohete.transform = tr.matmul([tr.scale(0.5,0.25,0.25), tr.translate(-1,0,0)])
    cohete.childs += [gpuChasisNegro]

    barra = sg.SceneGraphNode("barra")
    barra.transform = tr.matmul([tr.scale(0.3,1,0.1), tr.translate(-1.5, 0, 10), tr.rotationZ(np.pi / 4)])
    barra.childs += [gpuChasisRojo]

    pie = sg.SceneGraphNode("pie")
    pie.transform = tr.matmul([tr.rotationY(- np.pi / 8), tr.scale(0.1,0.1,0.5), tr.translate(0,0, 1.5)])
    pie.childs += [gpuChasisAmarillo]

    aleron = sg.SceneGraphNode("aleron")
    aleron.transform = tr.matmul([tr.uniformScale(0.8), tr.translate(-0.4,0,-0.4)])
    aleron.childs += [barra]
    aleron.childs += [pie]

    parachoqueFrontal = sg.SceneGraphNode("parachoqueFrontal")
    parachoqueFrontal.transform = tr.matmul([tr.translate(0.6,0,0), tr.scale(0.05,0.7,0.05)])
    parachoqueFrontal.childs += [gpuChasisAmarillo]

    parachoqueIzquierdo = sg.SceneGraphNode("parachoqueIzquierdo")
    parachoqueIzquierdo.transform = tr.matmul([tr.translate(0.25, 0.25, 0), tr.rotationZ(np.pi / 4), tr.scale(0.5,0.5,1)])
    parachoqueIzquierdo.childs += [parachoqueFrontal]

    parachoqueDerecho = sg.SceneGraphNode("parachoqueDerecho")
    parachoqueDerecho.transform = tr.matmul([tr.translate(0.25, -0.25, 0), tr.rotationZ(- np.pi / 4), tr.scale(0.5,0.5,1)])
    parachoqueDerecho.childs += [parachoqueFrontal]

    parachoqueSuperior = sg.SceneGraphNode("parachoqueSuperior")
    parachoqueSuperior.transform = tr.translate(0,0,0.1)
    parachoqueSuperior.childs += [parachoqueFrontal]
    parachoqueSuperior.childs += [parachoqueIzquierdo]
    parachoqueSuperior.childs += [parachoqueDerecho]

    parachoqueInferior = sg.SceneGraphNode("parachoqueInferior")
    parachoqueInferior.transform = tr.translate(0,0, - 0.2)
    parachoqueInferior.childs += [parachoqueSuperior]

    parachoque = sg.SceneGraphNode("parachoque")
    parachoque.transform = tr.matmul([tr.scale(1,0.75,0.75), tr.translate(0.15,0,0)])
    parachoque.childs += [parachoqueSuperior]
    parachoque.childs += [parachoqueInferior]

    chasis = sg.SceneGraphNode("chasis")
    chasis.transform = tr.translate(0, 0, -0.20)
    chasis.childs += [parachoque]
    chasis.childs += [cuerpo]
    chasis.childs += [cabina]
    chasis.childs += [cohete]
    chasis.childs += [aleron]

    # All pieces together
    car = sg.SceneGraphNode("car")
    car.childs += [chasis]
    car.childs += [ruedaDelantera]
    car.childs += [ruedaTrasera]

    return car

def createTextureQuad(image_filename, nx=1, ny=1):

    # Defining locations and texture coordinates for each vertex of the shape
    vertices = [
    #   positions        texture
        -1, -1, 0.0,  0, ny,
         1, -1, 0.0, nx, ny,
         1,  1, 0.0, nx, 0,
        -1,  1, 0.0,  0, 0]

    # Defining connections among vertices
    # We have a triangle every 3 indices specified
    indices = [
         0, 1, 2,
         2, 3, 0]

    textureFileName = image_filename

    return bs.Shape(vertices, indices, textureFileName)

def toGpuShapeWithImageLoaded(vertexData, indices, image_object, wrapMode=None, filterMode=None):
    gpuShape = es.GPUShape()

    gpuShape.size = len(indices)
    gpuShape.vao = glGenVertexArrays(1)
    gpuShape.vbo = glGenBuffers(1)
    gpuShape.ebo = glGenBuffers(1)

    # Vertex data must be attached to a Vertex Buffer Object (VBO)
    glBindBuffer(GL_ARRAY_BUFFER, gpuShape.vbo)
    glBufferData(GL_ARRAY_BUFFER, len(vertexData) * SIZE_IN_BYTES, vertexData, GL_STATIC_DRAW)

    # Connections among vertices are stored in the Elements Buffer Object (EBO)
    glBindBuffer(GL_ELEMENT_ARRAY_BUFFER, gpuShape.ebo)
    glBufferData(GL_ELEMENT_ARRAY_BUFFER, len(indices) * SIZE_IN_BYTES, indices, GL_STATIC_DRAW)

    gpuShape.texture = glGenTextures(1)

    glBindTexture(GL_TEXTURE_2D, gpuShape.texture)

    # texture wrapping params
    glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_WRAP_S, wrapMode)
    glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_WRAP_T, wrapMode)

    # texture filtering params
    glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER, filterMode)
    glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MAG_FILTER, filterMode)

    glTexImage2D(GL_TEXTURE_2D, 0, image_object.internalFormat, image_object.width, image_object.height, 0,
                 image_object.format, GL_UNSIGNED_BYTE, image_object.data)

    return gpuShape

def createSkybox(sky_image, quadSize, r):

    dx = quadSize/sky_image.width
    dy = quadSize/sky_image.height
    skybox_node = sg.SceneGraphNode("skybox")

    vertices1  = np.array([
        -r,  r, -r,  0*dx, 2*dy,
         r,  r, -r,  1*dx, 2*dy,
         r,  r,  r,  1*dx, 1*dy,
        -r,  r,  r,  0*dx, 1*dy]
        , dtype=np.float32)
    indices1 = np.array([
        0, 1, 2,
        2, 3, 0], dtype= np.uint32)

    sky1 = sg.SceneGraphNode("sky1")
    sky1.childs += [toGpuShapeWithImageLoaded(vertices1, indices1, sky_image, GL_REPEAT, GL_NEAREST)]
    skybox_node.childs += [sky1]

    def lerp(A, B, C):
        value = (C * A) + ((1 - C) * B)
        return value

    vertices2 = np.array([
        r, r, -r, 1 * dx, 2 * dy,
        r, -r, -r, 2 * dx, 2 * dy,
        r, -r, r, 2 * dx, 1 * dy,
        r, r, r, 1 * dx, 1 * dy]
        , dtype=np.float32)
    indices2 = np.array([
        0, 1, 2,
        2, 3, 0], dtype= np.uint32)
    sky2 = sg.SceneGraphNode("sky2")
    sky2.childs += [toGpuShapeWithImageLoaded(vertices2, indices2, sky_image, GL_REPEAT, GL_NEAREST)]
    skybox_node.childs += [sky2]

    vertices3 = np.array([
        r, -r, -r, 2 * dx, 2 * dy,
        -r, -r, -r, 3 * dx, 2 * dy,
        -r, -r, r, 3 * dx, 1 * dy,
        r, -r, r, 2 * dx, 1 * dy]
        , dtype=np.float32)
    indices3 = np.array([
        0, 1, 2,
        2, 3, 0], dtype= np.uint32)
    sky3 = sg.SceneGraphNode("sky3")
    sky3.childs += [toGpuShapeWithImageLoaded(vertices3, indices3, sky_image, GL_REPEAT, GL_NEAREST)]
    skybox_node.childs += [sky3]

    vertices4 = np.array([
        -r, -r, -r, 3 * dx, 2 * dy,
        -r,  r, -r, 4 * dx, 2 * dy,
        -r,  r,  r, 4 * dx, 1 * dy,
        -r, -r,  r, 3 * dx, 1 * dy]
        , dtype=np.float32)
    indices4 = np.array([
        0, 1, 2,
        2, 3, 0], dtype= np.uint32)
    sky4 = sg.SceneGraphNode("sky4")
    sky4.childs += [toGpuShapeWithImageLoaded(vertices4, indices4, sky_image, GL_REPEAT, GL_NEAREST)]
    skybox_node.childs += [sky4]

    vertices5= np.array([
        -r, r, -r, 1 * dx, 3 * dy,
        -r, -r, -r, 2 * dx, 3 * dy,
        r, -r, -r, 2 * dx, 2 * dy,
        r, r, -r, 1 * dx, 2 * dy]
        , dtype=np.float32)
    indices5= np.array([
        0, 1, 2,
        2, 3, 0], dtype= np.uint32)
    sky5 = sg.SceneGraphNode("sky5")
    sky5.childs += [toGpuShapeWithImageLoaded(vertices5, indices5, sky_image, GL_REPEAT, GL_NEAREST)]
    skybox_node.childs += [sky5]

    vertices6= np.array([
        r, r,  r, 1 * dx, 1 * dy,
        r, -r, r, 2 * dx, 1 * dy,
        -r, -r, r, 2 * dx, 0 * dy,
        -r, r, r, 1 * dx, 0 * dy]
        , dtype=np.float32)
    indices6 = np.array([
        0, 1, 2,
        2, 3, 0], dtype= np.uint32)
    sky6 = sg.SceneGraphNode("sky6")
    sky6.childs += [toGpuShapeWithImageLoaded(vertices6, indices6, sky_image, GL_REPEAT, GL_NEAREST)]
    skybox_node.childs += [sky6]
    skybox_node.transform = tr.translate(0,0, -r/4)
    return skybox_node

def lerp(A, B, C):
    value = (C * A) + ((1 - C) * B)
    return value