cd /d "D:\Users\Pierre\Documents\Info\CalculVoiture"
rem python -c "import py_compile; py_compile.compile('src/modules/Modelizing/CarModelized.py', 'bin/modules/Modelizing/CarModelized.pyc')"
rem python -c "import py_compile; py_compile.compile('src/modules/Modelizing/FuelModelized.py', 'bin/modules/Modelizing/FuelModelized.pyc')"
rem python -c "import py_compile; py_compile.compile('src/modules/Modelizing/DriverModelized.py', 'bin/modules/Modelizing/DriverModelized.pyc')"
rem python -c "import py_compile; py_compile.compile('src/modules/Modelizing/DrivertypeModelized.py', 'bin/modules/Modelizing/DrivertypeModelized.pyc')"
rem python -c "import py_compile; py_compile.compile('src/modules/Modelizing/ObjectModelized.py', 'bin/modules/Modelizing/ObjectModelized.pyc')"
cd "src\modules"
python zipModelizing.py
cd ..\..
move /Y src\modules\modelizing.zip bin\modules

python -c "import py_compile; py_compile.compile('src/modules/XmlCarManage.py', 'bin/modules/XmlCarManage.pyc')"
python -c "import py_compile; py_compile.compile('src/CalculVoiture.py', 'bin/CalculVoiture.pyc')"
xcopy /y src\logging_basil.conf bin\logging_basil.conf
xcopy /y src\HMI\CalculVoiture.glade bin\HMI\CalculVoiture.glade

python bin/CalculVoiture.pyc data/CarDatabase9.xml
pause