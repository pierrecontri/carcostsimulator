import Modelizing

import zipfile
a = zipfile.PyZipFile('modelizing.zip', 'w', zipfile.ZIP_DEFLATED)
a.writepy('Modelizing')
a.close()

#Using
#import sys
#sys.path.insert(0, '/w2/Txt/Training/mypackage.zip')
#import class_basic_1
#obj = class_basic_1.Basic('Wilma')
#obj.show()
