import pandas as pd
from django.core.management.base import BaseCommand
from mongo_app.upload.image_uploader import prepare_dataframe, upload_images


class Command(BaseCommand):
    help = "Upload images + metadata into MongoDB (GridFS) using .dta or .csv dataset"

    def add_arguments(self, parser):
        parser.add_argument(
            "--stata",
            type=str,
            help="Path to STATA (.dta) dataset"
        )
        parser.add_argument(
            "--csv",
            type=str,
            help="Path to CSV dataset"
        )
        parser.add_argument(
            "--images",
            type=str,
            required=True,
            help="Folder containing images"
        )

    def handle(self, *args, **kwargs):

        stata_path = kwargs.get("stata")
        csv_path = kwargs.get("csv")
        image_folder = kwargs["images"]

        # ------------------------------------
        # Load dataset
        # ------------------------------------
        if stata_path:
            self.stdout.write("📘 Loading STATA dataset...")
            try:
                df = pd.read_stata(stata_path, convert_categoricals=True)
            except Exception as e:
                self.stdout.write(self.style.ERROR(f"Error reading STATA file: {e}"))
                return

        elif csv_path:
            self.stdout.write("📗 Loading CSV dataset...")
            try:
                df = pd.read_csv(csv_path)
            except Exception as e:
                self.stdout.write(self.style.ERROR(f"Error reading CSV file: {e}"))
                return
        else:
            self.stdout.write(self.style.ERROR("❌ Please provide --stata or --csv"))
            return

        # ------------------------------------
        # Prepare dataframe
        # ------------------------------------
        df = prepare_dataframe(df)

        # ------------------------------------
        # Upload images
        # ------------------------------------
        self.stdout.write("🚀 Starting upload...")
        upload_images(df, image_folder)

        self.stdout.write(self.style.SUCCESS("🎉 Upload completed!"))
