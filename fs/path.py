"""
fs.path
=======

Useful functions for FS path manipulation.

This is broadly similar to the standard ``os.path`` module but works with
paths in the canonical format expected by all FS objects (forwardslash-separated,
optional leading slash).

"""


def normpath(path):
    """Normalizes a path to be in the format expected by FS objects.

    This function remove any leading or trailing slashes, collapses
    duplicate slashes, replaces forward with backward slashes, and generally
    tries very hard to return a new path string the canonical FS format.
    If the path is invalid, ValueError will be raised.
    
    :param path: path to normalize
    :returns: a valid FS path

    >>> normpath(r"foo\\bar\\baz")
    'foo/bar/baz'

    >>> normpath("/foo//bar/frob/../baz")
    '/foo/bar/baz'

    >>> normpath("foo/../../bar")
    Traceback (most recent call last)
        ...
    ValueError: too many backrefs in path 'foo/../../bar'

    """
    if not path:
        return path
    components = []
    for comp in path.replace('\\','/').split("/"):
        if not comp or comp == ".":
            pass
        elif comp == "..":
            try:
                components.pop()
            except IndexError:
                err = "too many backrefs in path '%s'" % (path,)
                raise ValueError(err)
        else:
            components.append(comp)
    if path[0] in "\\/":
        if not components:
            components = [""]
        components.insert(0, "")
    if isinstance(path, unicode):
        return u"/".join(components)
    else:
        return '/'.join(components)


def iteratepath(path, numsplits=None):
    """Iterate over the individual components of a path.
    
    :param path: Path to iterate over
    :numsplits: Maximum number of splits
    
    """
    path = relpath(normpath(path))
    if not path:
        return []
    if numsplits == None:
        return map(None, path.split('/'))
    else:
        return map(None, path.split('/', numsplits))
        
def recursepath(path, reverse=False):
    """Returns intermediate paths from the root to the given path
    
    :param reverse: reverses the order of the paths
    
    >>> recursepath('a/b/c')
    ['/', u'/a', u'/a/b', u'/a/b/c']
    
    """
    if reverse:
        paths = []
        path = abspath(path).rstrip("/")
        while path:
            paths.append(path)
            path = dirname(path).rstrip("/")
        return paths + ["/"]
    else:   
        paths = [""] + list(iteratepath(path))
        return ["/"] + [u'/'.join(paths[:i+1]) for i in xrange(1,len(paths))]
    
def abspath(path):
    """Convert the given path to an absolute path.

    Since FS objects have no concept of a 'current directory' this simply
    adds a leading '/' character if the path doesn't already have one.

    """
    if not path:
        return u'/'
    if not path.startswith('/'):
        return u'/' + path
    return path


def relpath(path):
    """Convert the given path to a relative path.

    This is the inverse of abspath(), stripping a leading '/' from the
    path if it is present.
    
    :param path: Path to adjust
    
    >>> relpath('/a/b')
    'a/b'

    """
    while path and path[0] == "/":
        path = path[1:]
    return path


def pathjoin(*paths):
    """Joins any number of paths together, returning a new path string.
    
    :param paths: Paths to join are given in positional arguments

    >>> pathjoin('foo', 'bar', 'baz')
    'foo/bar/baz'

    >>> pathjoin('foo/bar', '../baz')
    'foo/baz'

    >>> pathjoin('foo/bar', '/baz')
    '/baz'

    """
    absolute = False
    relpaths = []
    for p in paths:
        if p:
             if p[0] in '\\/':
                 del relpaths[:]
                 absolute = True
             relpaths.append(p)

    path = normpath("/".join(relpaths))
    if absolute and not path.startswith("/"):
        path = u"/" + path
    return path

# Allow pathjoin() to be used as fs.path.join()
join = pathjoin


def pathsplit(path):
    """Splits a path into (head, tail) pair.

    This function splits a path into a pair (head, tail) where 'tail' is the
    last pathname component and 'head' is all preceeding components.
    
    :param path: Path to split

    >>> pathsplit("foo/bar")
    ('foo', 'bar')

    >>> pathsplit("foo/bar/baz")
    ('foo/bar', 'baz')

    """
    split = normpath(path).rsplit('/', 1)
    if len(split) == 1:
        return (u'', split[0])
    return tuple(split)

# Allow pathsplit() to be used as fs.path.split()
split = pathsplit


def dirname(path):
    """Returns the parent directory of a path.

    This is always equivalent to the 'head' component of the value returned
    by pathsplit(path).
    
    :param path: A FS path

    >>> dirname('foo/bar/baz')
    'foo/bar'

    """
    return pathsplit(path)[0]


def basename(path):
    """Returns the basename of the resource referenced by a path.

    This is always equivalent to the 'head' component of the value returned
    by pathsplit(path).
    
    :param path: A FS path

    >>> basename('foo/bar/baz')
    'baz'

    """
    return pathsplit(path)[1]


def issamedir(path1, path2):
    """Return true if two paths reference a resource in the same directory.
    
    :param path1: An FS path
    :param path2: An FS path

    >>> issamedir("foo/bar/baz.txt", "foo/bar/spam.txt")
    True
    >>> issamedir("foo/bar/baz/txt", "spam/eggs/spam.txt")
    False

    """
    return pathsplit(normpath(path1))[0] == pathsplit(normpath(path2))[0]


