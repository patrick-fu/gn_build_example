//
//  GNBuildExample.h
//  GNBuildExample
//
//  Created by Patrick Fu on 2021/2/28.
//  Copyright © 2021 Patrick Fu. All rights reserved.
//

#import "GNBuildExampleDefines.h"

NS_ASSUME_NONNULL_BEGIN

@interface GNBuildExample : NSObject

/// Get the library's version number.
/// @return Version
+ (NSString *)getVersion;

/// Get message
/// @param type message type
/// @return message
+ (NSString *)getMessage:(GNBuildExampleMessageType)type;

@end

NS_ASSUME_NONNULL_END
