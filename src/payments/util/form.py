from flask import session, request



def to_session(name, required = True):
    try:
        session[name] = request.form[name]
        if session[name] == '' and required:
            return [name]
        else:
            return []
    except KeyError:
        if required:
            return [name]
        else:
            return []



def to_session_bool(name):
    try:
        session[name] = request.form[name] == 'true'
    except KeyError:
        session[name] = False
        
    return []