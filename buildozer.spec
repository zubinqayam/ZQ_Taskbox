[app]
title = INNM Taskbox
package.name = innmtaskbox
package.domain = org.zqailogic
source.dir = .
source.include_exts = py,png,jpg,kv,atlas,json,xlsx
version = 2.0.0

requirements = python3,kivy,pandas,openpyxl,requests

orientation = portrait
fullscreen = 0

android.api = 34
android.sdk = 34
android.ndk_api = 21
android.archs = arm64-v8a, armeabi-v7a

android.permissions = INTERNET, READ_EXTERNAL_STORAGE, WRITE_EXTERNAL_STORAGE

[buildozer]
log_level = 2
warn_on_root = 1
