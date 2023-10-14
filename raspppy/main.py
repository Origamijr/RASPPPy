import eel
import os
import sys
import argparse
import subprocess
import shutil
import platform

try:
    from numba.core.errors import NumbaDeprecationWarning, NumbaPendingDeprecationWarning
    import warnings

    warnings.simplefilter('ignore', category=NumbaDeprecationWarning)
    warnings.simplefilter('ignore', category=NumbaPendingDeprecationWarning)
except:
    pass

from raspppy.core.runtime import Runtime
import raspppy.core.config as conf
import raspppy.core.api

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('file', nargs='?', default=None, help='optional - file to open')
    parser.add_argument('--config', default=os.path.join(os.path.dirname(__file__), 'config.toml'), type=str, help='path to alternative config file')
    parser.add_argument('--electron', default=None, type=str, help='path to electron executable')
    args = parser.parse_args(sys.argv[1:])

    # load config
    conf.reload(args.config)

    # open initial patch
    if args.file is not None:
        Runtime.open_patch(args.file)
    else:
        Runtime.new_patch()

    # acquire electron executable
    if args.electron:
        # Use electron provided as an argument
        electron_path = os.path.abspath(args.electron)
    else:
        electron_path = shutil.which('electron')
        if electron_path:
            # Use default electron if installed already
            electron_path = os.path.abspath(electron_path)

        else: 
            # Use a locally downloaded electron
            npm_command = 'npm.cmd' if platform.system() == 'Windows' else 'npm'
            if not os.path.exists(os.path.join(os.path.dirname(__file__), 'node_modules')):
                # Last resort, install electron
                # Check npm is installed
                try:
                    subprocess.run([npm_command, '--version'], check=True, stdout=subprocess.PIPE)
                except FileNotFoundError:
                    print('npm is not installed. Please install npm to use this application.')
                    exit(1)

                # Install dependencies (should just be electron and its dependencies)
                try:
                    subprocess.run([npm_command, 'install'], check=True, cwd=os.path.dirname(__file__))
                except subprocess.CalledProcessError as e:
                    print(f'Error: {e}')
                    exit(1)
            electron_path = os.path.join(os.path.dirname(__file__), 'node_modules/electron/dist/electron')

    # change the path so electron sees the correct package.json
    os.chdir(os.path.dirname(__file__))

    # Start the client
    eel.init('client', allowed_extensions=['.js', '.html'])
    eel.browsers.set_path('electron', electron_path)
    
    def close_callback(route, websockets):
        Runtime.stop_dsp()
        os._exit(0)
    
    eel.start('index.html', mode='electron', close_callback=close_callback, blocking=False)

if __name__ == "__main__":
    sys.argv.append('examples/add_example.json')
    main()