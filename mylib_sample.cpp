/*********************************************************************
* Software License Agreement (BSD License)
*
*  Copyright (C) 2010-2012 Ken Tossell
*  All rights reserved.
*
*  Portions of Copyright (C) 2019 Katsumi.W
*
*  Redistribution and use in source and binary forms, with or without
*  modification, are permitted provided that the following conditions
*  are met:
*
*   * Redistributions of source code must retain the above copyright
*     notice, this list of conditions and the following disclaimer.
*   * Redistributions in binary form must reproduce the above
*     copyright notice, this list of conditions and the following
*     disclaimer in the documentation and/or other materials provided
*     with the distribution.
*   * Neither the name of the author nor other contributors may be
*     used to endorse or promote products derived from this software
*     without specific prior written permission.
*
*  THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS
*  "AS IS" AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT
*  LIMITED TO, THE IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS
*  FOR A PARTICULAR PURPOSE ARE DISCLAIMED. IN NO EVENT SHALL THE
*  COPYRIGHT OWNER OR CONTRIBUTORS BE LIABLE FOR ANY DIRECT, INDIRECT,
*  INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING,
*  BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES;
*  LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER
*  CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT
*  LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN
*  ANY WAY OUT OF THE USE OF THIS SOFTWARE, EVEN IF ADVISED OF THE
*  POSSIBILITY OF SUCH DAMAGE.
*********************************************************************/
#include <boost/python.hpp>
#include <boost/python/numpy.hpp>
#include <stdio.h>
#include <chrono>
#include <thread>
#include <algorithm>
#include <stdexcept>
#include <opencv2/highgui/highgui_c.h>
#include "libuvc/libuvc.h"
#include "mylib_sample.h"

namespace p = boost::python;
namespace np = boost::python::numpy;

/*********************************************************************
* 
*
*********************************************************************/

myUvcInject::myUvcInject() {
	_keeptime = 10;
	_width = 640;
	_height = 480;
	_fps = 30;
}

/*********************************************************************
* 
*
*********************************************************************/

void myUvcInject::cb(uvc_frame_t *frame, void *ptr) {
  myUvcInject* pThis = (myUvcInject*)ptr;

  uvc_frame_t *bgr;
  uvc_error_t ret;
  IplImage* cvImg;
  const bool flag_cv = true;


  size_t bgr_buf_len = frame->width * frame->height * 3;
  bgr = uvc_allocate_frame(bgr_buf_len);
  if (!bgr) {
    printf("unable to allocate bgr frame!");
    return;
  }

  ret = uvc_any2bgr(frame, bgr);
  if (ret) {
    uvc_perror(ret, "uvc_any2bgr");
    uvc_free_frame(bgr);
    return;
  }

	p::tuple shape = p::make_tuple(bgr_buf_len);
	np::dtype dtype = np::dtype::get_builtin<uint8_t>();
	np::ndarray array = np::zeros(shape, dtype);
  size_t N = array.shape(0);

  auto* p = reinterpret_cast<char *>(array.get_data());
  for(int ii=0; ii<N; ii++) {
    *(p+ii) = *((reinterpret_cast<char *>(bgr->data)+ii));

  }
	// Callback python function (Notify Callback)
  pThis->exec_notify_callback(array);

  if (flag_cv) {
    cvImg = cvCreateImageHeader(
        cvSize(bgr->width, bgr->height),
        IPL_DEPTH_8U,
        3);

    cvSetData(cvImg, bgr->data, bgr->width * 3); 
    // cvNamedWindow("SRC", CV_WINDOW_AUTOSIZE);
    cvShowImage("Src: C++", cvImg);
    cvWaitKey(10);

    cvReleaseImageHeader(&cvImg);
  }
  uvc_free_frame(bgr);
}
/*********************************************************************
* 
*
*********************************************************************/