def isprefix(path1, path2):
    """Return true is path1 is a prefix of path2.
    
    :param path1: An FS path
    :param path2: An FS path
    
    >>> isprefix("foo/bar", "foo/bar/spam.txt")
    True
    >>> isprefix("foo/bar/", "foo/bar")
    True
    >>> isprefix("foo/barry", "foo/baz/bar")
    False
    >>> isprefix("foo/bar/baz/", "foo/baz/bar")
    False

    """
    bits1 = path1.split("/")
    bits2 = path2.split("/")
    while bits1 and bits1[-1] == "":
        bits1.pop()
    if len(bits1) > len(bits2):
        return False
    for (bit1,bit2) in zip(bits1,bits2):
        if bit1 != bit2:
            return False
    return True

def forcedir(path):
    """Ensure the path ends with a trailing /
    
    :param path: An FS path

    >>> forcedir("foo/bar")
    'foo/bar/'
    >>> forcedir("foo/bar/")
    'foo/bar/'

    """

    if not path.endswith('/'):
        return path + '/'
    return path

def frombase(path1, path2):
    if not isprefix(path1, path2):
        raise ValueError("path1 must be a prefix of path2")
    return path2[len(path1):]


class PathMap(object):
    """Dict-like object with paths for keys.

    A PathMap is like a dictionary where the keys are all FS paths.  It allows
    various dictionary operations (e.g. listing values, clearing values) to
    be performed on a subset of the keys sharing some common prefix, e.g.::

        # list all values in the map
        pm.values()

        # list all values for paths starting with "/foo/bar"
        pm.values("/foo/bar")

    Under the hood, a PathMap is a trie-like structure where each level is
    indexed by path name component.  This allows lookups to be performed in
    O(number of path components) while permitting efficient prefix-based
    operations.
    """

    def __init__(self):
        self._map = {}

    def __getitem__(self,path):
        """Get the value stored under the given path."""
        m = self._map
        for name in iteratepath(path):
            try:
                m = m[name]
            except KeyError:
                raise KeyError(path)
        try:
            return m[""]
        except KeyError:
            raise KeyError(path)

    def __contains__(self,path):
        """Check whether the given path has a value stored in the map."""
        try:
            self[path]
        except KeyError:
            return False
        else:
            return True

    def __setitem__(self,path,value):
        """Set the value stored under the given path."""
        m = self._map
        for name in iteratepath(path):
            try:
                m = m[name]
            except KeyError:
                m = m.setdefault(name,{})
        m[""] = value

    def __delitem__(self,path):
        """Delete the value stored under the given path."""
        ms = [[self._map,None]]
        for name in iteratepath(path):
            try:
                ms.append([ms[-1][0][name],None])
            except KeyError:
                raise KeyError(path)
            else:
                ms[-2][1] = name
        try:
            del ms[-1][0][""]
        except KeyError:
            raise KeyError(path)
        else:
            while len(ms) > 1 and not ms[-1][0]:
                del ms[-1]
                del ms[-1][0][ms[-1][1]]

    def get(self,path,default=None):
        """Get the value stored under the given path, or the given default."""
        try:
            return self[path]
        except KeyError:
            return default

    def pop(self,path,default=None):
        """Pop the value stored under the given path, or the given default."""
        ms = [[self._map,None]]
        for name in iteratepath(path):
            try:
                ms.append([ms[-1][0][name],None])
            except KeyError:
                return default
            else:
                ms[-2][1] = name
        try:
            val = ms[-1][0].pop("")
        except KeyError:
            val = default
        else:
            while len(ms) > 1 and not ms[-1][0]:
                del ms[-1]
                del ms[-1][0][ms[-1][1]]
        return val

    def setdefault(self,path,value):
        m = self._map
        for name in iteratepath(path):
            try:
                m = m[name]
            except KeyError:
                m = m.setdefault(name,{})
        return m.setdefault("",value)

    def clear(self,root="/"):
        """Clear all entries beginning with the given root path."""
        m = self._map
        for name in iteratepath(root):
            try:
                m = m[name]
            except KeyError:
                return
        m.clear()

    def iterkeys(self,root="/",m=None):
        """Iterate over all keys beginning with the given root path."""
        if m is None:
            m = self._map
            for name in iteratepath(root):
                try:
                    m = m[name]
                except KeyError:
                    return
        for (nm,subm) in m.iteritems():
            if not nm:
                yield abspath(normpath(root))
            else:
                k = pathjoin(root,nm)
                for subk in self.iterkeys(k,subm):
                    yield subk

    def keys(self,root="/"):
        return list(self.iterkeys(root))

    def itervalues(self,root="/",m=None):
        """Iterate over all values whose keys begin with the given root path."""
        if m is None:
            m = self._map
            for name in iteratepath(root):
                try:
                    m = m[name]
                except KeyError:
                    return
        for (nm,subm) in m.iteritems():
            if not nm:
                yield subm
            else:
                k = pathjoin(root,nm)
                for subv in self.itervalues(k,subm):
                    yield subv

    def values(self,root="/"):
        return list(self.itervalues(root))

    def iteritems(self,root="/",m=None):
        """Iterate over all (key,value) pairs beginning with the given root."""
        if m is None:
            m = self._map
            for name in iteratepath(root):
                try:
                    m = m[name]
                except KeyError:
                    return
        for (nm,subm) in m.iteritems():
            if not nm:
                yield (abspath(normpath(root)),subm)
            else:
                k = pathjoin(root,nm)
                for (subk,subv) in self.iteritems(k,subm):
                    yield (subk,subv)

    def items(self,root="/"):
        return list(self.iteritems(root))

    def iternames(self,root="/"):
        """Iterate over all names beneath the given root path.

        This is basically the equivalent of listdir() for a PathMap - it yields
        the next level of name components beneath the given path.
        """
        m = self._map
        for name in iteratepath(root):
            try:
                m = m[name]
            except KeyError:
                return
        for (nm,subm) in m.iteritems():
            if nm and subm:
                yield nm

    def names(self,root="/"):
        return list(self.iternames(root))

