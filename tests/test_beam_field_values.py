import numpy as np
import pytest
from matplotlib import pyplot as plt

from compmec.strct.element import EulerBernoulli
from compmec.strct.material import Isotropic
from compmec.strct.profile import Circle
from compmec.strct.system import StaticSystem


@pytest.mark.order(9)
# @pytest.mark.dependency(
#     depends=["tests/test_one_circle_beam_charges.py::test_end"], scope="session"
# )
@pytest.mark.dependency()
def test_begin():
    pass


class TestFieldSingleBeamUncharged:
    def setup_system(self):
        self.lenght = 1000
        A = (0, 0, 0)
        B = (self.lenght, 0, 0)
        self.beam = EulerBernoulli([A, B])

        profile = Circle(R=4)
        material = Isotropic(E=210e3, nu=0.3)
        self.beam.section = material, profile

        system = StaticSystem()
        system.add_element(self.beam)
        A = self.beam.path(0)
        boundary_conditions = {"ux": 0, "uy": 0, "tz": 0}
        system.add_BC(A, boundary_conditions)
        self.npts = 11
        self.ts = np.linspace(0, 1, self.npts)
        self.beam.path.knot_insert(self.ts)
        system.run()

    @pytest.mark.order(9)
    @pytest.mark.timeout(5)
    @pytest.mark.dependency(depends=["test_begin"])
    def test_begin(self):
        pass

    @pytest.mark.order(9)
    @pytest.mark.dependency(depends=["TestFieldSingleBeamUncharged::test_begin"])
    def test_position(self):
        self.setup_system()
        curve = self.beam.field("p")  # Position curve
        values_test = curve(self.ts)
        values_good = np.zeros((self.npts, 3))
        values_good[:, 0] = self.lenght * self.ts
        np.testing.assert_allclose(values_test, values_good)

    @pytest.mark.order(9)
    @pytest.mark.dependency(depends=["TestFieldSingleBeamUncharged::test_begin"])
    def test_displacement(self):
        self.setup_system()
        curve = self.beam.field("u")  # Displacement curve
        values_test = curve(self.ts)
        values_good = np.zeros((self.npts, 3))
        np.testing.assert_allclose(values_test, values_good)

    @pytest.mark.order(9)
    @pytest.mark.dependency(depends=["TestFieldSingleBeamUncharged::test_begin"])
    def test_deformed(self):
        self.setup_system()
        curve = self.beam.field("d")  # Deformed curve
        values_test = curve(self.ts)
        values_good = np.zeros((self.npts, 3))
        values_good[:, 0] = self.lenght * self.ts
        np.testing.assert_allclose(values_test, values_good)

    @pytest.mark.order(9)
    @pytest.mark.dependency(depends=["TestFieldSingleBeamUncharged::test_begin"])
    def test_internal_force(self):
        self.setup_system()
        curve = self.beam.field("FI")  # Internal Force
        values_test = curve(self.ts)
        values_good = np.zeros((self.npts, 3))
        np.testing.assert_allclose(values_test, values_good)

    @pytest.mark.order(9)
    @pytest.mark.dependency(depends=["TestFieldSingleBeamUncharged::test_begin"])
    def test_external_force(self):
        self.setup_system()
        curve = self.beam.field("FE")  # External Force
        values_test = curve(self.ts)
        values_good = np.zeros((self.npts, 3))
        np.testing.assert_allclose(values_test, values_good)

    @pytest.mark.order(9)
    @pytest.mark.dependency(depends=["TestFieldSingleBeamUncharged::test_begin"])
    def test_internal_momentum(self):
        self.setup_system()
        curve = self.beam.field("MI")  # Internal Momentum
        values_test = curve(self.ts)
        values_good = np.zeros((self.npts, 3))
        np.testing.assert_allclose(values_test, values_good)

    @pytest.mark.order(9)
    @pytest.mark.dependency(depends=["TestFieldSingleBeamUncharged::test_begin"])
    def test_external_momentum(self):
        self.setup_system()
        curve = self.beam.field("ME")  # External Momentum
        values_test = curve(self.ts)
        values_good = np.zeros((self.npts, 3))
        np.testing.assert_allclose(values_test, values_good)

    @pytest.mark.order(9)
    @pytest.mark.dependency(
        depends=[
            "TestFieldSingleBeamUncharged::test_begin",
            "TestFieldSingleBeamUncharged::test_displacement",
            "TestFieldSingleBeamUncharged::test_position",
            "TestFieldSingleBeamUncharged::test_deformed",
            "TestFieldSingleBeamUncharged::test_internal_force",
            "TestFieldSingleBeamUncharged::test_external_force",
            "TestFieldSingleBeamUncharged::test_internal_momentum",
            "TestFieldSingleBeamUncharged::test_external_momentum",
        ]
    )
    def test_end(self):
        pass


