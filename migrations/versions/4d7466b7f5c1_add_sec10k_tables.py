"""Add sec10k tables

Revision ID: 4d7466b7f5c1
Revises: 450d100cd30b
Create Date: 2025-02-04 15:34:53.060422

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '4d7466b7f5c1'
down_revision = '450d100cd30b'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('core_sec10k__company_information',
    sa.Column('filename_sec10k', sa.Text(), nullable=False, comment='Name of filing as provided by SEC data portal.'),
    sa.Column('filer_count', sa.Integer(), nullable=False, comment='Index company information as some filings contain information for multiple companies.'),
    sa.Column('company_information_block', sa.Text(), nullable=False, comment='Title of block of data.'),
    sa.Column('company_information_block_count', sa.Integer(), nullable=False, comment='Some blocks are repeated, this defines the index of the data block.'),
    sa.Column('company_information_fact_name', sa.Text(), nullable=False, comment='Name of fact within a ``company_information_block``.'),
    sa.Column('company_information_fact_value', sa.Text(), nullable=False, comment='Value corresponding with ``company_information_fact_name``.'),
    sa.Column('report_date', sa.Date(), nullable=True, comment='Date reported.'),
    sa.PrimaryKeyConstraint('filename_sec10k', 'filer_count', 'company_information_block', 'company_information_block_count', 'company_information_fact_name', 'company_information_fact_value', name=op.f('pk_core_sec10k__company_information'))
    )
    op.create_table('core_sec10k__exhibit_21_company_ownership',
    sa.Column('filename_sec10k', sa.Text(), nullable=True, comment='Name of filing as provided by SEC data portal.'),
    sa.Column('subsidiary_company_name', sa.Text(), nullable=True, comment='Name of subsidiary company.'),
    sa.Column('subsidiary_location', sa.Text(), nullable=True, comment='Location of subsidiary company.'),
    sa.Column('fraction_owned', sa.Float(), nullable=True, comment='Fraction of subsidiary company owned by parent.'),
    sa.Column('report_date', sa.Date(), nullable=True, comment='Date reported.')
    )
    op.create_table('core_sec10k__filings',
    sa.Column('filename_sec10k', sa.Text(), nullable=False, comment='Name of filing as provided by SEC data portal.'),
    sa.Column('central_index_key', sa.Text(), nullable=True, comment='Identifier of the company in SEC database.'),
    sa.Column('company_name', sa.Text(), nullable=True, comment='Name of company submitting SEC 10k filing.'),
    sa.Column('sec10k_version', sa.Text(), nullable=True, comment='Specific version of SEC 10k filed.'),
    sa.Column('date_filed', sa.Date(), nullable=True, comment='Date filing was submitted.'),
    sa.Column('exhibit_21_version', sa.Text(), nullable=True, comment='Version of exhibit 21 submitted (if applicable).'),
    sa.Column('report_date', sa.Date(), nullable=True, comment='Date reported.'),
    sa.PrimaryKeyConstraint('filename_sec10k', name=op.f('pk_core_sec10k__filings'))
    )
    op.create_table('out_sec10k__parents_and_subsidiaries',
    sa.Column('company_id_sec', sa.Text(), nullable=True, comment="Algorithmically assigned ID for companies that file SEC 10k's or are referenced in exhibit 21 attachments to 10k's. May not be stable over time."),
    sa.Column('filename_sec10k', sa.Text(), nullable=True, comment='Name of filing as provided by SEC data portal.'),
    sa.Column('report_date', sa.Date(), nullable=True, comment='Date reported.'),
    sa.Column('central_index_key', sa.Text(), nullable=True, comment='Identifier of the company in SEC database.'),
    sa.Column('utility_id_eia', sa.Integer(), nullable=True, comment='The EIA Utility Identification number.'),
    sa.Column('street_address', sa.Text(), nullable=True, comment='Physical street address.'),
    sa.Column('address_2', sa.Text(), nullable=True, comment='Second line of the address.'),
    sa.Column('city', sa.Text(), nullable=True, comment='Name of the city.'),
    sa.Column('state', sa.Text(), nullable=True, comment='Two letter US state abbreviation.'),
    sa.Column('company_name_raw', sa.Text(), nullable=True, comment='Uncleaned name of company.'),
    sa.Column('date_of_name_change', sa.Date(), nullable=True, comment='Date of last name change of the company.'),
    sa.Column('company_name_former', sa.Text(), nullable=True, comment='Former name of company.'),
    sa.Column('industry_description_sic', sa.Text(), nullable=True, comment='Text description of Standard Industrial Classification (SIC)'),
    sa.Column('industry_id_sic', sa.Text(), nullable=True, comment="Four-digit Standard Industrial Classification (SIC) code identifying the company's primary industry. SIC codes have been replaced by NAICS codes in many applications, but are still used by the SEC."),
    sa.Column('state_of_incorporation', sa.Text(), nullable=True, comment='Two letter state code where company is incorporated.'),
    sa.Column('location_of_incorporation', sa.Text(), nullable=True, comment='Cleaned location of incorporation of the company.'),
    sa.Column('company_id_irs', sa.Text(), nullable=True, comment='ID of the company with the IRS.'),
    sa.Column('files_sec10k', sa.Boolean(), nullable=True, comment='Indicates whether the company files an SEC 10-K.'),
    sa.Column('parent_company_central_index_key', sa.Text(), nullable=True, comment="Central index key (CIK) of the company's parent company."),
    sa.Column('fraction_owned', sa.Float(), nullable=True, comment='Fraction of subsidiary company owned by parent.'),
    sa.ForeignKeyConstraint(['utility_id_eia', 'report_date'], ['core_eia860__scd_utilities.utility_id_eia', 'core_eia860__scd_utilities.report_date'], name=op.f('fk_out_sec10k__parents_and_subsidiaries_utility_id_eia_core_eia860__scd_utilities'))
    )
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_table('out_sec10k__parents_and_subsidiaries')
    op.drop_table('core_sec10k__filings')
    op.drop_table('core_sec10k__exhibit_21_company_ownership')
    op.drop_table('core_sec10k__company_information')
    # ### end Alembic commands ###
