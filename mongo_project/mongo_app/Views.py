# mongo_app/Views.py

from django.shortcuts import render
from django.http import JsonResponse, HttpResponse
from django.conf import settings
from .mongo_utils import get_mongo_connection
from django.shortcuts import render, redirect
from .forms import UploadSingleImageForm
import os, pandas as pd
from bson import ObjectId
import shutil
import zipfile


# # -------------- 1. MAIN FILTER VIEW --------------
# def index(request):
#     db, fs = get_mongo_connection(settings.MONGO_URI, settings.MONGO_DBNAME)

#     query = {}
#     selected_filters = {}

#     # ----------------- Multi-select filters -----------------
#     multi_select_fields = ['Province', 'District', 'Sector', 'b_products', 'b_nsu']
#     for field in multi_select_fields:
#         values = request.GET.getlist(field)
#         if values:
#             query[f"metadata.{field}"] = {"$in": values}
#         selected_filters[field] = values

#     # ----------------- bq3 (measurement unit) -----------------
#     bq3_value = request.GET.get("bq3")  # single select
#     if bq3_value:
#         query["metadata.bq3"] = bq3_value  # filter only if selected
#     selected_filters["bq3"] = [bq3_value] if bq3_value else []

#     # ----------------- Retrieve images -----------------
#     files = list(db.fs.files.find(query).limit(50))
#     results = []
#     for f in files:
#         metadata = f.get('metadata', {})
#         # Convert bq3 numeric value to human-readable unit
#         if metadata.get('bq3') == "1":
#             metadata['bq3_unit'] = "kg"
#         elif metadata.get('bq3') == "2":
#             metadata['bq3_unit'] = "litre"
#         else:
#             metadata['bq3_unit'] = ""
#         results.append({
#             'filename': f['filename'],
#             'file_id': str(f['_id']),
#             'metadata': metadata
#         })

#     # ----------------- Dropdown data -----------------
#     provinces = sorted(db.fs.files.distinct("metadata.Province"))
#     districts = sorted(db.fs.files.distinct("metadata.District"))
#     sectors = sorted(db.fs.files.distinct("metadata.Sector"))
#     products = sorted(db.fs.files.distinct("metadata.b_products"))
#     b_nsu_values = sorted(db.fs.files.distinct("metadata.b_nsu"))
#     bq3_values = sorted(db.fs.files.distinct("metadata.bq3"))

#     context = {
#         'results': results,
#         'provinces': provinces,
#         'districts': districts,
#         'sectors': sectors,
#         'products': products,
#         'b_nsu_values': b_nsu_values,
#         'bq3_values': bq3_values,
#         'selected_filters': selected_filters
#     }

#     return render(request, 'mongo_app/index.html', context)


# ------------------------------
# MAIN FILTER VIEW
# ------------------------------

def index(request):

    db, fs = get_mongo_connection(
        settings.MONGO_URI,
        settings.MONGO_DBNAME
    )

    # Query + filter tracking
    query = {}
    selected_filters = {}
    pretty_filters = {}   # <-- renamed keys for UI

    # Human readable names for UI
    FILTER_DISPLAY = {
        "Province": "Province",
        "District": "District",
        "Sector": "Sector",
        "b_products": "Product",
        "b_nsu": "NSU",
        "bq3": "Measurement Unit"
    }


    # ------------------------------------------------------
    # Multi-select filters
    # ------------------------------------------------------
    multi_select_fields = ['Province','District','Sector','b_products','b_nsu']

    for field in multi_select_fields:

        values = request.GET.getlist(field)

        if values:
            query[f"metadata.{field}"] = {"$in": values}

        selected_filters[field] = values
        pretty_filters[FILTER_DISPLAY[field]] = values


    # ------------------------------------------------------
    # Single select filter (measurement unit)
    # ------------------------------------------------------
    bq3 = request.GET.get("bq3")

    if bq3:
        query["metadata.bq3"] = bq3
        selected_filters["bq3"] = [bq3]
    else:
        selected_filters["bq3"] = []

    pretty_filters["Measurement Unit"] = selected_filters["bq3"]


    # ------------------------------------------------------
    # Retrieve images
    # ------------------------------------------------------
    files = list(db.fs.files.find(query).limit(50))

    results = []

    for f in files:

        metadata = f.get("metadata", {})

        # Convert numeric unit to readable text
        if metadata.get("bq3") == "1":
            metadata["bq3_unit"] = "kg"
        elif metadata.get("bq3") == "2":
            metadata["bq3_unit"] = "litre"
        else:
            metadata["bq3_unit"] = ""

        results.append({
            "filename": f["filename"],
            "file_id": str(f["_id"]),
            "metadata": metadata
        })


    # ------------------------------------------------------
    # Dropdown data
    # ------------------------------------------------------
    context = {
        "results": results,

        "provinces": sorted(db.fs.files.distinct("metadata.Province")),
        "districts": sorted(db.fs.files.distinct("metadata.District")),
        "sectors": sorted(db.fs.files.distinct("metadata.Sector")),
        "products": sorted(db.fs.files.distinct("metadata.b_products")),
        "b_nsu_values": sorted(db.fs.files.distinct("metadata.b_nsu")),
        "bq3_values": sorted(db.fs.files.distinct("metadata.bq3")),

        "selected_filters": pretty_filters   # <-- use renamed keys
    }

    return render(request, "mongo_app/index.html", context)



