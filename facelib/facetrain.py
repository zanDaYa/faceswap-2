
import sys
import os

import matplotlib.pyplot as plt

from faceinfo import FaceInfo,FaceLandmark,FacePoint,FacePose
from faceproc import FaceProc
from faceposebin import FacePoseBin, FacePoseBinDataFile
from faceset import FaceSet

# This is the top level module for the training part
# will take a list of facesets(the path), and port them into one 
# posebin
class FaceTrain:
	def __init__(self, faceset_root, posebin_root):
		self.faceset = FaceSet(faceset_root)
		self.posebin = FacePoseBin(posebin_root)
		self.posebin.init()
		self.fiducial_landmark = {}

	def train(self):
		self.dropbin()
		#self.recap()
		#self.alignment()
	
	def dropbin(self):
		# start a faceproc module
		faceproc = FaceProc(self.posebin)
		#print self.faceset.imagestream
		for image in self.faceset.imagestream:
			faceproc.proc_image(image)
	
	def recap(self):
		# we have a data file for the posebin set
		# and then we read each line out
		self.fiducial_landmark = {}
		load_results = self.posebin.data_file.load()
		for load_result in load_results:
			faceinfo = FaceInfo()
			faceinfo.parse(load_result)
			id = faceinfo.pose_bin_id
			if self.fiducial_landmark.has_key(id):
				self.fiducial_landmark[id].avg(faceinfo.landmark)
			else:
				self.fiducial_landmark[id] = faceinfo.landmark

	def alignment(self):
		# transform the images selected from the data file inside 
		# the posebin
		faceproc = FaceProc(self.posebin)
		load_results = self.posebin.data_file.load()
		for load_result in load_results:
			faceinfo = FaceInfo()
			faceinfo.parse(load_result)
			path = self.posebin.path + '/' + faceinfo.img_path
			faceproc.affine_transform(path, faceinfo.landmark, self.fiducial_landmark[faceinfo.pose_bin_id])

if __name__ == '__main__':
	if len(sys.argv) <= 2:
		print "usage: %s <faseset root> <posebin root>" % sys.argv[0]
		exit(1)

	faceset_root = sys.argv[1]
	posebin_root = sys.argv[2]

	facetrain = FaceTrain(faceset_root, posebin_root)
	facetrain.train()