#!/usr/bin/python
import ctypes
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

rgb_array = np.zeros(g_fps * g_width * g_height * 3, dtype=np.uint8)
rgb_array = rgb_array.reshape( g_fps, g_height, g_width, 3 )

rgb_array2 = Value( (((ctypes.c_uint8 * 3) * g_width ) * g_height ) * g_fps)

q = Queue(0)

global read_index
read_index = Value('i', -1 )

global write_index
write_index = Value('i', -1 )

global end_flag
end_flag = Value('i', 0 )

global use_q
use_q = Value('i', 0 )


####################################################################
# Refer: https://qiita.com/maiueo/items/b3021a8803859d35a46f

def valueToNdarray(v):
    return np.ctypeslib.as_array(v.get_obj())  # from Value to ndarray
	
####################################################################

def ndarrayToValue(n):
    n_h, n_w, n_ch = n.shape # get size, channel
    v = Value(((ctypes.c_uint8 * n_ch) * n_w) * n_h)  # create shamed mem same size, channel
    valueToNdarray(v)[:] = n  # copy
    return v

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

# 	if 0 <= write_index.value:
# 		print("RECEIVE {} ({})").format( write_index.value % g_fps, write_index.value )

	rgb = data.reshape( g_height, g_width ,3 )

	if use_q.value == 1 :
		q.put(rgb)
	else:
		array_index = write_index.value % g_fps
		v = ndarrayToValue( rgb )
# 		rgb_array2[array_index] = v
		rgb_array[array_index] = rgb

	write_index.value += 1

#####################################################################

t1 = np.arange(0.0, 5.0, 0.1)
t2 = np.arange(0.0, 5.0, 0.02)
t3 = np.arange(0.0, 2.0, 0.01)

#####################################################################

def f(t):
    s1 = np.cos(2*np.pi*t)
    e1 = np.exp(-t)
    return s1 * e1

#####################################################################

def myShowImageProc(r, w, e):
	last_show_index = 0

	fig, axarr = plt.subplots(2, 2, constrained_layout=True)

	axarr[0,0].set_xlabel('width (pix.)')
	axarr[0,0].set_ylabel('height (pix.)')

	axarr[0,1].plot(t1, f(t1), 'o', t2, f(t2), '-')
	axarr[0,1].set_title('subplot 1')
	axarr[0,1].set_xlabel('distance (m)')
	axarr[0,1].set_ylabel('Damped oscillation')
	fig.suptitle('Preview = received ndarray(from C++ callback)', fontsize=16)

	while not e.value == 1:
		if r.value < w.value :
			latency = w.value - r.value 

			if 0 <= r.value and 0 <= w.value:

				if  use_q.value == 1:

					if latency > 2:
						print("trim --->")
						for ii in range(latency-1):
							# print(ii)
							q.get()			
					img = q.get().reshape(g_height,g_width,3)
					print( img.shape )

					if img.ndim == 3:
						rgb = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
						axarr[0,0].imshow(rgb)
						plt.pause(0.01)
						last_show_index = w.value
					elif img.ndim == 2:
						axarr[0,0].imshow(img, cmap=plt.cm.gray)
						plt.pause(0.01)
						last_show_index = w.value

				else:
					print("R:{} W:{} Delay:{}").format( r.value, w.value, latency )
					array_index = (r.value) % g_fps

					flag_test = False
					if flag_test:
						img = np.full((g_height,g_width,3), r.value*8, dtype=np.uint8)
					else:
						img = rgb_array[array_index]

					if img.ndim == 3:
						rgb = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
						axarr[0,0].imshow(rgb)
						plt.pause(0.01)
					elif img.ndim == 2:
						axarr[0,0].imshow(img, cmap=plt.cm.gray)
						plt.pause(0.01)
					last_show_index = w.value
			else:
				print('Skip')

			r.value += 1



#####################################################################

def myInjectProc(inject_time, w, h, fps):
	inject = mylib_sample.myUvcInject()
	inject.set_pre_callback( my_uvc_test_pre_cb_func, inject  )
	inject.set_post_callback( my_uvc_test_post_cb_func, inject  )
	inject.execute( my_uvc_test_notify_cb_func, inject_time, w, h, fps )

#####################################################################

if __name__ == "__main__":

	keep_time = 300
	p = Process( target=myInjectProc, args=(keep_time, g_width, g_height, g_fps) )
	p.start()

	s = Process( target = myShowImageProc, args=(read_index, write_index, end_flag ) )
	s.start()

# 	s.join()
# 	p.join()
