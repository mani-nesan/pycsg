import struct
from csg.geom import Polygon


def _float_fmt(val):
    s = ("%.6f" % val).rstrip('0').rstrip('.')
    return '0' if s == '-0' else s


def _stl_write_facet(poly, f, binary=True):
    norm = poly.plane.normal
    v0, v1, v2 = poly.vertices
    if binary:
        data = struct.pack(
            '<3f 3f 3f 3f H',
            norm[0], norm[1], norm[2],
            v0.pos[0], v0.pos[1], v0.pos[2],
            v1.pos[0], v1.pos[1], v1.pos[2],
            v2.pos[0], v2.pos[1], v2.pos[2],
            0
        )
        f.write(data)
    else:
        v0 = " ".join(_float_fmt(x) for x in v0.pos)
        v1 = " ".join(_float_fmt(x) for x in v1.pos)
        v2 = " ".join(_float_fmt(x) for x in v2.pos)
        norm = " ".join(_float_fmt(x) for x in norm)
        vfmt = (
            "  facet normal {norm}\n"
            "    outer loop\n"
            "      vertex {v0}\n"
            "      vertex {v1}\n"
            "      vertex {v2}\n"
            "    endloop\n"
            "  endfacet\n"
        )
        data = vfmt.format(norm=norm, v0=v0, v1=v1, v2=v2)
        f.write(bytes(data, encoding='ascii'))


def save_polys_to_stl_file(polys, filename, binary=True):
    """
    Save polygons in STL file.
    polys - list of Polygons.
    filename - Name fo the STL file to save to.
    binary - if true (default), file is written in binary STL format.  Otherwise ASCII STL format.
    """
    # Convert all polygons to triangles.
    tris = []
    for poly in polys:
        vlen = len(poly.vertices)
        for n in range(1,vlen-1):
            tris.append(
                Polygon([
                    poly.vertices[0],
                    poly.vertices[n%vlen],
                    poly.vertices[(n+1)%vlen],
                ])
            )
    if binary:
        with open(filename, 'wb') as f:
            f.write(b'%-80s' % b'Binary STL Model')
            f.write(struct.pack('<I', len(tris)))
            for tri in tris:
                _stl_write_facet(tri, f, binary=binary)
    else:
        with open(filename, 'wb') as f:
            f.write(b"solid Model\n")
            for tri in tris:
                _stl_write_facet(tri, f, binary=binary)
            f.write(b"endsolid Model\n")
