[app]
title = Bad Dog
package.name = baddog
package.domain = org.baddog
source.dir = .
source.include_exts = py,png
version = 1.0
requirements = python3,sdl2,sdl2_image,sdl2_mixer,sdl2_ttf,pygame
orientation = landscape
fullscreen = 1
p4a.bootstrap = sdl2
android.api = 30
android.minapi = 21
android.accept_sdk_license = True
android.archs = armeabi-v7a

[buildozer]
log_level = 2
warn_on_root = 1
