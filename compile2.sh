# python -c "import py_compile; py_compile.compile('src/modules/Modelizing/CarModelized.py', 'bin/modules/Modelizing/CarModelized.pyc')"
# python -c "import py_compile; py_compile.compile('src/modules/Modelizing/FuelModelized.py', 'bin/modules/Modelizing/FuelModelized.pyc')"
# python -c "import py_compile; py_compile.compile('src/modules/Modelizing/DriverModelized.py', 'bin/modules/Modelizing/DriverModelized.pyc')"
# python -c "import py_compile; py_compile.compile('src/modules/Modelizing/DrivertypeModelized.py', 'bin/modules/Modelizing/DrivertypeModelized.pyc')"
# python -c "import py_compile; py_compile.compile('src/modules/Modelizing/ObjectModelized.py', 'bin/modules/Modelizing/ObjectModelized.pyc')"
cd "src/modules"
python zipModelizing.py
cd ../..
cp src/modules/modelizing.zip bin/modules
python -c "import py_compile; py_compile.compile('src/modules/XmlCarManage.py', 'bin/modules/XmlCarManage.pyc')"
python -c "import py_compile; py_compile.compile('src/CalculVoiture.py', 'bin/CalculVoiture.pyc')"
cp src/logging_basil.conf bin/logging_basil.conf
cp src/HMI/CalculVoiture.glade bin/HMI/CalculVoiture.glade

python bin/CalculVoiture.pyc data/CarDatabase9.xml

