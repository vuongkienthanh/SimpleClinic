set PYTHONOPTIMIZE=2
poetry run pyinstaller src\demo.py --onefile --add-data="src\bitmaps;bitmaps" --add-data="src\default_config.json;." --add-data="src\sample;sample" -i="logo\logo.ico"
