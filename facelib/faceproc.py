
import sys
import numpy as np
import scipy
from scipy import ndimage
import matplotlib.pyplot as plt

from faceinfo import FaceInfo, FaceLandmark, FacePoint, FacePose
from faceposebin import FacePoseBin
from facepp import API, File, APIError

# please don't copy this
API_KEY = 'bf7eae5ed9cf280218450523049d5f94'
API_SECRET = 'o6SeKJTnaoczTb-j6PBEGXvkiVz2hp71'
api = API(API_KEY, API_SECRET)

def get_transform_matrix(p1,p2,p3,s1,s2,s3):
    pri = np.matrix([p1,p2,p3]).T
    sec = np.matrix([s1,s2,s3]).T
   
    pri = np.vstack((pri, [1,1,1]))
    sec = np.vstack((sec, [1,1,1]))
    x1 = np.linalg.solve(pri.T, (sec.T)[:, 0])
    x2 = np.linalg.solve(pri.T, (sec.T)[:, 1])
    transform = np.vstack(((x1.T)[0,0:2], (x2.T)[0,0:2]))
    return transform

def affine_transform_image(img,p1,p2,p3,s1,s2,s3):
    transform = (get_transform_matrix(p1, p2, p3, s1, s2, s3)).T
    
    newshape = np.array(img.shape[0:2])*0.9
    c_in = 0.5*np.array(img.shape[0:2])
    c_out = 0.5*newshape
    #print transform, c_in, c_out
    offset = c_in-c_out.dot(transform.T)
    img_r = img[:,:,0]
    img_g = img[:,:,1]
    img_b = img[:,:,2]
    transimg_r = ndimage.interpolation.affine_transform(img_r,transform,order=4,offset=np.array((offset.item(0,0), offset.item(0,1))),output_shape=newshape,cval=0.0,output=np.float32)
    transimg_g = ndimage.interpolation.affine_transform(img_g,transform,order=4,offset=np.array((offset.item(0,0), offset.item(0,1))),output_shape=newshape,cval=0.0,output=np.float32)
    transimg_b = ndimage.interpolation.affine_transform(img_b,transform,order=4,offset=np.array((offset.item(0,0), offset.item(0,1))),output_shape=newshape,cval=0.0,output=np.float32)
    return np.dstack((transimg_r, transimg_g, transimg_b))

from pprint import pformat
# copied from hello.py
def print_result(hint, result):
    def encode(obj):
        if type(obj) is unicode:
            return obj.encode('utf-8')
        if type(obj) is dict:
            return {encode(k): encode(v) for (k, v) in obj.iteritems()}
        if type(obj) is list:
            return [encode(i) for i in obj]
        return obj
    print hint
    result = encode(result)
    print '\n'.join(['  ' + i for i in pformat(result, width = 75).split('\n')])


class FaceProc:
	def __init__(self, pose_bin):
		self.pose_bin = pose_bin

	def proc_face(self, face, img_width, img_height, img_name):
		print 'proc_face: face id', face['face_id']
		face_id = face['face_id']
		landmark = api.detection.landmark(face_id = face_id, type='25p')
		# crop the image
		center = face['position']['center']
		w = 200
		h = 200
		# scale a little bit
		#w *= 1.5
		#h *= 1.5 
		img = plt.imread(img_name)
		print img.shape
		x = center['x'] * img_width / 100
		y = center['y'] * img_height / 100
		(x0, x1) = (x-w/2, x+w/2)
		(y0, y1) = (y-h/2, y+h/2)
		face_img = img[y0:y1, x0:x1, :]
		if face_img.shape[0] == 0 or face_img.shape[1] == 0:
			print "Image broken..."
			return 
	 	#plt.imshow(face_img)
		#plt.show()
		# plt.imsave(face_id+'.png', face_img)
		
		# select corresponding pose bin
		pose = face['attribute']['pose']
		face_pose = FacePose(pose)
		
		# get alignment data
		face_landmark = FaceLandmark(landmark['result'][0]['landmark'], img_width, img_height)
		face_landmark.transform(x0, y0)
		name = img_name.split('.')[-2]
		name = name.split('/')[-1]
		print name
		self.pose_bin.save(face_img, face_id, face_pose, face_landmark, name)

	def proc_image(self, img_name):
		print 'proc_image: image file', img_name
		rst = api.detection.detect(img = File(img_name), attribute='pose')
		for face in rst['face']:
			# basically, there will be only one image in the lfw file
			
			self.proc_face(face, rst['img_width'], rst['img_height'], img_name)
		print 'proc_image: done'

	def affine_transform(self, img_name, mark1, mark2):
		origin_image = plt.imread(img_name)
		p1 = mark1.eye_ll.array()
		p2 = mark1.eye_rl.array()
		p3 = mark1.mouth_l.array()
		s1 = mark2.eye_ll.array()
		s2 = mark2.eye_rl.array()
		s3 = mark2.mouth_l.array()
		transimg = affine_transform_image(origin_image, p1, p2, p3, s1, s2, s3)
		plt.imshow(transimg)
		plt.show()




if __name__ == '__main__':
	if len(sys.argv) <= 2:
		print 'Usage: %s <image name> <pose bin>' % sys.argv[0]
		exit(1)
	img_name = sys.argv[1]
	pose_bin = FacePoseBin(sys.argv[2])

	face_proc = FaceProc(pose_bin)
	face_proc.proc_image(img_name)
	