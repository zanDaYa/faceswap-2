
import numpy as np

from scipy import misc, ndimage, matrix
from numpy import array, linalg, float32
from math import pi, sin, cos
from matplotlib.pyplot import imshow, show, cm

def get_transform_matrix(p1,p2,p3,s1,s2,s3):
    pri = matrix([p1,p2,p3]).T
    sec = matrix([s1,s2,s3]).T
   
    pri = np.vstack((pri, [1,1,1]))
    sec = np.vstack((sec, [1,1,1]))
    x1 = np.linalg.solve(pri.T, (sec.T)[:, 0])
    x2 = np.linalg.solve(pri.T, (sec.T)[:, 1])
    transform = np.vstack(((x1.T)[0,0:2], (x2.T)[0,0:2]))
    return transform

def affine_transform_image(p1,p2,p3,s1,s2,s3):
    transform = get_transform_matrix(p1, p2, p3, s1, s2, s3).T
    
    c_in=0.5*array(img.shape)
    c_out=array((256.0,256.0))
    offset = c_in-c_out.dot(transform.T)
    transimg = ndimage.interpolation.affine_transform(
        img,transform,order=2, offset=array((offset.item(0,0), offset.item(0,1))),output_shape=(513,513),cval=0.0,output=float32
    )
    return transimg

if __name__ == '__main__':
    img = misc.lena()
    transimg = affine_transform_image([0,1], [1,1], [0,0], [0.707,0.707], [1.414,0], [0,0])
    imshow(transimg, cmap=cm.gray); show()
