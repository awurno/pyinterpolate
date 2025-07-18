from copy import deepcopy

import geopandas as gpd
import numpy as np
import pandas as pd
import pytest
from shapely.geometry.point import Point

from pyinterpolate.core.data_models.blocks import Blocks
from .sample_data.dataprep import CANCER_DATA, CANCER_DATA_WITH_RAND_PTS, CANCER_DATA_WITH_CENTROIDS


def test_assigning_with_centroids():
    block = Blocks(
        **CANCER_DATA
    )
    assert isinstance(block, Blocks)
    assert 'lon' in block.ds.columns
    assert 'lat' in block.ds.columns
    assert isinstance(block.representative_points_array(), np.ndarray)
    assert isinstance(block.distances, pd.DataFrame)


def test_assigning_with_representative_points_centroids():
    block = Blocks(
        **CANCER_DATA_WITH_CENTROIDS
    )
    assert isinstance(block, Blocks)
    assert 'lon' in block.ds.columns
    assert 'lat' in block.ds.columns
    assert isinstance(block.representative_points_array(), np.ndarray)
    assert block.rep_points_column_name == 'centroid'
    assert isinstance(block.distances, pd.DataFrame)


def test_assigning_with_representative_points_random():
    block = Blocks(
        **CANCER_DATA_WITH_RAND_PTS
    )
    print('')
    print(block.ds.columns)
    assert isinstance(block, Blocks)
    assert 'lon' in block.ds.columns
    assert 'lat' in block.ds.columns
    assert isinstance(block.representative_points_array(), np.ndarray)
    assert block.rep_points_column_name == 'rep_points'
    assert isinstance(block.distances, pd.DataFrame)


def test_assigning_without_representative_points_calc_centroids():
    block = Blocks(
        **CANCER_DATA,
        representative_points_from_centroid=True
    )
    assert isinstance(block, Blocks)
    assert 'lon' in block.ds.columns
    assert 'lat' in block.ds.columns
    assert isinstance(block.representative_points_array(), np.ndarray)
    assert block.rep_points_column_name == 'representative_points'
    assert isinstance(block.distances, pd.DataFrame)


def test_assigning_without_representative_points_calc_random():
    block = Blocks(
        **CANCER_DATA,
        representative_points_from_random_sample=True
    )
    assert isinstance(block, Blocks)
    assert 'lon' in block.ds.columns
    assert 'lat' in block.ds.columns
    assert isinstance(block.representative_points_array(), np.ndarray)
    assert block.rep_points_column_name == 'representative_points'
    assert isinstance(block.distances, pd.DataFrame)


def test_attribute_error_points_from_centroid_and_from_random_samples():
    with pytest.raises(AttributeError) as _:
        _ = Blocks(
            **CANCER_DATA,
            representative_points_from_centroid=True,
            representative_points_from_random_sample=True
        )


def test_pop_method():
    block = Blocks(
        **CANCER_DATA
    )

    l_block = len(block)

    fips = 36121

    removed_block = block.pop(fips)

    assert isinstance(removed_block, Blocks)
    assert isinstance(removed_block.ds, gpd.GeoDataFrame)

    indexes = block.ds[block.index_column_name]
    assert fips not in indexes

    l2_block = len(block)
    assert l2_block == l_block - 1


def test_select_distances_between_blocks_method():
    block = Blocks(
        **CANCER_DATA
    )

    indexes = block.ds[block.index_column_name]
    idxs = np.random.choice(indexes, 10)

    dists = block.select_distances_between_blocks(idxs)
    assert isinstance(dists, np.ndarray)

    dist = block.select_distances_between_blocks(idxs[-1])
    assert isinstance(dist, np.ndarray)

    dists = block.select_distances_between_blocks(idxs, idxs)
    assert isinstance(dists, np.ndarray)

    dist = block.select_distances_between_blocks(idxs[-1], idxs[-1])
    assert isinstance(dist, np.floating)

    dists = block.select_distances_between_blocks(idxs, idxs[1])
    assert isinstance(dists, np.ndarray)

    dist = block.select_distances_between_blocks(idxs[1], idxs)
    assert isinstance(dist, np.ndarray)


def test_transform_crs():
    block = Blocks(
        **CANCER_DATA,
        angles_between_representative_points=True
    )

    sample_base = block.ds.iloc[0]
    sample_base_dists = block.distances.copy(deep=True).iloc[0, 1]
    sample_base_angles = deepcopy(block.angles)

    ks = list(sample_base_angles.keys())[0]

    block.transform_crs('EPSG:2180')

    sample_transformed = block.ds.iloc[0]
    sample_transformed_dists = block.distances.copy(deep=True).iloc[0, 1]
    sample_transformed_angles = deepcopy(block.angles)

    st_angles = sample_transformed_angles[ks]
    sb_angles = sample_base_angles[ks]

    assert sample_base[block._lon_col_name] != sample_transformed[block._lon_col_name]
    assert sample_transformed_dists != sample_base_dists
    assert sb_angles[1] != st_angles[1]


def test_block_index_outputs():
    block = Blocks(**CANCER_DATA)

    # Check block coordinates
    indexes = block.ds[block.index_column_name]
    idxs = np.random.choice(indexes, 10)
    block_id = idxs[0]

    coordinates = block.block_coordinates(block_id=block_id)
    assert isinstance(coordinates, Point)

    real_value = block.block_real_value(block_id=block_id)
    assert isinstance(real_value, float)
