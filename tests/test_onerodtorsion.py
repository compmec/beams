import numpy as np
import pytest

from compmec.strct.element import EulerBernoulli
from compmec.strct.material import Isotropic
from compmec.strct.section import Circle
from compmec.strct.solver import solve


@pytest.mark.order(2)
@pytest.mark.dependency(
    depends=[
        "tests/test_solver.py::test_end",
        "tests/test_material.py::test_end",
        "tests/test_structural1D.py::test_end",
        "tests/test_section.py::test_circle",
    ],
    scope="session",
)
def test_begin():
    pass


@pytest.mark.order(2)
@pytest.mark.timeout(2)
@pytest.mark.dependency(depends=["test_begin"])
def test_torsionXcircle():
    ntests = 10
    for i in range(ntests):
        E = np.random.uniform(1, 2)
        nu = np.random.uniform(0, 0.49)
        d = np.random.uniform(1, 2)
        L = np.random.uniform(1, 2)
        T = np.random.uniform(-1, 1)

        steel = Isotropic(E=E, nu=nu)
        circle = Circle(R=d / 2, nu=nu)
        A = (0, 0, 0)
        B = (L, 0, 0)
        bar = EulerBernoulli([A, B])
        bar.material = steel
        bar.section = circle

        U = np.empty((2, 6), dtype="object")
        F = np.zeros((2, 6))
        U[0, :] = 0
        F[1, 3] = T

        K = bar.stiffness_matrix()
        Utest, Ftest = solve(K, F, U)

        tx = 64 * T * L * (1 + nu) / (np.pi * E * d**4)
        Ugood = np.array([[0, 0, 0, 0, 0, 0], [0, 0, 0, tx, 0, 0]])
        Fgood = np.array([[0, 0, 0, -T, 0, 0], [0, 0, 0, T, 0, 0]])

        np.testing.assert_almost_equal(Utest, Ugood)
        np.testing.assert_almost_equal(Ftest, Fgood)


@pytest.mark.order(2)
@pytest.mark.timeout(2)
@pytest.mark.dependency(depends=["test_begin", "test_torsionXcircle"])
def test_torsionYcircle():
    ntests = 10
    for i in range(ntests):
        E = np.random.uniform(1, 2)
        nu = np.random.uniform(0, 0.49)
        d = np.random.uniform(1, 2)
        L = np.random.uniform(1, 2)
        T = np.random.uniform(-1, 1)

        steel = Isotropic(E=E, nu=nu)
        circle = Circle(R=d / 2, nu=nu)
        A = (0, 0, 0)
        B = (0, L, 0)
        bar = EulerBernoulli([A, B])
        bar.material = steel
        bar.section = circle

        U = np.empty((2, 6), dtype="object")
        F = np.zeros((2, 6))
        U[0, :] = 0
        F[1, 4] = T

        K = bar.stiffness_matrix()
        Utest, Ftest = solve(K, F, U)

        ty = 64 * T * L * (1 + nu) / (np.pi * E * d**4)
        Ugood = np.array([[0, 0, 0, 0, 0, 0], [0, 0, 0, 0, ty, 0]])
        Fgood = np.array([[0, 0, 0, 0, -T, 0], [0, 0, 0, 0, T, 0]])

        np.testing.assert_almost_equal(Utest, Ugood)
        np.testing.assert_almost_equal(Ftest, Fgood)


@pytest.mark.order(2)
@pytest.mark.timeout(2)
@pytest.mark.dependency(depends=["test_begin", "test_torsionXcircle"])
def test_torsionZcircle():
    ntests = 10
    for i in range(ntests):
        E = np.random.uniform(1, 2)
        nu = np.random.uniform(0, 0.49)
        d = np.random.uniform(1, 2)
        L = np.random.uniform(1, 2)
        T = np.random.uniform(-1, 1)

        steel = Isotropic(E=E, nu=nu)
        circle = Circle(R=d / 2, nu=nu)
        A = (0, 0, 0)
        B = (0, 0, L)
        bar = EulerBernoulli([A, B])
        bar.material = steel
        bar.section = circle

        U = np.empty((2, 6), dtype="object")
        F = np.zeros((2, 6))
        U[0, :] = 0
        F[1, 5] = T

        K = bar.stiffness_matrix()
        Utest, Ftest = solve(K, F, U)

        tz = 64 * T * L * (1 + nu) / (np.pi * E * d**4)
        Ugood = np.array([[0, 0, 0, 0, 0, 0], [0, 0, 0, 0, 0, tz]])
        Fgood = np.array([[0, 0, 0, 0, 0, -T], [0, 0, 0, 0, 0, T]])

        np.testing.assert_almost_equal(Utest, Ugood)
        np.testing.assert_almost_equal(Ftest, Fgood)


@pytest.mark.order(2)
@pytest.mark.timeout(2)
@pytest.mark.dependency(depends=["test_torsionXcircle", "test_torsionYcircle"])
def test_torsionXYcircle():
    ntests = 10
    for i in range(ntests):
        E = np.random.uniform(1, 2)
        nu = np.random.uniform(0, 0.49)
        d = np.random.uniform(1, 2)
        L = np.random.uniform(1, 2)
        T = np.random.uniform(-1, 1)
        r = np.random.uniform(-1, 1, 3) * [True, True, False]
        r /= np.linalg.norm(r)

        steel = Isotropic(E=E, nu=nu)
        circle = Circle(R=d / 2, nu=nu)
        A = (0, 0, 0)
        B = L * r
        bar = EulerBernoulli([A, B])
        bar.material = steel
        bar.section = circle

        U = np.empty((2, 6), dtype="object")
        F = np.zeros((2, 6))
        U[0, :] = 0
        F[1, 3:] = T * r

        K = bar.stiffness_matrix()
        Utest, Ftest = solve(K, F, U)

        tr = 64 * T * L * (1 + nu) / (np.pi * E * d**4)
        Ugood = np.zeros((2, 6))
        Fgood = np.zeros((2, 6))
        Ugood[1, 3:] = tr * r
        Fgood[0, 3:] = -T * r
        Fgood[1, 3:] = T * r

        np.testing.assert_almost_equal(Utest, Ugood)
        np.testing.assert_almost_equal(Ftest, Fgood)


