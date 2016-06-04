
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
	'left_eye_center',
	'right_eye_center',
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

def faceclone(src_name, dst_name):
    src_img = cv2.imread(src_name)
    dst_img = cv2.imread(dst_name)

    src_rst = api.detection.detect(img = File(src_name), attribute='pose')
    src_img_width   = src_rst['img_width']
    src_img_height  = src_rst['img_height']
    src_face        = src_rst['face'][0]

    dst_rst = api.detection.detect(img = File(dst_name), attribute='pose')
    dst_img_width   = dst_rst['img_width']
    dst_img_height  = dst_rst['img_height']
    dst_face        = dst_rst['face'][0]

    ss = np.array(get_feature_points(src_face, src_img_width, src_img_height), dtype=np.float32)
    ps = np.array(get_feature_points(dst_face, dst_img_width, dst_img_height), dtype=np.float32)
    map_matrix = cv2.getAffineTransform(ps, ss)

    #dsize = (300,300)
    map_result = cv2.warpAffine(dst_img, map_matrix, dsize=(src_img_width,src_img_height))
    
    extract_mask, center = contour.extract_face_mask(src_face['face_id'], src_img_width, src_img_height, src_name)
    # merge 
    ## first blending the border
    extract_alpha = contour.extract_face_alpha(src_face['face_id'], src_img_width, src_img_height, src_name)
    center = (map_result.shape[0]/2, map_result.shape[1]/2)
    map_result = cv2.seamlessClone(src_img, map_result, extract_mask, center, flags=cv2.NORMAL_CLONE)

    imap_matrix = cv2.invertAffineTransform(map_matrix)
    final = cv2.warpAffine(map_result, imap_matrix, dsize=(dst_img.shape[0:2]))
    return final

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
    map_result = cv2.warpAffine(dst_img, map_matrix, dsize=(src_img_width,src_img_height))
    
    extract_mask, center = contour.extract_face_mask(src_face['face_id'], src_img_width, src_img_height, src_name)
    cv2.imshow('contour', extract_mask)
    # merge 
    cv2.imshow('src', src_img)

    ## first blending the border
    extract_alpha = contour.extract_face_alpha(src_face['face_id'], src_img_width, src_img_height, src_name)
    cv2.imshow('contour', extract_alpha)
    # merge 
    #for x in xrange(src_img_width):
    #    for y in xrange(src_img_height):
    #        alpha = extract_alpha[y][x] 
    #        map_result[y][x][0] = (1-alpha) * map_result[y][x][0] + (alpha) * src_img[y][x][0]
    #        map_result[y][x][1] = (1-alpha) * map_result[y][x][1] + (alpha) * src_img[y][x][1]
    #        map_result[y][x][2] = (1-alpha) * map_result[y][x][2] + (alpha) * src_img[y][x][2]

    #cv2.imshow('map result', map_result)
   
    #center = src_face['position']['nose']
    #x = center['x'] * src_img_width / 100
    #y = center['y'] * src_img_height / 100
    #center = (int(x), int(y))
    center = (map_result.shape[0]/2, map_result.shape[1]/2)
    map_result = cv2.seamlessClone(src_img, map_result, extract_mask, center, flags=cv2.NORMAL_CLONE)

    cv2.imshow('merge', map_result)

    imap_matrix = cv2.invertAffineTransform(map_matrix)
    print map_result.shape
    print imap_matrix
    final = cv2.warpAffine(map_result, imap_matrix, dsize=(dst_img.shape[0:2]))
    cv2.imshow('final.png', final)
    cv2.imwrite(src_name+dst_name+'final.png', final)

    cv2.waitKey(0)
