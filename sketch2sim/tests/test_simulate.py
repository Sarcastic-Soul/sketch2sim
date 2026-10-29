from backend.pipeline.simulate import simulate
from backend.schemas import Circle, Goal, Part, Physics, Scene, Segment, Sensor


def scene_for(distance):
    return Scene(parts=[
        Part(id="ball_1", type="ball", shape=Circle(kind="circle", x=100, y=500, r=12), physics=Physics(mass=2, friction=0.2)),
        Part(id="floor", type="ramp", shape=Segment(kind="segment", a=(0, 0), b=(800, 0), thickness=8), physics=Physics(static=True)),
        Part(id="bell_1", type="bell", shape=Sensor(kind="sensor", x=100 + distance, y=500, r=25), physics=Physics(static=True)),
    ], goal=Goal(target="bell_1"))


def test_simulation_reaches_nearby_bell():
    result = simulate(scene_for(0))
    assert result.success is True


def test_simulation_reports_short_scene():
    result = simulate(scene_for(650))
    assert result.success is False
    assert result.metrics["closest_ball_bell_dist"] >= 0
