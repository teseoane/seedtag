from math import sqrt
from typing import List

from app.schemas import Coordinates, ScanData


class RadarSystem:
    """
    A class representing a radar system used to identify and prioritize targets based on protocols.

    Attributes:
        protocols (List[str]): A list of strings representing the radar system's protocols.
    """

    def __init__(self, protocols: List[str]) -> None:
        """
        Initialize the RadarSystem with a list of protocols.

        Args:
            protocols (List[str]): A list of strings representing the radar system's protocols.
        """
        self.protocols = protocols
        self.filters = [
            self._is_within_distance,
            self._should_avoid_mech,
            self._should_prioritize_mech,
            self._should_avoid_crossfire,
        ]
        self.sorting_methods = {
            'assist-allies': self._sort_by_allies,
            'closest-enemies': self._sort_by_closest_enemies,
            'furthest-enemies': self._sort_by_furthest_enemies,
        }

    def _distance(self, target: ScanData) -> float:
        """
        Calculate the Euclidean distance between the target and the radar system.

        Args:
            target (ScanData): The target for which to calculate the distance.
        """
        return sqrt(target.coordinates.x ** 2 + target.coordinates.y ** 2)

    def _is_within_distance(self, target: ScanData) -> bool:
        return self._distance(target) <= 100

    def _should_avoid_mech(self, target: ScanData) -> bool:
        return 'avoid-mech' not in self.protocols or target.enemies.type != 'mech'

    def _should_prioritize_mech(self, target: ScanData) -> bool:
        return 'prioritize-mech' not in self.protocols or target.enemies.type == 'mech'

    def _should_avoid_crossfire(self, target: ScanData) -> bool:
        return 'avoid-crossfire' not in self.protocols or target.allies is None

    def _apply_filters(self, targets: List[ScanData]) -> List[ScanData]:
        """
        Apply filters to the list of targets based on the radar system's protocols.

        Args:
            targets (List[ScanData]): A list of targets to be filtered.
        """
        return [t for t in targets if all(f(t) for f in self.filters)]

    def _sort_by_allies(self, targets: List[ScanData]) -> List[ScanData]:
        return sorted(targets, key=lambda t: t.allies if t.allies is not None else 0, reverse=True)

    def _sort_by_closest_enemies(self, targets: List[ScanData]) -> List[ScanData]:
        return sorted(targets, key=self._distance)

    def _sort_by_furthest_enemies(self, targets: List[ScanData]) -> List[ScanData]:
        return sorted(targets, key=self._distance, reverse=True)

    def _sort_targets_by_protocol(self, targets: List[ScanData]) -> List[ScanData]:
        """
        Sort the list of targets based on the radar system's protocols.

        Args:
            targets (List[ScanData]): A list of targets to be sorted.
        """
        for protocol in self.protocols:
            sort_method = self.sorting_methods.get(protocol)
            if sort_method:
                targets = sort_method(targets)
        return targets

    def find_next_target(self, targets: List[ScanData]) -> Coordinates:
        """
        Find the next target based on the radar system's protocols.

        Args:
            targets (List[ScanData]): A list of targets to choose from.

        Returns:
            Coordinates: The coordinates of the next target.

        Raises:
            ValueError: If no valid targets are found.
        """
        filtered_targets = self._apply_filters(targets)

        if not filtered_targets:
            raise ValueError('No valid targets found')

        sorted_targets = self._sort_targets_by_protocol(filtered_targets)

        return sorted_targets[0].coordinates