int myUvcInject::run(void ) 
{
  uvc_context_t *ctx;
  uvc_error_t res;
  uvc_device_t *dev;
  uvc_device_handle_t *devh;
  uvc_stream_ctrl_t ctrl;

  res = uvc_init(&ctx, NULL);

  if (res < 0) {
    uvc_perror(res, "uvc_init");
    return res;
  }

  puts("UVC initialized");

  res = uvc_find_device(
      ctx, &dev,
      0, 0, NULL);

  if (res < 0) {
    uvc_perror(res, "uvc_find_device");
  } else {
    puts("Device found");

    res = uvc_open(dev, &devh);

    if (res < 0) {
      uvc_perror(res, "uvc_open");
    } else {
      puts("Device opened");
	  printf("%d x %d x %d\n", _width, _height, _fps );

      uvc_print_diag(devh, stderr);
      res = uvc_get_stream_ctrl_format_size(
          devh, &ctrl, UVC_FRAME_FORMAT_YUYV, _width, _height, _fps
      );

      uvc_print_stream_ctrl(&ctrl, stderr);

      if (res < 0) {
        uvc_perror(res, "get_mode");
      } else {
        res = uvc_start_streaming(devh, &ctrl, myUvcInject::cb, this, 0);
        if (res < 0) {
          uvc_perror(res, "start_streaming");
        } else {




          printf("Streaming for %d seconds...\n", _keeptime );
          uvc_error_t resAEMODE = uvc_set_ae_mode(devh, 1);
          uvc_perror(resAEMODE, "set_ae_mode");
          int i;
          for (i = 1; i <= 5; i++) {
            /* uvc_error_t resPT = uvc_set_pantilt_abs(devh, i * 20 * 3600, 0); */
            /* uvc_perror(resPT, "set_pt_abs"); */
            uvc_error_t resEXP = uvc_set_exposure_abs(devh, 20 + i * 5);
            uvc_perror(resEXP, "set_exp_abs");
      	    std::this_thread::sleep_for(std::chrono::milliseconds(1000));
          }
      	  std::this_thread::sleep_for(std::chrono::milliseconds(_keeptime * 1000));
          uvc_stop_streaming(devh);
	        puts("Done streaming.");
        }
      }
      uvc_close(devh);
      puts("Device closed");
    }
    uvc_unref_device(dev);
  }
  uvc_exit(ctx);
  puts("UVC exited");

  return 0;
}


/*********************************************************************
* 
*
*********************************************************************/

np::ndarray myUvcInject::zero_init(uint32_t array_size) {
	p::tuple shape = p::make_tuple(array_size);
	np::dtype dtype = np::dtype::get_builtin<double>();
	np::ndarray array = np::zeros(shape, dtype);
	return array;
}


/*********************************************************************
* 
*
*********************************************************************/

void myUvcInject::execute( p::object python_notify_cb, boost::python::numpy::ndarray rgb, 
							int duration_sec, int width, int height, int fps ) 
{
	exec_pre_callback();

	_pfnPyCallbackNotify = python_notify_cb;

	_keeptime = duration_sec;
	_width = width;
	_height = height;
	_fps = fps;

	run();

	exec_post_callback();
}

/*********************************************************************
* 
*
*********************************************************************/

void myUvcInject::set_pre_callback(p::object python_cb_func, p::object user_data ) {
	this->_pfnPyCallbackPre = python_cb_func;
	this->_PyUserdataPre = user_data;
}

/*********************************************************************
* 
*
*********************************************************************/
void myUvcInject::exec_pre_callback() {
	this->_pfnPyCallbackPre(this->_PyUserdataPre);
}

/*********************************************************************
* 
*
*********************************************************************/

void  myUvcInject::set_post_callback(p::object python_cb_func, p::object user_data ) {
	this->_pfnPyCallbackPost = python_cb_func;
	this->_PyUserdataPost = user_data;
}

/*********************************************************************
* 
*
*********************************************************************/

void  myUvcInject::exec_post_callback() {
	this->_pfnPyCallbackPost( this->_PyUserdataPost);
}

/*********************************************************************
* 
*
*********************************************************************/

void myUvcInject::exec_notify_callback(boost::python::numpy::ndarray buffer) {
	this->_pfnPyCallbackNotify(buffer);
}


/////////////////////////////////////////////////////

/////////////////////////////////////////////////////

BOOST_PYTHON_MODULE(mylib_sample)
{
	using namespace boost::python;
	// using namespace boost::python::numpy;

  boost::python::numpy::initialize();

	class_<myUvcInject>("myUvcInject")
		.def("zero_init", &myUvcInject::zero_init)
		.def("execute", &myUvcInject::execute)
		.def("set_pre_callback", &myUvcInject::set_pre_callback)
		.def("set_post_callback", &myUvcInject::set_post_callback)
	;
}
