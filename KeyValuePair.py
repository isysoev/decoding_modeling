#For use to move the values alongside their keysclass KeyValuePair():        """    Creates a pair of values sortable by key.    """        def __init__(self, key, val):        self.key = key        self.val = val            def return_pair(self):        return (self.key, self.val)        def __str__(self):        return f"Key: {self.key}, Value: {self.val}"        def __lt__(self, other):        return len(self.key) < len(other.key)        def __gt__(self, other):        return len(self.key) > len(other.key)        def __eq__(self, other):        return len(self.key) == len(other.key)