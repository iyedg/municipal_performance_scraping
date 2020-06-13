import concurrent.futures

import pandas as pd
from loguru import logger
from tqdm import tqdm

from . import models
from .extractors import extract_performance_data, extract_raw_official_names

# from .transformers import (
#     transform_performance_response,
#     transform_performance_for_criteria,
#     transform_performance_for_evaluations,
# )


def load_governorates_prep(df):
    return (
        df.loc[:, ["id_gouvernorat", "Libelle_gouvernorat", "Libelle_gouvernorat_Fr"]]
        .rename(columns=dict(zip(df.columns, ["governorate_id", "name_ar", "name_fr"])))
        .drop_duplicates()
    )


def load_governorates():
    official_names_df = extract_raw_official_names()
    official_names_df.pipe(load_governorates_prep).to_sql(
        name="governorates", con=models.engine, if_exists="append", index=False
    )


def load_municipalities_prep(df):
    return df.loc[
        :, ["id_gouvernorat", "id_commune", "Libelle_commune", "Libelle_commune_fr"]
    ].pipe(
        lambda df: df.rename(
            columns=dict(
                zip(
                    df.columns,
                    ["governorate_id", "municipality_id", "name_ar", "name_fr"],
                )
            )
        )
    )


def load_municipalities():
    official_names_df = extract_raw_official_names()
    official_names_df.pipe(load_municipalities_prep).to_sql(
        name="municipalities", con=models.engine, if_exists="append", index=False
    )


def load_performance_criteria():
    perf_response = extract_performance_data(1313, 2017)
    transformed = transform_performance_for_criteria(perf_response)
    transformed.to_sql(
        name="criteria", con=models.engine, index=False, if_exists="append"
    )


def load_evaluation(df: pd.DataFrame):
    df.to_sql(name="evaluations", con=models.engine, if_exists="append", index=False)


def load_evaluations():

    municipality_ids = pd.read_sql("select * from municipalities;", con=models.engine)[
        "municipality_id"
    ]

    transformed_performance_data = []
    with concurrent.futures.ThreadPoolExecutor(max_workers=5) as executor:
        future_extracted_performance_data = {
            executor.submit(
                extract_performance_data, municipality_id=municipality_id, year=year,
            ): {"municipality_id": municipality_id, "year": year}
            for year in [2017, 2018]
            for municipality_id in tqdm(municipality_ids)
        }
        for future in tqdm(
            concurrent.futures.as_completed(future_extracted_performance_data)
        ):
            municipality_id, year = future_extracted_performance_data[future].values()
            logger.info(f"Result for {municipality_id} on {year}")
            try:
                transformed_performance_data.append(
                    transform_performance_for_evaluations(
                        future.result(), **future_extracted_performance_data[future],
                    ),
                )
            except Exception as e:
                logger.error(e)
    for t in transformed_performance_data:
        try:
            t.to_sql(
                name="evaluations", con=models.engine, index=False, if_exists="append"
            )
        except Exception as e:
            logger.error(e)
            break
