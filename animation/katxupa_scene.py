# Mar Azul - Lesson 21 animation: Djodje goes to the talhu and the merkadu to buy katxupa ingredients.
# Run headless:  python3 katxupa_scene.py [--frames A B] [--out DIR] [--preview]
import bpy, math, sys, os
from mathutils import Vector

args = sys.argv
OUT = args[args.index("--out") + 1] if "--out" in args else "/tmp/katxupa_frames"
F0, F1 = (int(args[args.index("--frames") + 1]), int(args[args.index("--frames") + 2])) if "--frames" in args else (1, 288)
PREVIEW = "--preview" in args

bpy.ops.wm.read_factory_settings(use_empty=True)
sc = bpy.context.scene
sc.frame_start, sc.frame_end = 1, 288
sc.render.fps = 24

def hexc(h, a=1.0):
    h = h.lstrip("#"); c = [int(h[i:i+2], 16) / 255 for i in (0, 2, 4)]
    return tuple((x / 12.92 if x <= 0.04045 else ((x + 0.055) / 1.055) ** 2.4) for x in c) + (a,)

MATS = {}
def mat(name, col, rough=0.55, emit=0.0):
    if name in MATS: return MATS[name]
    m = bpy.data.materials.new(name); m.use_nodes = True
    b = m.node_tree.nodes["Principled BSDF"]
    b.inputs["Base Color"].default_value = hexc(col)
    b.inputs["Roughness"].default_value = rough
    if emit:
        b.inputs["Emission Color"].default_value = hexc(col); b.inputs["Emission Strength"].default_value = emit
    MATS[name] = m; return m

def put(obj, m, smooth=True):
    obj.data.materials.append(m)
    if smooth and hasattr(obj.data, "polygons"):
        for p in obj.data.polygons: p.use_smooth = True
    return obj

