class FacePoint:
	def __init__(self, coord=None, w=None, h=None, x=None, y=None):
		if coord != None:
			self.x = float(coord['x']) * w / 100
			self.y = float(coord['y']) * h / 100
		else:
			self.x = x
			self.y = y
	def transform(self, x, y):
		if self.x <= x or self.y <= y:
			print "Something Wrong with the input (%f %f)" % (x, y)
			exit(1)
		self.x = self.x - x
		self.y = self.y - y
	def avg(self, point):
		self.x = (self.x + point.x)/2
		self.y = (self.y + point.y)/2
	def array(self):
		return [self.x, self.y]
	def __str__(self):
		return "%.2f %.2f" % (self.x, self.y)

class FaceLandmark:
	# dict is landmark['result'][0]['landmark']
	def __init__(self, landmark_dict=None, w=None, h=None, all_points=None):
		if landmark_dict != None:
			self.eye_ll 	= FacePoint(landmark_dict['left_eye_left_corner'], w, h)
			self.eye_lr 	= FacePoint(landmark_dict['left_eye_right_corner'], w, h)
			self.eye_rl 	= FacePoint(landmark_dict['right_eye_left_corner'], w, h)
			self.eye_rr 	= FacePoint(landmark_dict['right_eye_right_corner'], w, h)
			self.mouth_l 	= FacePoint(landmark_dict['mouth_left_corner'], w, h)
			self.mouth_r 	= FacePoint(landmark_dict['mouth_right_corner'], w, h)
		else:
			self.eye_ll 	= FacePoint(x=all_points[ 0], y=all_points[ 1])
			self.eye_lr 	= FacePoint(x=all_points[ 2], y=all_points[ 3])
			self.eye_rl 	= FacePoint(x=all_points[ 4], y=all_points[ 5])
			self.eye_rr 	= FacePoint(x=all_points[ 6], y=all_points[ 7])
			self.mouth_l 	= FacePoint(x=all_points[ 8], y=all_points[ 9])
			self.mouth_r 	= FacePoint(x=all_points[10], y=all_points[11])

	def transform(self, x, y):
		for idx in xrange(len(self.all_points)):
			print self.all_points[idx],
			self.all_points[idx].transform(x, y)
			print self.all_points[idx]
	def avg(self, landmark):
		self.eye_ll.avg(landmark.eye_ll )
		self.eye_lr.avg(landmark.eye_lr )
		self.eye_rl.avg(landmark.eye_rl )
		self.eye_rr.avg(landmark.eye_rr )
		self.mouth_l.avg(landmark.mouth_l)
		self.mouth_r.avg(landmark.mouth_r)
	def __str__(self):
		s = []
		for (k, v) in sorted(self.__dict__.items()):
			s.append("%s: %s" % (k, str(v)))
		return " ".join(s)

	@property
	def all_points(self):
	    return (self.eye_ll, self.eye_lr, self.eye_rl, self.eye_rr, self.mouth_l, self.mouth_r)
	

class FacePose:
	# pose_dict = pose_dict['attribute']['pose']
	def __init__(self, pose_dict=None, pose_list=None):
		if pose_dict != None:
			self.yaw = pose_dict['yaw_angle']['value']
			self.pitch = pose_dict['pitch_angle']['value']
			self.roll = pose_dict['roll_angle']['value']
		else:
			self.yaw = pose_list[0]
			self.pitch = pose_list[1]
			self.roll = pose_list[2]
	def __str__(self):
		return "yaw=%.2f pitch=%.2f roll=%.2f" % (self.yaw, self.pitch, self.roll)

class FaceInfo:
	def __init__(self, name=None, pose_bin_id=None, pose=None, landmark=None):
		self.name = name
		self.pose_bin_id = pose_bin_id
		self.pose = pose
		self.landmark = landmark
	def __str__(self):
		return "\nFace Id:\t" + str(self.name) + "\nPose Bin Id:\t" + str(self.pose_bin_id) + "\nPose:\t\t" + str(self.pose) + "\nLandmark:\t" + str(self.landmark)
	def parse(self, l):
		self.pose_bin_id = int(l[0])
		self.name = l[1]
		self.pose = FacePose(pose_list=map(float, l[2:5]))
		self.landmark = FaceLandmark(all_points=map(float, l[5:]))
	@property
	def img_path(self):
		return str(self.pose_bin_id) + '/' + self.name + '.png'
