import requests
import subprocess
import sys
import argparse
# https://github.com/al45tair/ds_store/
# https://ds-store.readthedocs.io/en/latest/
# https://github.com/electron-userland/electron-builder/blob/master/packages/dmg-builder/vendor/ds_store/store.py
from ds_store import DSStore

def get_ds_store(baseurl, path, tree,verbose=False):
    url = f"{baseurl}{path}/.ds_store"
    r = requests.get(url)
    if path != "":
        tree.append(path)
    if verbose:
        print(url)
    if r.status_code == 200:
        # Valid subtree
        with open(".ds_store", "wb") as f:
            f.write(r.content)
        f.close()

        # We get directory content
        data = get_data(path)

        # We create a new subtree
        subtree = []
        for sub in data:
            subtree.append(get_ds_store(baseurl,path + "/" + sub,[], verbose))
        # We attach this subtree to the main branch when it's over
        tree.append(subtree)

    return tree


def get_data(path):
    d = DSStore.open(".ds_store", "r+")
    data = []
    for i in d:
        if i.filename not in data:
            data.append(i.filename)
    return data

def print_data(tree, padding):
    for subtree in tree:
        if type(subtree) is list:
            print_data(subtree, padding + 1)
        else:
            line = "\t" * padding + subtree
            print(f"\033[{91+padding}m{line}\033[00m")

def parser():
    parser = argparse.ArgumentParser()
    parser.add_argument("-u", "--url", help="URL to the root DS_Store files", required=True)
    parser.add_argument("-v", "--verbose", help="Verbose output", action="store_true")
    args = parser.parse_args()
    return args

if __name__ == "__main__":
    args = parser()

    url = args.url

    print("[+] Running ...")

    tree = get_ds_store(url, "", [], args.verbose)

    print("[*] Finished.")
    if len(tree) == 0:
        print("[-] No sub-folders found.") 
    else:
        print("[+] Final Tree:\n")
        print_data(tree, -2)
        # Cleaning temp file
        subprocess.call(["rm", "-rf", ".ds_store"])

