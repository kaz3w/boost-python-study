#!/usr/bin/python

import mylib_sample
import numpy as np
import cv2
from PIL import Image
import matplotlib.pyplot as plt
import threading
import Queue

#####################################################################

rgb_array = np.zeros(480*640*3, dtype=np.int8)
rgb_array = rgb_array.reshape(480,640,3)
end_flag = False

q = Queue.Queue(0)

#####################################################################

def my_uvc_test_pre_cb_func(rBuffer):
	print("[Python] UVC PRE (state:pre-process)")

#####################################################################

def my_uvc_test_post_cb_func(rBuffer):
	print("[Python] UVC POST (state:post-process)")
	end_flag = True
	while True:
		try:
			q.task_done()
		except ValueError as e:
			return

#####################################################################

def my_uvc_test_notify_cb_func(data):
	print("[Python] UVC Notify (state:run)")
	q.put(data.reshape(480,640,3))

#####################################################################

def myShowImageThread():

	plt.ion()

	while True:
		img = q.get()
		if img.ndim == 3:
			rgb = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
			plt.imshow(rgb)

		elif img.ndim == 2:
			plt.imshow(img, cmap=plt.cm.gray)

		try:
			q.task_done()
		except ValueError as e:
			return
		
		# pythonplt.xticks([]), plt.yticks([])  # to hide tick values on X and Y axis
		print("[Python] UVC get from QUEUE (state:run)")
		# plt.pause(.03)
		plt.show()

#####################################################################

def myInjectThread():
   # execute only if run as a script
	inject = mylib_sample.myUvcInject()
	inject.set_pre_callback( my_uvc_test_pre_cb_func, inject  )
	inject.set_post_callback( my_uvc_test_post_cb_func, inject  )
	inject.execute( my_uvc_test_notify_cb_func, rgb_array, 20 )

#####################################################################


if __name__ == "__main__":

	show_thread = threading.Thread( target=myShowImageThread, args=())
	show_thread.start()

	inject_thread = threading.Thread( target=myInjectThread, args=())
	inject_thread.start()

	# while True:
	# 	img = q.get()
	# 	if img.ndim == 3:
	# 		rgb = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
	# 		plt.imshow(rgb)

	# 	elif img.ndim == 2:
	# 		plt.imshow(img, cmap=plt.cm.gray)

	# 	try:
	# 		q.task_done()
	# 	except ValueError as e:
	# 		pass
		
	# 	# pythonplt.xticks([]), plt.yticks([])  # to hide tick values on X and Y axis
	# 	print("[Python] UVC get from QUEUE (state:run)")
	# 	plt.pause(.01)
	# 	# plt.show()


    # execute only if run as a script
	# inject = mylib_sample.myUvcInject()
	# inject.set_pre_callback( my_uvc_test_pre_cb_func, inject  )
	# inject.set_post_callback( my_uvc_test_post_cb_func, inject  )
	# inject.execute( my_uvc_test_notify_cb_func, rgb_array, 20 )

	inject_thread.join()
	q.join()
