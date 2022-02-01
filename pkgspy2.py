import os
import json
from modulefinder import ModuleFinder
from stdlib_list import stdlib_list
import subprocess
import sys


# for some reason, the conda site-packages are not on the python2 path; fixing that up ---
import sys
sys.path.append('/opt/conda/envs/python2/lib/python2.7/site-packages')
from stdlib_list import stdlib_list

# todo -- needs to use the specific version of python that the nb file was using...
std_libs = stdlib_list("2.7")


def load_nb_json(path):
    return json.load(open(path, 'r'))


def get_nb_python_version(nb_json, path):
    try:
        kernel = nb_json["metadata"]["kernelspec"]
    except:
        print("Notebook file {} did not have a kernel.".format(path))
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
        print("path {} should be a directory...".format(path))
        sys.exit()
    print("converting notebooks at path, {}".format(path))
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
        # TODO Remove -------------------
        if ' ' not in p:
            continue
        # -------------------------------
        # convert notebook using nbcovert; handle files with spaces in the names
        outdir = '/data/output'
        if version == 'python2':
            outdir = '/data/py2'
        elif version == 'python3':
            outdir = '/data/py3'
        cmd = ['jupyter-nbconvert', '--to', 'script', "{}".format(full_path), '--output-dir', outdir]
        print("command: {}".format(cmd))
        try:
            subprocess.run(cmd, check=True, stdout=subprocess.PIPE)
            print("{} converted with exit code 0.".format(p))
        except subprocess.CalledProcessError:
            print("ERROR on {} (non-zero exit code).".format(p))
    print("final nb stats: ")
    print(nb_stats)


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
        return modules, ext_modules, "Syntax error: {}".format(e)
    except Exception as e:
        print("ERROR: Got exception trying to parse path {}; error: {}; skipping...\n".format(path, e))
        return modules, ext_modules, "Unknown error: {}".format(e)

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
    
    paths_processed.append(path)
    return modules, ext_modules, False


def print_mods(modules, pth):
    for name in modules:
        print(name)


def compute_packages():
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
    errors = {} # path: "error msg"
    total_no_errors = 0
    for p in os.listdir(pth):
        # ignore all non- .py files...        
        if p.endswith('.py'):
            print("Computing packages for {}...".format(p))
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
                    mod_cts[name] = 0
                mod_cts[name] += 1
    total_files = total_no_errors + len(errors.keys())
    total_with_errors = len(errors.keys())
    total_packages_found = len(mod_cts.keys())
    print('*  *  *  *  *  *  *  *  *  *  *  *  *  *  *  *  *  *  *  ')
    print("\nTotals:")
    print("-------")
    print("Total files processed: {}".format(total_files))
    print("Files processed without errors: {}".format(total_no_errors))
    print("Files processed with errors: {}".format(total_with_errors))
    print('Total unique packages found: {}'.format(total_packages_found))
    print("\nAll known modules, with counts of notebooks using them")
    print('------------------------------------------------------')
    for mod, ct in mod_cts.items():
        print(mod, ct)
    print('\nAll external Modules:')
    print('-----------------------')
    if len(ext_mod_cts.keys()) == 0:
        print("None found.")
    for mod, ct in ext_mod_cts.items():
        print(mod, ct)
    print("\nAll Notebooks with Errors:")
    print('--------------------------')
    for path, error in errors.items():
        print("{}: {}".format(path, error))

def main():
    convert_nbs = 'convert' in os.environ.keys()
    if convert_nbs:
        convert_notebooks()
    else:
        compute_packages()


if __name__ == "__main__":
    main()