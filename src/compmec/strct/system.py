from typing import Callable, Dict, Iterable, Tuple, Type, Union

import numpy as np

from compmec.strct.__classes__ import Element1D, Point, System
from compmec.strct.fields import ComputeFieldBeam
from compmec.strct.geometry import Geometry1D, Point3D
from compmec.strct.solver import solve


class StaticLoad(object):
    valid_keys = ["Fx", "Fy", "Fz", "Mx", "My", "Mz"]

    @classmethod
    def _verify_key(cls, key: str):
        if not isinstance(key, str):
            error_msg = f"Key must be an string. Received {type(key)}"
            raise TypeError(error_msg)
        if key not in cls.valid_keys:
            error_msg = f"Received key is invalid: {key}. Must be in {cls.valid_keys}"
            raise ValueError(error_msg)

    @classmethod
    def _verify_dict(cls, values: Dict[str, float]):
        if not isinstance(values, dict):
            error_msg = f"Values must be a dictionary, not {type(values)}"
            raise TypeError(error_msg)
        for key, item in values.items():
            cls._verify_key(key)
            if not isinstance(item, (float, int)):
                error_msg = f"Item in dictionary must be a 'float', not {type(item)}"
                raise TypeError(error_msg)

    def __init__(self):
        self._loads = []

    @property
    def loads(self):
        return self._loads

    def key2pos(self, key: str) -> int:
        self._verify_key(key)
        return self._key2pos(key)

    def _key2pos(self, key: str) -> int:
        return 3 * (["F", "M"].index(key[0])) + ["x", "y", "z"].index(key[1])

    def add_conc_load(self, index: int, values: Dict[str, float]) -> None:
        self._verify_dict(values)
        return self._add_conc_load(index, values)

    def _add_conc_load(self, index: int, values: Dict[str, float]) -> None:
        return self._add_conc_load_at_index(index, values)

    def add_dist_load(self, indexs: Iterable[int], values: dict, Ls: Iterable[float]):
        raise NotImplementedError

    def _add_conc_load_at_index(self, index: int, values: Dict[str, float]):
        for key, value in values.items():
            position = self.key2pos(key)
            self._loads.append((index, position, value))


class StaticBoundaryCondition(object):
    valid_keys = ["Ux", "Uy", "Uz", "tx", "ty", "tz"]

    @classmethod
    def _verify_key(cls, key: str):
        if not isinstance(key, str):
            raise TypeError(f"Key must be an string. Received {type(key)}")
        if key not in cls.valid_keys:
            error_msg = f"Received key is invalid: {key}. Must be in {cls.valid_keys}"
            raise ValueError(error_msg)

    @classmethod
    def _verify_dict(cls, values: Dict[str, float]):
        if not isinstance(values, dict):
            error_msg = f"Values must be a dictionary, not {type(values)}"
            raise TypeError(error_msg)
        for key, item in values.items():
            cls._verify_key(key)
            if not isinstance(item, (float, int)):
                error_msg = f"Item in dictionary must be a 'float', not {type(item)}"
                raise TypeError(error_msg)

    def __init__(self):
        self._BCs = []

    @property
    def bcvals(self):
        return self._BCs

    def key2pos(self, key: str) -> int:
        self._verify_key(key)
        return self._key2pos(key)

    def _key2pos(self, key: str) -> int:
        return 3 * (["U", "t"].index(key[0])) + ["x", "y", "z"].index(key[1])

    def add_BC(self, index: int, values: Dict[str, float]):
        self._verify_dict(values)
        return self._add_BC(index, values)

    def _add_BC(self, index: int, values: Dict[str, float]):
        for key, value in values.items():
            bcpos = self.key2pos(key)
            self._BCs.append((index, bcpos, value))


class StaticStructure(object):
    @classmethod
    def _verify_element(cls, element: Element1D):
        if not isinstance(element, Element1D):
            raise TypeError("To add an element, it must be a Structural 1D instance")

    def __init__(self):
        self._elements = []

    @property
    def elements(self):
        return self._elements

    def add_element(self, value: Element1D) -> None:
        self._verify_element(value)
        return self._add_element(value)

    def _add_element(self, value: Element1D) -> None:
        self._elements.append(value)


