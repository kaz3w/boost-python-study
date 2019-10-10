#!/usr/bin/python
from multiprocessing import Process, Value, Array, Queue
import numpy as np
import cv2
from PIL import Image
import matplotlib.pyplot as plt
import time
import mylib_sample



#####################################################################

g_width = 320
g_height = 240
g_fps = 30

#####################################################################

rgb_array = np.zeros(g_width * g_height * 3, dtype=np.int8)
rgb_array = rgb_array.reshape( g_height, g_width, 3 )

q = Queue(0)

global read_index
read_index = Value('i', 0 )

global write_index
write_index = Value('i', 0 )

global end_flag
end_flag = Value('i', 0 )

buf_size = 10


#####################################################################

def my_uvc_test_pre_cb_func(rBuffer):
	print("[Python] UVC PRE (state:pre-process)")

#####################################################################

def my_uvc_test_post_cb_func(rBuffer):
	global end_flag

	print("[Python] UVC POST (state:post-process)")
	end_flag.value = 1

#####################################################################

def my_uvc_test_notify_cb_func(data):
	global write_index
	data = data.reshape( g_height, g_width ,3 )
	# print("RECEIVE {}({})").format( write_index.value % buf_size, write_index.value )
	write_index.value += 1
	q.put(data)

#####################################################################

def f(t):
    s1 = np.cos(2*np.pi*t)
    e1 = np.exp(-t)
    return s1 * e1

t1 = np.arange(0.0, 5.0, 0.1)
t2 = np.arange(0.0, 5.0, 0.02)
t3 = np.arange(0.0, 2.0, 0.01)

def myShowImageProc(r, w, end_flag):
	last_show_index = 0
	# plt.figure(num = 'Dst: python')

	fig, axarr = plt.subplots(2, 2, constrained_layout=True)

	axarr[0,0].set_xlabel('width (pix.)')
	axarr[0,0].set_ylabel('height (pix.)')

	axarr[0,1].plot(t1, f(t1), 'o', t2, f(t2), '-')
	axarr[0,1].set_title('subplot 1')
	axarr[0,1].set_xlabel('distance (m)')
	axarr[0,1].set_ylabel('Damped oscillation')
	fig.suptitle('Preview = received ndarray(from C++ callback)', fontsize=16)

	while not end_flag.value == 1:
		if r.value <= w.value :
			latency = w.value - r.value 
			print("R:{} W:{} Delay:{}").format( r.value, w.value, latency )
			r.value += 1

			if latency > 2:
				print("trim --->")
				for ii in range(latency-1):
					print(ii)
					q.get()
				print("---> trim")

			img = q.get().reshape(g_height,g_width,3)
			if img.ndim == 3:
				rgb = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
				axarr[0,0].imshow(rgb)
				plt.pause(0.01)
				last_show_index = w.value
			elif img.ndim == 2:
				axarr[0,0].imshow(img, cmap=plt.cm.gray)
				plt.pause(0.01)
				last_show_index = w.value


#####################################################################

def myInjectProc(inject_time, w, h, fps):
	global rgb_array
	inject = mylib_sample.myUvcInject()
	inject.set_pre_callback( my_uvc_test_pre_cb_func, inject  )
	inject.set_post_callback( my_uvc_test_post_cb_func, inject  )
	inject.execute( my_uvc_test_notify_cb_func, rgb_array, inject_time, w, h, fps )

#####################################################################

if __name__ == "__main__":

	keep_time = 300
	p = Process( target=myInjectProc, args=(keep_time, g_width, g_height, g_fps) )
	p.start()

	s = Process( target = myShowImageProc, args=(read_index, write_index, end_flag) )
	s.start()
	p.join()
	s.join()
