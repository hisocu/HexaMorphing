import bpy
import mathutils as mu
import numpy as np


def usable_opposite(mesh):
    return len(mesh.polygons) == 1


def search_first(loops):
    for i in range(len(loops)):
        if loops[i].vertex_index == 0:
            return i
    raise


def safe_divide(x, y, default=0):
    return default if y == 0 else x / y


def gen_coefficient_matrices(values):
    assert len(values) == 3, 'size error'

    vec = np.array(values)
    zero3x3 = np.zeros((3, 3))

    anv = abs(safe_divide(vec, np.linalg.norm(vec), np.array([1, 0, 0])))

    sums = sum(anv) - anv
    lens = np.sqrt(np.dot(anv, anv) - anv**2)

    coef_lists = [[
        safe_divide(anv[i]**2, sums[j] * lens[(3 - i - j) % 3])
        if i != j else anv[i] for j in range(3)
    ] for i in range(3)]

    coef_mats = list(map(np.diag, coef_lists))

    return [
        mat if value >= 0 else zero3x3
        for mat, value in zip(coef_mats, values)
    ] + [
        mat if value < 0 else zero3x3 for mat, value in zip(coef_mats, values)
    ]


def map_blend(target, bases, blender, mappers):
    for i in range(len(target.vertices)):
        base_cos = [
            base.vertices[mapper(i)].co
            for base, mapper in zip(bases, mappers[1:])
        ]

        target.vertices[mappers[0](i)].co = blender(base_cos)


def planarize(target, bases, values, blender):
    bias_cos = [[
        getattr(base.vertices[0].co, 'xyz' [j]) if i % 3 == j else 0
        for j in range(3)
    ] for i, base in enumerate(bases)]

    pv = blender(bias_cos)
    vec = mu.Vector(values).normalized()
    tfpv = pv.project(vec)

    for tar_vec in target.vertices:
        tar_vec.co -= tar_vec.co.project(vec) - tfpv


def gen_mapper(target, base):
    return (
        lambda i: round(i * (len(base.vertices) - 1) / (len(target.vertices) - 1))
    )


def gen_rev_mapper(target, base):
    mapper = gen_mapper(target, base)

    return (lambda i: -(mapper(i) + 1))


def gen_loop_mapper(target, base):
    fst = search_first(target.loops)
    mapper = gen_mapper(target, base)

    return (lambda i: target.loops[fst + mapper(i)].vertex_index)


def gen_rev_loop_mapper(target, base):
    fst = search_first(target.loops)
    mapper = gen_mapper(target, base)

    return (lambda i: target.loops[-(fst + mapper(i) + 1)].vertex_index)


def gen_blender(values, opp_flags):
    coef_mats = gen_coefficient_matrices(values)
    coef_mats = [[(-1 if flag and i % 3 == j else 1) * mat[j]
                  for j in range(3)]
                 for i, (mat, flag) in enumerate(zip(coef_mats, opp_flags))]

    return (
        lambda bases: mu.Vector(np.einsum('ijk, ik -> j', coef_mats, bases)))


def hexa_morph(target, bases, values, opp_flags=(False, ) * 6):
    bases_list = [
        bases[(i + 3) % 3] if opp_flags[i] else bases[i]
        for i in range(len(bases))
    ]

    blender = gen_blender(values, opp_flags)

    mapper, rev_mapper = (gen_loop_mapper,
                          gen_rev_loop_mapper) if True in opp_flags else (
                              gen_mapper, gen_rev_mapper)

    mappers = [mapper(target, target)] + [
        rev_mapper(target, base) if opp_flag else mapper(target, base)
        for base, opp_flag in zip(bases_list, opp_flags)
    ]

    map_blend(target, bases_list, blender, mappers)

    planarize(target, bases_list, values, blender)
