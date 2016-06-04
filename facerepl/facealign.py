
import os
import sys
import cv2
import numpy as np
import contour
from facepp import API, File, APIError

API_KEY = 'bf7eae5ed9cf280218450523049d5f94'
API_SECRET = 'o6SeKJTnaoczTb-j6PBEGXvkiVz2hp71'
api = API(API_KEY, API_SECRET)

feature_list = [
	'left_eyebrow_left_corner',
	'right_eyebrow_right_corner',
	'contour_chin',
]
def get_feature_points(face, w, h):
	landmark = api.detection.landmark(face_id=face['face_id'], type='83p')
	result = []
	for v in feature_list:
		x = landmark['result'][0]['landmark'][v]['x'] * w / 100
		y = landmark['result'][0]['landmark'][v]['y'] * h / 100
		result.append([x,y])
	return result

if __name__ == '__main__':
    if len(sys.argv) <= 1:
        print "usage: %s <image src> <image dst>" % sys.argv[0]
        exit(1)
    # we assume that these a images are in the same pose bin
    src_name = sys.argv[1]
    dst_name = sys.argv[2]
    src_img = cv2.imread(sys.argv[1])
    dst_img = cv2.imread(sys.argv[2])

    src_rst = api.detection.detect(img = File(src_name), attribute='pose')
    src_img_width 	= src_rst['img_width']
    src_img_height 	= src_rst['img_height']
    src_face 		= src_rst['face'][0]

    dst_rst = api.detection.detect(img = File(dst_name), attribute='pose')
    dst_img_width 	= dst_rst['img_width']
    dst_img_height 	= dst_rst['img_height']
    dst_face 		= dst_rst['face'][0]

    # there's only one face in this case
    ss = np.array(get_feature_points(src_face, src_img_width, src_img_height), dtype=np.float32)
    ps = np.array(get_feature_points(dst_face, dst_img_width, dst_img_height), dtype=np.float32)

    print ps
    print ss
    map_matrix = cv2.getAffineTransform(ps, ss)
    print map_matrix

    #dsize = (300,300)
    map_result = cv2.warpAffine(dst_img, map_matrix, dsize=(300,300))
    
    extract_face = contour.extract_face(src_face['face_id'], src_img_width, src_img_height, src_name)
    cv2.imshow('extract source image', extract_face)

    # merge 
    for x in xrange(src_img_width):
    	for y in xrange(src_img_height):
    		if sum(extract_face[y][x]) == 0:
    			continue
    		else:
    			# here we need to change the light of extract face
    			map_result[y][x] = extract_face[y][x]
    cv2.imshow('merge', map_result)

    imap_matrix = cv2.invertAffineTransform(map_matrix)
    print map_result.shape
    print imap_matrix
    final = cv2.warpAffine(map_result, imap_matrix, dsize=(dst_img.shape[0:2]))
    cv2.imwrite('final.png', final)
    cv2.waitKey(0)
