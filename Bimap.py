"""
This module contains a simple immutable Bimap (a bi-directional map or dictionary)
between keys and values that supports (hopefully) constant time retrieval of
both values for keys and keys for values.
"""

class Bimap:
    
    def __init__(self, items, enforceBijection=True):
        """
        Initialize the bimap.

        Arguments:
        items - a sequence of pairs (key, value). The keys and values
        must be hashable objects.
        enforceBijection - flag indicating wheter to check if the items list
        defines a bijection. If set to false, and they do not define a bijection,
        then whenever a mapping can go to multiple items, then only one of
        them is returned.

        Raises:
        Exception - if the items parameter does not define a bijection. 
        """

        # Check if the keys and values are distinct
        if enforceBijection:
            keys = [item[0] for item in items]
            vals = [item[1] for item in items] 
            
            if len(set(keys)) < len(keys):
                raise Exception("Error in Bimap construction: keys not unique")

            if len(set(vals)) < len(vals):
                raise Exception("Error in Bimap construction: values not unique")


        # Construct the key->val map
        self.keyToVal = dict(items)

        # Construct the val->key map
        self.valToKey = dict([(val, key) for (key, val) in items])

    def key(self, value):
        """
        Retrieve the key for a value

        Raises:
        Exception - if there is no key for the supplied value
        """
        if value not in self.valToKey:
            raise Exception("Error in Bimap key(): No key for value %s" % value)

        return self.valToKey[value]

    def value(self, key):
        """
        Retrieve the value for a key

        Raises:
        Exception - if there is no value for the supplied value
        """
        if key not in self.keyToVal:
            raise Exception("Error in Bimap value(): No value for key %s" % key)

        return self.keyToVal[key]
        

        
