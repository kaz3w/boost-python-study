#!/usr/bin/python

import mylib_sample
import numpy as np
import cv2
from PIL import Image
import matplotlib.pyplot as plt
import threading
import Queue

#####################################################################

g_width = 640
g_height = 480
g_fps = 30

#####################################################################

rgb_array = np.zeros(g_width * g_height * 3, dtype=np.int8)
rgb_array = rgb_array.reshape( g_height, g_width, 3 )

end_flag = False

q = Queue.Queue(0)

write_index = 0;
read_index = 0;
buf_size = 10

# lock = threading.Lock()

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
	global write_index
	global q
	
# 	print("[Python] UVC Notify (state:run)")
	write_index = (write_index + 1) % buf_size
	print("Write {}").format( write_index )
	rgb = data
	data.reshape(480,640,3)
	q.put(rgb)

#####################################################################

def myShowImageThread():
	global read_index
	global q

# 	plt.ion()

	while True:
		read_index = (read_index+1) % buf_size
		print("Read {}").format( read_index )

		
# 		print("[Python] before GET (state:run)")
		img = q.get().reshape(g_height,g_width,3)
# 		print("[Python] after GET (state:run)")

# 		if img.ndim == 3:
# 			rgb = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
# 			plt.imshow(rgb)
# 
# 		elif img.ndim == 2:
# 			plt.imshow(img, cmap=plt.cm.gray)
# 
# 		try:
# 			q.task_done()
# 		except ValueError as e:
# 			return
	
		# pythonplt.xticks([]), plt.yticks([])  # to hide tick values on X and Y axis
# 		plt.pause(.01)
# 		plt.show()

#####################################################################

def myInjectThread(inject_time, w, h, fps):
	inject = mylib_sample.myUvcInject()
	inject.set_pre_callback( my_uvc_test_pre_cb_func, inject  )
	inject.set_post_callback( my_uvc_test_post_cb_func, inject  )
	inject.execute( my_uvc_test_notify_cb_func, rgb_array, inject_time, w, h, fps )

#####################################################################


if __name__ == "__main__":

	flag_thread = True
	
	if flag_thread:
		show_thread = threading.Thread( target = myShowImageThread, args=())
		show_thread.start()

	keep_time = 20
	inject_thread = threading.Thread( target=myInjectThread, 
										args=(keep_time, g_width, g_height, g_fps))
	inject_thread.start()

	if not flag_thread:
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
				pass
		
			# pythonplt.xticks([]), plt.yticks([])  # to hide tick values on X and Y axis
			print("[Python] UVC get from QUEUE (state:run)")
			plt.pause(.01)
			# plt.show()

    # execute only if run as a script
	# inject = mylib_sample.myUvcInject()
	# inject.set_pre_callback( my_uvc_test_pre_cb_func, inject  )
	# inject.set_post_callback( my_uvc_test_post_cb_func, inject  )
	# inject.execute( my_uvc_test_notify_cb_func, rgb_array, 20 )

	inject_thread.join()
	q.join()
