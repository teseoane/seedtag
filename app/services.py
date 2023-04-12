from math import sqrt
from typing import List

from app.schemas import ScanData


class Filter:
    def is_valid(self, target: ScanData) -> bool:
        raise NotImplementedError


class DistanceFilter(Filter):
    def __init__(self, max_distance: float) -> None:
        self.max_distance = max_distance

    def distance(self, target: ScanData) -> float:
        return sqrt(target.coordinates.x ** 2 + target.coordinates.y ** 2)

    def is_valid(self, target: ScanData) -> bool:
        return self.distance(target) <= self.max_distance


class MechFilter(Filter):
    def is_valid(self, target: ScanData) -> bool:
        return target.enemies.type != 'mech'


class PrioritizeMechFilter(Filter):
    def is_valid(self, target: ScanData) -> bool:
        return target.enemies.type == 'mech'


class CrossfireFilter(Filter):
    def is_valid(self, target: ScanData) -> bool:
        return target.allies is None


class SortingMethod:
    def sort(self, targets: List[ScanData]) -> List[ScanData]:
        raise NotImplementedError


class AlliesSort(SortingMethod):
    def sort(self, targets: List[ScanData]) -> List[ScanData]:
        return sorted(targets, key=lambda t: t.allies if t.allies is not None else 0, reverse=True)


class ClosestEnemiesSort(SortingMethod):
    def sort(self, targets: List[ScanData]) -> List[ScanData]:
        return sorted(targets, key=DistanceFilter(0).distance)


class FurthestEnemiesSort(SortingMethod):
    def sort(self, targets: List[ScanData]) -> List[ScanData]:
        return sorted(targets, key=DistanceFilter(0).distance, reverse=True)


class RadarSystem:
    def __init__(self, protocols: List[str]) -> None:
        self.filters = [DistanceFilter(100)]
        self.sorting_methods = []

        protocol_map = {
            'avoid-mech': MechFilter(),
            'prioritize-mech': PrioritizeMechFilter(),
            'avoid-crossfire': CrossfireFilter(),
            'assist-allies': AlliesSort(),
            'closest-enemies': ClosestEnemiesSort(),
            'furthest-enemies': FurthestEnemiesSort(),
        }

        for protocol in protocols:
            instance = protocol_map.get(protocol)
            if isinstance(instance, Filter):
                self.filters.append(instance)
            elif isinstance(instance, SortingMethod):
                self.sorting_methods.append(instance)

    def _apply_filters(self, targets: List[ScanData]) -> List[ScanData]:
        return [t for t in targets if all(f.is_valid(t) for f in self.filters)]

    def _sort_targets(self, targets: List[ScanData]) -> List[ScanData]:
        for sorting_method in self.sorting_methods:
            targets = sorting_method.sort(targets)
        return targets

    def find_next_target(self, targets: List[ScanData]) -> ScanData:
        filtered_targets = self._apply_filters(targets)

        if not filtered_targets:
            raise ValueError('No valid targets found')

        sorted_targets = self._sort_targets(filtered_targets)

        return sorted_targets[0]
