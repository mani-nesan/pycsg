import sys
import os
from collections import namedtuple

from OpenGL.GL import *
from OpenGL.GLUT import *
from OpenGL.GLU import *

sys.path.insert(0, os.getcwd())

from csg.core import CSG
from csg.geom import Vertex, Vector

from optparse import OptionParser

Light = namedtuple('Light', ['num', 'ambient', 'diffuse', 'position'])

lights = [
    Light(
        num=GL_LIGHT0,
        ambient=[0.3, 0.3, 0.3, 1.0],
        diffuse=[0.4, 0.4, 0.4, 1.0],
        position=[100.0, 100.0, 100.0, 0.0], # up and right, towards viewer
    ),
    Light(
        num=GL_LIGHT1,
        ambient=[0.3, 0.3, 0.3, 1.0],
        diffuse=[0.4, 0.4, 0.4, 1.0],
        position=[-100.0, 100.0, 100.0, 0.0], # up and left, towards viewer
    ),
    Light(
        num=GL_LIGHT2,
        ambient=[0.3, 0.3, 0.3, 1.0],
        diffuse=[0.4, 0.4, 0.4, 1.0],
        position=[0.0, -100.0, 100.0, 0.0], # down and center, towards user
    ),
]


rot = 0.0

class TestRenderable(object):
    def __init__(self, operation, wireframe):
        self.faces = []
        self.normals = []
        self.vertices = []
        self.colors = []
        self.vnormals = []
        self.list = -1
        self.wireframe = wireframe

        a = CSG.cube()
        b = CSG.cylinder(radius=0.5, start=[0., -2., 0.], end=[0., 2., 0.])
        for p in a.polygons:
            p.shared = [1.0, 0.0, 0.0, 1.0]
        for p in b.polygons:
            p.shared = [0.0, 1.0, 0.0, 1.0]

        recursionlimit = sys.getrecursionlimit()
        sys.setrecursionlimit(10000)
        try:
            if operation == 'subtract':
                polygons = a.subtract(b).toPolygons()
            elif operation == 'union':
                polygons = a.union(b).toPolygons()
            elif operation == 'intersect':
                polygons = a.intersect(b).toPolygons()
            else:
                raise Exception('Unknown operation: \'%s\'' % operation)
        except RuntimeError as e:
            raise RuntimeError(e)
        sys.setrecursionlimit(recursionlimit)

        for polygon in polygons:
            n = polygon.plane.normal
            indices = []
            for v in polygon.vertices:
                pos = [v.pos.x, v.pos.y, v.pos.z]
                if not pos in self.vertices:
                    self.vertices.append(pos)
                    self.vnormals.append([])
                index = self.vertices.index(pos)
                indices.append(index)
                self.vnormals[index].append(v.normal)
            self.faces.append(indices)
            self.normals.append([n.x, n.y, n.z])
            self.colors.append(polygon.shared)

        # setup vertex-normals
        ns = []
        for vns in self.vnormals:
            n = Vector(0.0, 0.0, 0.0)
            for vn in vns:
                n = n.plus(vn)
            n = n.dividedBy(len(vns))
            ns.append([a for a in n])
        self.vnormals = ns

    def render(self):
        if self.wireframe:
            glPolygonMode(GL_FRONT_AND_BACK, GL_LINE)
        if self.list < 0:
            self.list = glGenLists(1)
            glNewList(self.list, GL_COMPILE)

            for n, f in enumerate(self.faces):
                colors = self.colors[n]
                glMaterialfv(GL_FRONT, GL_DIFFUSE, colors)
                glMaterialfv(GL_FRONT, GL_SPECULAR, colors)
                glMaterialf(GL_FRONT, GL_SHININESS, 50.0)
                glColor4fv(colors)

                glBegin(GL_POLYGON)
                glNormal3fv(self.normals[n])
                for i in f:
                    # Disabled vertex normals to make faces clearer.
                    # if sum(x*x for x in self.vnormals[i]) > 1e-4:
                    #     glNormal3fv(self.vnormals[i])
                    glVertex3fv(self.vertices[i])
                glEnd()
            glEndList()
        glCallList(self.list)

renderable = None

def init():
    for light in lights:
        glLightfv(light.num, GL_AMBIENT, light.ambient)
        glLightfv(light.num, GL_DIFFUSE, light.diffuse)
        glLightfv(light.num, GL_POSITION, light.position)
        glEnable(light.num);
    glEnable(GL_LIGHTING);

    # Use depth buffering for hidden surface elimination.
    glEnable(GL_DEPTH_TEST);

    # Setup the view of the cube.
    glMatrixMode(GL_PROJECTION);
    gluPerspective(40.0, 640./480., 1.0, 10.0);
    glMatrixMode(GL_MODELVIEW);
    gluLookAt(0.0, 0.0, 5.0, 0.0, 0.0, 0.0, 0.0, 1.0, 0.)

def display():
    global rot
    glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)

    glPushMatrix()
    glTranslatef(0.0, 0.0, -1.0);
    glRotatef(rot*7, 1.0, 0.0, 0.0);
    glRotatef(rot*13, 0.0, 0.0, 1.0);
    rot += 0.1

    renderable.render()

    glPopMatrix()
    glFlush()
    glutSwapBuffers()
    glutPostRedisplay()

if __name__ == '__main__':
    parser = OptionParser()
    parser.add_option('-o', '--operation', dest='operation',
        type='str', default='subtract')
    parser.add_option('-w', '--wireframe', action='store_true')
    (options, args) = parser.parse_args()

    renderable = TestRenderable(options.operation, options.wireframe)

    glutInit()
    glutInitWindowSize(640,480)
    glutCreateWindow("CSG Test")
    glutInitDisplayMode(GLUT_DEPTH | GLUT_DOUBLE | GLUT_RGBA)
    glutDisplayFunc(display)

    init()

    glutMainLoop()
