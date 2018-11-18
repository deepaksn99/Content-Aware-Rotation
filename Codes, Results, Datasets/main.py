""" 

Content Aware Rotation, In ICCV 2013	
Authors: Kaiming He, Huiwen Chan, Jian Sun

An implementation by S Deepak Narayanan, Indian Institute of Technology Gandhinagar
16110142
"""


""" 
Standard Imports for the rest of the program 
"""
import pandas as pd
import matplotlib.pyplot as plt
import cv2 as cv
import numpy as np 
import random as rd 

from line_matrix import *
from shape_matrix import *
from extractlines import quantize_and_get
from boundary_matrix import *
from pk import *
from optimization import *

""" 
Here I am initialising all the parameters
"""



image = input('Enter the Image Number from the Dataset ')
angle = input('Enter the Angle of Rotation. For the exact angles, please refer to the RotationAngles.txt inside the Dataset directory ')

rotation_angle = float(angle)
delta = rotation_angle
print(image)
if int(image)!=9:
	img = cv.imread('Dataset/image'+image+'.png')
	Y,X = img.shape[:2]

	name = 'Dataset/image'+image+'.png.txt'
else:
	img = cv.imread('Dataset/image'+image+'.jpg')
	Y,X = img.shape[:2]

	name = 'Dataset/image'+image+'.jpg.txt'
"""
	Total Number of Quads created = 900. This is very 
	deterimental in deciding the amount of time the 
	program takes to run
"""

"""
	cx = Number of Quads along the horizontal direction
	cy = Number of Quads along the vertical direction
	n_quads = Total number of quads
	number_of_vertices  = Total Number of Mesh Vertices
	x_len = Distance between subsequent Quads along x_direction
	y_len = Distance between subsequent Quads along y_direction
	threshold and linesegthreshold = Used for choosing the correct 
		Line Segements among those that were detected.
	vertexX = List of all the X_coordinates of the grid points
	vertexY = List of all the Y_coordinates of the grid points
	gridX,gridY =  Meshgrid that we form using these vertices
"""

cx= int(X/30)
cy = int(Y/30)

n_quads = cx*cy
number_of_vertices = (cx+1)*(cy+1)
x_len = (X-1)/cx
y_len = (Y-1)/cy


threshold = 16
linesegthreshold = (x_len**2 + y_len**2)/64

temp = 0
vertexX = np.zeros(1)
while(1):
    temp+=x_len
    temp = (round(temp,10))
    vertexX = np.append(vertexX,temp)
    if temp>X-2:
        break
temp = 0
vertexY = np.zeros(1)
while(1):
    temp+=y_len
    temp = (round(temp,10))
    vertexY = np.append(vertexY,temp)
    if temp>Y-2:
        break

gridX, gridY = np.meshgrid(vertexX,vertexY)
Vx = np.reshape(gridX,number_of_vertices,1)
Vy = np.reshape(gridY,number_of_vertices,1)
V = np.zeros((number_of_vertices*2))
for i in range(number_of_vertices):
    V[2*i] = Vx[i]
    V[2*i+1] = Vy[i]
V = V+1
print('The Dimension of the Image are ',X,Y)


sdelta = np.zeros(90)
sdelta[0] = 1000
sdelta[44] = 1000
sdelta[45] = 1000
sdelta[89] = 1000


print("Line Extraction and Quantization Begin....")
lines = quantize_and_get(X,Y,threshold,linesegthreshold,x_len,y_len,delta,name)
print("Line Extraction and Quantization Done .... ")
print("Forming the functions for Shape, Line, Boundary and Rotation Constraints...")



"""
    Intialising Thetas Now
"""

thetas = np.ones((90))*delta

Pk_all,line,UK = formline(lines,number_of_vertices,x_len,y_len,vertexX,vertexY,thetas)
shape_preservation = formshape(vertexX,vertexY,number_of_vertices,n_quads)
boundary,b = formboundary(number_of_vertices,X,Y,gridX,gridY)

lambda_l = 100
lambda_b = 10**8
lambda_r = 100  

"""
	Optimization Begin
"""
print('Boundary Matrix Dimension is ',boundary.shape)
print('Shape Matrix Dimension is ',shape_preservation.shape)
print('Line Matrix Dimension is ',line.shape)
print('PK_all is ',Pk_all.shape)
print('Dimension of b used in fix_theta_solve_v is ',b.shape)

n = number_of_vertices
k = len(lines)
print('The Total Number of vertices used are', n)
print('The total number of lines detected using the author usage line segment detector are',k)

V_new = np.zeros(len(V))

dx = x_len; dy =y_len; N = number_of_vertices; x = vertexX; y = vertexY

"""
	dx, dy - Increments in X and Y, N is a parameter that we're passing - number of vertices
	x -> List of all the vertices in the meshgrid.
"""

for number_of_iteration in range(1,11):
	print("Iteration Number ", number_of_iteration)
	V_new = fix_theta_solve_v(line,shape_preservation,boundary,b,lambda_l,lambda_r,lambda_b,n,k)
	thetas = fix_v_solve_theta(UK,lines,thetas,V_new,rotation_angle,dx,dy,N,x,y,sdelta,lambda_l,lambda_r)
	if number_of_iteration!=10:
		Pk_all,line,UK = formline(lines,number_of_vertices,x_len,y_len,vertexX,vertexY,thetas)

print('Optimization Done. The Thetas and V have been stored in the results folder.\n')
print('Now, open the MATLAB script named as main.m and run the same.\n')


df = pd.DataFrame(thetas)
df.to_csv('theta.csv')
df = pd.DataFrame(V_new)
df.to_csv('vertex.csv')


