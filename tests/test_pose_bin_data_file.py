
import sys
sys.path.append('.')

from faceproc import FaceInfo
from faceposebin import FacePoseBinDataFile

if __name__ == '__main__':
	if len(sys.argv) <= 1:
		print "Usage: %s <posebin datafile>" % sys.argv[0]
		exit(1)
	data_file = FacePoseBinDataFile(sys.argv[1])
	load_results = data_file.load()

	for load_result in load_results:
		face_info = FaceInfo()
		face_info.parse(load_result)
		print face_info