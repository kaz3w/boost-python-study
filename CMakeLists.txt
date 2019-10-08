cmake_minimum_required(VERSION 3.0)
project(mylib)

if (NOT CMAKE_BUILD_TYPE)
  message(STATUS "No build type selected, default to Release")
  set(CMAKE_BUILD_TYPE "Release" CACHE STRING "" FORCE)
endif ()

if (NOT CMAKE_BUILD_TARGET)
  message(STATUS "No target type selected, default to both shared and static library")
  set(CMAKE_BUILD_TARGET "Both" CACHE STRING "" FORCE)
endif()

# The version number
set(mylib_VERSION_MAJOR 0)
set(mylib_VERSION_MINOR 1)
set(mylib_VERSION_PATCH 0)
set(mylib_DESCRIPTION "A bridge between C++ and Python/Numpy")
set(mylib_URL "https://github.com/kaz3w/boost-python-study/")

# Boost
set(BOOST_ROOT /usr)
add_compile_options(-std=c++11)
include_directories(${BOOST_ROOT}/include/boost)
link_directories(${BOOST_ROOT}/lib)


# Check Package
find_package(PkgConfig REQUIRED)

pkg_check_modules(PYTHON2 python2 REQUIRED)
include_directories(${PYTHON2_INCLUDE_DIRS})

add_library(mylib SHARED mylib.cpp)
set_target_properties(mylib PROPERTIES SUFFIX ".so")
target_link_libraries(mylib boost_numpy boost_python)

# Try to find OpenCV using a module or pkg-config. If that doesn't work, search for the header.
find_package(opencv QUIET)
if(OPENCV_FOUND)
  set(OPENCV_LINK_FLAGS ${OPENCV_LIBRARIES})
else()
  pkg_check_modules(OPENCV QUIET opencv)
  if(OPENCV_FOUND)
      set(OPENCV_INCLUDE_DIR ${OPENCV_INCLUDE_DIRS})
      set(OPENCV_LINK_FLAGS ${OPENCV_LDFLAGS})
  endif()
endif()

add_executable (example uvc_inject.cpp)

# add the executable
target_link_libraries(example uvc ${OPENCV_LDFLAGS})

