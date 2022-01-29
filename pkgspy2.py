import os
import json
import sys
from modulefinder import ModuleFinder

# for some reason, the conda site-packages are not on the python2 path; fixing that up ---
import sys
sys.path.append('/opt/conda/envs/python2/lib/python2.7/site-packages')
from stdlib_list import stdlib_list

# todo -- needs to use the specific version of python that the nb file was using...
std_libs = stdlib_list("2.7")


def load_nb_json(path):
    return json.load(open(path, 'r'))


def get_nb_python_version(nb_json):
    kernel = nb_json["metadata"]["kernelspec"]
    if '3' in kernel.get('name') or '3' in kernel.get('language') or '3' in kernel.get('display_name'):
        return 'python3'
    else:
        return 'python2'



def get_path():
    try:
        path = os.environ['path']
    except:
        print("Set the $path variable...")
        sys.exit()
    return path
    os.environ.get('files_list.txt')
    os.environ.get('checkpoint_file')


def get_mods_for_file(path, paths_processed):
    # these are the modules we can definitively determine are packages/objects imported; python was able to resolve 
    # them using the current environment.
    modules = set()
    # these are global symbols that python couldn't resolve.. it could be they are imports for packages that are not
    # installed in the current environment.
    ext_modules = set()
    finder = ModuleFinder()
    # could blow up for lots of reasons, including invalid syntax for this py version
    try:
        finder.run_script(path)
    except SyntaxError as e:
        print("ERROR: Could not parse python file at path: {}; Syntax error: {}. Check the python version.\n".format(path, e))
        return modules, ext_modules
    except Exception as e:
        print("ERROR: Got exception trying to parse path {}; error: {}; skipping...\n".format(path, e))
        return modules, ext_modules

    for name, mod in finder.modules.items():
        if name.startswith('_'):
            continue
        if name in std_libs:
            continue
        top_name = name.split('.')[0]
        if top_name in std_libs:
            continue
        modules.add(top_name)
    
    for x in finder.badmodules.keys():
        if x.startswith('_'):
            continue
        if x in std_libs:
            continue
        name = x.split('.')[0]
        if name in std_libs:
            continue
        ext_modules.add(name)
    
    paths_processed.appendd(path)
    return modules, ext_modules


def print_mods(modules, pth):
    for name in modules:
        print(name)


def main():
    paths_processed = []
    pth = get_path()
    if not os.path.isdir(pth):
        modules, ext_modules = get_mods_for_file(pth, paths_processed)
        print('3rd-party packages that are installed AND used in {}:'.format(pth))
        print_mods(modules, pth)
        print("\nExternal modules:")
        print_mods(ext_modules, pth)
        sys.exit()
    # input was a dir..
    mod_cts = {}
    ext_mod_cts = {}
    for p in os.listdir(pth):
        # ignore all non- .py files...        
        if p.endswith('.py'):
            mods, ext_mods = get_mods_for_file(os.path.join(pth, p), paths_processed)
            print("Known Modules:")
            for name in mods:
                if name not in mod_cts.keys():
                    mod_cts[name] = 0
                mod_cts[name] += 1
            for name in ext_mods:
                if name not in ext_mod_cts.keys():
                    mod_cts[name] = 0
                mod_cts[name] += 1
    for mod, ct in mod_cts.items():
        print(mod, ct)
    print('\nExternal Modules:')
    for mod, ct in ext_mod_cts.items():
        print(mod, ct)

if __name__ == "__main__":
    main()