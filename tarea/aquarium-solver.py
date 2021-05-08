
import sys
import json

import numpy as np
import scipy.sparse as sparse
import scipy.sparse.linalg as linalg
import matplotlib.pyplot as plt



#Json thingy


def jsonToDict(fileName):
    with open(fileName) as file:
        data = json.load(file)
        return data


#Setup
setup = sys.argv[1]
setup_info = jsonToDict(setup)
W= setup_info["width"]
H= setup_info["height"]
L= setup_info["lenght"]
F= setup_info["window_loss"]
heat_A= setup_info["heater_a"]
heat_B= setup_info["heater_b"]
T= setup_info["ambient_temperature"]
filename = setup_info["filename"]
h=0.2

#dirichet


# Number of unknowns
# left, bottom and top sides are known (Dirichlet condition)
# right side is unknown (Neumann condition)
nw = int(W / h) + 1
nl = int(L / h) + 1
nh = int(H / h)

# In this case, the domain is just a 3D rectangle
N = nw*nl*nh

# We define a function to convert the indices from i,j to k and viceversa
# i,j,k indexes the discrete domain in 3D.
# k parametrize those i,j, this way we can tidy the unknowns
# in a column vector and use the standard algebra

def getK(w,l,h):
    return   l*nw + w + h*(nw*nl)

