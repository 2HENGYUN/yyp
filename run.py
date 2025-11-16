import os
import sys

if getattr(sys, 'frozen', False):
    # EXE 运行时
    base_path = sys._MEIPASS
else:
    # python 运行时
    base_path = os.path.dirname(os.path.abspath(__file__))

app_path = os.path.join(base_path, 'app.py')

os.system(f'streamlit run "{app_path}"')
