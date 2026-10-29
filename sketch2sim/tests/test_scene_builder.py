from backend.pipeline.scene_builder import build_scene, to_world
from backend.schemas import LabeledPart


def part(kind, points):
    return LabeledPart(type=kind, polygon=points, box=(0, 0, 10, 10))


def test_to_world_flips_canvas_y():
    assert to_world((10, 25)) == (10.0, 575.0)


def test_build_scene_assigns_stable_ids_and_goal():
    scene = build_scene([
        part("ball", [(100, 100), (120, 100), (110, 110)]),
        part("ramp", [(100, 300), (300, 200)]),
        part("bell", [(700, 200), (720, 220)]),
    ], "ring the bell")
    assert [p.id for p in scene.parts] == ["ball_1", "ramp_1", "bell_1"]
    assert scene.goal.target == "bell_1"
    assert scene.parts[0].shape.y == 496.6666666666667
