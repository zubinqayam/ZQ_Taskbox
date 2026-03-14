[app]
title = INNM Taskbox
package.name = innmtaskbox
package.domain = org.zqailogic
source.dir = .
source.include_exts = py,png,jpg,kv,atlas,json,xlsx
version = 2.0.0

# Only include packages that have p4a recipes.
# pandas and openpyxl do NOT have p4a recipes and will break the build.
# The app should guard these imports at runtime (they will be absent on Android).
requirements = python3,kivy,requests

orientation = portrait
fullscreen = 0

android.minapi = 23
android.api = 34
android.sdk = 34
android.ndk_api = 23
# Single ABI for faster/reliable CI debug builds.
# Add armeabi-v7a back once the build is stable.
android.archs = arm64-v8a
android.release_artifact = apk
android.accept_sdk_license = True

android.permissions = INTERNET, READ_EXTERNAL_STORAGE, WRITE_EXTERNAL_STORAGE

# Use latest stable p4a to avoid NDK r25b incompatibilities
p4a.branch = master

[buildozer]
log_level = 2
warn_on_root = 1