def getIJK(n):
    k = n // (nw*nl)
    i = n % nw
    j = (n // nw) - k*nl
    
    return (i, j, k)

A = sparse.lil_matrix((N,N)) # We use a sparse matrix in order to spare memory, since it has many 0's

# In this vector we will write all the right side of the equations
b = np.zeros((N,))

for w in range(0, nw):
    for l in range(0, nl):
        for h in range(0, nh):
            k = getK(w,l,h)
            #coeficients
            k_right = getK(w+1, l, h)
            k_left = getK(w-1, l, h)
            k_front = getK(w, l+1, h)
            k_back = getK(w, l-1, h)
            k_roof = getK(w, l, h+1)
            k_floor = getK(w, l, h-1)
            

            #interior
            if 1 <= w and w <= nw - 2 and 1 <= l and l <= nl - 2 and 1 <= h and h <= nh-2:
                
                A[k, k_right] = 1
                A[k, k_left] = 1
                A[k, k_front] = 1
                A[k, k_back] = 1
                A[k, k_roof] = 1
                A[k, k_floor] = 1
                A[k,k] = -6
                b[k] = 0
            
            # calentadorA
            elif  w >= nw//3 and w <= 2*nw//3 and l >= nl-(2*nl//5) and l <= nl-(nl//5) and h == 0:
               
                A[k, k_right] = 0
                A[k, k_left] = 0
                A[k, k_front] = 0
                A[k, k_back] = 0
                A[k, k_roof] = 0
                A[k, k] = 1
                b[k] =  heat_A

            # CalentadorB
            elif w >= nw//3 and w <= 2*nw//3 and l >= nl//5  and l <= 2*nl//5 and h == 0:
                
                A[k, k_right] = 0
                A[k, k_left] = 0
                A[k, k_front] = 0
                A[k, k_back] = 0
                A[k, k_roof] = 0
                A[k, k] = 1
                b[k] =  heat_B
            #derecha
            elif w == nw-1 and 1 <= l and l <= nl - 2 and 1 <= h and h <= nh-2:
                
                A[k, k_left] = 2
                A[k, k_front] = 1
                A[k, k_back] = 1
                A[k, k_roof] = 1
                A[k, k_floor] = 1
                A[k,k] = -6
                b[k] = -2*F*h
            
            #izquierda
            elif w == 0 and 1 <= l and l <= nl - 2 and 1 <= h and h <= nh-2:
                
                A[k, k_right] = 2

                A[k, k_front] = 1
                A[k, k_back] = 1
                A[k, k_roof] = 1
                A[k, k_floor] = 1
                A[k,k] = -6
                b[k] = -2*F*h
            
            #adelante
            elif 1 <= w and w <= nw-2 and l == nl-1 and 1 <= h and h <= nh-2:
                
                A[k, k_right] = 1
                A[k, k_left] = 1
               
                A[k, k_back] = 2
                A[k, k_roof] = 1
                A[k, k_floor] = 1
                A[k,k] = -6
                b[k] = -2*F*h

            #al final
            elif 1 <= w and w <= nw-2 and l == 0 and 1 <= h and h <= nh-2:
                
                A[k, k_right] = 1
                A[k, k_left] = 1
                A[k, k_front] = 2
                
                A[k, k_roof] = 1
                A[k, k_floor] = 1
                A[k,k] = -6
                b[k] = -2*F*h

            # roof techo con T
            elif 1 <= w and w <= nw - 2 and 1 <= l and l <= nl-2 and h == nh-1:
                
                A[k, k_right] = 1
                A[k, k_left] = 1
                A[k, k_front] = 1
                A[k, k_back] = 1
                
                A[k, k_floor] = 1
                A[k,k] = -6
                b[k] = -T

            #floor            
            elif 1 <= w and w <= nw - 2 and 1 <= l and l <= nl-2 and h == 0:
               
                A[k, k_right] = 1
                A[k, k_left] = 1
                A[k, k_front] = 1
                A[k, k_back] = 1
                A[k, k_roof] = 2
                
                A[k,k] = -6
                b[k] = 0
            
            #inferior derecha
            elif w == nw-1 and 1 <= l and l <= nl - 2 and h == 0:
                
                
                A[k, k_left] = 2
                A[k, k_front] = 1
                A[k, k_back] = 1
                A[k, k_roof] = 2
                
                A[k,k] = -6
                b[k]  = -2*F*h
            
            # inferior izquierda 
            elif w == 0 and 1 <= l and l <= nl - 2 and h == 0:
                
                A[k, k_right] = 2
                
                A[k, k_front] = 1
                A[k, k_back] = 1
                A[k, k_roof] = 2
                
                A[k,k] = -6
                b[k] = -2*F*h

            #inferior trasera
            elif 1 <= w and w <= nw-2 and l == 0 and h == 0:
                
                A[k, k_right] = 1
                A[k, k_left] = 1
                A[k, k_front] = 2
                
                A[k, k_roof] = 2
                
                A[k,k] = -6
                b[k] = -2*F*h
            
            #inferior delantera
            elif 1 <= w and w <= nw-2 and l == nl-1 and h == 0:
                
                A[k, k_right] = 1
                A[k, k_left] = 1
                
                A[k, k_back] = 2
                A[k, k_roof] = 2
                
                A[k,k] = -6
                b[k] = -2*F*h

            #derecha delantera
            elif w == nw-1 and l == nl-1 and 1 <= h and h <= nh-2:
               
                
                A[k, k_left] = 2
                
                A[k, k_back] = 2
                A[k, k_roof] = 1
                A[k, k_floor] = 1
                A[k,k] = -6
                b[k] = -4*F*h
            
            #derecha trasera 
            elif w == nw-1 and l == 0 and 1 <= h and h <= nh-2:
            
                
                A[k, k_left] = 2
                
                A[k, k_back] = 2
                A[k, k_roof] = 1
                A[k, k_floor] = 1
                A[k,k] = -6
                b[k] = -4*F*h

            # left front
            elif w == 0 and l == nl-1 and 1 <= h and h <= nh-2:
                
                A[k, k_right] = 2
               
                
                A[k, k_back] = 2
                A[k, k_roof] = 1
                A[k, k_floor] = 1
                A[k,k] = -6
                b[k] = -4*F*h
            
            # left back
            elif w == 0 and l == 0 and 1 <= h and h <= nh-2:
                
                A[k, k_right] = 2
                                
                A[k, k_front] = 2
                A[k, k_roof] = 1
                A[k, k_floor] = 1
                A[k,k] = -6
                b[k] = -4*F*h

            #lo mismo pal techo esquinas
            # right front
            elif w == nw-1 and l == nl-1 and h == nh-1:
                
                A[k, k_left] = 2
                A[k, k_back] = 2
                A[k, k_floor] = 1
                A[k,k] = -6
                b[k] = -(4*F*h + T)
            
            # right back
            elif w == nw-1 and l == 0 and h == nh-1:
                
                A[k, k_left] = 2
                A[k, k_front] = 2
                A[k, k_floor] = 1
                A[k,k] = -6
                b[k] = -(4*F*h + T)

            # left front
            elif w == 0 and l == nl-1 and h == nh-1:
                
                A[k, k_right] = 2
                A[k, k_back] = 2
                A[k, k_floor] = 1
                A[k,k] = -6
                b[k] = -(4*F*h + T)
            
            # left back
            elif w == 0 and l == 0 and h == nh-1:
                
                A[k, k_right] = 2
                A[k, k_front] = 2
                A[k, k_floor] = 1
                A[k,k] = -6
                b[k] = -(4*F*h + T)

            #pal techo pero los lao's
            # right side
            elif w== nw-1 and 1 <= l and l <= nl - 2 and h == nh-1:
                
                A[k, k_left] = 2
                A[k, k_front] = 1
                A[k, k_back] = 1
                A[k, k_floor] = 1
                A[k, k] = -6
                b[k] = -(2*F*h + T)
            # left side
            elif w == 0 and 1 <= l and l <= nl - 2 and h == nh-1:
                
                A[k, k_right] = 2
                A[k, k_front] = 1
                A[k, k_back] = 1
                A[k, k_floor] = 1
                A[k, k] = -6
                b[k] =-(2*F*h + T)
            
            # front side
            elif 1 <= w and w <= nw-2 and l == nl-1 and h == nh-1:
                
                A[k, k_right] = 1
                A[k, k_left] = 1
                A[k, k_back] = 2
                A[k, k_floor] = 1
                A[k, k] = -6
                b[k] = -(2*F*h + T)

            # back side
            elif 1 <= w and w <= nw-2 and l == 0 and h == nh-1:
                
                A[k, k_right] = 1
                A[k, k_left] = 1
                A[k, k_front] = 2
                A[k, k_floor] = 1
                A[k, k] = -6
                b[k] = -(2*F*h + T)
            
            # corner lower front right
            elif (w, l, h) == (nw-1, nl-1, 0):
               
                A[k, k_left] = 2
                A[k, k_back] = 2
                A[k, k_roof] = 2
                A[k, k] = -6
                b[k] = -4*F*h  

            # corner lower front left
            elif (w, l, h) == (0,nl-1,0):
                
                A[k, k_right] = 2
                A[k, k_back] = 2
                A[k, k_roof] = 2
                A[k, k] = -6
                b[k] = -4*F*h  

            # corner lower back right
            elif (w, l, h) == (nw-1,0,0):
                
                A[k, k_left] = 2
                A[k, k_front] = 2
                A[k, k_roof] = 2
                A[k, k] = -6
                b[k] = -4*h*F

            # corner lower back left
            elif (w, l, h) == (0,0,0):
                
                A[k, k_right] = 2
                A[k, k_front] = 2
                A[k, k_roof] = 2
                A[k,k] = -6
                b[k] = -4*h*F         

            else:
                print("Point (" + str(w) + ", " + str(l) + ", " + str(h) + ") missed!")
                print("Associated point index is " + str(k))
                raise Exception()

# Solving our system
#x = np.linalg.solve(A, b)
x = linalg.spsolve(A, b)

u = np.zeros((nw,nl,nh))

for e in range(0, N):
    w,l,h = getIJK(e)
    u[w,l,h] = x[e]

ub = np.zeros((nw,nl,nh+1))
ub[0:nw, 0:nl,0:nh] = u[:,:,:]
ub[0:nw, 0:nl, nh] = T
print(ub) 

np.save(filename, ub)

#visual------

#X, Y, Z = np.mgrid[0:W:16j, 0:L:31j, 0:H:21j]



#fig = plt.figure()
#ax = plt.axes(projection='3d')



#scatter = ax.scatter(X,Y,Z, c=ub, cmap='winter', alpha=1, s=75, marker='s')
#fig.colorbar(scatter, shrink=0.5, aspect=5) # This is the colorbar at the side

#ax.set_title('Preview')
#ax.set_xlabel('Width')
#ax.set_ylabel('Length')
#ax.set_zlabel('Hight')

# Note:
# imshow is also valid but it uses another coordinate system,
# a data transformation is required
#ax.imshow(ub.T)

#plt.show()
