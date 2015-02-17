#!/usr/bin/env python


from payments import app
if __name__ == '__main__':
#     import logging
#     log = logging.getLogger('werkzeug')
#     log.setLevel(logging.DEBUG)
#     
    app.run(debug = True)