import pytest

from app.schemas import Coordinates, Enemies, ScanData
from app.services import (
    AlliesSort,
    ClosestEnemiesSort,
    CrossfireFilter,
    DistanceFilter,
    FurthestEnemiesSort,
    MechFilter,
    PrioritizeMechFilter,
    RadarSystem,
)


# Test cases for DistanceFilter
def test_distance_filter_init():
    df = DistanceFilter(10)
    assert df.max_distance == 10


def test_distance_filter_distance():
    df = DistanceFilter(10)
    sd1 = ScanData(coordinates=Coordinates(x=3, y=4), enemies=Enemies(type='mech', number=1), allies=2)
    sd2 = ScanData(coordinates=Coordinates(x=5, y=12), enemies=Enemies(type='mech', number=1), allies=2)

    assert df.distance(sd1) == 5.0
    assert df.distance(sd2) == 13.0


def test_distance_filter_is_valid():
    df = DistanceFilter(10)
    sd1 = ScanData(coordinates=Coordinates(x=3, y=4), enemies=Enemies(type='mech', number=1), allies=2)
    sd2 = ScanData(coordinates=Coordinates(x=5, y=12), enemies=Enemies(type='mech', number=1), allies=2)

    assert df.is_valid(sd1) is True
    assert df.is_valid(sd2) is False


def test_distance_filter_is_valid_with_border_case():
    df = DistanceFilter(10)
    sd1 = ScanData(coordinates=Coordinates(x=6, y=8), enemies=Enemies(type='mech', number=1), allies=2)

    assert df.is_valid(sd1) is True


# Test cases for MechFilter
def test_mech_filter_is_valid():
    mf = MechFilter()
    sd1 = ScanData(coordinates=Coordinates(x=3, y=4), enemies=Enemies(type='mech', number=1), allies=2)
    sd2 = ScanData(coordinates=Coordinates(x=5, y=12), enemies=Enemies(type='infantry', number=1), allies=2)

    assert mf.is_valid(sd1) is False
    assert mf.is_valid(sd2) is True


# Test cases for PrioritizeMechFilter
def test_prioritize_mech_filter_is_valid():
    pmf = PrioritizeMechFilter()
    sd1 = ScanData(coordinates=Coordinates(x=3, y=4), enemies=Enemies(type='mech', number=1), allies=2)
    sd2 = ScanData(coordinates=Coordinates(x=5, y=12), enemies=Enemies(type='infantry', number=1), allies=2)

    assert pmf.is_valid(sd1) is True
    assert pmf.is_valid(sd2) is False


# Test cases for CrossfireFilter
def test_crossfire_filter_is_valid():
    cf = CrossfireFilter()
    sd1 = ScanData(coordinates=Coordinates(x=3, y=4), enemies=Enemies(type='mech', number=1), allies=2)
    sd2 = ScanData(coordinates=Coordinates(x=5, y=12), enemies=Enemies(type='infantry', number=1), allies=None)

    assert cf.is_valid(sd1) is False
    assert cf.is_valid(sd2) is True


# Test cases for AlliesSort
def test_allies_sort():
    asort = AlliesSort()
    sd1 = ScanData(coordinates=Coordinates(x=3, y=4), enemies=Enemies(type='mech', number=1), allies=2)
    sd2 = ScanData(coordinates=Coordinates(x=5, y=12), enemies=Enemies(type='infantry', number=1), allies=5)
    sd3 = ScanData(coordinates=Coordinates(x=8, y=10), enemies=Enemies(type='infantry', number=1), allies=None)
    targets = [sd1, sd2, sd3]
    sorted_targets = asort.sort(targets)

    assert sorted_targets == [sd2, sd1, sd3]


# Test cases for ClosestEnemiesSort
def test_closest_enemies_sort():
    ces = ClosestEnemiesSort()
    sd1 = ScanData(coordinates=Coordinates(x=3, y=4), enemies=Enemies(type='mech', number=1), allies=2)
    sd2 = ScanData(coordinates=Coordinates(x=5, y=12), enemies=Enemies(type='infantry', number=1), allies=2)
    sd3 = ScanData(coordinates=Coordinates(x=1, y=2), enemies=Enemies(type='infantry', number=1), allies=5)
    targets = [sd1, sd2, sd3]
    sorted_targets = ces.sort(targets)

    assert sorted_targets == [sd3, sd1, sd2]


