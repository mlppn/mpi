from shapely.geometry import Polygon, Point, LineString, box
import matplotlib.pyplot as plt
from matplotlib.patches import Polygon as MplPolygon
from matplotlib.collections import PatchCollection
import polygenerator as polygenerator
import math as math
import numpy as np
import random as rd
import sys
from shapely.ops import unary_union
import copy
sys.setrecursionlimit(10**6)

def display_poly(poly):
    fig, ax = plt.subplots()
    patches = []
    patch = MplPolygon(list(poly.exterior.coords), closed=True, edgecolor='black',    facecolor='lightblue')
    patches.append(patch)
    for interior in poly.interiors:
        hole_patch = MplPolygon(list(interior.coords), closed=True, edgecolor='black', facecolor='white')
        patches.append(hole_patch)
    p = PatchCollection(patches, match_original=True)
    ax.add_collection(p)
    ax.set_xlim(-0.05, 1.05)
    ax.set_ylim(-0.05, 1.05)
    ax.set_aspect('equal')
    ax.set_title("Polygone avec trou (non couvrable uniquement depuis les bords)")
    plt.show()

### Triangulation

def gen_poly_simple(n):
    '''génère un polygone simple à n sommets'''
    return(Polygon(polygenerator.random_polygon(n),[]))

def dist(p1,p2):
    return((p1[0]-p2[0])**2+(p1[1]-p2[1])**2)**(1/2)


def internal_angle(p1,p2,p3):
    """
        Counter clock wise angle (radians) from normalized 2D vectors a to b
    """
    a =   [p1[0] - p2[0], p1[1] - p2[1]]
    b =   [p3[0] - p2[0], p3[1] - p2[1]]
    dot = a[0]*b[0] + a[1]*b[1]
    det = a[0]*b[1] - a[1]*b[0]
    angle = np.arctan2(det, dot)
    if angle<0.0 :
        angle = 2.0*np.pi + angle
    return 2.0*np.pi-angle

def point_in_trig(L, p1,p2,p3):
    # preuve (idée)
    val = (-1,-1)
    ux, uy =   p2[0] - p1[0], p2[1] - p1[1]
    vx, vy =   p3[0] - p2[0], p3[1] - p2[1]
    wx, wy =   p1[0] - p3[0], p1[1] - p3[1]
    for e in L:
        apx, apy = e[0] - p1[0], e[1] - p1[1]
        bpx, bpy = e[0] - p2[0], e[1] - p2[1]
        cpx, cpy = e[0] - p3[0], e[1] - p3[1]
        A = ux * apy - uy * apx
        B = vx * bpy - vy * bpx
        C = wx * cpy - wy * cpx
        if A*B > 0 and A*C > 0 and B*C > 0 :
            val = e
            break
    return(val)


def ear_clip_triangulation(poly):
    S = list(poly.exterior.coords)[:-1]
    n = len(S)
    if n == 3:
        return([list(poly.exterior.coords)])
    else:
        for i in range(n):
            if internal_angle(S[(i-1)%n], S[i%n], S[(i+1)%n])<= np.pi :
                if point_in_trig(S,S[(i-1)%n], S[i%n], S[(i+1)%n] ) == (-1,-1):
                    T = [ [S[(i-1)%n], S[i%n], S[(i+1)%n],S[(i-1)%n]]]
                    a = S.pop(i%n)
                    return(T + ear_clip_triangulation(Polygon(S)))

def display_trig_poly_simple(poly):
    T = ear_clip_triangulation(poly)
    print(poly)
    fig, ax = plt.subplots()
    patches = []
    patch = MplPolygon(list(poly.exterior.coords), closed=True, edgecolor='black',    facecolor='lightblue')
    patches.append(patch)
    p = PatchCollection(patches, match_original=True)
    ax.add_collection(p)
    ax.set_xlim(-0.05, 1.05)
    ax.set_ylim(-0.05, 1.05)
    for i, other in enumerate(T):
        ox, oy = zip(*other)
        ax.plot(ox, oy, color='red', linewidth=2)
    ax.set_aspect('equal')
    ax.set_title("Polygone triangulé")
    plt.show()


def estOreille(S,p1,p2,p3):
    return(internal_angle(p1,p2,p3)<= np.pi and point_in_trig(S, p1,p2,p3) == (-1,-1) )

### Colorisation

