import os.path as osp
import sys
root_dir    = osp.dirname(osp.dirname(osp.abspath(__file__)))
print("root_dir:{}".format(root_dir))
thirdparty_dir  = osp.join(root_dir, '3rdparty')
thirdparty_lib_dir   = osp.join(thirdparty_dir, 'lib/python3.6/site-packages')
sys.path.insert(0, root_dir)
sys.path.insert(0, thirdparty_lib_dir)
sys.path.insert(0, thirdparty_dir)
print(sys.path)
