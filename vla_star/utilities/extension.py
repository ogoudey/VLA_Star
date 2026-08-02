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

class Rendering(Extension): # essentially WWW
    def __init__(self):
        pass

class Unity(Rendering, Internet): # localhost IP
    def __init__(self, address: tuple[str, int], project_dir: str, game_object_name):
        self.host, self.port = address[0], address[1]
        self.project_dir = project_dir
        self.game_object_name = game_object_name
