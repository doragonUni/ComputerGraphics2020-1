import numpy as np
import glfw
import matplotlib.pyplot as mpl
from mpl_toolkits.mplot3d import Axes3D
import csv 

def generateT(t):
    return np.array([[1, t, t**2, t**3]]).T


def CatmullRomMatrix(P1, P2 , P3 , P4):
    P = np.concatenate((P1, P2, P3, P4), axis=1)
    Mcr = 0.5*np.array([[0, -1, 2, -1], [2, 0, -5, 3], [0, 1, 4, -3], [0, 0, -1, 1]])   

    return np.matmul(P,  Mcr)

def plotCurve(ax, curve, label, color=(0,0,1)):
    
    xs = curve[:, 0]
    ys = curve[:, 1]
    zs = curve[:, 2]
    
    ax.plot(xs, ys, zs, label=label, color=color)



# M is the cubic curve matrix, N is the number of samples between 0 and 1
def evalCurve(M, N):
    # The parameter t should move between 0 and 1
    ts = np.linspace(0.0, 1.0, N)
    
    # The computed value in R3 for each sample will be stored here
    curve = np.ndarray(shape=(N, 3), dtype=float)
    
    for i in range(len(ts)):
        T = generateT(ts[i])
        curve[i, 0:3] = np.matmul(M, T).T
        
    return curve

P1 = np.array([[0, 1, 0]]).T
P2 = np.array([[0, 1, 1]]).T
P3 = np.array([[0, 3, 3]]).T
P4 = np.array([[0, 2, 1]]).T
P5 = np.array([[5, 5, 0]]).T
P6 = np.array([[5, 5, 3]]).T
P7 = np.array([[5, 4, 5]]).T
P8 = np.array([[5, 1, 7]]).T
P9 = np.array([[5, 5, 10]]).T
Puntos = [P1,P2,P3,P4,P5,P6,P7,P8,P9]
#PTO1 = [P1,P2,P3,P4]
#PTO2 = [P2,P3,P4,P5]

def catmullRom(Puntos):

    i=1
    CatmullSpline = []
    while i < len(Puntos)-2:
        N=750
        
        CMR = CatmullRomMatrix(Puntos[i-1], Puntos[i], Puntos[i+1], Puntos[i+2])
        
        CatmullSegment = evalCurve(CMR, N)
        for k in range(N):
            CatmullSpline.append(CatmullSegment[k])
        
        
        
        i+=1

    CatmullSpline = np.array(CatmullSpline)
    return CatmullSpline

def catmullPoints1to4(Puntos):  #SOLO 4 PUNTOS

    
    CatmullSpline = []
    
    N=10
        
    CMR = CatmullRomMatrix(Puntos[0], Puntos[1], Puntos[2], Puntos[3])
        
    CatmullSegment = evalCurve(CMR, N)
    CatmullSpline.append(CatmullSegment)
      

    return CatmullSegment

def csvToPArray(filename):
    points = []

    with open(filename, 'r') as file:
        for line in file.readlines():
            aux = line.strip().split(',')
            
            points += [np.array([[float(coord) for coord in aux[0:]]]).T]
    return points


def catmullRom5POINTS(points):
    
    CMR1=CatmullRomMatrix(points[0], points[1], points[2], points[3])
    CMR2=CatmullRomMatrix(points[1], points[2], points[3], points[4])
    N=750
    CatmullSegment1 = evalCurve(CMR1, N)
    CatmullSegment2 = evalCurve(CMR2, N)

    CatmullSpline = []
    for i in range(N):
        CatmullSpline.append(CatmullSegment1[i])
    for k in range(N):
        CatmullSpline.append(CatmullSegment2[k])
    print(CatmullSpline)
    CatmullSpline = np.array(CatmullSpline)

    return CatmullSpline

def separacion(catmull):
    x = [i[0] for i in catmull]
    y = [i[1] for i in catmull]
    z = [i[2] for i in catmull]
    return x, y, z

#a= catmullRom(Puntos)


#testeo = catmullRom(Puntos)
#print(testeo)

#a,b,c = separacion(testeo)
#print(a)

#one = catmullPoints23(PTO1)
#two = catmullPoints23(PTO2)


if __name__ == "__main__":
    
    # Setting up the matplotlib display for 3D
    #fig = mpl.figure()
    #ax = fig.gca(projection='3d')
        
    
    """
    Example for cM
    """
    
    
    

    
    
    
    
    #plotCurve(ax, a , "CMR curve")
    #plotCurve(ax, two, "CMR curve2")
    
    

    
    # Adding a visualization of the control points
    #controlPoints = np.concatenate((P1, P2, P3, P4, P5, P6,P7,P8,P9), axis=1)
    #ax.scatter(controlPoints[0,3], controlPoints[0,3], controlPoints[0,3], color=(1,0,0))
    
    #ax.set_xlabel('x')
    #ax.set_ylabel('y')
    #ax.set_zlabel('z')
    #ax.legend()
    #mpl.show()