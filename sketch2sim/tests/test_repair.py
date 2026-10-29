from backend.pipeline.repair import apply_edits
from backend.schemas import Circle, Goal, Part, Physics, Scene


def make_scene():
    return Scene(
        goal=Goal(target="bell_1"),
        parts=[
            Part(id="ball_1", type="ball", shape=Circle(kind="circle", x=10, y=20, r=8), physics=Physics(mass=2)),
            Part(id="bell_1", type="bell", shape=Circle(kind="circle", x=100, y=20, r=12), physics=Physics(static=True)),
        ],
    )


def test_move_edit_is_validated_and_does_not_mutate_input():
    original = make_scene()
    updated = apply_edits(original, [{"op": "move", "part": "ball_1", "dx": 20, "dy": -5}])
    assert original.parts[0].shape.x == 10
    assert updated.parts[0].shape.x == 30
    assert updated.parts[0].shape.y == 15


def test_unknown_edit_is_ignored():
    original = make_scene()
    updated = apply_edits(original, [{"op": "explode", "part": "ball_1"}])
    assert updated == original
