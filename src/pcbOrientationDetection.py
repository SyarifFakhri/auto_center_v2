import numpy as np
import cv2
import time
from sklearn.svm import LinearSVC
from sklearn.preprocessing import StandardScaler
from sklearn.model_selection import train_test_split
from skimage.feature import hog
from pathlib import Path
import os
import pickle
from tinydb import TinyDB, Query


class PcbDetector():
	def __init__(self, settings,currentCameraType):
		self.cap = cv2.VideoCapture(1)
		self.classifierPath = '../assets/classifier'
		self.scalerPath = "../assets/scaler"
		self.classifier = None

		# Define parameters for feature extraction
		self.color_space = 'LUV'  # Can be RGB, HSV, LUV, HLS, YUV, YCrCb
		self.orient = 8  # HOG orientations
		self.pix_per_cell = 12  # HOG pixels per cell
		self.cell_per_block = 2  # HOG cells per block
		self.hog_channel = 0  # Can be 0, 1, 2, or "ALL"
		self.spatial_size = (32, 32)  # Spatial binning dimensions
		self.hist_bins = 64  # Number of histogram bins
		self.spatial_feat = True  # Spatial features on or off
		self.hist_feat = True  # Histogram features on or off
		self.hog_feat = True  # HOG features on or off

		self.x = settings['ai_roi_x']
		self.y = settings['ai_roi_y']
		self.w = settings['ai_roi_w']
		self.h = settings['ai_roi_h']

		self.picScale = 1.5

		self.rootPath = '../assets/test'# + currentCameraType

	def get_hog_features(self,img, orient, pix_per_cell, cell_per_block, vis=False, feature_vec=True):
		if vis == True:  # Call with two outputs if vis==True to visualize the HOG
			features, hog_image = hog(img, orientations=orient,
						  pixels_per_cell=(pix_per_cell, pix_per_cell),
						  cells_per_block=(cell_per_block, cell_per_block),
						  transform_sqrt=True, feature_vector=feature_vec)
			return features, hog_image
		else:  # Otherwise call with one output
			features = hog(img, orientations=orient,
				       pixels_per_cell=(pix_per_cell, pix_per_cell),
				       cells_per_block=(cell_per_block, cell_per_block),
				       transform_sqrt=True,
				       feature_vector=feature_vec)
			return features

	# Define a function to compute binned color features
	def bin_spatial(self,img, size=(16, 16)):
		return cv2.resize(img, size).ravel()

	# Define a function to compute color histogram features
	def color_hist(self,img, nbins=32):
		ch1 = np.histogram(img[:, :, 0], bins=nbins, range=(0, 256))[0]  # We need only the histogram, no bins edges
		ch2 = np.histogram(img[:, :, 1], bins=nbins, range=(0, 256))[0]
		ch3 = np.histogram(img[:, :, 2], bins=nbins, range=(0, 256))[0]
		hist = np.hstack((ch1, ch2, ch3))
		return hist

	# Define a function to extract features from a list of images
	def img_features(self,feature_image, spatial_feat, hist_feat, hog_feat, hist_bins, orient,
			 pix_per_cell, cell_per_block, hog_channel):
		file_features = []
		if spatial_feat == True:
			spatial_features = self.bin_spatial(feature_image, size=self.spatial_size)
			# print 'spat', spatial_features.shape
			file_features.append(spatial_features)
		if hist_feat == True:
			# Apply color_hist()
			hist_features = self.color_hist(feature_image, nbins=hist_bins)
			# print 'hist', hist_features.shape
			file_features.append(hist_features)
		if hog_feat == True:
			# Call get_hog_features() with vis=False, feature_vec=True
			if hog_channel == 'ALL':
				hog_features = []
				for channel in range(feature_image.shape[2]):
					hog_features.append(self.get_hog_features(feature_image[:, :, channel],
									     orient, pix_per_cell, cell_per_block,
									     vis=False, feature_vec=True))
					hog_features = np.ravel(hog_features)
			else:
				feature_image = cv2.cvtColor(feature_image, cv2.COLOR_LUV2RGB)
				feature_image = cv2.cvtColor(feature_image, cv2.COLOR_RGB2GRAY)
				hog_features = self.get_hog_features(feature_image[:, :], orient,
								pix_per_cell, cell_per_block, vis=False, feature_vec=True)
			# print 'hog', hog_features.shape
			# Append the new feature vector to the features list
			file_features.append(hog_features)
		return file_features

	def extract_features(self,imgs, color_space='RGB', spatial_size=(32, 32),
			     hist_bins=32, orient=9,
			     pix_per_cell=8, cell_per_block=2, hog_channel=0,
			     spatial_feat=True, hist_feat=True, hog_feat=True):
		# Create a list to append feature vectors to
		features = []
		# Iterate through the list of images
		for file_p in imgs:
			file_features = []
			print(file_p)
			image = cv2.imread(str(file_p))  # Read in each imageone by one
			image = cv2.resize(image, (128, 128))
			# apply color conversion if other than 'RGB'
			if color_space != 'RGB':
				if color_space == 'HSV':
					feature_image = cv2.cvtColor(image, cv2.COLOR_RGB2HSV)
				elif color_space == 'LUV':
					feature_image = cv2.cvtColor(image, cv2.COLOR_RGB2LUV)
				elif color_space == 'HLS':
					feature_image = cv2.cvtColor(image, cv2.COLOR_RGB2HLS)
				elif color_space == 'YUV':
					feature_image = cv2.cvtColor(image, cv2.COLOR_RGB2YUV)
				elif color_space == 'YCrCb':
					feature_image = cv2.cvtColor(image, cv2.COLOR_RGB2YCrCb)
			else:
				feature_image = np.copy(image)
			file_features = self.img_features(feature_image, spatial_feat, hist_feat, hog_feat, hist_bins, orient,
						     pix_per_cell, cell_per_block, hog_channel)
			features.append(np.concatenate(file_features))
		return features  # Return list of feature vectors

	def single_img_features(self,img, color_space='RGB', spatial_size=(32, 32),
				hist_bins=32, orient=9,
				pix_per_cell=8, cell_per_block=2, hog_channel=0,
				spatial_feat=True, hist_feat=True, hog_feat=True):
		# 1) Define an empty list to receive features
		img_features = []
		# 2) Apply color conversion if other than 'RGB'
		if color_space != 'RGB':
			if color_space == 'HSV':
				feature_image = cv2.cvtColor(img, cv2.COLOR_RGB2HSV)
			elif color_space == 'LUV':
				feature_image = cv2.cvtColor(img, cv2.COLOR_RGB2LUV)
			elif color_space == 'HLS':
				feature_image = cv2.cvtColor(img, cv2.COLOR_RGB2HLS)
			elif color_space == 'YUV':
				feature_image = cv2.cvtColor(img, cv2.COLOR_RGB2YUV)
			elif color_space == 'YCrCb':
				feature_image = cv2.cvtColor(img, cv2.COLOR_RGB2YCrCb)
		else:
			feature_image = np.copy(img)
		# 3) Compute spatial features if flag is set
		if spatial_feat == True:
			spatial_features = self.bin_spatial(feature_image, size=spatial_size)
			# 4) Append features to list
			img_features.append(spatial_features)
		# 5) Compute histogram features if flag is set
		if hist_feat == True:
			hist_features = self.color_hist(feature_image, nbins=hist_bins)
			# 6) Append features to list
			img_features.append(hist_features)
		# 7) Compute HOG features if flag is set
		if hog_feat == True:
			if hog_channel == 'ALL':
				hog_features = []
				for channel in range(feature_image.shape[2]):
					hog_features.extend(self.get_hog_features(feature_image[:, :, channel],
									     orient, pix_per_cell, cell_per_block,
									     vis=False, feature_vec=True))
			else:
				hog_features = self.get_hog_features(feature_image[:, :, hog_channel], orient,
								pix_per_cell, cell_per_block, vis=False, feature_vec=True)
			# 8) Append features to list
			img_features.append(hog_features)
		# 9) Return concatenated array of features
		return np.concatenate(img_features)

	def saveTrainingImages(self):
		upCounter = 0
		downCounter = 0
		leftCounter = 0
		rightCounter = 0

		while True:
			ret, frame = self.cap.read()
			picWidth = int(640 * self.picScale)
			picHeight = int(480 * self.picScale)
			frame = cv2.resize(frame,(picWidth, picHeight))
			x = self.x
			y = self.y
			w = self.w
			h = self.h
			frame = frame[y:y+h, x:x+w]
			if ret:
				cv2.imshow("frame", frame)
				key = cv2.waitKey(1)
				if key == ord('w'):
					saveLoc = os.path.join(self.rootPath, '/up/up_' + str(upCounter) + '.jpg')
					# print("Saved" + saveLoc)
					upCounter += 1
					cv2.imwrite(saveLoc, frame)
				elif key == ord('a'):
					saveLoc = os.path.join(self.rootPath, '/left/left_' + str(leftCounter) + '.jpg')
					# print("Saved" + saveLoc)
					leftCounter += 1
					cv2.imwrite(saveLoc, frame)
				elif key == ord('s'):
					saveLoc = os.path.join(self.rootPath, '/down/down_' + str(downCounter) + '.jpg')
					# print("Saved" + saveLoc)
					downCounter += 1
					cv2.imwrite(saveLoc, frame)
				elif key == ord('d'):
					saveLoc = os.path.join(self.rootPath, '/right/right_' + str(rightCounter) + '.jpg')
					# print("Saved" + saveLoc)
					rightCounter += 1
					cv2.imwrite(saveLoc, frame)
			print("UP:", upCounter, end=' ')
			print("DOWN:", downCounter, end=' ')
			print("LEFT:", leftCounter, end=' ')
			print("RIGHT:", rightCounter)

	def loadModel(self):
		self.classifier = pickle.load(open(self.classifierPath,'rb'))
		self.X_scaler = pickle.load(open(self.scalerPath, 'rb'))

	def runInferenceSingleImage(self, frame):
		if self.classifier is None:
			assert 0, "Model not loaded. Ensure that you have loaded a model first. Maybe run loadModel()?"
		x = self.x
		y = self.y
		w = self.w
		h = self.h
		picWidth = int(640 * self.picScale)
		picHeight = int(480 * self.picScale)
		frame = cv2.resize(frame,(picWidth, picHeight))
		frame = frame[y:y + h, x:x + w]
		frame = cv2.resize(frame, (128, 128))
		features = self.single_img_features(
			frame, color_space=self.color_space,
			spatial_size=self.spatial_size, hist_bins=self.hist_bins,
			orient=self.orient, pix_per_cell=self.pix_per_cell,
			cell_per_block=self.cell_per_block,
			hog_channel=self.hog_channel, spatial_feat=self.spatial_feat,
			hist_feat=self.hist_feat, hog_feat=self.hog_feat)
		test_features = self.X_scaler.transform(np.array(features).reshape(1, -1))
		prediction = self.classifier.predict(test_features)
		lbls = ['up', 'down', 'left', 'right']
		return prediction, lbls

	def runInference(self):
		if self.classifier is None:
			assert 0, "Model not loaded. Ensure that you have loaded a model first."

		while True:
			ret, frame = self.cap.read()
			x = self.x
			y = self.y
			w = self.w
			h = self.h
			picWidth = int(640 * self.picScale)
			picHeight = int(480 * self.picScale)
			frame = cv2.resize(frame,(picWidth, picHeight))
			original_frame = frame.copy()
			frame = frame[y:y + h, x:x + w]
			roi = frame.copy()
			frame = cv2.resize(frame, (128, 128))
			features = self.single_img_features(
				frame, color_space=self.color_space,
				spatial_size=self.spatial_size, hist_bins=self.hist_bins,
				orient=self.orient, pix_per_cell=self.pix_per_cell,
				cell_per_block=self.cell_per_block,
				hog_channel=self.hog_channel, spatial_feat=self.spatial_feat,
				hist_feat=self.hist_feat, hog_feat=self.hog_feat)
			test_features = self.X_scaler.transform(np.array(features).reshape(1, -1))

			prediction = self.classifier.predict(test_features)
			lbls = ['up', 'down', 'left', 'right']
			print(lbls[prediction[0]])

			cv2.imshow("frame", original_frame)
			cv2.imshow("roi", roi)
			cv2.waitKey(1)

	def runTraining(self):
		image_dir = Path(self.rootPath)
		folders = [directory for directory in image_dir.iterdir() if directory.is_dir()]
		categories = [fo.name for fo in folders]
		print("categories: ", categories)
		up = []
		down = []
		left = []
		right = []

		for i, direc in enumerate(folders):
			for file in direc.iterdir():
				if str(direc) == os.path.join(image_dir, 'up'):
					up.append(file)
				elif str(direc) == os.path.join(image_dir, 'down'):
					down.append(file)
				elif str(direc) == os.path.join(image_dir, 'left'):
					left.append(file)
				elif str(direc) == os.path.join(image_dir, 'right'):
					right.append(file)

		color_space = self.color_space  # Can be RGB, HSV, LUV, HLS, YUV, YCrCb
		orient = self.orient  # HOG orientations
		pix_per_cell = self.pix_per_cell  # HOG pixels per cell
		cell_per_block = self.cell_per_block  # HOG cells per block
		hog_channel = self.hog_channel  # Can be 0, 1, 2, or "ALL"
		spatial_size = self.spatial_size  # Spatial binning dimensions
		hist_bins = self.hist_bins  # Number of histogram bins
		spatial_feat = self.spatial_feat # Spatial features on or off
		hist_feat = self.hist_feat  # Histogram features on or off
		hog_feat = self.hog_feat # HOG features on or off

		up_features = self.extract_features(up, color_space=color_space,
					       spatial_size=spatial_size, hist_bins=hist_bins,
					       orient=orient, pix_per_cell=pix_per_cell,
					       cell_per_block=cell_per_block,
					       hog_channel=hog_channel, spatial_feat=spatial_feat,
					       hist_feat=hist_feat, hog_feat=hog_feat)

		down_features = self.extract_features(down, color_space=color_space,
						 spatial_size=spatial_size, hist_bins=hist_bins,
						 orient=orient, pix_per_cell=pix_per_cell,
						 cell_per_block=cell_per_block,
						 hog_channel=hog_channel, spatial_feat=spatial_feat,
						 hist_feat=hist_feat, hog_feat=hog_feat)

		left_features = self.extract_features(left, color_space=color_space,
						 spatial_size=spatial_size, hist_bins=hist_bins,
						 orient=orient, pix_per_cell=pix_per_cell,
						 cell_per_block=cell_per_block,
						 hog_channel=hog_channel, spatial_feat=spatial_feat,
						 hist_feat=hist_feat, hog_feat=hog_feat)

		right_features = self.extract_features(right, color_space=color_space,
						  spatial_size=spatial_size, hist_bins=hist_bins,
						  orient=orient, pix_per_cell=pix_per_cell,
						  cell_per_block=cell_per_block,
						  hog_channel=hog_channel, spatial_feat=spatial_feat,
						  hist_feat=hist_feat, hog_feat=hog_feat)
		X = np.vstack((up_features, down_features, left_features, right_features)).astype(np.float64)
		# print(X)
		self.X_scaler = StandardScaler().fit(X)  # Fit a per-column scaler
		scaled_X = self.X_scaler.transform(X)  # Apply the scaler to X

		up_label = np.full((1, len(up_features)), 0)[0]
		down_label = np.full((1, len(down_features)), 1)[0]
		left_label = np.full((1, len(left_features)), 2)[0]
		right_label = np.full((1, len(right_features)), 3)[0]
		y = np.hstack((up_label, down_label, left_label, right_label))  # Define the labels vector

		# Split up data into randomized training and test sets
		X_train, X_test, y_train, y_test = train_test_split(scaled_X, y, test_size=0.2, random_state=22)

		print('Using:', orient, 'orientations', pix_per_cell,
		      'pixels per cell and', cell_per_block, 'cells per block')
		print('Feature vector length:', len(X_train[0]))
		svc = LinearSVC(loss='hinge')  # Use a linear SVC
		t = time.time()  # Check the training time for the SVC
		svc.fit(X_train, y_train)  # Train the classifier
		t2 = time.time()
		print(round(t2 - t, 2), 'Seconds to train SVC...')
		print('Test Accuracy of SVC = ', round(svc.score(X_test, y_test), 4))  # Check the score of the SVC
		pickle.dump(svc, open(self.classifierPath, 'wb'))
		pickle.dump(self.X_scaler, open(self.scalerPath, 'wb'))
		self.classifier = svc

if __name__ == '__main__':
	settingsConfig = TinyDB('settings.json')
	settingsConfigField = Query()
	currentCamera = 'cp1p'
	picSettings = settingsConfig.get(settingsConfigField.title == 'settingsConfig')
	detector = PcbDetector(picSettings[currentCamera],currentCamera)

	###SAVE TRAINING DATA###
	#detector.saveTrainingImages()

	###RUN TRAINING###
	#detector.runTraining()

	###RUN INFERENCE###
	detector.loadModel()
	detector.runInference()

