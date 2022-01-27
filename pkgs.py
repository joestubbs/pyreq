import os
import sys
from modulefinder import ModuleFinder
from stdlib_list import stdlib_list

std_libs = stdlib_list("3.7")



def get_path():
    try:
        path = os.environ['path']
    except:
        print("Set the $path variable...")
        sys.exit()
    return path


def get_mods_for_file(path):
    modules = set()
    finder = ModuleFinder()
    finder.run_script(path)

    for name, mod in finder.modules.items():
        if name.startswith('_'):
            continue
        if name in std_libs:
            continue
        top_name = name.split('.')[0]
        if top_name in std_libs:
            continue
        modules.add(top_name)
    return modules

def print_mods(modules, pth):
    print(f'3rd-party packages that are installed AND used in {pth}:')
    for name in modules:
        print(name)


def main():
    pth = get_path()
    if not os.path.isdir(pth):
        modules = get_mods_for_file(pth)
        print_mods(modules, pth)
        sys.exit()
    # input was a dir..
    mod_cts = {}
    for p in os.listdir(pth):
        # ignore all non- .py files...        
        if p.endswith('.py'):
            mods = get_mods_for_file(os.path.join(pth, p))
            for name in mods:
                if name not in mod_cts.keys():
                    mod_cts[name] = 0
                mod_cts[name] += 1
    for mod, ct in mod_cts.items():
        print(mod, ct)

if __name__ == "__main__":
    main()