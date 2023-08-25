import eel

from core.runtime import Runtime

eel.init('client', allowed_extensions=['.js', '.html'])

@eel.expose                         # Expose this function to Javascript
def handleinput(x):
    print('%s' % x)

eel.say_hello_js('connected!')   # Call a Javascript function

eel.start('index.html')             # Start (this blocks and enters loop)