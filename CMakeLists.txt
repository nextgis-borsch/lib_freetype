################################################################################
# Project:  Lib FreeType
# Purpose:  CMake build scripts
# Author:   Dmitry Baryshnikov, dmitry.baryshnikov@nexgis.com
################################################################################
# Copyright (C) 2017-2018, NextGIS <info@nextgis.com>
#
# Permission is hereby granted, free of charge, to any person obtaining a
# copy of this software and associated documentation files (the "Software"),
# to deal in the Software without restriction, including without limitation
# the rights to use, copy, modify, merge, publish, distribute, sublicense,
# and/or sell copies of the Software, and to permit persons to whom the
# Software is furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included
# in all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS
# OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL
# THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING
# FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER
# DEALINGS IN THE SOFTWARE.
################################################################################

cmake_minimum_required(VERSION 2.8.12 FATAL_ERROR)

project(freetype)

if(NOT DEFINED PACKAGE_VENDOR)
    set(PACKAGE_VENDOR NextGIS)
endif()

if(NOT DEFINED PACKAGE_BUGREPORT)
    set(PACKAGE_BUGREPORT info@nextgis.com)
endif()

# Some init settings
set(CMAKE_COLOR_MAKEFILE ON)
# Set path to additional CMake modules
set(CMAKE_MODULE_PATH ${CMAKE_SOURCE_DIR}/cmake ${CMAKE_MODULE_PATH})

