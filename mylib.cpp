#include "mylib.h"
#include <boost/python.hpp>
#include <boost/python/numpy.hpp>
#include <memory>	// std::shared_ptr

namespace p = boost::python;
namespace np = boost::python::numpy;

/*********************************************************************
* 
*
*********************************************************************/

np::ndarray myBuffer::zero_init(uint32_t array_size) {
	p::tuple shape = p::make_tuple(array_size);
	np::dtype dtype = np::dtype::get_builtin<double>();
	np::ndarray array = np::zeros(shape, dtype);
	return array;
}

/*********************************************************************
* 
*
*********************************************************************/

void myBuffer::execute(uint32_t count, p::object python_notify_cb, p::object user_data ) 
{
	exec_pre_callback();
	for (int ii=0; ii<count; ii++) {
		python_notify_cb(user_data);
	}
	exec_post_callback();
}

/*********************************************************************
* 
*
*********************************************************************/

void myBuffer::set_pre_callback(p::object python_cb_func, p::object user_data ) {
	this->_pfnPyCallbackPre = python_cb_func;
	this->_PyUserdataPre = user_data;
}

/*********************************************************************
* 
*
*********************************************************************/
void myBuffer::exec_pre_callback() {
	this->_pfnPyCallbackPre(this->_PyUserdataPre);
}

/*********************************************************************
* 
*
*********************************************************************/

void  myBuffer::set_post_callback(p::object python_cb_func, p::object user_data ) {
	this->_pfnPyCallbackPost = python_cb_func;
	this->_PyUserdataPost = user_data;
}

/*********************************************************************
* 
*
*********************************************************************/

void  myBuffer::exec_post_callback() {
	this->_pfnPyCallbackPost( this->_PyUserdataPost);
}

/*********************************************************************
* 
*
*********************************************************************/
void myBuffer::sum(int a, int b) {
	_sum = a + b;
}

/////////////////////////////////////////////////////

BOOST_PYTHON_MODULE(mylib)
 {
	using namespace boost::python;
	using namespace boost::python::numpy;

	boost::python::numpy::initialize();

	class_<myBuffer>("myBuffer")
		.def("zero_init", &myBuffer::zero_init)
		.def("execute", &myBuffer::execute)
		.def("set_pre_callback", &myBuffer::set_pre_callback)
		.def("set_post_callback", &myBuffer::set_post_callback)
		.def("sum", &myBuffer::sum)
		.def_readwrite("_sum", &myBuffer::_sum)
		.def_readwrite("_pfnPyCallbackPre", &myBuffer::_pfnPyCallbackPre)
		.def_readwrite("_pfnPyCallbackPost", &myBuffer::_pfnPyCallbackPost)
	;
}