# -------------- 2. CASCADED DROPDOWN ENDPOINT --------------
def get_child_options(request):
    """AJAX endpoint: returns districts for a province or sectors for a district."""
    db, _ = get_mongo_connection(settings.MONGO_URI, settings.MONGO_DBNAME)
    parent_field = request.GET.get("parent_field")
    parent_value = request.GET.get("parent_value")

    if parent_field == "Province":
        options = db.fs.files.distinct("metadata.District", {"metadata.Province": parent_value})
    elif parent_field == "District":
        options = db.fs.files.distinct("metadata.Sector", {"metadata.District": parent_value})
    else:
        options = []

    return JsonResponse({"options": sorted(options)})


# # -------------- 3. EXPORT FILTERED DATA --------------
# def export_csv(request):
#     # Connect to MongoDB
#     db, fs = get_mongo_connection(settings.MONGO_URI, settings.MONGO_DBNAME)

#     # Build query from filters
#     query = {}
#     multi_select_fields = ['Province', 'District', 'Sector', 'b_products', 'b_nsu']
#     for field in multi_select_fields:
#         values = request.GET.getlist(field)
#         if values:
#             query[f"metadata.{field}"] = {"$in": values}

#     # bq3 single filter (measurement unit)
#     bq3_value = request.GET.get("bq3")
#     if bq3_value:
#         query["metadata.bq3"] = bq3_value

#     # Get matching files
#     files = list(db.fs.files.find(query))

#     # Define export folder
#     export_folder = "exported_images"

#     # ✅ Remove any old exports completely before writing new ones
#     if os.path.exists(export_folder):
#         shutil.rmtree(export_folder)
#     os.makedirs(export_folder, exist_ok=True)

#     # Prepare CSV data
#     rows = []
#     for f in files:
#         meta = f.get("metadata", {})

#         # Convert measurement unit
#         if meta.get('bq3') == "1":
#             meta['bq3_unit'] = "kg"
#         elif meta.get('bq3') == "2":
#             meta['bq3_unit'] = "litre"
#         else:
#             meta['bq3_unit'] = ""

#         rows.append(meta)

#         # ✅ Always save fresh images (old ones were cleared)
#         image_path = os.path.join(export_folder, f['filename'])
#         with open(image_path, "wb") as img:
#             img.write(fs.get(f["_id"]).read())
    
#     # If no rows, return an empty CSV message
#     if not rows:
#         response = HttpResponse("No matching data found.", content_type="text/plain")
#         response['Content-Disposition'] = 'attachment; filename="filtered_data.csv"'
#         return response

#     # Create DataFrame
#     df = pd.DataFrame(rows)

#     # ✅ Rename columns to meaningful names
#     rename_map = {
#         "combined_id": "Image_name",
#         "enumerator": "Enumerator",
#         "seqnum": "Sequential_number",
#         "b_code_produit_unite": "Product_unit_code",
#         "b_group": "Group",
#         "b_products": "Product",
#         "b_nsu": "NSU",
#         "bq3": "Measurement_unit",
#         "bq5": "Weight_in_grams",
#         "bq6": "Group_code",
#         "bq7": "Weight_converted_in_kg_litre",
#         "bq3_unit": "Unit_string",
#         "Province": "Province",
#         "District": "District",
#         "Sector": "Sector",
#     }

#     # Apply renaming (only those present in DataFrame)
#     df.rename(columns={k: v for k, v in rename_map.items() if k in df.columns}, inplace=True)

#     # Save CSV file
#     csv_path = os.path.join(export_folder, "filtered_data.csv")
#     df.to_csv(csv_path, index=False)

#     # Return CSV as download
#     with open(csv_path, "rb") as f:
#         response = HttpResponse(f.read(), content_type="text/csv")
#         response['Content-Disposition'] = 'attachment; filename=\"filtered_data.csv\"'
#         return response
    

#     # # Save CSV file
#     # df = pd.DataFrame(rows)
#     # csv_path = os.path.join(export_folder, "filtered_data.csv")
#     # df.to_csv(csv_path, index=False)

#     # # Return CSV as download
#     # with open(csv_path, "rb") as f:
#     #     response = HttpResponse(f.read(), content_type="text/csv")
#     #     response['Content-Disposition'] = 'attachment; filename="filtered_data.csv"'
#     #     return response

