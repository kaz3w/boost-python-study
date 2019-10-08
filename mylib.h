#ifndef __MYLIB_H_INCLUDED__
#define __MYLIB_H_INCLUDED__

#include <boost/python.hpp>
#include <boost/python/numpy.hpp>

/////////////////////////////////////////////////////

class myBuffer
{
public:
	myBuffer() {}

	// like calloc (malloc + fill zero)
	boost::python::numpy::ndarray zero_init(uint32_t array_size);

	// Run buffer
	void execute(uint32_t count, boost::python::object python_notify_cb, boost::python::object user_data );

	// Register PRE Callback
	void set_pre_callback(boost::python::object python_cb_func, boost::python::object user_data );
	void exec_pre_callback();

	// Register POST Callback
	void set_post_callback(boost::python::object python_cb_func, boost::python::object user_data );
	void exec_post_callback();

	/////////////////////////////////////////////////////
	// just simple test
	void sum(int a, int b);

	/////////////////////////////////////////////////////
	// Attributes
	int _sum;
	boost::python::object _pfnPyCallbackPre;
	boost::python::object _PyUserdataPre;
	boost::python::object _pfnPyCallbackPost;
	boost::python::object _PyUserdataPost;
};

#endif //!__MYLIB_H_INCLUDED__
