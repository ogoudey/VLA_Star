from starter.starter import Starter

import sys

if __name__ == "__main__":
    name = sys.argv[1]

    vla_star = Starter.try_load_by_name(sys.argv[1]) # really just a production
    if not vla_star:
        print(f"[Start] Could not find {name}")

    vla_star_starter = Starter(vla_star)
    good = vla_star_starter.start() # no args. But this should be filled. This loads context.
    vla_star_starter.try_pickle_vla_star()

    