class TestFieldCantileverCircularEulerBeam:
    def setup_system(self):
        self.lenght = 1000
        A = (0, 0, 0)
        B = (self.lenght, 0, 0)
        self.beam = EulerBernoulli([A, B])

        self.E = 210e3
        self.nu = 0.3
        self.d = 8
        profile = Circle(R=self.d / 2)
        material = Isotropic(E=self.E, nu=self.nu)
        self.beam.section = material, profile

        system = StaticSystem()
        system.add_element(self.beam)
        boundary_conditions = {"ux": 0, "uy": 0, "tz": 0}
        system.add_BC(A, boundary_conditions)

        self.applied_force = 10
        system.add_load(B, {"Fy": self.applied_force})

        self.npts = 101
        self.ts = np.linspace(0, 1, self.npts)
        self.beam.path.knot_insert(self.ts)
        system.run()

    @pytest.mark.order(9)
    @pytest.mark.timeout(5)
    @pytest.mark.dependency(
        depends=[
            "test_begin",
            "TestFieldSingleBeamUncharged::test_end",
        ]
    )
    def test_begin(self):
        pass

    @pytest.mark.order(9)
    @pytest.mark.dependency(
        depends=["TestFieldCantileverCircularEulerBeam::test_begin"]
    )
    def test_position(self):
        self.setup_system()
        curve = self.beam.field("p")  # Position curve
        values_test = curve(self.ts)
        values_good = np.zeros((self.npts, 3))
        values_good[:, 0] = self.lenght * self.ts
        np.testing.assert_allclose(values_test, values_good)

    @pytest.mark.order(9)
    @pytest.mark.dependency(
        depends=["TestFieldCantileverCircularEulerBeam::test_begin"]
    )
    def test_displacement(self):
        self.setup_system()
        curve = self.beam.field("u")  # Displacement curve
        values_test = curve(self.ts)
        values_good = np.zeros((self.npts, 3))
        values_good[:, 1] = 64 * self.applied_force * self.lenght**3
        values_good[:, 1] *= 1.5 * self.ts**2 - 0.5 * self.ts**3
        values_good[:, 1] /= 3 * self.E * np.pi * self.d**4
        np.testing.assert_allclose(values_test, values_good)

    @pytest.mark.order(9)
    @pytest.mark.dependency(
        depends=["TestFieldCantileverCircularEulerBeam::test_begin"]
    )
    def test_deformed(self):
        self.setup_system()
        curve = self.beam.field("d")  # Deformed curve
        values_test = curve(self.ts)
        values_good = np.zeros((self.npts, 3))
        values_good[:, 0] = self.lenght * self.ts
        values_good[:, 1] = 64 * self.applied_force * self.lenght**3
        values_good[:, 1] *= 1.5 * self.ts**2 - 0.5 * self.ts**3
        values_good[:, 1] /= 3 * self.E * np.pi * self.d**4
        np.testing.assert_allclose(values_test, values_good)

    @pytest.mark.order(9)
    # @pytest.mark.skip()
    @pytest.mark.dependency(
        depends=["TestFieldCantileverCircularEulerBeam::test_begin"]
    )
    def test_internal_force(self):
        self.setup_system()
        curve = self.beam.field("FI")  # Internal Force
        values_test = curve(self.ts)
        values_good = np.zeros((self.npts, 3))
        values_good[1:-1, 1] = -self.applied_force
        np.testing.assert_allclose(values_test, values_good, atol=1e-6)

    @pytest.mark.order(9)
    @pytest.mark.dependency(
        depends=["TestFieldCantileverCircularEulerBeam::test_begin"]
    )
    def test_external_force(self):
        self.setup_system()
        curve = self.beam.field("FE")  # External Force
        values_test = curve(self.ts)
        values_good = np.zeros((self.npts, 3))
        values_good[0, 1] = -self.applied_force
        values_good[-1, 1] = self.applied_force
        np.testing.assert_allclose(values_test, values_good, atol=1e-6)

    @pytest.mark.order(9)
    # @pytest.mark.skip()
    @pytest.mark.dependency(
        depends=["TestFieldCantileverCircularEulerBeam::test_begin"]
    )
    def test_internal_momentum(self):
        self.setup_system()
        curve = self.beam.field("MI")  # Internal Momentum
        values_test = curve(self.ts)
        values_good = np.zeros((self.npts, 3))
        values_good[1:-1, 2] = -self.applied_force * self.lenght * (1 - self.ts[1:-1])
        np.testing.assert_allclose(values_test, values_good, atol=1e-4)

    @pytest.mark.order(9)
    # @pytest.mark.skip()
    @pytest.mark.dependency(
        depends=["TestFieldCantileverCircularEulerBeam::test_begin"]
    )
    def test_external_momentum(self):
        self.setup_system()
        curve = self.beam.field("ME")  # External Momentum
        values_test = curve(self.ts)
        values_good = np.zeros((self.npts, 3))
        values_good[0, 2] = -self.applied_force * self.lenght
        np.testing.assert_allclose(values_test, values_good, atol=1e-4)

    @pytest.mark.order(9)
    @pytest.mark.dependency(
        depends=[
            "TestFieldCantileverCircularEulerBeam::test_begin",
            "TestFieldCantileverCircularEulerBeam::test_displacement",
            "TestFieldCantileverCircularEulerBeam::test_position",
            "TestFieldCantileverCircularEulerBeam::test_deformed",
            "TestFieldCantileverCircularEulerBeam::test_internal_force",
            "TestFieldCantileverCircularEulerBeam::test_external_force",
            "TestFieldCantileverCircularEulerBeam::test_internal_momentum",
            "TestFieldCantileverCircularEulerBeam::test_external_momentum",
        ]
    )
    def test_end(self):
        pass


@pytest.mark.order(9)
@pytest.mark.dependency(
    depends=[
        "test_begin",
        "TestFieldSingleBeamUncharged::test_end",
        "TestFieldCantileverCircularEulerBeam::test_end",
    ]
)
def test_end():
    pass