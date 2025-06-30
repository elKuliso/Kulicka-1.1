[app]
title = Kulinka
package.name = kulinka
package.domain = org.example
version = 1.0
source.dir = .
source.include_exts = py,png,jpg,kv,atlas
requirements = python3.9, pygame==2.1.3, cython==0.29.36, pyjnius>=1.5.0
orientation = portrait
fullscreen = 1
log_level = 2
entrypoint = main.py

[buildozer]
log_level = 2
warn_on_root = 1
