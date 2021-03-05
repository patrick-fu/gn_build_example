# gn_build_example

A GN build example demo project for [https://github.com/patrick-fu/gn_build](https://github.com/patrick-fu/gn_build)

This project demonstrates how to organize and build iOS/macOS shared framework (XCFramework) and static library with GN & Ninja.

> If you are new to GN, it is recommended to play with [Google’s minimal GN example](https://gn.googlesource.com/gn/+/HEAD/examples/simple_build) first.

## Structure

```sh
.
├── .gn
├── BUILD.gn
├── README.md
├── build # Core GN build configs and toolchains
├── build.py # Build entry scripts
├── buildscripts # Other helper build scripts
├── buildtools # GN/Ninja binary, stored with Git LFS
├── src # Example project dir
│   ├── BUILD.gn
│   ├── common # Example project common source
│   │   ├── BUILD.gn
│   │   ├── impl
│   │   ├── include # Common source's headers
│   │   └── module
│   │       ├── BUILD.gn
│   │       └── base64 # Deps module
│   ├── platform
│   │   └── darwin # Example project objc warpper source
│   └── src_build_args.gni # Build args
└── version.json
```

## Environmental dependence

1. Python@3.7 or higher.

> We use the 'GN' and 'Ninja' binaries in the `./buildtools` directory in the repository and do not rely on external sources.

## Build guide

Use the `./build.py` entry script in the project root directory.

Build products will be in the `./_out` directory.

> Release

```sh
# Build iOS Release
python3 build.py --ios

# Build macOS Release
python3 build.py --mac
```

> Debug

```sh
# Only create Ninja Build Files for iOS Debug and Xcode Project for development but not compile
python3 build.py --ios --debug --only-gen

# Build macOS Debug
python3 build.py --ios --debug
```

> Specify architecture (used when developing self-test verification to shorten compilation time)

```sh
# Build iOS Debug (arm64, x86_64)
python3 build.py --ios --ios-cpu arm64 x64 --debug

# Build macOS Release (x64)
python3 build.py --mac --mac-cpu x64
```

> Specify product type (common "C" header or "Objective-C" wrapper header)

```sh
# Build iOS Release of "C" header
python3 build.py --ios --ios-lang c

# Build macOS Debug of "Objective-C" header (default)
python3 build.py --mac --mac-lang objc
```

## FAQ

1. Error occurred while building iOS

    ```blank
    "ERROR at //build/config/ios/ios_sdk.gni:189:33: Script returned non-zero exit code."
    ...
    Automatic code signing identity selection was enabled but could not
    find exactly one codesigning identity matching "Apple Development".
    ...
    ```

    Your keychain contains multiple `Apple Development` identity, please open `./buildscripts/gn.py` and search for `ios_code_signing_identity_team_name`, fill in the team name pattern of the specific identify to be used.
