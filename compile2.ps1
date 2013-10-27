python -c "import py_compile; py_compile.compile('src/modules/CarModelized.py', 'bin/modules/CarModelized.pyc')"
python -c "import py_compile; py_compile.compile('src/modules/XmlCarManage.py', 'bin/modules/XmlCarManage.pyc')"
python -c "import py_compile; py_compile.compile('src/CalculVoiture.py', 'bin/CalculVoiture.pyc')"
xcopy /y src\HMI\CalculVoiture.glade bin\HMI\CalculVoiture.glade
python bin/CalculVoiture.pyc data/CarDatabase.xml