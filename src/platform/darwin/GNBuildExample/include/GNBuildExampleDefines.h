//
//  GNBuildExampleDefines.h
//  GNBuildExample
//
//  Created by Patrick Fu on 2021/2/28.
//  Copyright © 2021 Patrick Fu. All rights reserved.
//

#import <Foundation/Foundation.h>

#if TARGET_OS_IPHONE
#import <UIKit/UIKit.h>
#elif TARGET_OS_OSX
#import <AppKit/AppKit.h>
#endif

NS_ASSUME_NONNULL_BEGIN

typedef NS_ENUM(NSUInteger, GNBuildExampleMessageType) {
    GNBuildExampleMessageTypeRaw = 0,
    GNBuildExampleMessageTypeBase64 = 1
};

NS_ASSUME_NONNULL_END
