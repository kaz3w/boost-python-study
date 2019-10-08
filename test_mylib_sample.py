#!/usr/bin/python

import mylib_sample
import numpy as np

#####################################################################

def my_uvc_test_pre_cb_func(rBuffer):
	print("[Python] UVC PRE (state:pre-process)")

#####################################################################

def my_uvc_test_post_cb_func(rBuffer):
	print("[Python] UVC POST (state:post-process)")

#####################################################################

def my_uvc_test_notify_cb_func(rBuffer):
	print("[Python] UVC Notify (state:run)")

#####################################################################

inject = mylib_sample.myUvcInject()
inject.set_pre_callback( my_uvc_test_pre_cb_func, inject  )
inject.set_post_callback( my_uvc_test_post_cb_func, inject  )
inject.execute( my_uvc_test_notify_cb_func, inject )
