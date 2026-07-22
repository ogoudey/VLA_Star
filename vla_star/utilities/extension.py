class Extension:
    on: bool
    def __init__(self):
        pass

class Network(Extension):
    def __init__(self):
        pass

class Internet(Network):
    def __init__(self):
        pass

class LanguageExtension(Extension):
    def __init__(self):
        pass
    
class Text(LanguageExtension, Internet):
    def __init__(self):
        pass

class VLANet(Internet): # essentially WWW
    def __init__(self):
        pass