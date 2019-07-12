"""
Test MCOE (marginal cost of electricity) module functionality.

This set of test attempts to exercise all of the functions which are used in
the calculation of the marginal cost of electricity (MCOE), based on fuel
costs reported to EIA, and non-fuel operating costs reported to FERC.  Much
of what these functions do is attempt to correctly attribute data reported on a
per plant basis to individual generators.

For now, these calculations are only using the EIA fuel cost data. FERC Form 1
non-fuel production costs have yet to be integrated.
"""
import logging

import pandas as pd
import pytest

logger = logging.getLogger(__name__)


@pytest.mark.eia860
@pytest.mark.eia923
@pytest.mark.post_etl
@pytest.mark.mcoe
def test_capacity_factor(pudl_out_eia):
    """Test the capacity factor calculation."""
    logger.info("Calculating generator capacity factors...")
    cf = pudl_out_eia.capacity_factor()
    logger.info(f"Successfully pulled {len(cf)} records")


@pytest.mark.eia860
@pytest.mark.mcoe
@pytest.mark.post_etl
def test_bga(pudl_out_eia):
    """Test the boiler generator associations."""
    logger.info("Inferring complete boiler-generator associations...")
    bga = pudl_out_eia.bga()
    gens_simple = pudl_out_eia.gens_eia860()[['report_date',
                                              'plant_id_eia',
                                              'generator_id',
                                              'fuel_type_code_pudl']]
    bga_gens = bga[['report_date', 'plant_id_eia',
                    'unit_id_pudl', 'generator_id']].drop_duplicates()

    gens_simple = pd.merge(gens_simple, bga_gens,
                           on=['report_date', 'plant_id_eia', 'generator_id'],
                           validate='one_to_one')
    units_simple = gens_simple.drop('generator_id', axis=1).drop_duplicates()
    units_fuel_count = \
        units_simple.groupby(
            ['report_date',
             'plant_id_eia',
             'unit_id_pudl'])['fuel_type_code_pudl'].count().reset_index()
    units_fuel_count.rename(
        columns={'fuel_type_code_pudl': 'fuel_type_count'}, inplace=True)
    units_simple = pd.merge(units_simple, units_fuel_count,
                            on=['report_date', 'plant_id_eia', 'unit_id_pudl'])
    num_multi_fuel_units = len(units_simple[units_simple.fuel_type_count > 1])
    multi_fuel_unit_fraction = num_multi_fuel_units / len(units_simple)
    logger.warning(
        f"{multi_fuel_unit_fraction:.0%} of generation units contain "
        f"generators with differing primary fuels.")


@pytest.mark.eia860
@pytest.mark.eia923
@pytest.mark.post_etl
@pytest.mark.mcoe
def test_hr_by_unit(pudl_out_eia):
    """Calculate heat rates on a per generation unit basis."""
    logger.info("Calculating heat rates by generation unit...")
    hr_by_unit = pudl_out_eia.hr_by_unit()
    logger.info(f"{len(hr_by_unit)} generation unit heat rates calculated.")

    key_cols = ['report_date', 'plant_id_eia', 'unit_id_pudl']
    if not single_records(hr_by_unit, key_cols=key_cols):
        raise AssertionError("Found non-unique unit heat rates!")


@pytest.mark.eia860
@pytest.mark.eia923
@pytest.mark.post_etl
@pytest.mark.mcoe
def test_hr_by_gen(pudl_out_eia):
    """Calculate heat reates on a per-generator basis."""
    logger.info("Calculating heat rates for individual generators...")
    hr_by_gen = pudl_out_eia.hr_by_gen()
    logger.info(f"{len(hr_by_gen)} generator heat rates calculated.")

    if not single_records(hr_by_gen):
        raise AssertionError("Found non-unique generator heat rates!")


@pytest.mark.eia860
@pytest.mark.eia923
@pytest.mark.post_etl
@pytest.mark.mcoe
def test_fuel_cost(pudl_out_eia):
    """Calculate fuel costs on a per-generator basis, and sanity check."""
    logger.info("Calculating fuel costs by individual generator...")
    fc = pudl_out_eia.fuel_cost()
    logger.info(f"{len(fc)} per-generator fuel costs calculated.")
    if not single_records(fc):
        raise AssertionError("Found non-unique generator fuel cost records!")


def single_records(df,
                   key_cols=['report_date', 'plant_id_eia', 'generator_id']):
    """Test whether dataframe has a single record per generator."""
    len_1 = len(df)
    len_2 = len(df.drop_duplicates(subset=key_cols))
    return bool(len_1 == len_2)


def nonunique_gens(df,
                   key_cols=['plant_id_eia', 'generator_id', 'report_date']):
    """Generate a list of all the non-unique generator records for testing."""
    unique_gens = df.drop_duplicates(subset=key_cols)
    dupes = df[~df.isin(unique_gens)].dropna()
    dupes = dupes.sort_values(by=key_cols)
    return dupes