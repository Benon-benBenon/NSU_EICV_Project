import pandas as pd
import gc
from django.core.management.base import BaseCommand
from mongo_app.upload.image_uploader import prepare_dataframe, upload_images


class Command(BaseCommand):
    help = "Upload images + metadata into MongoDB using chunked processing"

    def add_arguments(self, parser):
        parser.add_argument("--stata", type=str)
        parser.add_argument("--csv", type=str)
        parser.add_argument("--images", type=str, required=True)
        parser.add_argument("--chunksize", type=int, default=1000)

    def handle(self, *args, **kwargs):
        stata_path = kwargs.get("stata")
        csv_path = kwargs.get("csv")
        image_folder = kwargs["images"]
        chunksize = kwargs["chunksize"]
        if not (stata_path or csv_path):
            self.stderr.write("❌ Provide --stata or --csv")
            return

        # Choose reader
        if stata_path:
            reader = pd.read_stata(
                stata_path,
                chunksize=chunksize,
                convert_categoricals=True,
                preserve_dtypes=False
            )
        else:
            reader = pd.read_csv(csv_path, chunksize=chunksize)

        total_uploaded = total_skipped = total_missing = 0

        for i, chunk in enumerate(reader, start=1):
            self.stdout.write(f"🔹 Processing chunk {i} ({len(chunk)} rows)")

            chunk = prepare_dataframe(chunk)
            u, s, m = upload_images(chunk, image_folder)

            total_uploaded += u
            total_skipped += s
            total_missing += m

            # 🔥 CRITICAL: FREE MEMORY HERE
            del chunk
            gc.collect()

        self.stdout.write(self.style.SUCCESS(
            f"🎉 DONE | Uploaded={total_uploaded} Skipped={total_skipped} Missing={total_missing}"
        ))
