#!/usr/bin/python
import mylib
import numpy as np


def my_test_pre_cb_func(rBuffer):
	print("PRE (state:pre-process)")


def my_test_post_cb_func(rBuffer):
	print("POST (state:post-process)")
	rBuffer.sum( 100, 200)
	print("result: " + str(rBuffer._sum))



def my_test_notify_cb_func(rBuffer):
	print("Notify (state:run)")


########
b = mylib.myBuffer()
b.set_pre_callback( my_test_pre_cb_func, b  )
b.set_post_callback( my_test_post_cb_func, b  )
b.execute(10, my_test_notify_cb_func, b)
