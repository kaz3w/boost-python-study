#!/usr/bin/python
import mylib_sample
import numpy as np
import cv2
from PIL import Image
import matplotlib.pyplot as plt
import threading
import Queue
import time
import concurrent.futures
from concurrent.futures import ProcessPoolExecutor, as_completed

#####################################################################

import multiprocessing.managers as m

class myProxyManager(m.BaseManager):
	pass


class mySharedClass:
	def __init__(self):
		self.shared = dict()

	def set(self, **kwargs):
		for key,value in kwargs.items():
			self.shared[key] = value
	
	def get(self, *args):
		return {key: self.shared[key] for key in args} if args else self.shared

myProxyManager.register("mySharedClass", mySharedClass )


# myProxyManager.start()
# myProxyManager.mySharedClass.set( "write_index",  0 )
# myProxyManager.mySharedClass.set( "read_index", 0 )


#####################################################################

g_width = 640
g_height = 480
g_fps = 30

#####################################################################

rgb_array = np.zeros(g_width * g_height * 3, dtype=np.int8)
rgb_array = rgb_array.reshape( g_height, g_width, 3 )

end_flag = False

# q = Queue.Queue(0)

write_index = 0
read_index = 0


buf_size = 10

# lock = threading.Lock()

#####################################################################

def my_uvc_test_pre_cb_func(rBuffer):
	print("[Python] UVC PRE (state:pre-process)")

#####################################################################

def my_uvc_test_post_cb_func(rBuffer):
	global end_flag

	print("[Python] UVC POST (state:post-process)")
	end_flag = True
	# while True:
	# 	try:
	# 		q.task_done()
	# 	except ValueError as e:
	# 		return

#####################################################################

def my_uvc_test_notify_cb_func(data):
	global write_index

	data = data.reshape( g_height, g_width ,3 )
	print("Write {}({})").format( write_index % buf_size, write_index )
	write_index = write_index + 1
	# q.put(data)

#####################################################################

def myShowImageThread(read_index, write_index):
	# global read_index
	# global write_index
	global end_flag

	print("Read {} ({})").format(  read_index % buf_size, read_index )

	while not end_flag:
		if read_index <= write_index:
			print("Read {}({}) late:{}").format(  read_index % buf_size, read_index, write_index-read_index )
			read_index = read_index + 1
		else:
			print("Skip: R:{} W:{} late:{}").format(  read_index, write_index, write_index-read_index )
		
		time.sleep(0.01)

	# 	# if read_index <= write_index:
	# 	# 	print("Read {}({}) late:{}").format(  read_index % buf_size, read_index, write_index-read_index )
	# 	# 	read_index = read_index + 1
	# 	# else:
	# 	# 	print("XX")

	# print("====================")

	return "Complete Show"


		# img = q.get().reshape(g_height,g_width,3)
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
	global rgb_array
	inject = mylib_sample.myUvcInject()
	inject.set_pre_callback( my_uvc_test_pre_cb_func, inject  )
	inject.set_post_callback( my_uvc_test_post_cb_func, inject  )
	inject.execute( my_uvc_test_notify_cb_func, rgb_array, inject_time, w, h, fps )
	return "Complete Injection"

#####################################################################

def main():
	    with concurrent.futures.ProcessPoolExecutor() as executor:
			all_process = []

			global end_flag
			global shared
			global read_index
			global write_index

			end_flag = False

			keep_time = 20
			job = executor.submit(myInjectThread, keep_time, g_width, g_height, g_fps )
			all_process.append(job)

			show = executor.submit(myShowImageThread, read_index, write_index )
			all_process.append(show)

			for job in as_completed( all_process ):
				print( job.result())

			# inject_thread = threading.Thread( target=myInjectThread, 
			# 									args=(keep_time, g_width, g_height, g_fps))
			# inject_thread.start()


if __name__ == "__main__":
	main()