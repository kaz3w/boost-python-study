cmake_minimum_required(VERSION 3.0)
project(mylib)

# The version number
set(mylib_VERSION_MAJOR 0)
set(mylib_VERSION_MINOR 1)

# Boost
set(BOOST_ROOT /usr/include/boost)
 
add_compile_options(-std=c++11)

find_package(PkgConfig REQUIRED)


# OpenCV defines targets with transitive dependencies not with namespaces but using opencv_ prefix. 
# This targets provide necessary include directories and linked flags.
find_package(OpenCVPkg REQUIRED
   COMPONENTS
     opencv_core
     opencv_highgui
)


pkg_check_modules(PYTHON2 python2 REQUIRED)
include_directories(${PYTHON2_INCLUDE_DIRS})

include_directories(${BOOST_ROOT}/include)
link_directories(${BOOST_ROOT}/lib)

add_library(mylib SHARED mylib.cpp)
set_target_properties(mylib PROPERTIES SUFFIX ".so")

target_link_libraries(mylib boost_numpy boost_python)

include_directories ("${PROJECT_SOURCE_DIR}/MathFunctions")
#add_subdirectory (MathFunctions)

# add the executable
add_executable (example uvc_inject.cpp)
target_link_libraries(example
    PRIVATE
      LibUVC::UVC
      opencv_core
      opencv_highgui
  )

