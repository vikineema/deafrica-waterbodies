import numpy as np
import geopandas as gpd


def id_field_values_is_unique(input_gdf: gpd.geopandas.GeoDataFrame,
                              id_field: str) -> bool:
    """
    Check if values of `id_field` column are unique or not in GeoDataFrame.

    Parameters
    ----------
    input_gdf : gpd.geopandas.GeoDataFrame
        GeoDataFrame to check.
    id_field : str
        Unique key column in GeoDataFrame.

    Returns
    -------
    bool
        `id_field` column values are unique or not.
    """
    no_of_gdf_rows = len(input_gdf)
    no_of_unique_id = np.size(input_gdf[id_field].unique())

    return no_of_gdf_rows == no_of_unique_id


def guess_id_field(input_gdf: gpd.geopandas.GeoDataFrame,
                   use_id: str = "") -> str:
    """
    Guess the name of the ID column in the GeoDataFrame, if no column name is
    passed to the `use_id` parameter.
    If a column name is passed to `use_id`, check if the ids in the column are
    unique.

    Parameters
    ----------
    input_gdf : gpd.geopandas.GeoDataFrame
        GeoDataFrame to guess ID column for.
    use_id : str, optional
        Unique key column in GeoDataFrame, by default "".

    Returns
    -------
    str
        ID column name

    """

    input_gdf_columns = list(input_gdf.columns)

    # Check if values in passed use_id column are unique.
    if use_id:
        if use_id not in input_gdf_columns:
            raise ValueError(f"Couldn't find ID column '{use_id}' in the vector file columns: {input_gdf_columns}.")
        else:
            if id_field_values_is_unique(input_gdf, use_id):
                return use_id
            else:
                raise ValueError(
                    f"Values in the {use_id} column are not unique."
                )

    # Guess ID column to use.
    else:
        possible_id_columns = [
            # In order of preference.
            "UID",
            "WB_ID",
            "FID_1",
            "FID",
            "ID",
            "OBJECTID",
            "ORIG_FID",
            "FeatureID",
        ]

        guess_result = []

        for guess in possible_id_columns:
            if guess in input_gdf_columns:
                guess_result.append(guess)

        # If none of the possible_id_columns columns were found, 
        # let us try the lower case.
        if not guess_result:
            for guess in possible_id_columns:
                guess = guess.lower()
                if guess in input_gdf_columns:
                    guess_result.append(guess)

        if not guess_result:
            raise ValueError(f"Couldn't find any ID column {possible_id_columns} in the vector file columns: {input_gdf_columns}.")
        else:
            for list_index, list_item in enumerate(guess_result):
                if id_field_values_is_unique(input_gdf, list_item):
                    return list_item
                else:
                    if list_index + 1 == len(guess_result):
                        raise ValueError(f"ID values in the column(s) {guess_result} are not unique.")
                    else:
                        continue