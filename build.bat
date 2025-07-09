# pip install pyinstaller

pyinstaller MPlus.spec
# 也可以使用：
# pyinstaller --onedir --noconsole --icon=ICON.ico --add-data "./functions;functions" --add-data "ICON.ico;." --name MPlus --distpath dist --workpath build --hidden-import=PySide6 MarkPlus.py
