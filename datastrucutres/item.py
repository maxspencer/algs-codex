'''

    This file contains the base class/interface definition for the items
    involved in these datastructures. You are free to implement your own
    classes of items provided they implement the interface described here.


'''

class Item(object):
    '''The base class for Items. 

    Note: The modules of the different datastructures may define subclasses of
    this class.
    '''
    def __init__(self, key = 0, payload = None):
        self.key = key
        self.payload = payload

    def __str__(self):
        return "<Item: key={!s}, payload={!r}>".format(self.key, self.payload)
