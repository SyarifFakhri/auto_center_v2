import numpy as np
import cv2
import time
from sklearn.svm import LinearSVC
from sklearn.preprocessing import StandardScaler
from sklearn.model_selection import train_test_split
from skimage.feature import hog
from pathlib import Path

def get_hog_features(img, orient, pix_per_cell, cell_per_block, vis=False, feature_vec=True):
	if vis == True: # Call with two outputs if vis==True to visualize the HOG
		features, hog_image = hog(img, orientations=orient,
								  pixels_per_cell=(pix_per_cell, pix_per_cell),
								  cells_per_block=(cell_per_block, cell_per_block),
								  transform_sqrt=True,
								  visualise=vis, feature_vector=feature_vec)
		return features, hog_image
	else:      # Otherwise call with one output
		features = hog(img, orientations=orient,
					   pixels_per_cell=(pix_per_cell, pix_per_cell),
					   cells_per_block=(cell_per_block, cell_per_block),
					   transform_sqrt=True,
						feature_vector=feature_vec)
		return features

# Define a function to compute binned color features
def bin_spatial(img, size=(16, 16)):
	return cv2.resize(img, size).ravel()

# Define a function to compute color histogram features
def color_hist(img, nbins=32):
	ch1 = np.histogram(img[:,:,0], bins=nbins, range=(0, 256))[0]#We need only the histogram, no bins edges
	ch2 = np.histogram(img[:,:,1], bins=nbins, range=(0, 256))[0]
	ch3 = np.histogram(img[:,:,2], bins=nbins, range=(0, 256))[0]
	hist = np.hstack((ch1, ch2, ch3))
	return hist


# Define a function to extract features from a list of images
def img_features(feature_image, spatial_feat, hist_feat, hog_feat, hist_bins, orient,
						pix_per_cell, cell_per_block, hog_channel):
	file_features = []
	if spatial_feat == True:
		spatial_features = bin_spatial(feature_image, size=spatial_size)
		#print 'spat', spatial_features.shape
		file_features.append(spatial_features)
	if hist_feat == True:
		# Apply color_hist()
		hist_features = color_hist(feature_image, nbins=hist_bins)
		#print 'hist', hist_features.shape
		file_features.append(hist_features)
	if hog_feat == True:
	# Call get_hog_features() with vis=False, feature_vec=True
		if hog_channel == 'ALL':
			hog_features = []
			for channel in range(feature_image.shape[2]):
				hog_features.append(get_hog_features(feature_image[:,:,channel],
										orient, pix_per_cell, cell_per_block,
										vis=False, feature_vec=True))
				hog_features = np.ravel(hog_features)
		else:
			feature_image = cv2.cvtColor(feature_image, cv2.COLOR_LUV2RGB)
			feature_image = cv2.cvtColor(feature_image, cv2.COLOR_RGB2GRAY)
			hog_features = get_hog_features(feature_image[:,:], orient,
							pix_per_cell, cell_per_block, vis=False, feature_vec=True)
				#print 'hog', hog_features.shape
			# Append the new feature vector to the features list
		file_features.append(hog_features)
	return file_features

def single_img_features(img, color_space='RGB', spatial_size=(32, 32),
						hist_bins=32, orient=9,
						pix_per_cell=8, cell_per_block=2, hog_channel=0,
						spatial_feat=True, hist_feat=True, hog_feat=True):
	#1) Define an empty list to receive features
	img_features = []
	#2) Apply color conversion if other than 'RGB'
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
	else: feature_image = np.copy(img)
	#3) Compute spatial features if flag is set
	if spatial_feat == True:
		spatial_features = bin_spatial(feature_image, size=spatial_size)
		#4) Append features to list
		img_features.append(spatial_features)
	#5) Compute histogram features if flag is set
	if hist_feat == True:
		hist_features = color_hist(feature_image, nbins=hist_bins)
		#6) Append features to list
		img_features.append(hist_features)
	#7) Compute HOG features if flag is set
	if hog_feat == True:
		if hog_channel == 'ALL':
			hog_features = []
			for channel in range(feature_image.shape[2]):
				hog_features.extend(get_hog_features(feature_image[:,:,channel],
									orient, pix_per_cell, cell_per_block,
									vis=False, feature_vec=True))
		else:
			hog_features = get_hog_features(feature_image[:,:,hog_channel], orient,
						pix_per_cell, cell_per_block, vis=False, feature_vec=True)
		#8) Append features to list
		img_features.append(hog_features)
	#9) Return concatenated array of features
	return np.concatenate(img_features)

def extract_features(imgs, color_space='RGB', spatial_size=(32, 32),
						hist_bins=32, orient=9,
						pix_per_cell=8, cell_per_block=2, hog_channel=0,
						spatial_feat=True, hist_feat=True, hog_feat=True):
	# Create a list to append feature vectors to
	features = []
	# Iterate through the list of images
	for file_p in imgs:
		file_features = []
		print(file_p)
		image = cv2.imread(str(file_p)) # Read in each imageone by one
		image = cv2.resize(image, (128,128))
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
		else: feature_image = np.copy(image)
		file_features = img_features(feature_image, spatial_feat, hist_feat, hog_feat, hist_bins, orient,
						pix_per_cell, cell_per_block, hog_channel)
		features.append(np.concatenate(file_features))
	return features # Return list of feature vectors


