from distutils.version import LooseVersion

import cms


GTE_CMS_35 = LooseVersion(cms.__version__) >= LooseVersion('3.5')
