import os
import json
import sys
from modulefinder import ModuleFinder
from stdlib_list import stdlib_list
import subprocess
from sysconfig import get_python_version


# todo -- needs to use the specific version of python that the nb file was using...
std_libs = stdlib_list("3.7")


def load_nb_json(path):
    return json.load(open(path, 'r'))


def get_nb_python_version(nb_json, path):
    try:
        kernel = nb_json["metadata"]["kernelspec"]
    except:
        print(f"Notebook file {path} did not have a kernel.")
        return 'none'
    if '3' in kernel.get('name') or '3' in kernel.get('language') or '3' in kernel.get('display_name'):
        return 'python3'
    else:
        return 'python2'


def convert_notebooks():
    path = get_path()
    nb_stats = {'python2': 0, 'python3': 0, 'none': 0}
    # can set to do a dry run
    dry_run = 'dry_run' in os.environ.keys()
    if dry_run:
        print("dry run... only printing stats")
    if not os.path.isdir(path):
        print(f"path {path} should be a directory...")
        sys.exit()
    print(f"converting notebooks at path, {path}")
    for p in os.listdir(path):
        # only parse ipynb files
        if not p.endswith('.ipynb'):
            continue
        full_path = os.path.join(path, p)
        nb_json = load_nb_json(full_path)
        version = get_nb_python_version(nb_json, p)
        nb_stats[version] += 1
        if dry_run:
            continue
        # -------------------------------
        # convert notebook using nbcovert; handle files with spaces in the names
        outdir = '/data/output'
        if version == 'python2':
            outdir = '/data/py2'
        elif version == 'python3':
            outdir = '/data/py3'
        cmd = ['jupyter-nbconvert', '--to', 'script', f"{full_path}", '--output-dir', outdir]
        print(f"command: {cmd}")
        try:
            subprocess.run(cmd, check=True, stdout=subprocess.PIPE)
            print(f"{p} converted with exit code 0.")
        except subprocess.CalledProcessError:
            print(f"ERROR on {p} (non-zero exit code).")
    print("final nb stats: ")
    print(nb_stats)


def get_path():
    try:
        path = os.environ['path']
    except:
        print("Set the $path variable...")
        sys.exit()
    return path


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
        print(f"ERROR: Could not parse python file at path: {path}; Syntax error: {e}. Check the python version.\n")
        return modules, ext_modules, f"Syntax error: {e}"
    except Exception as e:
        print(f"ERROR: Got exception trying to parse path {path}; error: {e}; skipping...\n")
        return modules, ext_modules, f"Unknown error: {e}"

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
        if x in moodules:
            continue
        name = x.split('.')[0]
        if name in std_libs:
            continue
        ext_modules.add(name)
    
    paths_processed.append(path)
    return modules, ext_modules, False


def print_mods(modules, pth):
    for name in modules:
        print(name)


def compute_packages():
    paths_processed = []
    pth = get_path()
    if not os.path.isdir(pth):
        modules, ext_modules, error = get_mods_for_file(pth, paths_processed)
        print(f'3rd-party packages that are installed AND used in {pth}:')
        print_mods(modules, pth)
        print("\nExternal modules:")
        print_mods(ext_modules, pth)
        sys.exit()
    # input was a dir..
    mod_cts = {}
    ext_mod_cts = {}
    errors = {} # path: "error msg"
    total_no_errors = 0
    for p in os.listdir(pth):
        # ignore all non- .py files...        
        if p.endswith('.py'):
            print(f"Computing packages for {p}...")
            mods, ext_mods, error = get_mods_for_file(os.path.join(pth, p), paths_processed)
            if error:
                errors[p] = error
                continue
            total_no_errors += 1
            for name in mods:
                if name not in mod_cts.keys():
                    mod_cts[name] = 0
                mod_cts[name] += 1
            for name in ext_mods:
                if name not in ext_mod_cts.keys():
                    ext_mod_cts[name] = 0
                ext_mod_cts[name] += 1
    total_files = total_no_errors + len(errors.keys())
    total_with_errors = len(errors.keys())
    total_packages_found = len(mod_cts.keys())
    print('*  *  *  *  *  *  *  *  *  *  *  *  *  *  *  *  *  *  *  ')
    print("\nTotals:")
    print("-------")
    print(f"Total files processed: {total_files}")
    print(f"Files processed without errors: {total_no_errors}")
    print(f"Files processed with errors: {total_with_errors}")
    print(f'Total unique packages found: {total_packages_found}')
    print("\nAll known modules, with counts of notebooks using them")
    print('------------------------------------------------------')
    sorted_mod_cts = dict(sorted(mod_cts.items(), key=lambda item: item[1],reverse=True))
    for mod, ct in sorted_mod_cts.items():
        print(mod, ct)
    print(f'\nAll external Modules:')
    print('-----------------------')
    if len(ext_mod_cts.keys()) == 0:
        print("None found.")
    for mod, ct in ext_mod_cts.items():
        print(mod, ct)
    print("\nAll Notebooks with Errors:")
    print('--------------------------')
    for path, error in errors.items():
        print(f"{path}: {error}")


def main():
    convert_nbs = 'convert' in os.environ.keys()
    if convert_nbs:
        convert_notebooks()
    else:
        compute_packages()


if __name__ == "__main__":
    main()