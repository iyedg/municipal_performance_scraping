import re
import pandera as pa
from pandera import check_output
from itertools import chain, cycle
from typing import List, Union, Dict
from loguru import logger

import pandas as pd


transformed_performance_df_schema = pa.DataFrameSchema(
    columns={
        "criterion_id": pa.Column(pa.Int, nullable=False),
        "name_ar": pa.Column(pa.String, nullable=False),
        "name_fr": pa.Column(pa.String, nullable=False),
        "max_score": pa.Column(pa.Int, nullable=False),
        "score": pa.Column(pa.Int, nullable=False),
        "parent_id": pa.Column(pa.Int, nullable=True),
    }
)
id_regex = r"(?P<{}>\d+)"
var_name_regex = r"(?:_(?P<{}>[a-z]+_[a|f]r|[a-z]+)(?:_|$)+|$)"

levels = ["domain", "sub_domain", "criterion"]
id_names = [f"{id_name}_id" for id_name in levels]
var_names = [f"{var_name}_var_name" for var_name in levels]

regex_components = chain.from_iterable(zip(id_names, var_names))

performance_regex = re.compile(
    "?".join(
        [
            component.format(name)
            for component, name in zip(
                cycle([id_regex, var_name_regex]), regex_components
            )
        ]
    )
)


def json_to_df(json: Dict):
    normalized_df = pd.json_normalize(json, sep="_").melt()
    return (
        normalized_df["variable"]
        .str.extract(performance_regex)
        .pipe(lambda df: df.join(normalized_df))
        .pipe(
            lambda df: df.assign(
                sub_domain_id=df["domain_id"].str.cat(df["sub_domain_id"])
            )
        )
        .pipe(
            lambda df: df.assign(
                criterion_id=df["sub_domain_id"].str.cat(df["criterion_id"])
            )
        )
    )


def transform_level(
    df: pd.DataFrame,
    mask: pd.Series,
    id_var: str,
    var_name_column: str,
    values_column: str = "value",
    parent_id_var: str = None,
):
    if parent_id_var:
        subset_columns = chain.from_iterable(
            [[id_var, parent_id_var], [var_name_column, values_column]]
        )
        pivot_index: Union[List[str], str] = ["parent_id", "criterion_id"]
    else:
        subset_columns = chain.from_iterable(
            [[id_var], [var_name_column, values_column]]
        )
        pivot_index = "criterion_id"

    transformed_level_df = (
        df.pipe(lambda df: df.loc[mask, subset_columns])
        .pipe(
            lambda df: df.rename(
                columns={id_var: "criterion_id", parent_id_var: "parent_id"}
            )
        )
        .pipe(
            lambda df: df.pivot_table(
                index=pivot_index,
                columns=var_name_column,
                values=values_column,
                aggfunc="first",
            )
        )
        .reset_index()
    )
    if not parent_id_var:
        return transformed_level_df.drop(columns=["sommedom", "perf", "annee"])
    return transformed_level_df


@check_output(transformed_performance_df_schema)
def transform_performance_response(json: Dict) -> pd.DataFrame:
    standardized_column_names = {
        "nom_ar": "name_ar",
        "nom_fr": "name_fr",
        "notecrit": "score",
        "crmaxnote": "max_score",
        "maxnote": "max_score",
        "note": "score",
        "ar": "name_ar",
        "fr": "name_fr",
        "maxdom": "max_score",
        "notedom": "score",
    }

    json_as_df = json_to_df(json)

    criterion_mask = json_as_df["sub_domain_id"].notna()
    sub_domain_mask = (
        json_as_df["criterion_id"].isna() & json_as_df["sub_domain_id"].notna()
    )
    domain_mask = json_as_df["criterion_id"].isna() & json_as_df["sub_domain_id"].isna()

    criteria_df = json_as_df.pipe(
        lambda df: transform_level(
            df,
            criterion_mask,
            id_var="criterion_id",
            parent_id_var="sub_domain_id",
            var_name_column="criterion_var_name",
        )
    ).rename(columns=standardized_column_names)
    sub_domains_df = json_as_df.pipe(
        lambda df: transform_level(
            df,
            sub_domain_mask,
            id_var="sub_domain_id",
            parent_id_var="domain_id",
            var_name_column="sub_domain_var_name",
        )
    ).rename(columns=standardized_column_names)
    domains_df = json_as_df.pipe(
        lambda df: transform_level(
            df, domain_mask, id_var="domain_id", var_name_column="domain_var_name",
        )
    ).rename(columns=standardized_column_names)

    return (
        pd.concat([domains_df, sub_domains_df, criteria_df])
        .pipe(lambda df: df.assign(institution="government"))
        .pipe(
            lambda df: df.assign(
                criterion_id=pd.to_numeric(df["criterion_id"]),
                max_score=pd.to_numeric(df["max_score"]),
                score=pd.to_numeric(df["score"]),
                parent_id=pd.to_numeric(df["parent_id"]),
                name_ar=df["name_ar"].str.replace("\r\n", " "),
                name_fr=df["name_fr"].str.replace("\r\n", " "),
            )
        )
        .reset_index(drop=True)
    )


def transform_performance_for_criteria(json: Dict):
    return transform_performance_response(json).drop(columns=["score"])


def transform_performance_for_evaluations(json: Dict, municipality_id: int, year: int):
    return (
        transform_performance_response(json)
        .pipe(lambda df: df.assign(municipality_id=municipality_id, year=year))
        .drop(columns=["name_ar", "name_fr", "max_score", "parent_id", "institution"])
    )
