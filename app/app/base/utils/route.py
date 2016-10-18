class route(object):

    _routes = []
    #_values = Configuration.values()
    
    def __init__(self, uri):
        self._uri = uri
        
    def __call__(self, _handler):
        
        if type(self._uri) is list:
            for x in self._uri:
                self._routes.append((x, _handler))
        else:
            self._routes.append((self._uri, _handler))
        return _handler

    @classmethod
    def get_routes(self):
        return self._routes

    @classmethod
    def get_uris(self):
        uris = []
        for item in self._routes:
            (uri, obj) = item
            uris.append(uri)
        return uris
    
    @classmethod
    def is_valid_request(self, _uri, _obj):
        check_buck = {}
        for item in self._routes:
            (uri, obj) = item 
            check_buck[uri] = obj  
        if check_buck.get(_uri, None) and check_buck.get(_uri, None) != _obj: 
            return False
        elif not check_buck.get(_uri, None): 
            return False
        elif  check_buck.get(_uri, None) and not check_buck.get(_uri): 
            return False
        return True