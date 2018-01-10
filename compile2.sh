python3 -c "import compileall; compileall.compile_dir('src/modules/Modelizing', force=True)"

#python3 -c "import py_compile; py_compile.compile('src/modules/Modelizing, 'bin/modules/Modelizing.pyc')"

#python3 src/modules/zipModelizing.py
#mv modelizing.zip bin/modules

python3 -c "import py_compile; py_compile.compile('src/modules/XmlCarManage.py', 'bin/modules/XmlCarManage.pyc')"
python3 -c "import py_compile; py_compile.compile('src/CalculVoiture.py', 'bin/CalculVoiture.pyc')"
cp src/logging_basil.conf bin/logging_basil.conf
cp src/HMI/CalculVoiture.glade bin/HMI/CalculVoiture.glade

#python3 bin/CalculVoiture.pyc data/CarDatabase9.xml

