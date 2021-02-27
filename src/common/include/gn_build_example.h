#ifndef __GN_BUILD_EXAMPLE_H__
#define __GN_BUILD_EXAMPLE_H__

#include "gn_build_example_defines.h"

GBE_BEGIN_DECLS

/**
 * Get the library's version number.
 * @return Version
 */
GBE_API const char * GBE_CALL gn_build_example_get_version();

/**
 * Get message
 * @param type message type
 * @return message
 */
GBE_API const char * GBE_CALL gn_build_example_get_message(enum gn_build_example_message_type type);

GBE_END_DECLS

#endif //__GN_BUILD_EXAMPLE_H__