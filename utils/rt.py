#!/usr/bin/python3

from feedmejack import *

if __name__ == '__main__':

    tool = tools.Tool()
    arc = shapes.Plate(xyz.XY(100,100), 100)

    s = [masks.Boundary(lambda x: \
                 (x in shapes.Box(xyz.XY(0,0), xyz.XY(100,100))) \
                 or (x in shapes.Box(xyz.XY(100,100), xyz.XY(200,200))) \
                 or (x in shapes.Box(xyz.XY(0, 50), xyz.XY(50,100)) \
                 and x in shapes.Plate(xyz.XY(50,150), 50)), positive=False)]

    mask = masks.ShapeMask(*s, positive=False)

    ar = rasters.PlateRasterizer(arc, tool, mask)
    #print("ar.points: %s" % (ar.points,))

    header = """\
<html>
<body>

<h1>My first SVG</h1>

<svg width="200" height="200">
"""
    footer="""\
</svg>

</body>
</html>
"""
    points = ""
    t='<circle cx="%0.02f" cy="%0.02f" r="1" stroke-width="0.01" fill="red"/>\n'
    for p in ar.points:
        points += t % (p.x, p.y)

    print("%s%s%s" % (header, points, footer))
