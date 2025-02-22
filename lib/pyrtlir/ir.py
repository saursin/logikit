################################################################################
# RTL Intermediate Representation
################################################################################
import uuid

################################################################################
# Util functions

def get_uuid(nchars=''):
    return str(uuid.uuid4().int)[:nchars]



################################################################################
# IR Elements

# Base class for all IR elements
class NetObj:
    def __init__(self, name=None):
        self._name = name or get_uuid(8)
        self._parent = None

    def __repr__(self):
        return self.name