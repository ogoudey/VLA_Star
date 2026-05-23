def get_good(arg:int=-1) -> str:
    match arg:
        case -1:
            return ""
        case 0:
            return "When you chat, communicating to the user, only use noun phrases that correspond to symbols in your context window. E.g. Lever 1 => 'the lever'. Don't use noun phrases that are certain truthful references."
        case 1:
            return "When you chat, communicating to the user, only use referring expressions that evaluate to True in the context of EXACTLY what you know about the world you're in."
        case 2:
            return "When you chat, communicating to the user, only use referring expressions that evaluate to True in the context of EXACTLY what you know about the world you're in. Don't use the symbol name exactly (e.g. 'Lever 2')"
        case _:
            return ""