if(OSX_FRAMEWORK AND (BUILD_SHARED_LIBS OR BUILD_STATIC_LIBS))
  message(FATAL_ERROR "Only OSX_FRAMEWORK key or any or both BUILD_SHARED_LIBS
                       and BUILD_STATIC_LIBS keys are permitted")
endif()

if(OSX_FRAMEWORK)
    set(INSTALL_BIN_DIR "bin" CACHE INTERNAL "Installation directory for executables" FORCE)
    set(INSTALL_LIB_DIR "Library/Frameworks" CACHE INTERNAL "Installation directory for libraries" FORCE)
    set(INSTALL_INC_DIR "${INSTALL_LIB_DIR}/${PROJECT_NAME}.framework/Headers" CACHE INTERNAL "Installation directory for headers" FORCE)
    set(INSTALL_CMAKECONF_DIR ${INSTALL_LIB_DIR}/${PROJECT_NAME}.framework/Resources/CMake CACHE INTERNAL "Installation directory for cmake config files" FORCE)
    set(SKIP_INSTALL_HEADERS ON)
    set(SKIP_INSTALL_FILES ON)
    set(SKIP_INSTALL_EXPORT ON)
    set(CMAKE_MACOSX_RPATH ON)
else()
    include(GNUInstallDirs)

    set(INSTALL_BIN_DIR ${CMAKE_INSTALL_BINDIR} CACHE INTERNAL "Installation directory for executables" FORCE)
    set(INSTALL_LIB_DIR ${CMAKE_INSTALL_LIBDIR} CACHE INTERNAL "Installation directory for libraries" FORCE)
    set(INSTALL_INC_DIR ${CMAKE_INSTALL_INCLUDEDIR} CACHE INTERNAL "Installation directory for headers" FORCE)
    set(INSTALL_DOC_DIR ${CMAKE_INSTALL_DOCDIR} CACHE INTERNAL "Share directory for data" FORCE)
    set(INSTALL_CMAKECONF_DIR ${CMAKE_INSTALL_DATADIR}/${PROJECT_NAME}/CMake CACHE INTERNAL "Installation directory for cmake config files" FORCE)
endif()

if(CMAKE_GENERATOR_TOOLSET MATCHES "v([0-9]+)_xp")
    add_definitions(-D_WIN32_WINNT=0x0501)
endif()

include(util)
check_version(VERSION_MAJOR VERSION_MINOR VERSION_PATCH)
set(VERSION ${VERSION_MAJOR}.${VERSION_MINOR}.${VERSION_PATCH})
set(PROJECT_VERSION ${VERSION_MAJOR}.${VERSION_MINOR}.${VERSION_PATCH})
set(SHARED_LIBRARY_VERSION ${VERSION_MAJOR}.${VERSION_MINOR})

if(OSX_FRAMEWORK)
    set(FRAMEWORK_VERSION "${VERSION_MAJOR}")
endif()

report_version(${PROJECT_NAME} ${VERSION})

# Compiler definitions for building the library
add_definitions(-DFT2_BUILD_LIBRARY)

include(FindAnyProject)

# Find dependencies
foreach (d ZLIB BZip2 PNG HarfBuzz)
  string(TOUPPER "${d}" D)

  find_anyproject(${d} DEFAULT ON NAMES ${d} BZ2 bz2 libbzip2)

  if (${d}_FOUND OR ${D}_FOUND)
    message(STATUS "Building with ${d}")
  endif ()
endforeach ()

message(STATUS
  "Creating directory ${PROJECT_BINARY_DIR}/include/freetype/config")
file(MAKE_DIRECTORY "${PROJECT_BINARY_DIR}/include/freetype/config")


# Create the configuration file
include(CheckIncludeFile)
message(STATUS
  "Creating file ${PROJECT_BINARY_DIR}/include/freetype/config/ftconfig.h")

if (UNIX)
  check_include_file("unistd.h" HAVE_UNISTD_H)
  check_include_file("fcntl.h" HAVE_FCNTL_H)
  check_include_file("stdint.h" HAVE_STDINT_H)

  file(READ "${PROJECT_SOURCE_DIR}/builds/unix/ftconfig.in"
    FTCONFIG_H)
  if (HAVE_UNISTD_H)
    string(REGEX REPLACE
      "#undef +(HAVE_UNISTD_H)" "#define \\1"
      FTCONFIG_H "${FTCONFIG_H}")
  endif ()
  if (HAVE_FCNTL_H)
    string(REGEX REPLACE
      "#undef +(HAVE_FCNTL_H)" "#define \\1"
      FTCONFIG_H "${FTCONFIG_H}")
  endif ()
  if (HAVE_STDINT_H)
    string(REGEX REPLACE
      "#undef +(HAVE_STDINT_H)" "#define \\1"
      FTCONFIG_H "${FTCONFIG_H}")
  endif ()
  string(REPLACE "/undef " "#undef "
    FTCONFIG_H "${FTCONFIG_H}")
  file(WRITE "${PROJECT_BINARY_DIR}/include/freetype/config/ftconfig.h-new"
    "${FTCONFIG_H}")
else ()
  file(READ "${PROJECT_SOURCE_DIR}/include/freetype/config/ftconfig.h"
    FTCONFIG_H)

    string(REPLACE <match_string>
           <replace_string> <output variable>
           <input> [<input>...])

    string(REPLACE "FT_BEGIN_HEADER"
"
FT_BEGIN_HEADER

#ifdef freetype_EXPORTS
#define FT_EXPORT(x) __declspec(dllexport) x
#define FT_EXPORT_DEF(x) __declspec(dllexport) x
#define FT_EXPORT_VAR(x) __declspec(dllexport) x
#else
#define FT_EXPORT(x) __declspec(dllimport) x
#define FT_EXPORT_DEF(x) __declspec(dllimport) x
#define FT_EXPORT_VAR(x) __declspec(dllimport) x
#endif
"
FTCONFIG_H "${FTCONFIG_H}"
    )

    #define FT_BASE(x) __declspec(dllexport) x
    #define FT_BASE(x) __declspec(dllimport) x

  file(WRITE "${PROJECT_BINARY_DIR}/include/freetype/config/ftconfig.h-new"
    "${FTCONFIG_H}")
endif ()
execute_process(COMMAND ${CMAKE_COMMAND} -E copy_if_different
  "${PROJECT_BINARY_DIR}/include/freetype/config/ftconfig.h-new"
  "${PROJECT_BINARY_DIR}/include/freetype/config/ftconfig.h")


# Create the options file
message(STATUS
  "Creating file ${PROJECT_BINARY_DIR}/include/freetype/config/ftoption.h")

file(READ "${PROJECT_SOURCE_DIR}/include/freetype/config/ftoption.h"
  FTOPTION_H)
if (ZLIB_FOUND)
  string(REGEX REPLACE
    "/\\* +(#define +FT_CONFIG_OPTION_SYSTEM_ZLIB) +\\*/" "\\1"
    FTOPTION_H "${FTOPTION_H}")
endif ()
if (BZIP2_FOUND)
  string(REGEX REPLACE
    "/\\* +(#define +FT_CONFIG_OPTION_USE_BZIP2) +\\*/" "\\1"
    FTOPTION_H "${FTOPTION_H}")
endif ()
if (PNG_FOUND)
  string(REGEX REPLACE
    "/\\* +(#define +FT_CONFIG_OPTION_USE_PNG) +\\*/" "\\1"
    FTOPTION_H "${FTOPTION_H}")
endif ()
if (HARFBUZZ_FOUND)
  string(REGEX REPLACE
    "/\\* +(#define +FT_CONFIG_OPTION_USE_HARFBUZZ) +\\*/" "\\1"
    FTOPTION_H "${FTOPTION_H}")
    include_directories(${HARFBUZZ_INCLUDE_DIRS}/harfbuzz)
endif ()
file(WRITE "${PROJECT_BINARY_DIR}/include/freetype/config/ftoption.h-new"
  "${FTOPTION_H}")
execute_process(COMMAND ${CMAKE_COMMAND} -E copy_if_different
  "${PROJECT_BINARY_DIR}/include/freetype/config/ftoption.h-new"
  "${PROJECT_BINARY_DIR}/include/freetype/config/ftoption.h")


# Specify library include directories
include_directories("${PROJECT_SOURCE_DIR}/include")
include_directories(BEFORE "${PROJECT_BINARY_DIR}/include")



set(PUBLIC_HEADERS include/ft2build.h)
file(GLOB PUBLIC_FT_HEADERS "include/freetype/*.h")
file(GLOB PUBLIC_CONFIG_HEADERS "include/freetype/config/*.h")
file(GLOB PRIVATE_HEADERS "include/freetype/internal/*.h")


set(BASE_SRCS
    src/autofit/autofit.c
    src/base/ftbase.c
    src/base/ftbbox.c
    src/base/ftbdf.c
    src/base/ftbitmap.c
    src/base/ftcid.c
    src/base/ftfstype.c
    src/base/ftgasp.c
    src/base/ftglyph.c
    src/base/ftgxval.c
    src/base/ftinit.c
    src/base/ftmm.c
    src/base/ftotval.c
    src/base/ftpatent.c
    src/base/ftpfr.c
    src/base/ftstroke.c
    src/base/ftsynth.c
    src/base/ftsystem.c
    src/base/fttype1.c
    src/base/ftwinfnt.c
    src/bdf/bdf.c
    src/bzip2/ftbzip2.c
    src/cache/ftcache.c
    src/cff/cff.c
    src/cid/type1cid.c
    src/gzip/ftgzip.c
    src/lzw/ftlzw.c
    src/pcf/pcf.c
    src/pfr/pfr.c
    src/psaux/psaux.c
    src/pshinter/pshinter.c
    src/psnames/psnames.c
    src/raster/raster.c
    src/sfnt/sfnt.c
    src/smooth/smooth.c
    src/truetype/truetype.c
    src/type1/type1.c
    src/type42/type42.c
    src/winfonts/winfnt.c
)

if (WIN32)
  enable_language(RC)
  list(APPEND BASE_SRCS builds/windows/ftdebug.c
                        src/base/ftver.rc)
elseif (WINCE)
  list(APPEND BASE_SRCS builds/wince/ftdebug.c)
else ()
  list(APPEND BASE_SRCS src/base/ftdebug.c)
endif ()

set(LIB_NAME ${PROJECT_NAME})
if(BUILD_SHARED_LIBS)
    add_library(${LIB_NAME} SHARED ${BASE_SRCS} ${PUBLIC_HEADERS} ${PUBLIC_FT_HEADERS} ${PUBLIC_CONFIG_HEADERS})
    set_target_properties(${LIB_NAME} PROPERTIES DEFINE_SYMBOL freetype_EXPORTS)
elseif(OSX_FRAMEWORK)
    add_library(${LIB_NAME} SHARED ${BASE_SRCS} ${PUBLIC_HEADERS} ${PUBLIC_FT_HEADERS} ${PUBLIC_CONFIG_HEADERS})
    set_property(SOURCE ${PUBLIC_CONFIG_HEADERS}
      PROPERTY MACOSX_PACKAGE_LOCATION Headers/freetype/config
    )
    set_property(SOURCE ${PUBLIC_FT_HEADERS}
      PROPERTY MACOSX_PACKAGE_LOCATION Headers/freetype
    )
    set_target_properties(${LIB_NAME} PROPERTIES
      FRAMEWORK TRUE
      FRAMEWORK_VERSION ${FRAMEWORK_VERSION}
      MACOSX_FRAMEWORK_SHORT_VERSION_STRING ${VERSION}
      MACOSX_FRAMEWORK_BUNDLE_VERSION ${VERSION}
      MACOSX_FRAMEWORK_IDENTIFIER org.freetype.freetype
      XCODE_ATTRIBUTE_INSTALL_PATH "@rpath"
      PUBLIC_HEADER "${PUBLIC_HEADERS}"
      )
else()
    add_library(${LIB_NAME} STATIC ${BASE_SRCS} ${PUBLIC_HEADERS} ${PUBLIC_FT_HEADERS} ${PUBLIC_CONFIG_HEADERS})
endif()

set_target_properties (${LIB_NAME} PROPERTIES
    VERSION ${VERSION}
    SOVERSION ${VERSION_MAJOR})

set_target_properties(
  ${LIB_NAME} PROPERTIES
    C_VISIBILITY_PRESET hidden)

target_compile_definitions(
  ${LIB_NAME} PRIVATE FT2_BUILD_LIBRARY)

if (WIN32)
    target_compile_definitions(${LIB_NAME} PRIVATE _CRT_SECURE_NO_WARNINGS _CRT_NONSTDC_NO_WARNINGS)
    if (BUILD_SHARED_LIBS)
      target_compile_definitions(${LIB_NAME} PRIVATE DLL_EXPORT)
    endif ()
endif ()

target_link_extlibraries(${LIB_NAME})

if (NOT SKIP_INSTALL_HEADERS AND NOT SKIP_INSTALL_ALL)
  install(DIRECTORY ${PROJECT_SOURCE_DIR}/include/
    DESTINATION ${INSTALL_INC_DIR}/freetype2
    PATTERN "internal" EXCLUDE
    PATTERN "ftconfig.h" EXCLUDE
    PATTERN "ftoption.h" EXCLUDE
    )
  install(FILES
    ${PROJECT_BINARY_DIR}/include/freetype/config/ftconfig.h
    ${PROJECT_BINARY_DIR}/include/freetype/config/ftoption.h
    DESTINATION ${INSTALL_INC_DIR}/freetype2/freetype/config
    )
endif ()

set(PACKAGE_NAME ${PROJECT_NAME})
string(TOUPPER ${PACKAGE_NAME} PACKAGE_UPPER_NAME)

if (NOT SKIP_INSTALL_LIBRARIES AND NOT SKIP_INSTALL_ALL)
  install(TARGETS ${LIB_NAME}
        EXPORT ${PACKAGE_UPPER_NAME}Targets
        RUNTIME DESTINATION ${INSTALL_BIN_DIR}
        LIBRARY DESTINATION ${INSTALL_LIB_DIR}
        ARCHIVE DESTINATION ${INSTALL_LIB_DIR}
        INCLUDES DESTINATION ${INSTALL_INC_DIR}
        FRAMEWORK DESTINATION ${INSTALL_LIB_DIR}
    )
endif ()

# Export package ===============================================================

# Add path to includes to build-tree export
target_include_directories(${LIB_NAME} PUBLIC
  $<BUILD_INTERFACE:${CMAKE_CURRENT_SOURCE_DIR}>
  $<BUILD_INTERFACE:${CMAKE_CURRENT_BINARY_DIR}>
)

# Add all targets to the build-tree export set
export(TARGETS ${LIB_NAME}
    FILE ${PROJECT_BINARY_DIR}/${PACKAGE_UPPER_NAME}Targets.cmake)

if(REGISTER_PACKAGE)
    # Export the package for use from the build-tree
    # (this registers the build-tree with a global CMake-registry)
    export(PACKAGE ${PACKAGE_UPPER_NAME})
endif()

# Create the ZLIBConfig.cmake file
configure_file(cmake/PackageConfig.cmake.in
    ${PROJECT_BINARY_DIR}/${PACKAGE_UPPER_NAME}Config.cmake @ONLY)

if(NOT SKIP_INSTALL_LIBRARIES AND NOT SKIP_INSTALL_ALL)
    # Install the <Package>Config.cmake
    install(FILES
      ${PROJECT_BINARY_DIR}/${PACKAGE_UPPER_NAME}Config.cmake
      DESTINATION ${INSTALL_CMAKECONF_DIR} COMPONENT dev)

    # Install the export set for use with the install-tree
    install(EXPORT ${PACKAGE_UPPER_NAME}Targets DESTINATION ${INSTALL_CMAKECONF_DIR} COMPONENT dev)
endif()

# Archiving ====================================================================

set(CPACK_PACKAGE_NAME "${PACKAGE_NAME}")
set(CPACK_PACKAGE_VENDOR "${PACKAGE_VENDOR}")
set(CPACK_PACKAGE_VERSION "${VERSION}")
set(CPACK_PACKAGE_DESCRIPTION_SUMMARY "${PACKAGE_NAME} Installation")
set(CPACK_PACKAGE_RELOCATABLE TRUE)
set(CPACK_ARCHIVE_COMPONENT_INSTALL ON)
set(CPACK_GENERATOR "ZIP")
set(CPACK_MONOLITHIC_INSTALL ON)
set(CPACK_STRIP_FILES TRUE)

# Get cpack zip archive name
get_cpack_filename(${VERSION} PROJECT_CPACK_FILENAME)
set(CPACK_PACKAGE_FILE_NAME ${PROJECT_CPACK_FILENAME})

include(CPack)
