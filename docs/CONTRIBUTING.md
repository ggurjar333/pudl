
## How to add a new data source
1. Add the new data source to the datastore module and datastore update script.
    The datastore module contains all the functionality required to acquire the data from their reporting agencies, and organize it locally in advance of the ETL process. New data sources should be organized under “data/<agency>/<source>/” e.g. “data/ferc/form1” or “data/eia/form923” Larger data sources that are available as compressed zipfiles can be left zipped to save local disk space. Organization of a data source beneath the source directory may depend on the source. For data which is compiled annually, we typically make one subdirectory for each year, but some data sources provide all the data in one file for all years (e.g. the MSHA mine info). The datastore update script can be run at the command line to pull down new data, or to refresh old data if it’s been updated. The user should be able to specify subsets of the data to pull or refresh -- e.g. a set of years, or a set of states -- especially in the case of large datasets. In some cases, opening several download connections in parallel may dramatically reduce the time it takes to acquire the data (e.g. pulling don the EPA CEMS dataset over FTP). The constants.py module contains several dictionaries which define what years etc. are available in the data

2. Define database tables.
    Create a new module in the models subpackage. The name of the module should be the datasource name. New modules need to import the entities module (“import pudl.models.entities”) and must be imported in the init.py module (“import pudl.models.datasource”). This way the database schema will include this module when it is first initialized. PUDL uses SQLAlchemy. Each datatable must have a class definition (see PlanAnnualEIA in pudl.models.eia as an example). Make sure your tables are normalized - see the Database Design Guidelines.

2. Extract.
    The raw inputs to the extract step should be the pointers to the datastore and any parameters on grabbing the dataset (i.e. the working years, locational constraints if applicable). The outcome of the extract module should be a dictionary of dataframes with keys that correspond to the original datasource table/tab/file name with each row corresponding to one record. These raw dataframes should not be largely altered from their original structures in this step, with the exception of creating records. For example, the EIA 923 often reports a year’s worth of monthly data in one row and the extract step transforms the single row into twelve monthly records.  If possible, attempt to keep the dataset in its most compressed format on disk during the extract step. For large data sources stored in zip files (e.g. epacems), there is no need to unzip the files as pandas is able to read directly from zipped files. For extracting data from other databases (as opposed to CSV files, spreadsheets, etc.) you may need to populate a live database locally, and read from it (e.g. the FERC Form 1 database, which we clone into postgres from the FoxPro/DBF format used by FERC).

3. Transform.
    The inputs to the transform step should be the dictionary of raw dataframes and any dataset constraints (i.e. working years, tables, and geographical constraints). The output should be a dictionary of transformed dataframes which look exactly like what you want to end up in the database tables. The key of the dictionary should be the name of the datatables as defined in the models. Largely, there is one function per data table. If one datatable needs any information such as the index from another table (see fuel_receipts_costs_eia923 and coalmine_eia923, this will require the transform functions to be called in a particular order but the process is largely the same. All the organization of the data into normalized tables happens in the transform step. During this step, any cleaning of the original data is done, such as:
      1. Standardizing units / unit conversions.
      2. Casting to appropriate data types (string, int, float, etc.).
      3. Conversion to appropriate NA or NaN values for missing data.
      4. Coding of categorical variables (e.g. fuel type)
      5. Coding/categorization of freeform string fields (e.g. fuel types in FERC Form 1)
      6. Correction of glaring reporting errors if possible (e.g. when someone reports MWh instead of kWh for net generation, or BTU instead of MMBTU)
4. Load.
    Each of the dataframes that comes out of the transform step represents a database table that needs to be loaded into the database. Pandas has a native df.to_sql() functionality for inserting records from a dataframe into a database table, but it’s extremely slow. Instead, we use postgres’ native COPY_FROM function, which is designed for loading large CSV files directly into the database very efficiently. Rather than writing the dataframe out to a file on disk, we create an in-memory file-like object, and read directly from that. For this to work, all the dataframe and database table columns need to be named identically, and the strings that are read by postgres from the in-memory CSV file need to be readily interpretable as the data type that is associated with the column in the table definition. Because Python doesn’t have a native NA value for integers, but postgres does, just before the dataframes are loaded into the database we convert any integer NA sentinel values

5. Glue.
    Largely, the glue should be the information that creates the ability to connect one dataset to another. The glue should be able to be thoroughly independent from the ingest of the dataset (there should be no PULD glue id’s in any of the datasource tables and there should be no foreign key relationships from any of the glue tables to the datasource specific tables). These connector keys can be added in the output functions but having them be integral to the database ingestion would make the glue a dependency for adding new datasources, which we want to avoid. The process for adding glue will be very different depending on the datasets your trying to glue together. The EIA and FERC plants and utilities are currently mapped by hand in a spreadsheet and pulled into tables. The FERC and EIA units ids that will end up living in a glue table will be created through the datazipper. There should be one module in the glue subpackage for each inter-dataset glue (i.e. ferc1_eia or  cems_eia) as well as table definitions in the models.glue.py module. If possible, there should be foreign key constraints from the underlying dataset entity tables (i.e. plants_entity_eia) to the glue tables so that we do not accidentally store glue that does not refer to the underlying dataset.

6. Output.
    The output subpackage compiles interesting information from the database in tabular form for interactive use in dataframes, or for export. Each data source should have its own module in the output subpackage, and within that module there should be a function allowing the output of each of the core tables in the database which come from that data source.  These tabular outputs can and should be denormalized, and include additional information a user might commonly want to work with -- for example including the names of plants and utilities rather than just their IDs. In addition to those data source specific tabular output modules, there’s also a tabular output class PudlTabl defined in pudltabl.py. This class can be used to pull and store subsets of the data from the database, and can also use modules within the analysis subpackage to calculate interesting derived quantities, and provide it as a tabular output.  See the analysis.mcoe module as an example for how this works.

7. Tests.
    Test cases need to be created for each data set’s ETL process. We’re able to exhaustively test the ETL process locally for each dataset, and have set up continuous integration using Travis CI on GitHub so that it pulls down a small subset of each dataset for basic ETL testing.