
import sys

import cv2
import numpy as np
from matplotlib import pyplot as plt

import contour
from facepp import API, File, APIError

API_KEY = 'bf7eae5ed9cf280218450523049d5f94'
API_SECRET = 'o6SeKJTnaoczTb-j6PBEGXvkiVz2hp71'
api = API(API_KEY, API_SECRET)

def crop_face(face, img, img_height, img_width):
	center = face['position']['center']
	# scale a little bit
	w = face['position']['width'] * img_width / 100 
	h = face['position']['height'] * img_height / 100 
	x = center['x'] * img_width / 100 
	y = center['y'] * img_height / 100
	(x0, x1) = (x-w/2, x+w/2)
	(y0, y1) = (y-h/2, y+h/2)
	face_img = img[y0:y1, x0:x1, :]
	return face_img

def histogram_match(src_face_img, dst_face_img):
	#cv2.imshow('src', src_face)
	#cv2.imshow('dst', dst_face)
	#print src_face.shape, dst_face.shape
	#print src_face
	src_hist, bin = np.histogram(src_face_img.flatten(), 256, [0,256])
	src_cdf = src_hist.cumsum()
	src_cdf_norm = src_cdf * src_hist.max()/ src_cdf.max()
	
	dst_hist, bin = np.histogram(dst_face_img.flatten(), 256, [0,256])
	dst_cdf = dst_hist.cumsum()
	dst_cdf_norm = dst_cdf * dst_hist.max()/ dst_cdf.max()
	#plt.plot(dst_cdf_norm, color='r')
	# apply the histogram matching
	src_min = src_face_img.min()
	src_max = src_face_img.max()
	dst_min = dst_face_img.min()
	dst_max = dst_face_img.max()
	
	lut = np.zeros((256,1))
	g_J = 0
	for g_I in xrange(256):
		while g_J < 255 and src_cdf_norm[g_J] < dst_cdf_norm[g_I]:
			g_J += 1
		lut[g_I] = g_J
	print lut.T

	res_img = src_face_img.copy()
	for x in xrange(src_face_img.shape[0]):
		for y in xrange(src_face_img.shape[1]):
			#print res_img[x][y],
			res_img[x][y] = lut[src_face_img[x][y]]
			#print res_img[x][y]
	#cv2.imshow('rst', res_img)
	#cv2.waitKey(0)

	new_hist, bin = np.histogram(res_img.flatten(), 256, [0,256])
	new_cdf = new_hist.cumsum()
	new_cdf_norm = new_cdf * new_hist.max()/ new_cdf.max()
	#plt.plot(src_cdf_norm, color='b')
	#plt.plot(dst_cdf_norm, color='r')
	#plt.plot(new_cdf_norm, color='y')
	
	#plt.hist(src_face_img.flatten(), 256, [0,256], color='g')
	#plt.hist(res_img.flatten(), 256, [0,256], color='y')
	#plt.xlim([0,256])
	#plt.show()
	return res_img

if __name__ == '__main__':
 	if len(sys.argv) <= 2:
		print "usage: %s <image src> <image dst>" % sys.argv[0]
		exit(1)
	
	# we assume that these a images are in the same pose bin
	src_name = sys.argv[1]
	dst_name = sys.argv[2]
	src_img = cv2.imread(sys.argv[1])
	dst_img = cv2.imread(sys.argv[2])
	print src_name, dst_name
	src_rst = api.detection.detect(img = File(src_name), attribute='pose')
	src_img_width 	= src_rst['img_width']
	src_img_height 	= src_rst['img_height']
	src_face 		= src_rst['face'][0]

	dst_rst = api.detection.detect(img = File(dst_name), attribute='pose')
	dst_img_width 	= dst_rst['img_width']
	dst_img_height 	= dst_rst['img_height']
	dst_face 		= dst_rst['face'][0]

	#crop_face(src_face, src_img, src_img_height, src_img_width)

	src_crop_img = crop_face(src_face, src_img, src_img_height, src_img_width)
	dst_crop_img = crop_face(dst_face, dst_img, dst_img_height, dst_img_width)

	src_crop_split = cv2.split(src_crop_img)
	dst_crop_split = cv2.split(dst_crop_img)
	new_face_b = histogram_match(src_crop_split[0], dst_crop_split[0])
	new_face_g = histogram_match(src_crop_split[1], dst_crop_split[1])
	new_face_r = histogram_match(src_crop_split[2], dst_crop_split[2])
	
	new_face = cv2.merge([new_face_b,new_face_g,new_face_r])

	#print dst_face.shape
	#dst_face = np.array(map(lambda x: lut[x], dst_face))
	#print dst_face.
	cv2.imshow('target face', src_crop_img)
	cv2.imshow('original face', dst_crop_img)
	cv2.imshow('dst face', new_face)
	#dst_hist, bin = np.histogram(dst_face.flatten(), 256, [1,256])
	#dst_cdf = dst_hist.cumsum()
	#dst_cdf_norm = dst_cdf * dst_hist.max()/ dst_cdf.max()
	#plt.plot(src_cdf_norm, color='b')
	#plt.plot(dst_cdf_norm, color='r')
	#plt.hist(src_face.flatten(), 256, [1,255], color='g')
	#plt.hist(dst_face.flatten(), 256, [1,255], color='y')
	#plt.xlim([0,256])
	plt.show()
	#cv2.imshow('extract src image', src_face)
	#cv2.imshow('extract dst image', dst_face)
	cv2.waitKey(0)