# Read in cars and notcars
image_dir = Path("../assets/test")
folders = [directory for directory in image_dir.iterdir() if directory.is_dir()]
categories = [fo.name for fo in folders]
up = []
down = []
left = []
right = []

for i, direc in enumerate(folders):
	for file in direc.iterdir():
		if str(direc) == '../assets/test/up':
			up.append(file)
		elif str(direc) == '../assets/test/down':
			down.append(file)
		elif str(direc) == '../assets/test/left':
			left.append(file)
		elif str(direc) == '../assets/test/right':
			right.append(file)
## Uncomment if you need to reduce the sample size
#sample_size = 500
#cars = cars[0:sample_size]
#notcars = notcars[0:sample_size]
print(len(up))
print(len(down))

# Define parameters for feature extraction
color_space = 'LUV' # Can be RGB, HSV, LUV, HLS, YUV, YCrCb
orient = 8  # HOG orientations
pix_per_cell = 12 # HOG pixels per cell
cell_per_block = 2 # HOG cells per block
hog_channel = 0 # Can be 0, 1, 2, or "ALL"
spatial_size = (32, 32) # Spatial binning dimensions
hist_bins = 64    # Number of histogram bins
spatial_feat = True # Spatial features on or off
hist_feat = True # Histogram features on or off
hog_feat = True # HOG features on or off

up_features = extract_features(up, color_space=color_space,
						spatial_size=spatial_size, hist_bins=hist_bins,
						orient=orient, pix_per_cell=pix_per_cell,
						cell_per_block=cell_per_block,
						hog_channel=hog_channel, spatial_feat=spatial_feat,
						hist_feat=hist_feat, hog_feat=hog_feat)
# print 'up samples: ', len(car_features)
down_features = extract_features(down, color_space=color_space,
						spatial_size=spatial_size, hist_bins=hist_bins,
						orient=orient, pix_per_cell=pix_per_cell,
						cell_per_block=cell_per_block,
						hog_channel=hog_channel, spatial_feat=spatial_feat,
						hist_feat=hist_feat, hog_feat=hog_feat)

left_features = extract_features(left, color_space=color_space,
						spatial_size=spatial_size, hist_bins=hist_bins,
						orient=orient, pix_per_cell=pix_per_cell,
						cell_per_block=cell_per_block,
						hog_channel=hog_channel, spatial_feat=spatial_feat,
						hist_feat=hist_feat, hog_feat=hog_feat)

right_features = extract_features(right, color_space=color_space,
						spatial_size=spatial_size, hist_bins=hist_bins,
						orient=orient, pix_per_cell=pix_per_cell,
						cell_per_block=cell_per_block,
						hog_channel=hog_channel, spatial_feat=spatial_feat,
						hist_feat=hist_feat, hog_feat=hog_feat)
# print ('down samples: ', len(notcar_features))
X = np.vstack((up_features, down_features, left_features, right_features)).astype(np.float64)
# print(X)
X_scaler = StandardScaler().fit(X) # Fit a per-column scaler
scaled_X = X_scaler.transform(X) # Apply the scaler to X

up_label = np.full((1, len(up_features)),0)[0]
down_label = np.full((1, len(down_features)),1)[0]
left_label = np.full((1, len(left_features)),2)[0]
right_label = np.full((1, len(right_features)),3)[0]
y = np.hstack((up_label, down_label, left_label, right_label)) # Define the labels vector

# Split up data into randomized training and test sets
X_train, X_test, y_train, y_test = train_test_split(scaled_X, y, test_size=0.2, random_state=22)

print('Using:',orient,'orientations', pix_per_cell,
	'pixels per cell and', cell_per_block,'cells per block')
print('Feature vector length:', len(X_train[0]))
svc = LinearSVC(loss='hinge') # Use a linear SVC
t=time.time() # Check the training time for the SVC
svc.fit(X_train, y_train) # Train the classifier
t2 = time.time()
print(round(t2-t, 2), 'Seconds to train SVC...')
print('Test Accuracy of SVC = ', round(svc.score(X_test, y_test), 4)) # Check the score of the SVC

cap = cv2.VideoCapture(1)

while True:
	ret, frame = cap.read()
	x = 160
	y = 165
	w = 140
	h = 140
	frame = frame[y:y + h, x:x + w]
	original_frame = frame.copy()
	frame = cv2.resize(frame, (128,128))
	features = single_img_features(
		frame, color_space=color_space,
							spatial_size=spatial_size, hist_bins=hist_bins,
							orient=orient, pix_per_cell=pix_per_cell,
							cell_per_block=cell_per_block,
							hog_channel=hog_channel, spatial_feat=spatial_feat,
							hist_feat=hist_feat, hog_feat=hog_feat)
	test_features = X_scaler.transform(np.array(features).reshape(1, -1))

	prediction = svc.predict(test_features)
	lbls = ['up', 'down', 'left', 'right']
	print(lbls[prediction[0]])

	cv2.imshow("frame", original_frame)
	cv2.waitKey(1)