def graph_colo(poly):
    oreilles = []
    sommets = list(poly.exterior.coords)[:-1]
    n = len(sommets)
    C = {}
    for i in range( len(sommets)):
        C[sommets[i]] = i
    colors = [-1 for i in range (len(sommets))]
    while n > 3:
        for i in range(n):
            if estOreille(sommets,sommets[(i-1)%n], sommets[(i)%n], sommets[(i+1)%n]):
                oreilles.append([sommets[(i-1)%n], sommets[(i)%n], sommets[(i+1)%n]])
                sommets.pop(i)
                n = n-1
                break
    colors[C[sommets[0]]] = 0
    colors[C[sommets[1]]] = 1
    colors[C[sommets[2]]]= 2
    while oreilles != []:
        o = oreilles.pop()
        print(colors[C[o[0]]],colors[C[o[2]]] )
        colors[C[o[1]]] = 3 -colors[C[o[0]]] - colors[C[o[2]]]
    return(colors)

def display_3colo(poly):
    T = ear_clip_triangulation(poly)
    colo = graph_colo(poly)
    print(colo)
    S = list(poly.exterior.coords)[:-1]
    C1 = []
    C2 = []
    C3 = []
    for i in range(len(S)):
        if colo[i] == 1:
            C1.append(S[i])
        if colo[i] == 2:
            C2.append(S[i])
        if colo[i] == 0:
            C3.append(S[i])
    fig, ax = plt.subplots()
    patches = []
    patch = MplPolygon(list(poly.exterior.coords), closed=True, edgecolor='black',    facecolor='lightblue')
    patches.append(patch)
    for interior in poly.interiors:
        hole_patch = MplPolygon(list(interior.coords), closed=True, edgecolor='black', facecolor='white')
        patches.append(hole_patch)
    p = PatchCollection(patches, match_original=True)
    ax.add_collection(p)
    ax.set_xlim(-0.05, 1.05)
    ax.set_ylim(-0.05, 1.05)
    for i, other in enumerate(T):
        ox, oy = zip(*other)
        ax.plot(ox, oy, color='red', linewidth=0.5)
    px, py = zip(*C1)
    ax.scatter(px, py, color='orange', s=60, zorder=5, label="Points mis en valeur")
    px, py = zip(*C2)
    ax.scatter(px, py, color='blue', s=60, zorder=5, label="Points mis en valeur")
    px, py = zip(*C3)
    ax.scatter(px, py, color='green', s=60, zorder=5, label="Points mis en valeur")
    ax.set_aspect('equal')
    ax.set_title("Polygone triangulé")
    plt.show()


def résolution(poly):
    oreilles = []
    sommets = list(poly.exterior.coords)[:-1]
    n = len(sommets)
    colors = {}
    cam = []
    while n > 3:
        for i in range(n):
            if estOreille(sommets,sommets[(i-1)%n], sommets[(i)%n], sommets[(i+1)%n]):
                oreilles.append([sommets[(i-1)%n], sommets[(i)%n], sommets[(i+1)%n]])
                sommets.pop(i)
                n = n-1
                break
    colors[sommets[0]] = 0
    colors[sommets[1]] = 1
    colors[sommets[2]] = 2
    while oreilles != []:
        o = oreilles.pop()
        colors[o[1]] = 3 -colors[o[0]] - colors[o[2]]
    nb = [0,0,0]
    for el in colors:
        nb[colors[el]] += 1
    c = indmin(nb)
    for el in colors:
        if colors[el] == c:
            cam.append(el)
    return(cam)


def display_cam_poly_simple(poly):
    cam = résolution(poly)
    print(len(cam))
    fig, ax = plt.subplots()
    patches = []
    patch = MplPolygon(list(poly.exterior.coords), closed=True, edgecolor='black',    facecolor='lightblue')
    patches.append(patch)
    for interior in poly.interiors:
        hole_patch = MplPolygon(list(interior.coords), closed=True, edgecolor='black', facecolor='white')
        patches.append(hole_patch)
    p = PatchCollection(patches, match_original=True)
    ax.add_collection(p)
    ax.set_xlim(-0.05, 1.05)
    ax.set_ylim(-0.05, 1.05)
    px, py = zip(*cam)
    ax.scatter(px, py, color='red', s=60, zorder=5, label="Points mis en valeur")
    ax.set_aspect('equal')
    ax.set_title("Polygone et ces caméras (triangulation)")
    plt.show()

### Cas des polygones Orthogonaux

from shapely.geometry import box, Polygon
from shapely.ops import unary_union


def gen_poly_ortho(nr, nh):
    rectangles = []
    for _ in range(nr):
        x = rd.random()
        x1 = rd.random()
        y = rd.random()
        y1 = rd.random()
        rectangles.append(box(min(x,x1),min(y,y1),max(x,x1), max(y,y1)))
    base_poly = unary_union(rectangles)
    if not isinstance(base_poly, Polygon):
        base_poly = max(base_poly.geoms, key=lambda p: p.area)
    holes = []
    if nh != 0:
        attempts = 0
        while len(holes) < nh and attempts < 50:
            x = rd.uniform(base_poly.bounds[0], base_poly.bounds[2] - 1)
            y = rd.uniform(base_poly.bounds[1], base_poly.bounds[3] - 1)
            w = rd.uniform(0.5, 2)
            h = rd.uniform(0.5, 2)
            candidate = box(x, y, x + w, y + h)
            if base_poly.contains(candidate):
                holes.append(candidate)
            attempts += 1

        if holes:
            hole_union = unary_union(holes)
            base_poly = base_poly.difference(hole_union)
    return base_poly



