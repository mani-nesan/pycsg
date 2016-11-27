import sys
import os

from optparse import OptionParser

sys.path.insert(0, os.getcwd())

from csg.core import CSG


def render_to_stl_files(operation):
    a = CSG.cube()
    b = CSG.cylinder(radius=0.5, start=[0., -2., 0.], end=[0., 2., 0.])

    recursionlimit = sys.getrecursionlimit()
    sys.setrecursionlimit(10000)
    try:
        if not operation:
            raise Exception('Unknown operation: \'%s\'' % operation)
        elif 'subtract'.startswith(operation):
            result = a.subtract(b)
        elif 'union'.startswith(operation):
            result = a.union(b)
        elif 'intersection'.startswith(operation):
            result = a.intersect(b)
        else:
            raise Exception('Unknown operation: \'%s\'' % operation)
    except RuntimeError as e:
        raise RuntimeError(e)
    sys.setrecursionlimit(recursionlimit)

    result.saveSTL('ascii.stl', binary=False)
    result.saveSTL('binary.stl', binary=True)


if __name__ == '__main__':
    parser = OptionParser()
    parser.add_option('-o', '--operation', dest='operation',
        type='str', default='subtract')
    (options, args) = parser.parse_args()
    render_to_stl_files(options.operation)

