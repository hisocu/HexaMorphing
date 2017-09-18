import bpy
import mathutils as mu
import numpy as np


def usable_opposite(mesh):
    return len(mesh.polygons) == 1


def safe_divide(x, y, default=0):
    return default if y == 0 else x / y


def sign(x):
    return safe_divide(x, abs(x), 1)


def calc_coefficient_matrices(values):
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


def gen_blender(values, *_):
    coef_mats = calc_coefficient_matrices(values)

    return (
        lambda bases: mu.Vector(np.einsum('ijk, ik -> j', coef_mats, bases)))


def gen_rmo_blender(values, opposite_flags, *_):
    coef_mats = calc_coefficient_matrices(values)

    for i in range(6):
        if opposite_flags[i]:
            coef_mats[i][i % 3] *= -1

    return (
        lambda bases: mu.Vector(np.einsum('ijk, ik -> j', coef_mats, bases)))


def gen_rbo_blender(values, opposite_flags, reversible_axis, *_):
    coef_mats = calc_coefficient_matrices(values)

    for i in range(6):
        if opposite_flags[i]:
            coef_mats[i][i % 3] *= -1

        for j in range(3):
            if reversible_axis == 'xyz' [j] and i % 3 != j:
                if opposite_flags[i]:
                    coef_mats[i][j] *= -1

                if opposite_flags[j]:
                    coef_mats[i][j] *= -sign(values[j])
                elif opposite_flags[j + 3]:
                    coef_mats[i][j] *= sign(values[j])

    return (
        lambda bases: mu.Vector(np.einsum('ijk, ik -> j', coef_mats, bases)))


def search_first(loops):
    for i in range(len(loops)):
        if loops[i].vertex_index == 0:
            return i
    raise


def gen_mapper(target, base, *_):
    return (
        lambda i: round(i * (len(base.vertices) - 1) / (len(target.vertices) - 1))
    )


def gen_loop_mapper(target, base, *_):
    fst = search_first(target.loops)
    mapper = gen_mapper(target, base)

    return (
        lambda i: target.loops[(fst + mapper(i)) % len(target.loops)].vertex_index
    )


def gen_rev_loop_mapper(target, base, *_):
    fst = search_first(target.loops)
    mapper = gen_mapper(target, base)

    return (
        lambda i: target.loops[-((fst + mapper(i)) % len(target.loops) + 1)].vertex_index
    )


def is_oppopsite_loop_mappable(target):
    return len(target.polygons) == 1


def is_reverse_mapping_omittable(target, opposite_flags):
    return is_oppopsite_loop_mappable(target) and True in opposite_flags


def is_reverse_base_omittable(target, opposite_flags, reversible_axis):
    return is_reverse_mapping_omittable(target,
                                        opposite_flags) and reversible_axis in 'xyz'


def complement_bases(bases, opposite_flags):
    return [bases[(i + 3) % 6] if opposite_flags[i] else bases[i] for i in range(6)]


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


def hexa_morph(target, bases, values, opposite_flags, reversible_axis):
    blender = gen_blender
    mapper, rev_mapper = (gen_mapper, ) * 2

    if is_reverse_mapping_omittable(target, opposite_flags):
        blender = gen_rmo_blender
        bases = complement_bases(bases, opposite_flags)
        mapper, rev_mapper = gen_loop_mapper, gen_rev_loop_mapper

        if is_reverse_base_omittable(target, opposite_flags, reversible_axis):
            blender = gen_rbo_blender
            rev_mapper = gen_loop_mapper

    blend = blender(values, opposite_flags, reversible_axis)
    maps = [mapper(target, target)] + [
        rev_mapper(target, base) if flag else mapper(target, base)
        for base, flag in zip(bases, opposite_flags)
    ]

    map_blend(target, bases, blend, maps)

    planarize(target, bases, values, blend)