def sphere(loc, scale, m, seg=24):
    bpy.ops.mesh.primitive_uv_sphere_add(segments=seg, ring_count=seg // 2, location=loc)
    o = bpy.context.object; o.scale = scale; return put(o, m)
def cube(loc, scale, m, bevel=0.0):
    bpy.ops.mesh.primitive_cube_add(location=loc); o = bpy.context.object; o.scale = scale
    if bevel:
        md = o.modifiers.new("b", "BEVEL"); md.width = bevel; md.segments = 3
    return put(o, m, smooth=bool(bevel))
def cyl(loc, r, d, m, rot=(0, 0, 0), v=24):
    bpy.ops.mesh.primitive_cylinder_add(vertices=v, radius=r, depth=d, location=loc, rotation=rot)
    return put(bpy.context.object, m)
def cone(loc, r1, r2, d, m, rot=(0, 0, 0), v=24):
    bpy.ops.mesh.primitive_cone_add(vertices=v, radius1=r1, radius2=r2, depth=d, location=loc, rotation=rot)
    return put(bpy.context.object, m)
def text(body, loc, size, m, rot=(math.radians(80), 0, 0)):
    bpy.ops.object.text_add(location=loc, rotation=rot)
    o = bpy.context.object; o.data.body = body; o.data.size = size
    o.data.align_x = "CENTER"; o.data.extrude = 0.04; o.data.bevel_depth = 0.01
    o.data.materials.append(m); return o
def key(o, f, **kw):
    for k, v in kw.items():
        setattr(o, k, v); o.keyframe_insert(k, frame=f)

# ---------- palette ----------
OCEAN, LIGHT, CREAM = "#0B3D7A", "#7EC8E3", "#F4E3C3"
m_ground = mat("ground", "#EAD6B0", 0.9)
m_cream = mat("cream", CREAM, 0.6)
m_ocean = mat("ocean", OCEAN, 0.4)
m_light = mat("light", LIGHT, 0.4)
m_wood = mat("wood", "#9A6B43", 0.8)
m_red = mat("red", "#C8463D", 0.6)
m_white = mat("white", "#FFFFFF", 0.5)
m_meat = mat("meat", "#D9737A", 0.45)
m_fat = mat("fat", "#F6D7D2", 0.5)
m_saus = mat("saus", "#8E3B2E", 0.4)
m_chick = mat("chick", "#F2C9A0", 0.5)
m_corn = mat("corn", "#F6C431", 0.5)
m_bean = mat("bean", "#7A3B2A", 0.35)
m_bean2 = mat("bean2", "#C9A36A", 0.4)
m_cass = mat("cass", "#8B5E3C", 0.85)
m_swp = mat("swp", "#A2465A", 0.6)
m_pump = mat("pump", "#E8862F", 0.5)
m_onion = mat("onion", "#E7C39A", 0.4)
m_leaf = mat("leaf", "#5E9E50", 0.6)
m_black = mat("black", "#13213A", 0.2)
m_pot = mat("pot", "#2C3442", 0.3)
m_fire = mat("fire", "#FFA436", 0.5, emit=4.0)
m_steam = mat("steam", "#FFFFFF", 0.9)
m_katx = mat("katx", "#C99A3E", 0.4)

# ---------- world ----------
w = bpy.data.worlds.new("w"); sc.world = w; w.use_nodes = True
w.node_tree.nodes["Background"].inputs["Color"].default_value = hexc("#BFE6F5")
w.node_tree.nodes["Background"].inputs["Strength"].default_value = 0.9

bpy.ops.mesh.primitive_plane_add(size=80, location=(0, 0, 0)); put(bpy.context.object, m_ground, False)
# back wall of the street (light blue houses)
for i, (x, col, h) in enumerate([(-9, LIGHT, 4.2), (-4.5, CREAM, 3.6), (0, LIGHT, 4.6), (4.5, CREAM, 3.8), (9, LIGHT, 4.4), (13.5, CREAM, 3.6), (18, LIGHT, 4.2)]):
    cube((x, 5.5, h / 2), (2.2, 0.4, h / 2), mat(f"house{i}", col, 0.8), 0.05)
    for wx in (-0.9, 0.9):
        cube((x + wx, 5.05, h * 0.62), (0.4, 0.06, 0.5), m_ocean, 0.03)

# ---------- stall builder ----------
def stall(x, awning_a, awning_b, label):
    cube((x, 1.2, 0.55), (1.9, 0.75, 0.55), m_wood, 0.04)          # counter
    cube((x, 1.2, 1.12), (1.95, 0.8, 0.03), m_cream, 0.01)          # top
    for px in (-1.85, 1.85):
        cyl((x + px, 1.9, 1.5), 0.06, 3.0, m_wood)
    for k in range(8):                                               # striped awning
        a = cube((x - 1.75 + k * 0.5, 1.3, 2.8), (0.25, 0.75, 0.04), awning_a if k % 2 == 0 else awning_b)
        a.rotation_euler = (math.radians(-28), 0, 0)
    for o in bpy.context.scene.objects: pass
    cube((x, 1.95, 3.45), (1.3, 0.05, 0.35), m_white, 0.05)            # sign board
    text(label, (x, 1.88, 3.3), 0.42, m_ocean, rot=(math.radians(90), 0, 0))

TALHU_X, MERK_X, KITCH_X = -4.0, 4.0, 12.0
stall(TALHU_X, m_red, m_white, "talhu")
stall(MERK_X, m_ocean, m_light, "merkadu")

# ---------- goods ----------
def meat_piece(loc):
    o = sphere(loc, (0.28, 0.2, 0.13), m_meat); f = sphere((loc[0] + 0.14, loc[1], loc[2] + 0.06), (0.1, 0.17, 0.08), m_fat)
    f.parent = o; f.matrix_parent_inverse = o.matrix_world.inverted(); return o
goods_talhu = []
goods_talhu.append(meat_piece((TALHU_X - 1.1, 1.0, 1.28)))
goods_talhu.append(meat_piece((TALHU_X - 0.4, 0.95, 1.28)))
s = cyl((TALHU_X + 0.4, 0.95, 1.25), 0.08, 0.6, m_saus, rot=(0, math.radians(90), 0.3)); goods_talhu.append(s)
s = cyl((TALHU_X + 0.45, 1.15, 1.25), 0.08, 0.6, m_saus, rot=(0, math.radians(90), -0.2))
c = sphere((TALHU_X + 1.2, 1.0, 1.35), (0.32, 0.24, 0.22), m_chick); goods_talhu.append(c)
for k in range(3):   # hanging sausages
    cyl((TALHU_X - 1.2 + k * 0.4, 1.85, 2.45), 0.06, 0.6, m_saus)

goods_merk = []
def corn(loc):
    o = bpy.ops.mesh.primitive_uv_sphere_add(segments=12, ring_count=8, location=loc); o = bpy.context.object
    o.scale = (0.12, 0.12, 0.32); o.rotation_euler = (0, math.radians(80), 0); put(o, m_corn)
    return o
goods_merk.append(corn((MERK_X - 1.3, 0.95, 1.3))); corn((MERK_X - 1.3, 1.2, 1.3)); corn((MERK_X - 1.0, 1.1, 1.42))
bowl = cyl((MERK_X - 0.45, 1.0, 1.22), 0.3, 0.16, m_wood)
for k in range(14):
    sphere((MERK_X - 0.45 + 0.18 * math.cos(k), 1.0 + 0.18 * math.sin(k * 1.7), 1.33), (0.05, 0.04, 0.04), m_bean if k % 2 else m_bean2, 8)
beans = sphere((MERK_X - 0.45, 1.0, 1.38), (0.12, 0.1, 0.07), m_bean, 12); goods_merk.append(beans)
o = sphere((MERK_X + 0.25, 0.95, 1.28), (0.38, 0.09, 0.09), m_cass, 12); o.rotation_euler = (0, 0, 0.4); goods_merk.append(o)
o = sphere((MERK_X + 0.7, 1.15, 1.3), (0.22, 0.13, 0.13), m_swp, 16); goods_merk.append(o)
o = sphere((MERK_X + 1.25, 1.0, 1.43), (0.32, 0.32, 0.25), m_pump); goods_merk.append(o)
st = cyl((MERK_X + 1.25, 1.0, 1.7), 0.03, 0.12, m_leaf); st.parent = o; st.matrix_parent_inverse = o.matrix_world.inverted()
o = sphere((MERK_X + 1.4, 0.6, 1.25), (0.11, 0.11, 0.12), m_onion, 12); goods_merk.append(o)

# ---------- kitchen: pot on a fire ----------
for k in range(5):
    cyl((KITCH_X + 0.55 * math.cos(k * 1.256), 0.8 + 0.55 * math.sin(k * 1.256), 0.12), 0.12, 0.25, mat("stone", "#8A8A8A", 0.9))
fire = cone((KITCH_X, 0.8, 0.35), 0.4, 0.0, 0.7, m_fire)
pot = cyl((KITCH_X, 0.8, 1.0), 0.75, 0.9, m_pot, v=40)
cyl((KITCH_X, 0.8, 1.42), 0.7, 0.06, m_katx, v=40)          # the katxupa inside
fl = bpy.data.lights.new("fire", "POINT"); fl.energy = 120; fl.color = (1, 0.6, 0.25)
flo = bpy.data.objects.new("fireL", fl); sc.collection.objects.link(flo); flo.location = (KITCH_X, 0.2, 0.6)
for f in range(1, 289, 6):
    fire.scale = (1, 1, 1 + 0.18 * math.sin(f * 0.9)); fire.keyframe_insert("scale", frame=f)

# ---------- Djodje (little shark) ----------
dj = bpy.data.objects.new("Djodje", None); sc.collection.objects.link(dj)
def part(o): o.parent = dj; return o
body = part(sphere((0, 0, 0), (0.75, 0.42, 0.42), m_ocean, 32))
part(sphere((0.08, -0.08, -0.12), (0.62, 0.33, 0.3), m_cream, 32))
part(cone((-0.05, 0, 0.42), 0.22, 0.0, 0.45, m_ocean, rot=(0, math.radians(-18), 0)))           # dorsal fin
tail = part(cone((-0.88, 0, 0.12), 0.08, 0.28, 0.45, m_ocean, rot=(0, math.radians(70), 0)))
part(cone((0.15, -0.38, -0.12), 0.14, 0.0, 0.35, m_ocean, rot=(math.radians(60), 0, 0)))       # side fins
part(cone((0.15, 0.38, -0.12), 0.14, 0.0, 0.35, m_ocean, rot=(math.radians(-60), 0, 0)))
for y in (-0.22, 0.22):
    part(sphere((0.52, -0.33 if y < 0 else 0.33, 0.12), (0.09, 0.05, 0.11), m_white, 16))
    part(sphere((0.56, -0.37 if y < 0 else 0.37, 0.12), (0.05, 0.03, 0.07), m_black, 12))
part(sphere((0.68, -0.2, -0.06), (0.1, 0.12, 0.03), m_black, 12)).rotation_euler = (0, 0, 0.6)  # smile
# basket in Djodje's fin
bpy.ops.mesh.primitive_torus_add(major_radius=0.32, minor_radius=0.04, location=(0.25, -0.55, -0.2))
handle = part(put(bpy.context.object, m_wood)); handle.rotation_euler = (math.radians(90), 0, 0)
basket = part(cyl((0.25, -0.55, -0.48), 0.32, 0.32, m_wood))
dj.rotation_euler = (0, 0, math.radians(-90 + 20))   # face camera-ish, swimming to +x

# path: talhu -> merkadu -> kitchen, bobbing like in water
STOPS = [(1, TALHU_X - 5.0), (40, TALHU_X + 2.7), (110, TALHU_X + 2.7), (150, MERK_X + 2.7), (215, MERK_X + 2.7), (250, KITCH_X - 1.9), (288, KITCH_X - 1.9)]
for f, x in STOPS:
    dj.location = (x, -0.4, 1.55); dj.keyframe_insert("location", index=0, frame=f)
for f in range(1, 289, 4):
    dj.location.z = 1.55 + 0.12 * math.sin(f * 0.25); dj.keyframe_insert("location", index=2, frame=f)
    dj.rotation_euler.x = 0.06 * math.sin(f * 0.25 + 1); dj.keyframe_insert("rotation_euler", index=0, frame=f)
for f in range(1, 289, 3):
    tail.rotation_euler = (math.radians(25) * math.sin(f * 0.8), math.radians(70), 0); tail.keyframe_insert("rotation_euler", frame=f)

def basket_at(f):
    sc.frame_set(f); bpy.context.view_layer.update(); return basket.matrix_world.translation.copy() + Vector((0, 0, 0.25))

def hop(o, f_start, dest, dur=14, shrink=True):
    """Item jumps on an arc into dest, then vanishes."""
    start = o.location.copy()
    key(o, f_start, location=start, scale=o.scale.copy())
    sc0 = o.scale.copy()
    for k in range(1, dur + 1):
        t = k / dur
        p = start.lerp(dest, t); p.z += 1.2 * math.sin(math.pi * t)
        o.location = p; o.keyframe_insert("location", frame=f_start + k)
    if shrink:
        key(o, f_start + dur, scale=sc0); key(o, f_start + dur + 3, scale=Vector((0.001, 0.001, 0.001)))

# child objects of a good (fat on meat) follow via parenting
def adopt(children_near, parent):
    pass

# talhu items into basket, frames 50..100
for i, g in enumerate(goods_talhu):
    hop(g, 50 + i * 13, basket_at(50 + i * 13 + 14))
for i, g in enumerate(goods_merk):
    hop(g, 158 + i * 9, basket_at(158 + i * 9 + 14))

# basket goods fly into the pot at the end
pot_top = Vector((KITCH_X, 0.8, 1.55))
fly = []
for i, (mm, sz) in enumerate([(m_meat, (0.2, 0.15, 0.1)), (m_corn, (0.1, 0.1, 0.22)), (m_saus, (0.07, 0.07, 0.25)), (m_pump, (0.18, 0.18, 0.14)), (m_bean, (0.1, 0.08, 0.06)), (m_cass, (0.22, 0.07, 0.07))]):
    b0 = basket_at(254 + i * 4)
    o = sphere(b0, sz, mm, 12)
    key(o, 1, scale=Vector((0.001, 0.001, 0.001))); key(o, 253 + i * 4, scale=Vector((0.001, 0.001, 0.001)))
    key(o, 254 + i * 4, scale=Vector(sz))
    hop(o, 254 + i * 4, pot_top + Vector((0.2 * math.cos(i), 0.2 * math.sin(i), 0)), dur=12)

# steam puffs
for i in range(7):
    o = sphere((KITCH_X + 0.3 * math.sin(i * 2), 0.8, 1.6), (0.2, 0.2, 0.2), m_steam, 12)
    o.visible_shadow = False
    period = 40; off = i * 6
    for cyc in range(8):
        f = 1 + off + cyc * period
        key(o, f, location=Vector((KITCH_X + 0.3 * math.sin(i * 2), 0.8, 1.55)), scale=Vector((0.05, 0.05, 0.05)))
        key(o, f + period - 1, location=Vector((KITCH_X + 0.3 * math.sin(i * 2) + 0.4 * math.sin(i), 0.8 + 0.2, 3.3)), scale=Vector((0.45, 0.45, 0.45)))
        key(o, f + period, scale=Vector((0.001, 0.001, 0.001)))

# title "Katxupa rika!" pops at the end
title = text("Katxupa rika!", (KITCH_X, -0.3, 3.4), 0.7, m_ocean, rot=(math.radians(84), 0, 0))
key(title, 1, scale=Vector((0.001, 0.001, 0.001))); key(title, 262, scale=Vector((0.001, 0.001, 0.001)))
key(title, 270, scale=Vector((1.15, 1.15, 1.15))); key(title, 275, scale=Vector((1, 1, 1)))

# ---------- camera follows Djodje ----------
cam_d = bpy.data.cameras.new("cam"); cam_d.lens = 32
cam = bpy.data.objects.new("cam", cam_d); sc.collection.objects.link(cam); sc.camera = cam
tgt = bpy.data.objects.new("tgt", None); sc.collection.objects.link(tgt)
tc = cam.constraints.new("TRACK_TO"); tc.target = tgt; tc.track_axis = "TRACK_NEGATIVE_Z"; tc.up_axis = "UP_Y"
CAM = [(1, TALHU_X - 1.5), (40, TALHU_X + 0.9), (110, TALHU_X + 0.9), (150, MERK_X + 0.9), (215, MERK_X + 0.9), (250, KITCH_X - 0.8), (288, KITCH_X - 0.8)]
for f, x in CAM:
    cam.location = (x, -7.8, 3.3); cam.keyframe_insert("location", frame=f)
    tgt.location = (x, 1.0, 1.6); tgt.keyframe_insert("location", frame=f)
# ease all keyframes nicely
for o in bpy.data.objects:
    if o.animation_data and o.animation_data.action:
        try:
            for fc in o.animation_data.action.fcurves:
                for kp in fc.keyframe_points: kp.interpolation = "BEZIER"
        except AttributeError:
            pass

# ---------- light ----------
sun = bpy.data.lights.new("sun", "SUN"); sun.energy = 3.2; sun.angle = math.radians(8); sun.color = (1, 0.96, 0.9)
so = bpy.data.objects.new("sun", sun); sc.collection.objects.link(so); so.rotation_euler = (math.radians(50), math.radians(-20), math.radians(-30))

# ---------- render settings ----------
r = sc.render
r.engine = "CYCLES"; sc.cycles.device = "CPU"
sc.cycles.samples = 8 if PREVIEW else 20
sc.cycles.use_denoising = True
sc.cycles.max_bounces = 4
r.resolution_x, r.resolution_y = (480, 270) if PREVIEW else (960, 540)
r.resolution_percentage = 100
r.image_settings.file_format = "PNG"
sc.view_settings.view_transform = "Standard"
os.makedirs(OUT, exist_ok=True)
sc.frame_start, sc.frame_end = F0, F1
r.filepath = os.path.join(OUT, "f_")
bpy.ops.render.render(animation=True)
print("RENDERED", F0, F1)
