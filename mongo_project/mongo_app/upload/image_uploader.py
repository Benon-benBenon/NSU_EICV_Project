import os
import pandas as pd
import numpy as np
from pymongo import MongoClient
import gridfs

# -------------------------------------------
# Connect to MongoDB
# -------------------------------------------
client = MongoClient("mongodb://localhost:27017/")
db = client["metadata_ncu_image_database"]
fs = gridfs.GridFS(db)

# -------------------------------------------
# Metadata fields that will be saved
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
    "id1",  # Province
    "id2",  # District
    "id3"   # Sector
]

# ---------------------------------------------------
# CLEAN + PREPARE DATAFRAME
# ---------------------------------------------------
def prepare_dataframe(df):

    # Zero padding
    df["enumerator_padded"] = df["enumerator"].astype(str).str.zfill(4)
    df["seqnum_padded"] = df["seqnum"].astype(str).str.zfill(4)
    df["b_code_produit_unite_padded"] = df["b_code_produit_unite"].astype(str).str.zfill(6)

    # Combined ID
    df["combined_id"] = (
        "D"
        + df["enumerator_padded"]
        + df["seqnum_padded"]
        + df["b_code_produit_unite_padded"]
    )

    # Remove bad rows
    df = df.replace(["na", "Na", "NA", "NaN", ""], np.nan)
    df = df.dropna(subset=["combined_id", "b_products"])
    df = df.dropna()
    df = df.drop_duplicates(subset=["combined_id"]).reset_index(drop=True)

    print(f"✅ Cleaned dataset shape: {df.shape}")

    return df


# ---------------------------------------------------
# UPLOAD IMAGES TO MONGODB GRIDFS
# ---------------------------------------------------
def upload_images(df, image_folder):

    uploaded = 0
    skipped = 0
    missing = []

    all_files = os.listdir(image_folder)

    for _, row in df.iterrows():
        combined_id = str(row["combined_id"])

        # Find image file
        image_file = next((f for f in all_files if f.startswith(combined_id)), None)

        if image_file is None:
            print(f"❌ Missing image for ID: {combined_id}")
            missing.append(combined_id)
            continue

        image_path = os.path.join(image_folder, image_file)

        # Skip duplicates
        exists = db.fs.files.find_one({"metadata.combined_id": combined_id})
        if exists:
            print(f"⚠️ Skipped (already exists): {image_file}")
            skipped += 1
            continue

        # ---------------------------------------------
        # BUILD METADATA FROM WHITELIST
        #----------------------------------------------
        metadata = {}

        for col in ALLOWED_METADATA_FIELDS:
            if col in row:
                val = row[col]
                metadata[col] = None if pd.isna(val) else val

        # Add readable aliases
        metadata["province_id"] = metadata.get("id1")
        metadata["Province"] = metadata.get("id1")

        metadata["district_id"] = metadata.get("id2")
        metadata["District"] = metadata.get("id2")

        metadata["sector_id"] = metadata.get("id3")
        metadata["Sector"] = metadata.get("id3")

        # ---------------------------------------------
        # UPLOAD TO GRIDFS
        # ---------------------------------------------
        with open(image_path, "rb") as f:
            file_id = fs.put(f, filename=image_file, metadata=metadata)

        uploaded += 1
        print(f"✅ Uploaded: {image_file}  → file_id={file_id}")

    # Summary
    print("\n----------- UPLOAD SUMMARY -----------")
    print(f"Uploaded: {uploaded}")
    print(f"Skipped duplicates: {skipped}")
    print(f"Missing images: {len(missing)}")

    return uploaded, skipped, missing
