#include "src/common/include/gn_build_example.h"
#include "src/common/module/base64/Base64.h"
#include <string>

const char * gn_build_example_get_version() {
#ifndef GBE_VERSION
#define GBE_VERSION "Unknown"
#endif
    return GBE_VERSION;
}

const char * gn_build_example_get_message(enum gn_build_example_message_type type) {

#ifndef GBE_CUSTOM_MESSAGE
#define GBE_CUSTOM_MESSAGE "Hello World!" // Default message
#endif
    const char *raw_message = GBE_CUSTOM_MESSAGE;
    if (type == gn_build_example_message_type_raw) {
        return raw_message;
    } else if (type == gn_build_example_message_type_base_64) {
        int raw_length = strlen(raw_message);
        int encoded_length = base64_enc_len(raw_length);
        char *encoded_message = new char[encoded_length];
        base64_encode(encoded_message, (char *)raw_message, raw_length);
        return encoded_message;
    } else {
        return "Unknown type";
    }
}