@pytest.mark.order(2)
@pytest.mark.timeout(2)
@pytest.mark.dependency(depends=["test_torsionYcircle", "test_torsionZcircle"])
def test_torsionYZcircle():
    ntests = 10
    for i in range(ntests):
        E = np.random.uniform(1, 2)
        nu = np.random.uniform(0, 0.49)
        d = np.random.uniform(1, 2)
        L = np.random.uniform(1, 2)
        T = np.random.uniform(-1, 1)
        r = np.random.uniform(-1, 1, 3) * [False, True, True]
        r /= np.linalg.norm(r)

        steel = Isotropic(E=E, nu=nu)
        circle = Circle(R=d / 2, nu=nu)
        A = (0, 0, 0)
        B = L * r
        bar = EulerBernoulli([A, B])
        bar.material = steel
        bar.section = circle

        U = np.empty((2, 6), dtype="object")
        F = np.zeros((2, 6))
        U[0, :] = 0
        F[1, 3:] = T * r

        K = bar.stiffness_matrix()
        Utest, Ftest = solve(K, F, U)

        tr = 64 * T * L * (1 + nu) / (np.pi * E * d**4)
        Ugood = np.zeros((2, 6))
        Fgood = np.zeros((2, 6))
        Ugood[1, 3:] = tr * r
        Fgood[0, 3:] = -T * r
        Fgood[1, 3:] = T * r

        np.testing.assert_almost_equal(Utest, Ugood)
        np.testing.assert_almost_equal(Ftest, Fgood)


@pytest.mark.order(2)
@pytest.mark.timeout(2)
@pytest.mark.dependency(depends=["test_torsionXcircle", "test_torsionZcircle"])
def test_torsionXZcircle():
    ntests = 10
    for i in range(ntests):
        E = np.random.uniform(1, 2)
        nu = np.random.uniform(0, 0.49)
        d = np.random.uniform(1, 2)
        L = np.random.uniform(1, 2)
        T = np.random.uniform(-1, 1)
        r = np.random.uniform(-1, 1, 3) * [True, False, True]
        r /= np.linalg.norm(r)

        steel = Isotropic(E=E, nu=nu)
        circle = Circle(R=d / 2, nu=nu)
        A = (0, 0, 0)
        B = L * r
        bar = EulerBernoulli([A, B])
        bar.material = steel
        bar.section = circle

        U = np.empty((2, 6), dtype="object")
        F = np.zeros((2, 6))
        U[0, :] = 0
        F[1, 3:] = T * r

        K = bar.stiffness_matrix()
        Utest, Ftest = solve(K, F, U)

        tr = 64 * T * L * (1 + nu) / (np.pi * E * d**4)
        Ugood = np.zeros((2, 6))
        Fgood = np.zeros((2, 6))
        Ugood[1, 3:] = tr * r
        Fgood[0, 3:] = -T * r
        Fgood[1, 3:] = T * r

        np.testing.assert_almost_equal(Utest, Ugood)
        np.testing.assert_almost_equal(Ftest, Fgood)


@pytest.mark.order(2)
@pytest.mark.timeout(2)
@pytest.mark.dependency(
    depends=["test_torsionXYcircle", "test_torsionYZcircle", "test_torsionXZcircle"]
)
def test_torsionRcircle():
    ntests = 10
    for i in range(ntests):
        r = np.random.uniform(-1, 1, 3)
        r /= np.linalg.norm(r)
        E = np.random.uniform(1, 2)
        nu = np.random.uniform(0, 0.49)
        d = np.random.uniform(1, 2)
        L = np.random.uniform(1, 2)
        T = np.random.uniform(-1, 1)

        steel = Isotropic(E=E, nu=nu)
        circle = Circle(R=d / 2, nu=nu)
        A = (0, 0, 0)
        B = L * r
        bar = EulerBernoulli([A, B])
        bar.material = steel
        bar.section = circle

        U = np.empty((2, 6), dtype="object")
        F = np.zeros((2, 6))
        U[0, :] = 0
        F[1, 3:] = T * r

        K = bar.stiffness_matrix()
        Utest, Ftest = solve(K, F, U)

        tr = 64 * T * L * (1 + nu) / (np.pi * E * d**4)
        Ugood = np.zeros((2, 6))
        Fgood = np.zeros((2, 6))
        Ugood[1, 3:] = tr * r
        Fgood[0, 3:] = -T * r
        Fgood[1, 3:] = T * r

        np.testing.assert_almost_equal(Utest, Ugood)
        np.testing.assert_almost_equal(Ftest, Fgood)


@pytest.mark.order(2)
@pytest.mark.dependency(depends=["test_begin", "test_torsionRcircle"])
def test_end():
    pass


def main():
    test_begin()
    test_torsionXcircle()
    test_torsionYcircle()
    test_torsionZcircle()
    test_torsionXYcircle()
    test_torsionYZcircle()
    test_torsionXZcircle()
    test_torsionRcircle()
    test_end()


if __name__ == "__main__":
    main()