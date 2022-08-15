set PYTHONOPTIMIZE=2

poetry run pyinstaller src\main.py --noconsole --add-data="src\bitmaps;bitmaps" --add-data="src\default_config.json;." -i="logo\logo.ico"