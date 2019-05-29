from distutils.version import LooseVersion

import cms

GTE_CMS_35 = LooseVersion(cms.__version__) >= LooseVersion('3.5')


def is_authenticated(user):
    try:
        return user.is_authenticated()  # Django<1.10
    except TypeError:
        return user.is_authenticated  # Django>=1.10
