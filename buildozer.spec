[app]
title = Bad Dog
package.name = baddog
package.domain = org.baddog

source.dir = .
source.include_exts = py,png,jpg,atlas

version = 1.0

requirements = python3,kivy,pygame

orientation = landscape

osx.python_version = 3
osx.kivy_version = 1.9.1

fullscreen = 1

android.permissions = INTERNET
android.api = 31
android.minapi = 21
android.ndk = 25b
android.sdk = 31
android.accept_sdk_license = True

android.archs = arm64-v8a, armeabi-v7a

[buildozer]
log_level = 2
warn_on_root = 1
