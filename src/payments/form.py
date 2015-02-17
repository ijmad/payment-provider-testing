from flask import session, request



def handle_form_var(name, required = True):
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



def handle_form_var_boolean(name):
    try:
        session[name] = request.form[name] == 'true'
    except KeyError:
        session[name] = False
        
    return []