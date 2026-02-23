import os
import pandas as pd
import numpy as np
from pymongo import MongoClient,ASCENDING
import gridfs

# -------------------------------------------
# MongoDB Connection
# -------------------------------------------
client = MongoClient("mongodb://localhost:27017/")
db = client["new_method_metadata_ncu_image_database"]
fs = gridfs.GridFS(db)

# -------------------------------------------
# CREATE INDEX (VERY IMPORTANT)
# -------------------------------------------
db.fs.files.create_index(
    [("metadata.combined_id", ASCENDING)],
    unique=True,
    name="idx_combined_id"
)

# -------------------------------------------
# Metadata whitelist
# -------------------------------------------
ALLOWED_METADATA_FIELDS = [
    "combined_id",
    "enumerator",
    "seqnum",
    "b_code_produit_unite",
    "b_groups",
    "b_products",
    "b_nsu",
    "bq3",
    "bq5",
    "bq6",
    "bq7",
    "id1",  #  id1 Province
    "id2",  #  id2 District
    "id3"   #  id3 Sector
]

# ---------------------------------------------------
# CLEAN + PREPARE DATAFRAME (PER CHUNK)
# ---------------------------------------------------
def prepare_dataframe(df):
    df = df.copy()

    df["enumerator_padded"] = df["enumerator"].astype(str).str.zfill(4)
    df["seqnum_padded"] = df["seqnum"].astype(str).str.zfill(4)
    df["b_code_produit_unite_padded"] = (
        df["b_code_produit_unite"].astype(str).str.zfill(6)
    )

    df["combined_id"] = (
        "D"
        + df["enumerator_padded"]
        + df["seqnum_padded"]
        + df["b_code_produit_unite_padded"]
    )

    df = df.replace(["na", "Na", "NA", "NaN", ""], np.nan)
    df = df.dropna(subset=["combined_id", "b_products"])
    df = df.drop_duplicates(subset=["combined_id"])

    return df


# ---------------------------------------------------
# UPLOAD IMAGES (STREAMING SAFE)
# ---------------------------------------------------
def upload_images(df, image_folder):
    uploaded, skipped, missing = 0, 0, 0

    # FAST LOOKUP TABLE
    image_map = {
        f.split(".")[0]: f for f in os.listdir(image_folder)
    }

    for _, row in df.iterrows():
        combined_id = str(row["combined_id"])

        image_file = image_map.get(combined_id)
        if not image_file:
            missing += 1
            continue

        # Skip duplicates (fast via index)
        if db.fs.files.find_one({"metadata.combined_id": combined_id}):
            skipped += 1
            continue

        metadata = {
            col: None if pd.isna(row[col]) else row[col]
            for col in ALLOWED_METADATA_FIELDS
            if col in row
        }

        metadata.update({
            "Province": metadata.get("id1"), #id1  Province
            "District": metadata.get("id2"), #id2  District
            "Sector": metadata.get("id3"),  #id3   Sector
        })

        image_path = os.path.join(image_folder, image_file)

        with open(image_path, "rb") as f:
            fs.put(f, filename=image_file, metadata=metadata)

        uploaded += 1

    return uploaded, skipped, missing
