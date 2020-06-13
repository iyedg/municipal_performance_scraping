import pandas as pd
import pandera as pa
from glom import T, glom

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


def clean_string(s: str) -> str:
    return str(s).replace("\r\n", " ").strip()


def transform_raw_performance_response(raw_response: dict) -> pd.DataFrame:
    normalized_data = []

    domain_spec = {
        "name_ar": ("ar", clean_string),
        "name_fr": ("fr", clean_string),
        "max_score": ("maxdom", int),
        "score": ("notedom", int),
    }

    subdomain_spec = {
        "name_ar": ("nom.ar", clean_string),
        "name_fr": ("nom.fr", clean_string),
        "max_score": ("maxnote", int),
        "score": ("note", int),
    }

    criterion_spec = {
        "name_ar": ("nom.ar", clean_string),
        "name_fr": ("nom.fr", clean_string),
        "max_score": ("crmaxnote", int),
        "score": ("notecrit", int),
    }

    for domain_id, domain in raw_response.items():
        normalized_domain = {"parent_id": None, "criterion_id": domain_id}
        glommed = glom(domain, domain_spec)

        normalized_domain.update(glommed)
        normalized_data.append(normalized_domain)

        for subdomain_id, subdomain in glom(domain, ("sd", T.items())):
            normalized_subdomain = {
                "parent_id": domain_id,
                "criterion_id": f"{domain_id}{subdomain_id}",
            }
            glommed = glom(subdomain, subdomain_spec)

            normalized_subdomain.update(glommed)
            normalized_data.append(normalized_subdomain)

            for criterion_id, criterion in glom(subdomain, ("cr", T.items())):
                normalized_criterion = {
                    "parent_id": subdomain_id,
                    "criterion_id": f"{domain_id}{subdomain_id}{criterion_id}",
                }
                glommed = glom(criterion, criterion_spec)

                normalized_criterion.update(glommed)
                normalized_data.append(normalized_criterion)
    return pd.DataFrame(normalized_data)
