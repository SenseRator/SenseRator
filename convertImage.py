import os
import cv2
import numpy as np

path = 'Data\\raw_images'

def grayscale(file_path, resize=None):
	fd = open(file_path)
	rows = 1080
	cols = 1440
	f = np.fromfile(fd, dtype=np.uint8,count=rows*cols)
	im = f.reshape((rows, cols)) #notice row, column format
	if resize != None:
		im = cv2.resize(im, dsize=resize, interpolation=cv2.INTER_AREA)

	return im
	# cv2.imshow('Test Drive', im)
	# 17 ms = 60 fps
	# cv2.waitKey(17)
	# cv2.destroyAllWindows()

