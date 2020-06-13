from typing import Dict, List, Union

import pandera as pa

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


def all_numeric_keys(d: dict) -> bool:
    return all([str(key).isnumeric() for key in d.keys()])


def indent_keys(d: dict, indented_key: str = "id") -> list:
    """
    Return a list of dictionaries where the keys of the input dictionary are values in the child dictionaries.
    """
    dicts = []
    for key, value in d.items():
        value[indented_key] = key
        dicts.append(value)
    return dicts


def format_json(
    raw_performance_response: dict, parent_id: str = None
) -> Union[List[Dict], Dict]:
    if all_numeric_keys(raw_performance_response):
        indented = indent_keys(raw_performance_response)
        return [format_json(d) for d in indented]
    else:
        new_dict = {}
        for key, value in raw_performance_response.items():
            if isinstance(value, dict):
                if all_numeric_keys(value):
                    new_dict[key] = format_json(value)
                else:
                    # merge child name dicts into parent dict
                    new_dict.update(value)
            else:
                new_dict[key] = value
        return new_dict
