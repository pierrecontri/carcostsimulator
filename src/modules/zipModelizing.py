import sys, os
local_directory = os.path.dirname(os.path.realpath(__file__))
sys.path.append(local_directory)

from Modelizing import *

import zipfile
a = zipfile.PyZipFile('modelizing.zip', 'w', zipfile.ZIP_DEFLATED)
a.writepy(os.path.join(local_directory, 'Modelizing'))
a.close()

#Using
#import sys
#sys.path.insert(0, '/w2/Txt/Training/mypackage.zip')
#import class_basic_1
#obj = class_basic_1.Basic('Wilma')
#obj.show()
