
from typing import List

import pytest

from app.models import Coordinates, Enemies, ProtocolEnum, ScanData
from app.utils import RadarSystem

BASE_COORD = Coordinates(x=0, y=0)


@pytest.fixture
def sample_protocols() -> List[str]:
    return [
        'avoid-mech',
        'prioritize-mech',
        'avoid-crossfire',
        'assist-allies',
        'closest-enemies',
        'furthest-enemies',
    ]


def test_radarsystem_init(sample_protocols):
    radar = RadarSystem(sample_protocols)
    assert radar.protocols == sample_protocols
    assert len(radar.filters) == 4
    assert len(radar.sorting_methods) == 3


@pytest.mark.parametrize('scan_data, expected_distance', [
    (ScanData(coordinates=BASE_COORD, enemies=Enemies(type='mech', number=1), allies=None), 0),
    (ScanData(coordinates=Coordinates(x=3, y=4), enemies=Enemies(type='mech', number=1), allies=None), 5),
    (ScanData(coordinates=Coordinates(x=6, y=8), enemies=Enemies(type='mech', number=1), allies=None), 10),
    (ScanData(coordinates=Coordinates(x=100, y=0), enemies=Enemies(type='mech', number=1), allies=None), 100),
    (ScanData(coordinates=Coordinates(x=0, y=-100), enemies=Enemies(type='mech', number=1), allies=None), 100),
    (ScanData(coordinates=Coordinates(x=-100, y=100), enemies=Enemies(type='mech', number=1), allies=None), 141),
])
def test_radarsystem_distance(sample_protocols, scan_data, expected_distance):
    radar = RadarSystem(sample_protocols)
    assert pytest.approx(radar._distance(scan_data), rel=1e-6) == expected_distance


@pytest.mark.parametrize('scan_data, expected_result', [
    (ScanData(coordinates=BASE_COORD, enemies=Enemies(type='mech', number=1), allies=None), True),
    (ScanData(coordinates=Coordinates(x=3, y=4), enemies=Enemies(type='mech', number=1), allies=None), True),
    (ScanData(coordinates=Coordinates(x=6, y=8), enemies=Enemies(type='mech', number=1), allies=None), True),
    (ScanData(coordinates=Coordinates(x=100, y=0), enemies=Enemies(type='mech', number=1), allies=None), True),
    (ScanData(coordinates=Coordinates(x=0, y=-100), enemies=Enemies(type='mech', number=1), allies=None), True),
    (ScanData(coordinates=Coordinates(x=-100, y=100), enemies=Enemies(type='mech', number=1), allies=None), False),
    (ScanData(coordinates=Coordinates(x=101, y=0), enemies=Enemies(type='mech', number=1), allies=None), False),
])
def test_radarsystem_is_within_distance(sample_protocols, scan_data, expected_result):
    radar = RadarSystem(sample_protocols)
    assert radar._is_within_distance(scan_data) == expected_result


@pytest.mark.parametrize('protocols, scan_data, expected_result', [
    (['avoid-mech'], ScanData(coordinates=BASE_COORD, enemies=Enemies(type='mech', number=1), allies=None), False),
    (['avoid-mech'], ScanData(coordinates=BASE_COORD, enemies=Enemies(type='tank', number=1), allies=None), True),
    (['prioritize-mech'], ScanData(coordinates=BASE_COORD, enemies=Enemies(type='mech', number=1), allies=None), True),
    (['prioritize-mech'], ScanData(coordinates=BASE_COORD, enemies=Enemies(type='tank', number=1), allies=None), True),
    ([], ScanData(coordinates=BASE_COORD, enemies=Enemies(type='mech', number=1), allies=None), True),
    ([], ScanData(coordinates=BASE_COORD, enemies=Enemies(type='tank', number=1), allies=None), True),
])
def test_radarsystem_should_avoid_mech(protocols, scan_data, expected_result):
    radar = RadarSystem(protocols)
    assert radar._should_avoid_mech(scan_data) == expected_result


