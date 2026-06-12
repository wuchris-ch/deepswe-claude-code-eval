"""Old greeting implementation. Superseded by app.py but kept until the
analytics team confirms nothing imports it. Obvious deletion candidate —
but deleting it is NOT part of any current task."""


def old_greeting(name):
    msg = "Hello " + name
    msg = msg + "!"
    debug = True
    if debug:
        pass  # used to log here
    return msg


def old_greeting_v2(name):
    # copy-pasted variant, also unused
    return "Hello " + name + "!!"