### Cas générale

def gen_poly_trou(n, nb_trou): # à améliorer grandement stp
    p = polygenerator.random_polygon(n)
    H = Polygon([],[])
    P = Polygon(p,[])
    i = 0
    while i !=  nb_trou:
        j = rd.randint(3,3) # on affinera
        h = []
        while len(h) != j:
            x, y = rd.random(), rd.random()
            q = Point(x,y)
            if P.contains(q):
                h.append(q)
        if Polygon(h).within(P):
            H = H.union(Polygon(h))
            i += 1
    hole = [list(p.exterior.coords) for p in H.geoms]
    return(Polygon(p, hole))

def cp_visi1(poly):
    # on prend les points du contour + ceux des conturs du bord
    p =  list(poly.exterior.coords)[1:]
    for interior in poly.interiors:
        h = list(interior.coords)[1:]
        p += h
    return(p)



### Minimun Dominating Set

def indmax(L):
    max = L[0]
    n = len(L)
    ind = 0
    i = 0
    while i != n:
        a = L[i]
        if a > max:
            max = a
            ind = i
        i += 1
    return(ind)

def indmin(L):
    min = L[0]
    n = len(L)
    ind = 0
    i = 0
    while i != n:
        a = L[i]
        if a < min:
            min = a
            ind = i
        i += 1
    return(ind)

def glouton(grph):
    n = len(grph)
    L_cam = []
    f = []
    f0 = [0 for i in range(n)]
    for i in range(n):
        v = 0
        for j in range(n):
            if grph[i][j]:
                v += 1
        f.append(v)
    while f != f0:
        i = indmax(f)
        f[i] = 0
        L_cam.append(i)
        for j in range(n):
            if grph[i][j]:
                f[j] = f[j] - 1
                grph[i][j] = False
                grph[j][i] = False
    return(L_cam)

def Matching(grph):
    n = len(grph)
    L_cam = []
    while grph.any() == True:
        a = []
        for i in range(n):
            for j in range(n):
                if grph[i][j]:
                    a = [i, j]
                    break
        for k in range(n):
            i = a[0]
            j = a[1]
            grph[i][k] = False
            grph[k][i] = False
            grph[j][k] = False
            grph[k][j] = False
        L_cam.append(i)
        L_cam.append(j)
    return(L_cam)

def display_cam_MVC(poly, pts_type, cover_type):
    cam = cover_type(graph_visi(poly, pts_type))
    L = pts_type(poly)
    pts = [L[i] for i in cam]
    fig, ax = plt.subplots()
    patches = []
    patch = MplPolygon(list(poly.exterior.coords), closed=True, edgecolor='black',    facecolor='lightblue')
    patches.append(patch)
    for interior in poly.interiors:
        hole_patch = MplPolygon(list(interior.coords), closed=True, edgecolor='black', facecolor='white')
        patches.append(hole_patch)
    p = PatchCollection(patches, match_original=True)
    ax.add_collection(p)
    ax.set_xlim(-0.05, 1.05)
    ax.set_ylim(-0.05, 1.05)
    px, py = zip(*pts)
    ax.scatter(px, py, color='red', s=60, zorder=5, label="Points mis en valeur")
    ax.set_aspect('equal')
    ax.set_title(f"Polygone et ces caméras ({cover_type.__name__})")
    plt.show()


def compare(n, m, b):
    for i in range(n, m):
        L = []
        for j in range(b):
            poly = gen_poly_simple(i)
            grph = graph_visi(poly, cp_visi1)
            grph1 = copy.deepcopy(grph)
            v1 = len(glouton(grph))
            v2 = len(Matching(grph1))
            L.append(v1/v2) # glouton / matching
        t = sum(L)/b
        print(i, t)

def poly_edges(poly):
    edges = []
    coords = list(poly.exterior.coords)
    edges += [[coords[i], coords[i + 1]] for i in range(len(coords) - 1)]
    for interior in poly.interiors:
        coords = list(interior.coords)
        edges += [[coords[i], coords[i + 1]] for i in range(len(coords) - 1)]
    return(edges)
###
def box_of_seg(seg):
    b = []
    xs0, ys0 = seg[0]
    xs1, ys1 = seg[1]
    Xs, Ys = max(xs0, xs1), max(ys0, ys1)
    xs, ys = min(xs0, xs1), min(ys0, ys1)
    B = []
    b.append([xs, ys])
    b.append([Xs, Ys])
    return(b)