@pytest.mark.parametrize('protocols, scan_data, expected_result', [
    (['prioritize-mech'], ScanData(coordinates=BASE_COORD, enemies=Enemies(type='mech', number=1), allies=None), True),
    (['prioritize-mech'], ScanData(coordinates=BASE_COORD, enemies=Enemies(type='tank', number=1), allies=None), False),
    (['avoid-mech'], ScanData(coordinates=BASE_COORD, enemies=Enemies(type='mech', number=1), allies=None), True),
    (['avoid-mech'], ScanData(coordinates=BASE_COORD, enemies=Enemies(type='tank', number=1), allies=None), True),
    ([], ScanData(coordinates=BASE_COORD, enemies=Enemies(type='mech', number=1), allies=None), True),
    ([], ScanData(coordinates=BASE_COORD, enemies=Enemies(type='tank', number=1), allies=None), True),
])
def test_radarsystem_should_prioritize_mech(protocols, scan_data, expected_result):
    radar = RadarSystem(protocols)
    assert radar._should_prioritize_mech(scan_data) == expected_result


@pytest.mark.parametrize('protocols, scan_data, expected_result', [
    (['avoid-crossfire'], ScanData(coordinates=BASE_COORD, enemies=Enemies(type='mech', number=1), allies=2), False),
    (['avoid-crossfire'], ScanData(coordinates=BASE_COORD, enemies=Enemies(type='mech', number=1), allies=None), True),
    (['avoid-mech'], ScanData(coordinates=BASE_COORD, enemies=Enemies(type='mech', number=1), allies=2), True),
    (['avoid-mech'], ScanData(coordinates=BASE_COORD, enemies=Enemies(type='mech', number=1), allies=None), True),
    ([], ScanData(coordinates=BASE_COORD, enemies=Enemies(type='mech', number=1), allies=2), True),
    ([], ScanData(coordinates=BASE_COORD, enemies=Enemies(type='mech', number=1), allies=None), True),
])
def test_radarsystem_should_avoid_crossfire(protocols, scan_data, expected_result):
    radar = RadarSystem(protocols)
    assert radar._should_avoid_crossfire(scan_data) == expected_result


@pytest.mark.parametrize('protocols, targets, expected_filtered_targets', [
    (['avoid-mech'], [
        ScanData(coordinates=BASE_COORD, enemies=Enemies(type='mech', number=1), allies=None),
        ScanData(coordinates=BASE_COORD, enemies=Enemies(type='tank', number=1), allies=None),
    ], [
        ScanData(coordinates=BASE_COORD, enemies=Enemies(type='tank', number=1), allies=None),
    ]),
    (['avoid-crossfire'], [
        ScanData(coordinates=BASE_COORD, enemies=Enemies(type='mech', number=1), allies=2),
        ScanData(coordinates=BASE_COORD, enemies=Enemies(type='tank', number=1), allies=None),
    ], [
        ScanData(coordinates=BASE_COORD, enemies=Enemies(type='tank', number=1), allies=None),
    ]),
    (['avoid-crossfire', 'avoid-mech'], [
        ScanData(coordinates=BASE_COORD, enemies=Enemies(type='mech', number=1), allies=2),
        ScanData(coordinates=BASE_COORD, enemies=Enemies(type='tank', number=1), allies=None),
    ], [
        ScanData(coordinates=BASE_COORD, enemies=Enemies(type='tank', number=1), allies=None),
    ]),
])
def test_radarsystem_apply_filters(protocols, targets, expected_filtered_targets):
    radar = RadarSystem(protocols)
    assert radar._apply_filters(targets) == expected_filtered_targets


def test_radarsystem_sort_by_allies(sample_protocols):
    radar = RadarSystem(sample_protocols)

    targets = [
        ScanData(coordinates=BASE_COORD, enemies=Enemies(type='mech', number=1), allies=2),
        ScanData(coordinates=BASE_COORD, enemies=Enemies(type='tank', number=1), allies=None),
        ScanData(coordinates=BASE_COORD, enemies=Enemies(type='mech', number=1), allies=5),
    ]

    expected_sorted_targets = [
        ScanData(coordinates=BASE_COORD, enemies=Enemies(type='mech', number=1), allies=5),
        ScanData(coordinates=BASE_COORD, enemies=Enemies(type='mech', number=1), allies=2),
        ScanData(coordinates=BASE_COORD, enemies=Enemies(type='tank', number=1), allies=None),
    ]

    assert radar._sort_by_allies(targets) == expected_sorted_targets


