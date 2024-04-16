import pandas as pd
import requests
from dagster import Output, MetadataValue, asset

from ..resources import MongoDBResource


@asset(compute_kind="python")
def raw_storage_providers_filrep_reputation() -> Output[pd.DataFrame]:
    """
    Storage Provider reputation data from Filrep (https://filrep.io).
    """

    url = "https://api.filrep.io/api/v1/miners"

    storage_providers = pd.DataFrame(requests.get(url).json()["miners"])
    storage_providers["name"] = storage_providers["tag"].apply(lambda x: x.get("name"))
    storage_providers = storage_providers.convert_dtypes()

    return Output(
        storage_providers.drop(
            columns=[
                "id",
                "price",
                "verifiedPrice",
                "minPieceSize",
                "maxPieceSize",
                "rawPower",
                "qualityAdjPower",
                "creditScore",
            ]
        ),
        metadata={
            "Sample": MetadataValue.md(storage_providers.sample(5).to_markdown())
        },
    )


@asset(compute_kind="python")
def raw_retrieval_bot_measures(reputation_db: MongoDBResource) -> Output[pd.DataFrame]:
    """
    Retrieval bot measures.
    """

    collection_names = [
        "retrievalbot_1",
        "retrievalbot_2",
        "retrievalbot_3",
        "retrievalbot_4",
        "retrievalbot_5",
        "retrievalbot_6",
        "glif_retrieval_bot",
    ]

    df = pd.DataFrame()

    for name in collection_names:
        c = reputation_db.get_collection("reputation", name)

        collection_df = pd.DataFrame.from_records(c.find())

        df = pd.concat([df, collection_df], ignore_index=True)

    df.drop(columns=["_id"], inplace=True)

    return Output(df, metadata={"Sample": MetadataValue.md(df.sample(5).to_markdown())})