class StaticSystem(System):
    def __new__(cls):
        if not hasattr(cls, "instance"):
            cls.instance = super(StaticSystem, cls).__new__(cls)
        return cls.instance

    def __init__(self):
        self._geometry = Geometry1D()
        self._structure = StaticStructure()
        self._loads = StaticLoad()
        self._boundarycondition = StaticBoundaryCondition()
        self._solution = None

    def add_element(self, element: Element1D):
        self._structure.add_element(element)

    def add_conc_load(self, point: Point3D, loads: Dict[str, float]):
        """
        Add a load in a specific point.
        Example:
            point = (1.0, 3.5, -2.0)
            system.add_conc_load(point, {"Fx": -30})
        The available loads are combinations of ("F", "M") and ("x", "y", "z", "n", "v", "w").
        Example:
            Fx: Force in x direction
            Mn: Momentum in normal direction
        """
        StaticLoad._verify_dict(loads)
        index = Point3D(point).get_index()
        self._loads.add_conc_load(index, loads)

    def add_dist_load(
        self,
        element: Element1D,
        function: Callable[[float], Tuple[float, float, float]],
    ):
        """
        Add a distribueted load in a interval.
        Example:
            beamAB = EulerBernoulli([A, B])
            def force(t: float):
                interval = (0.2, 0.5, 0.7)
                loadsFy = (10, -30, 30)
            system.add_dist_load(beamAB, interval, {"Fy": loadsFy})
        All the values inside interval must be in [0, 1]
        The available loads are the same as 'add_conc_load' function:
            ("Fx", "Fy", "Fz", "Fn", "Fv", "Fw",
             "Mx", "My", "Mz", "Mn", "Mv", "Mw")
        The quantities of the interval must be tha same as each load.
        The loads are linear defined. That means:
            At (0.5) the value of "Fy" is -30
            At (0.6) the value of "Fy" is 0
            At (0.7) the value of "Fy" is 30
        """
        if not isinstance(element, Element1D):
            raise TypeError("Element must be Element1D")
        if not callable(function):
            raise TypeError("The function must be callable")
        raise NotImplementedError

    def add_BC(self, point: Point3D, bcvals: dict):
        StaticBoundaryCondition._verify_dict(bcvals)
        index = Point3D(point).get_index()
        self._boundarycondition.add_BC(index, bcvals)

    def __getpointsfrom(self, element: Element1D):
        for t in element.ts:
            point = element.path(t)
            point = Point3D(point)
            if point not in self._geometry:
                self._geometry.add_point(point)

    def mount_U(self) -> np.ndarray:
        npts = self._geometry.npts
        U = np.empty((npts, 6), dtype="object")
        for global_index, position, displacement in self._boundarycondition.bcvals:
            local_index = self._geometry._global_indexs.index(global_index)
            U[local_index, position] = displacement
        return U

    def mount_F(self) -> np.ndarray:
        npts = self._geometry.npts
        F = np.zeros((npts, 6))
        for global_index, position, loads in self._loads.loads:
            local_index = self._geometry._global_indexs.index(global_index)
            F[local_index, position] += loads
        return F

    def mount_K(self) -> np.ndarray:
        npts = self._geometry.npts
        K = np.zeros((npts, 6, npts, 6))
        for element in self._structure.elements:
            Kloc = element.stiffness_matrix()
            local_indexs = []
            for t in element.ts:
                searchpoint = element.path(t)
                local_index = self._geometry.find_point(searchpoint)
                local_indexs.append(local_index)
            for i, indi in enumerate(local_indexs):
                for j, indj in enumerate(local_indexs):
                    K[indi, :, indj, :] += Kloc[i, :, j, :]
        return K

    def run(self):
        if len(self._structure.elements) == 0:
            error_msg = "You must have at least one element to run the simulation"
            raise ValueError(error_msg)
        for element in self._structure.elements:
            self.__getpointsfrom(element)
        print("Point3D.all_index_points = ")
        print(Point3D.all_indexed_instances)
        print("Geometry global indexs = ")
        print(self._geometry._global_indexs)
        print("Geometry local points = ")
        print(self._geometry.points)
        K = self.mount_K()
        F = self.mount_F()
        U = self.mount_U()
        U, F = solve(K, F, U)
        self._solution = U
        self.apply_on_elements()

    def apply_on_elements(self):
        for element in self._structure.elements:
            npts = len(element.ts)
            points = element.path(element.ts)
            indexs = np.zeros(npts, dtype="int32")
            for i, p in enumerate(points):
                indexs[i] = self._geometry.find_point(p)
            Uelem = np.zeros((npts, 6))
            for i, j in enumerate(indexs):
                Uelem[i, :] = self._solution[j, :]
            field = ComputeFieldBeam(element, Uelem)
            element.set_field(field)
