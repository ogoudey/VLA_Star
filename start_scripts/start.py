from starter.starter import Starter
from host.host import Host

import sys

if __name__ == "__main__":
    name = sys.argv[1]

    vla_star = Starter.try_load_by_name(sys.argv[1]) # really just a production
    if not vla_star:
        print(f"[Start] Could not find {name}")
    Host.list_vla_star(vla_star)
    Host.sync_manifest()
    vla_star_starter = Starter(vla_star)
    good = vla_star_starter.start() # no args. But this should be filled. This loads context.
    vla_star_starter.try_pickle_vla_star()
    Host.update_vla_star_on_list(vla_star)
    Host.sync_manifest()


    
    if vla_star_starter:
        good = vla_star_starter.start() # no args. But this should be filled.
    else:
        

    