# Test cases for FurthestEnemiesSort
def test_furthest_enemies_sort():
    fes = FurthestEnemiesSort()
    sd1 = ScanData(coordinates=Coordinates(x=3, y=4), enemies=Enemies(type='mech', number=1), allies=2)
    sd2 = ScanData(coordinates=Coordinates(x=5, y=12), enemies=Enemies(type='infantry', number=1), allies=2)
    sd3 = ScanData(coordinates=Coordinates(x=1, y=2), enemies=Enemies(type='infantry', number=1), allies=5)
    targets = [sd1, sd2, sd3]
    sorted_targets = fes.sort(targets)

    assert sorted_targets == [sd2, sd1, sd3]


# Test cases for RadarSystem __init__
def test_radar_system_init():
    protocols = [
        'avoid-mech',
        'prioritize-mech',
        'avoid-crossfire',
        'assist-allies',
        'closest-enemies',
        'furthest-enemies',
    ]
    radar_system = RadarSystem(protocols)

    assert isinstance(radar_system.filters[0], DistanceFilter)
    assert isinstance(radar_system.filters[1], MechFilter)
    assert isinstance(radar_system.filters[2], PrioritizeMechFilter)
    assert isinstance(radar_system.filters[3], CrossfireFilter)
    assert isinstance(radar_system.sorting_methods[0], AlliesSort)
    assert isinstance(radar_system.sorting_methods[1], ClosestEnemiesSort)
    assert isinstance(radar_system.sorting_methods[2], FurthestEnemiesSort)


# Test cases for RadarSystem _apply_filters
def test_radar_system_apply_filters():
    protocols = ['avoid-mech', 'avoid-crossfire']
    radar_system = RadarSystem(protocols)

    sd1 = ScanData(coordinates=Coordinates(x=3, y=4), enemies=Enemies(type='mech', number=1), allies=2)
    sd2 = ScanData(coordinates=Coordinates(x=5, y=12), enemies=Enemies(type='infantry', number=1), allies=2)
    sd3 = ScanData(coordinates=Coordinates(x=1, y=2), enemies=Enemies(type='infantry', number=1), allies=None)
    targets = [sd1, sd2, sd3]

    filtered_targets = radar_system._apply_filters(targets)
    assert filtered_targets == [sd3]


# Test cases for RadarSystem _sort_targets
def test_radar_system_sort_targets():
    protocols = ['closest-enemies']
    radar_system = RadarSystem(protocols)

    sd1 = ScanData(coordinates=Coordinates(x=3, y=4), enemies=Enemies(type='mech', number=1), allies=2)
    sd2 = ScanData(coordinates=Coordinates(x=5, y=12), enemies=Enemies(type='infantry', number=1), allies=5)
    sd3 = ScanData(coordinates=Coordinates(x=1, y=2), enemies=Enemies(type='infantry', number=1), allies=None)
    targets = [sd1, sd2, sd3]

    sorted_targets = radar_system._sort_targets(targets)
    assert sorted_targets == [sd3, sd1, sd2]


# Test cases for RadarSystem find_next_target
def test_radar_system_find_next_target():
    protocols = ['avoid-mech', 'assist-allies', 'closest-enemies']
    radar_system = RadarSystem(protocols)

    sd1 = ScanData(coordinates=Coordinates(x=3, y=4), enemies=Enemies(type='mech', number=1), allies=2)
    sd2 = ScanData(coordinates=Coordinates(x=5, y=12), enemies=Enemies(type='infantry', number=1), allies=5)
    sd3 = ScanData(coordinates=Coordinates(x=1, y=2), enemies=Enemies(type='infantry', number=1), allies=3)
    targets = [sd1, sd2, sd3]

    next_target = radar_system.find_next_target(targets)
    assert next_target == sd3


def test_radar_system_find_next_target_no_valid_targets():
    protocols = ['avoid-crossfire']
    radar_system = RadarSystem(protocols)

    sd1 = ScanData(coordinates=Coordinates(x=3, y=4), enemies=Enemies(type='mech', number=1), allies=2)
    sd2 = ScanData(coordinates=Coordinates(x=5, y=12), enemies=Enemies(type='infantry', number=1), allies=2)
    sd3 = ScanData(coordinates=Coordinates(x=1, y=2), enemies=Enemies(type='infantry', number=1), allies=5)
    targets = [sd1, sd2, sd3]

    with pytest.raises(ValueError, match='No valid targets found'):
        radar_system.find_next_target(targets)
