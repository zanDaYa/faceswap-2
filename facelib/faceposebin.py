
import os
import sys

import matplotlib.pyplot as plt
#from faceproc import FaceInfo

POSE_BIN_COL_STEPS = 5
POSE_BIN_ROW_STEPS = 3
POSE_BIN_COL_RANGE = (-25, 25)
POSE_BIN_ROW_RANGE = (-15, 15)

class FacePoseBinDataFile:
	def __init__(self, data_file):
		self.path = data_file
	def load(self):
		data_file_handler = open(self.path, 'r')
		load_result = []
		for line in data_file_handler.readlines():
			load_result.append(line.strip().split(" "))
			#FaceInfo(face_id, pose_bin_id, pose, landmark)
		return load_result

# FacePoseBin is a class that deal with the low-level operations 
# on the pose bin directory, including:
# 1. Image save: give yaw and pitch, this class could push image
# inside the corresponding bin
# 2. Image name list retrieve: give a bin name, return a list of 
# image names
# 3. Init, clean, ...
class FacePoseBin:
	def __init__(self, path=None):
		self.path = path # this path is to pose bin
		#self.data_file = FacePoseBinDataFile(self.data_file_path())
		self.num_pose_bins = POSE_BIN_COL_STEPS * POSE_BIN_ROW_STEPS

	def data_file_path(self):
		return self.path + '/datafile.txt'

	def bin2path(self, pose_bin_id):
		if pose_bin_id > self.num_pose_bins or pose_bin_id < 0:
			print "invalid bin id:", pose_bin_id
			return None
		return self.path + '/' + str(pose_bin_id)

	def clear(self):
		if os.path.isdir(self.path) == False:
			print "pose bin dir path %s not exists ..." % self.path
			return
		for root, dirs, files in os.walk(self.path):
			for img_file in files:
				os.remove(root+'/'+img_file)

	def clear_bin(self, pose_bin_id):
		pose_bin_path = self.bin2path(pose_bin_id)
		if pose_bin_id == None:
			return 
		if os.path.isdir(pose_bin_path) == False:
			for root, dirs, files in os.walk(self.path):
				for dir_name in dirs: os.remove(root+'/'+dir_name)
				for file_name in files: os.remove(root+'/'+file_name)

	def init(self):
		self.clear() # clean the pose bin path first
		if os.path.isdir(self.path) == False:
			print "pose bin dir path %s not exists, creating one ..." % self.path
			os.makedirs(self.path)
		for i in xrange(self.num_pose_bins+1):
			bin_path = self.bin2path(i)
			if os.path.isdir(bin_path) == False:
				print "pose bin %d doesn't have a dir path, creating one ..." % i
				os.makedirs(bin_path)
			else:
				self.clear_bin(i)
	def angle2id(self, angle, range, steps):
		if angle < range[0] or angle >= range[1]:
			return 0
		return int((angle-range[0])/(float(range[1]-range[0])/steps) + 1)
	def get_pose_bin_id(self, yaw, pitch):
		col_id = self.angle2id(yaw, POSE_BIN_COL_RANGE, POSE_BIN_COL_STEPS)
		row_id = self.angle2id(pitch, POSE_BIN_ROW_RANGE, POSE_BIN_ROW_STEPS)
		if col_id == 0 or row_id == 0:
			return 0
		return col_id + (row_id-1) * POSE_BIN_COL_STEPS

	def save(self, face_img, face_id, pose, landmark, name):
		# save the face image
		pose_bin_id = self.get_pose_bin_id(pose.yaw, pose.pitch)
		#print "Yaw=%d Pitch=%d Bin Name=%d" % (int(pose.yaw), int(pose.pitch), pose_bin_id)
		save_path = self.bin2path(pose_bin_id) + '/' + name + '.png'
		#print "saving image to path:", save_path
		plt.imsave(save_path, face_img)
		# save the data file
		# this data file could be optimized, by sorting the face_id
		print "saving image data file to path:", self.data_file_path()

		# here will change what we want to store
		# basically, we need the following data for ranking
		# 1. yaw, pitch and roll: yaw and pitch should match first, 
		# and then roll.
		# 2. distance between eyes: to estimate the resolution
		# 3. and also I think I need the name, but this could be provided by
		# using the image file name
		data_file_handler = open(self.data_file_path(), 'a')
		print >>data_file_handler, "%d"%pose_bin_id,
		print >>data_file_handler, "%s"%name,
		print >>data_file_handler, "%d %d %d"%(pose.yaw, pose.pitch, pose.roll),
		for point in landmark.all_points:
			print >>data_file_handler, point,
		print >>data_file_handler, ""
		return save_path

if __name__ == '__main__':
	if len(sys.argv) <= 2:
		print "Usage: %s <posebin_dirname>" % sys.argv[0]
		exit(1)
	face_pose_bin = FacePoseBin(sys.argv[1])
	face_pose_bin.init() 
	face_pose_bin.data_file_path()