# -------------- 4. SERVE IMAGE --------------
def get_image(request, file_id):
    _, fs = get_mongo_connection(settings.MONGO_URI, settings.MONGO_DBNAME)
    file_data = fs.get(ObjectId(file_id)).read()
    return HttpResponse(file_data, content_type="image/jpeg")

def export_csv(request):
    # Connect to MongoDB
    db, fs = get_mongo_connection(settings.MONGO_URI, settings.MONGO_DBNAME)

    # ------------------------------
    # Build query from filters
    # ------------------------------
    query = {}
    multi_select_fields = ['Province', 'District', 'Sector', 'b_products', 'b_nsu']
    for field in multi_select_fields:
        values = request.GET.getlist(field)
        if values:
            query[f"metadata.{field}"] = {"$in": values}

    # Single-select filter
    bq3_value = request.GET.get("bq3")
    if bq3_value:
        query["metadata.bq3"] = bq3_value

    # ------------------------------
    # Fetch matching files
    # ------------------------------
    files = list(db.fs.files.find(query))

    # ------------------------------
    # Prepare export directory
    # ------------------------------
    base_folder = "exported_csv"
    csv_folder = os.path.join(base_folder, "csv_data")

    # Clear previous export
    if os.path.exists(base_folder):
        shutil.rmtree(base_folder)
    os.makedirs(csv_folder, exist_ok=True)

    # ------------------------------
    # Collect metadata for CSV
    # ------------------------------
    rows = []
    for f in files:
        meta = f.get("metadata", {}).copy()

    
        # Convert measurement unit
        if str(meta.get('bq3')) == "1":
            meta['bq3_unit'] = "kg"
        elif str(meta.get('bq3')) == "2":
            meta['bq3_unit'] = "litre"
        else:
            meta['bq3_unit'] = ""

        rows.append(meta)

    # ------------------------------
    # Handle empty case
    # ------------------------------
    if not rows:
        response = HttpResponse("No matching data found.", content_type="text/plain")
        response['Content-Disposition'] = 'attachment; filename="no_data.txt"'
        return response

    # ------------------------------
    # Build DataFrame
    # ------------------------------
    df = pd.DataFrame(rows)

    rename_map = {
        "combined_id": "Image_name",
        "enumerator": "Enumerator",
        "seqnum": "Sequential_number",
        "b_code_produit_unite": "Product_unit_code",
        "b_group": "Group",
        "b_products": "Product",
        "b_nsu": "NSU",
        "bq3": "Measurement_unit",
        "bq5": "Weight_in_grams",
        "bq6": "Group_code",
        "bq7": "Weight_converted_in_kg_litre",
        "bq3_unit": "Unit_string",
        "Province": "Province",
        "District": "District",
        "Sector": "Sector",
    }

    df.rename(columns={k: v for k, v in rename_map.items() if k in df.columns}, inplace=True)

    # ------------------------------
    # Save CSV
    # ------------------------------
    csv_path = os.path.join(csv_folder, "filtered_data.csv")
    df.to_csv(csv_path, index=False)

    # ------------------------------
    # ZIP only the CSV folder
    # ------------------------------
    zip_filename = "exported_csv.zip"
    zip_path = os.path.join(settings.BASE_DIR, zip_filename)

    with zipfile.ZipFile(zip_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
        for root, dirs, files in os.walk(base_folder):
            for file in files:
                abs_path = os.path.join(root, file)
                rel_path = os.path.relpath(abs_path, base_folder)
                zipf.write(abs_path, rel_path)

    # ------------------------------
    # Return ZIP as download
    # ------------------------------
    with open(zip_path, "rb") as f:
        response = HttpResponse(f.read(), content_type="application/zip")
        response['Content-Disposition'] = f'attachment; filename="{zip_filename}"'
        return response


db, fs = get_mongo_connection(settings.MONGO_URI, settings.MONGO_DBNAME)

def upload_single_entry(request):

    if request.method == "POST":
        form = UploadSingleImageForm(request.POST, request.FILES)

        if form.is_valid():
            data = form.cleaned_data
            uploaded_file = request.FILES["image_file"]
            combined_id = data["combined_id"]
            filename = f"{combined_id}.jpg"

            # Check duplicate
            exists = db.fs.files.find_one({"metadata.combined_id": combined_id})
            if exists:
                return render(request, "upload_form.html", {
                    "form": form,
                    "error": "Entry with this Combined ID already exists."
                })

            # Save to GridFS
            file_id = fs.put(
                uploaded_file.read(),
                filename=filename,
                metadata=data
            )

            return render(request, "mongo_app/upload_form.html", {
                "form": UploadSingleImageForm(),
                "success": f"Successfully uploaded (file_id: {file_id})"
            })

    else:
        form = UploadSingleImageForm()

    return render(request, "mongo_app/upload_form.html", {"form": form})
