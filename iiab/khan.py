"""Khan Academy Video Utilities"""
import re
import os


def split_path(path):
    """Parse a full file pathname into its components.
    Returns a list of (number, name) tuples.
    number may be None."""
    path = path.rstrip("\n")
    path, ext = os.path.splitext(path)
    split = [None] + re.split('(?: [-] |/)([0-9]?[0-9][0-9]) (?:- )?', path)
    assert(len(split) % 2 == 0)
    c = []
    for i in range(0, len(split), 2):
        if split[i] is not None:
            n = int(split[i])
        else:
            n = None
        c.append((n, split[i + 1]))
    return c


def assign_number_to_top_categories(paths):
    """Assign numbers to the top categories
    returned by split_path for consistency"""
    cats = {}

    def assign_number(path):
        name = path[0][1]
        n = cats.setdefault(name, len(cats) + 1)
        return [(n, name)] + path[1:]
    return map(assign_number, paths)


def categories_to_tree(categories, paths):
    """Takes output from assign_number_to_top_categories and creates a tree
    of dictionaries.  The keys are the numeric index and the values are
    tuples of (name, sub-tree)"""
    d = (None, {})
    for cat, fullpath in zip(categories, paths):
        pos = d
        for idx, (n, name) in enumerate(cat):
            if idx == len(cat) - 1:
                v = fullpath
            else:
                v = {}
            entry = pos[1].setdefault(n, (name, v))
            assert(pos[1][n][0] == name)
            pos = entry
    return d[1]


def load_paths(filename):
    """Load and parse a file of paths into a tree structure"""
    paths = [x.rstrip("\n") for x in open(filename, "r").readlines()]
    cats = [split_path(x) for x in paths]
    cats = assign_number_to_top_categories(cats)
    tree = categories_to_tree(cats, paths)
    return tree


def get(tree, s):
    """Get the tree node or full pathname for a specified
    tuple of indices such as (1, 3, 2).  Returns None if not found."""
    if len(s) == 0:
        return None
    e = tree[s[0]]
    if len(s) == 1:
        return e[1]
    return get(e[1], s[1:])


def find(root, extension=".webm"):
    """File files with specified extension under root"""
    found = []
    cwd = os.getcwd()
    os.chdir(root)
    for path, dirs, files in os.walk('.'):
        path = path[2:]  # Remove './'
        for f in files:
            if extension is None or f[-len(extension):] == extension:
                found.append(os.path.join(path, f))
    os.chdir(cwd)
    return found