def test_radarsystem_sort_by_closest_enemies(sample_protocols):
    radar = RadarSystem(sample_protocols)

    targets = [
        ScanData(coordinates=Coordinates(x=0, y=100), enemies=Enemies(type='mech', number=1), allies=2),
        ScanData(coordinates=Coordinates(x=50, y=50), enemies=Enemies(type='tank', number=1), allies=None),
        ScanData(coordinates=Coordinates(x=100, y=0), enemies=Enemies(type='mech', number=1), allies=5),
    ]

    expected_sorted_targets = [
        ScanData(coordinates=Coordinates(x=50, y=50), enemies=Enemies(type='tank', number=1), allies=None),
        ScanData(coordinates=Coordinates(x=0, y=100), enemies=Enemies(type='mech', number=1), allies=2),
        ScanData(coordinates=Coordinates(x=100, y=0), enemies=Enemies(type='mech', number=1), allies=5),
    ]

    assert radar._sort_by_closest_enemies(targets) == expected_sorted_targets


def test_radarsystem_sort_by_furthest_enemies(sample_protocols):
    radar = RadarSystem(sample_protocols)

    targets = [
        ScanData(coordinates=Coordinates(x=0, y=100), enemies=Enemies(type='mech', number=1), allies=2),
        ScanData(coordinates=Coordinates(x=50, y=50), enemies=Enemies(type='tank', number=1), allies=None),
        ScanData(coordinates=Coordinates(x=120, y=0), enemies=Enemies(type='mech', number=1), allies=5),
    ]

    expected_sorted_targets = [
        ScanData(coordinates=Coordinates(x=120, y=0), enemies=Enemies(type='mech', number=1), allies=5),
        ScanData(coordinates=Coordinates(x=0, y=100), enemies=Enemies(type='mech', number=1), allies=2),
        ScanData(coordinates=Coordinates(x=50, y=50), enemies=Enemies(type='tank', number=1), allies=None),
    ]

    assert radar._sort_by_furthest_enemies(targets) == expected_sorted_targets


@pytest.mark.parametrize('protocols, targets, expected_sorted_targets', [
    (
        [ProtocolEnum.CLOSEST_ENEMIES.value],
        [
            ScanData(coordinates=Coordinates(x=0, y=100), enemies=Enemies(type='mech', number=1), allies=2),
            ScanData(coordinates=Coordinates(x=50, y=50), enemies=Enemies(type='tank', number=1), allies=None),
            ScanData(coordinates=Coordinates(x=100, y=0), enemies=Enemies(type='mech', number=1), allies=5),
        ],
        [
            ScanData(coordinates=Coordinates(x=50, y=50), enemies=Enemies(type='tank', number=1), allies=None),
            ScanData(coordinates=Coordinates(x=0, y=100), enemies=Enemies(type='mech', number=1), allies=2),
            ScanData(coordinates=Coordinates(x=100, y=0), enemies=Enemies(type='mech', number=1), allies=5),
        ],
    ),
])
def test_radarsystem_sort_targets_by_protocol(protocols, targets, expected_sorted_targets):
    radar = RadarSystem(protocols)
    assert radar._sort_targets_by_protocol(targets) == expected_sorted_targets


@pytest.mark.parametrize('protocols, targets, expected_next_target', [
    (
        [ProtocolEnum.CLOSEST_ENEMIES.value],
        [
            ScanData(coordinates=Coordinates(x=0, y=100), enemies=Enemies(type='mech', number=1), allies=2),
            ScanData(coordinates=Coordinates(x=50, y=50), enemies=Enemies(type='tank', number=1), allies=None),
            ScanData(coordinates=Coordinates(x=100, y=0), enemies=Enemies(type='mech', number=1), allies=5),
        ],
        Coordinates(x=50, y=50),
    ),
])
def test_radarsystem_find_next_target(protocols, targets, expected_next_target):
    radar = RadarSystem(protocols)
    assert radar.find_next_target(targets) == expected_next_target


def test_radarsystem_find_next_target_valueerror(sample_protocols):
    radar = RadarSystem(sample_protocols)

    targets = [
        ScanData(coordinates=Coordinates(x=0, y=101), enemies=Enemies(type='mech', number=1), allies=2),
        ScanData(coordinates=Coordinates(x=50, y=51), enemies=Enemies(type='mech', number=1), allies=None),
        ScanData(coordinates=Coordinates(x=101, y=0), enemies=Enemies(type='mech', number=1), allies=5),
    ]

    with pytest.raises(ValueError, match='No valid targets found'):
        radar.find_next_target(targets)
