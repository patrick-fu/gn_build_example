#ifndef __GN_BUILD_EXAMPLE_DEFINES_H__
#define __GN_BUILD_EXAMPLE_DEFINES_H__

/* Macros which declare an exportable function */
#define GBE_API

/* Macros which declare an exportable variable */
#define GBE_VAR extern

/* Macros which declare the called convention for exported functions */
#define GBE_CALL

#if defined(_WIN32) /* For MSVC */
    #undef GBE_API
    #undef GBE_VAR
    #undef GBE_CALL
    #if defined(GN_BUILD_EXAMPLE_EXPORTS)
        #define GBE_API __declspec(dllexport)
        #define GBE_VAR __declspec(dllexport)
    #else
        #define GBE_API __declspec(dllimport)
        #define GBE_VAR __declspec(dllimport) extern
    #endif
    #define GBE_CALL __cdecl
#else /* For GCC or clang */
    #undef GBE_API
    #define GBE_API __attribute__((visibility("default")))
#endif

#ifdef __cplusplus
#define GBE_BEGIN_DECLS    extern "C" {
#define GBE_END_DECLS      }
#else
#define GBE_BEGIN_DECLS
#define GBE_END_DECLS
#endif

/* Compatibility for C */
#ifndef __cplusplus
#include <stdbool.h>
#endif

#if defined(__APPLE_OS__) || defined(__APPLE__)
#include "TargetConditionals.h"
#endif

enum gn_build_example_message_type {
    gn_build_example_message_type_raw = 0,
    gn_build_example_message_type_base_64 = 1
};

#endif //__GN_BUILD_EXAMPLE_DEFINES_H__