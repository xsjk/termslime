set(CMAKE_CXX_FLAGS "-std=c++20")
cmake_minimum_required(VERSION 3.5)

project( termslime )

find_package( OpenCV REQUIRED )
message(STATUS "OpenCV library status:")
message(STATUS "    config: ${OpenCV_DIR}")
message(STATUS "    version: ${OpenCV_VERSION}")
message(STATUS "    libraries: ${OpenCV_LIBS}")
message(STATUS "    include path: ${OpenCV_INCLUDE_DIRS}")

add_executable( tslime tslime.cpp )
target_link_libraries(tslime PRIVATE ${OpenCV_LIBS})
target_include_directories(tslime PRIVATE ${OpenCV_INCLUDE_DIRS})
