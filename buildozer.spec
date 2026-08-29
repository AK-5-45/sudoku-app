[app]
title = Sudoku
package.name = sudoku
package.domain = org.sudoku.app
source.dir = .
source.include_exts = py,png,jpg,kv,atlas,mp3,ttf,ogg,wav
version = 1.0
requirements = python3,kivy
orientation = portrait
osx.python_version = 3
osx.kivy_version = 2.2.1

# =============================================================================
# КРИТИЧЕСКИ ВАЖНЫЕ НАСТРОЙКИ (ОНИ БЕЗ РЕШЁТОК #)
# Именно они предотвращают ошибку с лицензией Build-Tools 37
# =============================================================================
android.api = 33
android.minapi = 21
android.ndk = 27c
android.build_tools_version = 33.0.2
android.accept_sdk_license = True
# =============================================================================

android.archs = arm64-v8a, armeabi-v7a
fullscreen = 0
log_level = 2

[buildozer]
log_level = 2
warn_on_root = 1
