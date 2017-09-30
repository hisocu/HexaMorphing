import bpy
import mathutils as mu
import numpy as np
from functools import partial
from itertools import repeat
from operator import mul, add


def composite(f, g):
    return (lambda *args: f(g(*args)))


def is_opposite_loop_mappable(target):
    return len(target.polygons) == 1


def is_reverse_base_interpolateble(reversible_axis):
    return reversible_axis in 'xyz'


def calc_coefficient_matrices(values):
    assert len(values) == 3, 'size error'

    def safe_divide(x, y, default=0):
        return default if y == 0 else x / y

    vec = np.array(values)
    anv = abs(safe_divide(vec, np.linalg.norm(vec), np.array([1, 0, 0])))

    sums = sum(anv) - anv
    lens = np.sqrt(np.dot(anv, anv) - anv**2)

    coef_lists = [[safe_divide(anv[i]**2, sums[j] * lens[(3 - i - j) % 3]) if i != j else anv[i] for j in range(3)] for i in range(3)]

    coef_mats = list(map(mu.Matrix, map(np.diag, coef_lists)))

    return [mat if value >= 0 else 0 for mat, value in zip(coef_mats, values)] + [mat if value < 0 else 0 for mat, value in zip(coef_mats, values)]


def mapping(target, base, i):
    return round(i * (len(base.vertices) - 1) / (len(target.vertices) - 1))


def loop_mapping(target, i):
    return target.loops[i % len(target.loops)].vertex_index


def reverse_loop_mapping(target, i):
    return target.loops[-(i % len(target.loops) + 1)].vertex_index


def get_vertex(base, i):
    return mu.Vector(base.vertices[i].co)


def search_approximater(target, src_vertex, dst_vertex):
    mx = 0
    app = 0

    for i in range(len(target.vertices)):
        sm = 0.

        for j in range(len(target.vertices)):
            s = src_vertex(j)
            d = dst_vertex(j + i)
            sm += s.dot(d)

        if i == 0 or mx < sm:
            mx = sm
            app = i

    return app


def search_approximaters(target, bases_vertex, reference_axis):
    x, y, z = mu.Vector((1, 0, 0)), mu.Vector((0, 1, 0)), mu.Vector((0, 0, 1))
    xyz = [x, y, z, -x, -y, -z]

    mat = [mu.Matrix(np.diag([1 if i != j else 0 for j in range(3)])) for i in range(3)] * 2
    rot = [[(xyz[i].rotation_difference(xyz[j]).to_matrix() * mat[i]) if i % 3 != j % 3 else 0 for j in range(6)] for i in range(6)]

    return [[
        search_approximater(target,
                            composite(partial(mul, rot[reference_axis + 3 * i][j]), bases_vertex[reference_axis + 3 * i]),
                            composite(partial(mul, mat[j]), bases_vertex[j])) for j in range(6)
    ] for i in range(2)]


def gen_fb_vertex_getters(target, bases, reference_axis):
    mappers = list(map(partial, repeat(partial(mapping, target)), bases))
    mappers = list(map(partial(composite, partial(loop_mapping, target)), mappers[:3])) +\
            list(map(partial(composite, partial(reverse_loop_mapping, target)), mappers[3:]))

    vgetters = list(map(composite, map(partial, repeat(get_vertex), bases), mappers))
    front, back = search_approximaters(target, vgetters, reference_axis)

    front_mappers = mappers[:3] + list(map(composite, mappers[3:], map(partial, repeat(add), front[3:])))
    back_mappers = list(map(composite, mappers[:3], map(partial, repeat(add), back[:3]))) + mappers[3:]

    front_vgetters = list(map(composite, map(partial, repeat(get_vertex), bases), front_mappers))
    back_vgetters = list(map(composite, map(partial, repeat(get_vertex), bases), back_mappers))

    mats = [mu.Matrix(np.diag([1 if i != j else -1 for j in range(3)])) for i in range(3)]
    front_vgetters = front_vgetters[:3] + list(map(composite, map(partial, repeat(mul), mats), front_vgetters[3:]))
    back_vgetters = back_vgetters[:3] + list(map(composite, map(partial, repeat(mul), mats), back_vgetters[3:]))

    return front_vgetters, back_vgetters


def tri_morph(target, front_vgetters, back_vgetters, reference_axis, values):
    vgetters = front_vgetters if values[reference_axis] >= 0 else back_vgetters

    coef_mats = calc_coefficient_matrices(values)

    axis_mats = [mu.Matrix(np.diag([0 if i != j else 1 for j in range(3)])) for i in range(3)] * 2
    axis_vertices = list(map(composite, map(partial, repeat(mul), coef_mats), map(composite, map(partial, repeat(mul), axis_mats), vgetters)))

    pv = sum([vgetter(0) for vgetter in axis_vertices], mu.Vector((0,) * 3))
    vec = mu.Vector(values).normalized()
    tfpv = pv.project(vec)

    vgetters = list(map(composite, map(partial, repeat(mul), coef_mats), vgetters))

    t_map = composite(partial(loop_mapping, target), partial(mapping, target, target))
    verts = target.vertices

    for i in range(len(verts)):
        ti = t_map(i)
        verts[ti].co = sum([vgetter(i) for vgetter in vgetters], mu.Vector((0,) * 3))
        verts[ti].co -= verts[ti].co.project(vec) - tfpv
