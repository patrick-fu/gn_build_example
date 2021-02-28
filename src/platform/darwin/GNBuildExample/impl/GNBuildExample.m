//
//  GNBuildExample.m
//  GNBuildExample
//
//  Created by Patrick Fu on 2021/2/28.
//  Copyright © 2021 Patrick Fu. All rights reserved.
//

#import "src/platform/darwin/GNBuildExample/include/GNBuildExample.h"
#include "src/common/include/gn_build_example.h"

@interface GNBuildExample ()

@end

@implementation GNBuildExample

+ (NSString *)getVersion {
    return [NSString stringWithUTF8String:gn_build_example_get_version()];
}

+ (NSString *)getMessage:(GNBuildExampleMessageType)type {
    const char * message = gn_build_example_get_message((enum gn_build_example_message_type)type);
    return [NSString stringWithUTF8String:message];
}

@end
