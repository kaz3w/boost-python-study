#ifndef __MYLIB_SAMPLE_H_INCLUDED__
#define __MYLIB_SAMPLE_H_INCLUDED__

#include <boost/python.hpp>
#include <boost/python/numpy.hpp>
#include "libuvc/libuvc.h"

/////////////////////////////////////////////////////

class myUvcInject
{
public:
	myUvcInject() {}


	//
	int run(void);
	static void cb(uvc_frame_t *frame, void *ptr);

	// like calloc (malloc + fill zero)
	boost::python::numpy::ndarray zero_init(uint32_t array_size);

	// Run buffer
	void execute(boost::python::object python_notify_cb, boost::python::object user_data );

	// Register PRE Callback
	void set_pre_callback(boost::python::object python_cb_func, boost::python::object user_data );
	void exec_pre_callback();

	// Register POST Callback
	void set_post_callback(boost::python::object python_cb_func, boost::python::object user_data );
	void exec_post_callback();

	void exec_notify_callback();


	// Attributes
	boost::python::object _pfnPyCallbackPre;
	boost::python::object _PyUserdataPre;
	boost::python::object _pfnPyCallbackPost;
	boost::python::object _PyUserdataPost;

	boost::python::object _pfnPyCallbackNotify;
	boost::python::object _PyUserdataNotify;

};

#endif //!__MYLIB_SAMPLE_H_INCLUDED__
