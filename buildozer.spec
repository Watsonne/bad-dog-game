[app]
title = Bad Dog
package.name = baddog
package.domain = org.baddog
source.dir = .
source.include_exts = py,png
version = 1.0
requirements = python3,pygame
orientation = landscape
fullscreen = 1
p4a.bootstrap = sdl2
android.permissions = INTERNET
android.api = 31
android.minapi = 21
android.accept_sdk_license = True
android.archs = arm64-v8a

[buildozer]
log_level = 2
warn_on_root = 1