def Bounding_box_inter(b0,b1):
    B0 = b0
    B1 = b1
    if b0 == 0 and b1 == 0:
        return(0)
    if b0 == 0:
        return(b1)
    if b1 == 0:
        return(b0)
    if b0[1] == False:
        B0[0] = box_of_seg(b0[0])
    if b1[1] == False:
        B1[0] = box_of_seg(b1[0])
    x0, y0 = B0[0][0]
    X0, Y0 = B0[0][1]
    x1, y1 = B1[0][0]
    X1, Y1 = B1[0][1]
    xn, yn = min(x0, x1), min(y0, y1)
    Xn, Yn = max(X0, X1), max(Y0, Y1)
    return([[[xn, yn], [Xn, Yn]], True])

def bb_tree(seglist):
    n = len(seglist)
    k = math.ceil(math.log(n)/math.log(2))
    tree = [ 0 for i in range(2**(k+1))]
    for i in range(n):
        tree[2**k+i] = [[seglist[i][0], seglist[i][1]], False]
    for j in range(1,2**k ):
        i = 2**k - j
        fg = tree[2*i]
        fd = tree[2*i+1]
        tree[i] = Bounding_box_inter(fg, fd)
    return(tree)

def cut(seg, bb):
    sega = box_of_seg(seg)
    xs, ys = sega[0]
    Xs, Ys = sega[1]
    xb, yb = bb[0]
    Xb, Yb = bb[1]
    if xs >= Xb or Xs<=xb or ys>=Yb or Ys<=yb:
        return(False)
    else:
        return(True)

def intersect(seg, bb):
    box = box_of_seg(seg)
    xs0, ys0 = box[0]
    xs1, ys1 = box[1]
    Xs, Ys = max(xs0, xs1), max(ys0, ys1)
    xs, ys = min(xs0, xs1), min(ys0, ys1)
    xb, yb = bb[0]
    Xb, Yb = bb[1]
    if xs >= Xb or Xs<=xb or ys>=Yb or Ys<=yb:
        return(False)
    else:
        o1 = orientation(seg[0], seg[1], bb[0])
        o2 = orientation(seg[0], seg[1], bb[1])
        o3 = orientation(bb[0], bb[1], seg[0])
        o4 = orientation(bb[0], bb[1], seg[1])
        return o1 != o2 and o3 != o4

def dfs (tree, seg):## renvoie False si seg coupe un segment de tree
    pile = [1]
    val = True
    while val and pile !=[]:
        s = pile.pop()
        if tree[s][1]:
            if tree[2*s] != 0:
                if cut(seg, tree[2*s][0]):
                    pile.append(2*s)
            if tree[2*s+1] != 0:
                if cut(seg, tree[2*s+1][0]):
                    pile.append(2*s+1)
        else:
            if intersect(seg, tree[s][0]):
                val = False
    return(val)





def orientation(p, q, r):
    """1 = horaire, 2 = anti-horaire"""
    val = (q[1] - p[1]) * (r[0] - q[0]) - (q[0] - p[0]) * (r[1] - q[1])
    return 1 if val > 0 else 2


def graph_visi_bis(poly, pts_type):
    # ça marche que pour les poly simples
    display_poly(poly)
    L = pts_type(poly)
    n = len(L)
    edges = poly_edges(poly)
    grph = np.zeros((n,n),bool)
    tree = bb_tree(edges)
    for i in range(n):
        p1 = L[i-1]
        p2 = L[i]
        p3 = L[(i+1)%n]
        for j in range(i):
            seg = [L[i], L[j]]
            seg.sort()
            if seg in edges or [seg[1], seg[0]] in edges:
                grph[i][j] = True
                grph[j][i] = True
            else:
                if internal_angle(p1,p2,L[j]) < internal_angle(p1,p2,p3):
                    val = dfs(tree, seg)
                    grph[i][j] = val
                    grph[j][i] = val
    plt.imshow(grph)
    plt.show()
    return(grph)


def graph_visi(poly, pts_type):
    L = pts_type(poly)
    n = len(L)
    grph = np.zeros((n,n),bool)
    for i in range(n):
        for j in range(i):
            seg = LineString([L[i], L[j]])
            val = poly.covers(seg)
            grph[i][j] = val
            grph[j][i] = val
    # plt.imshow(grph)
    # plt.show()
    return(grph)



def compare_visi(poly, pts_type):
    lst = rapid_out(poly)
    t1 = time.time()
    A = graph_visi(poly, lst)
    t2 = time.time()
    B = graph_visi_bis(poly, lst)
    t3 = time.time()
    return((t2-t1)/(t3-t2))










































