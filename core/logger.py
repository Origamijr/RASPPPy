callbacks = []

def add_callback(fn):
    callbacks.append(fn)

def log(s):
    s = repr(s)
    for fn in callbacks:
        fn(s)

add_callback(print)