

import sys
import os
import cv2 

from faceinfo import FaceInfo, FacePose, FaceLandmark
from facepp import API, File, APIError
from faceposebin import FacePoseBin, FacePoseBinDataFile

# please don't copy this
API_KEY = 'bf7eae5ed9cf280218450523049d5f94'
API_SECRET = 'o6SeKJTnaoczTb-j6PBEGXvkiVz2hp71'
api = API(API_KEY, API_SECRET)

def distance_by_pose(p1, p2):
		d = (p1.yaw-p2.yaw) ** 2 + (p1.pitch-p2.pitch) ** 2 + (p1.roll-p2.roll)**2
		return d

def distance_by_eye(l1, l2):
	d1 = (l1.eye_ll.x-l1.eye_rr.x) ** 2 + (l1.eye_ll.y - l1.eye_rr.y) ** 2
	d2 = (l2.eye_ll.x-l2.eye_rr.x) ** 2 + (l2.eye_ll.y - l2.eye_rr.y) ** 2
	return abs(d1-d2)

def compare_by_faceinfo(i1,i2,cur_face_info):
	#print cur_face_info.pose
	d1 = distance_by_pose(i1.pose, cur_face_info.pose)
	d2 = distance_by_pose(i2.pose, cur_face_info.pose)
	#print d1, d2, d1 > d2
	if abs(d1-d2) < 1e-6:
		eye_d1 = distance_by_eye(i1.landmark, cur_face_info.landmark)
		eye_d2 = distance_by_eye(i2.landmark, cur_face_info.landmark)
		return int(eye_d1 - eye_d2)
	else:
		return int(d1 - d2)

class FaceRank:
	def __init__(self, info, datafile):
		self.cur_face_info = info
		self.datafile = datafile

	def rank(self):
		face_posebin_id = self.cur_face_info.pose_bin_id

		faceinfos = [] # just append the face with same posebin_id
		for load_data in self.datafile.load():
			faceinfo = FaceInfo()
			faceinfo.parse(load_data)
			if faceinfo.pose_bin_id == face_posebin_id:
				faceinfos.append(faceinfo)

		print "there're %d number of images in the library could match posebin" % len(faceinfos)
		print "finding the most match function"

		# first sort by matching the yaw, pitch and roll
		# and then sort by the distance between eyes
		images = []
		faceinfos.sort(lambda x, y: compare_by_faceinfo(x,y,self.cur_face_info))
		return faceinfos

if __name__ == '__main__':
	if len(sys.argv) <= 1:
		print "usage: %s <image>" % sys.argv[0]
		exit(1)

	# first detect the new image:
	img_name = sys.argv[1]
	img = cv2.imread(img_name)

	dummybin = FacePoseBin()
	datafile = FacePoseBinDataFile('../datafile.txt')
	print datafile
	rst = api.detection.detect(img = File(img_name), attribute='pose')
	img_width = rst['img_width']
	img_height = rst['img_height']
	for face in rst['face']:
		face_id = face['face_id']
		landmark = api.detection.landmark(face_id = face_id, type='25p')
		pose = face['attribute']['pose']
		face_pose = FacePose(pose)
		face_landmark = FaceLandmark(landmark['result'][0]['landmark'], img_width, img_height)

		cur_face_info = FaceInfo()
		cur_face_info.pose = face_pose
		cur_face_info.landmark = face_landmark

		face_posebin_id = dummybin.get_pose_bin_id(face_pose.yaw, face_pose.pitch)
		print face_id
		print face_pose
		print face_landmark
		print 'current face has posebin id %d' % face_posebin_id
		cur_face_info.pose_bin_id = face_posebin_id

		facerank = FaceRank(cur_face_info, datafile)
		faceinfos = facerank.rank()

		print "found and sorted %d faces" % len(faceinfos)