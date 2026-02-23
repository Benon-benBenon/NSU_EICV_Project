# To import data (images and corresponding metadata) into mongodb database run the following command

## open terminal where your project folder is, then type:
```bash
python manage.py upload_images --stata /home/ben/Desktop/Store_image_in_mongodb/synthetic_cleaned_new_dataset.dta --images /home/ben/Desktop/Store_image_in_mongodb/NEW_IMAGES

```

### New Method for inserting data into mongodb database using chunks and `each chunk` get deleted from memory before next chunk being processed.
```bash
python manage.py upload_images   --csv /home/ben/Desktop/Store_image_in_mongodb/synthetic_final_cleaned_new_dataset.csv   --images /home/ben/Desktop/Store_image_in_mongodb/NEW_IMAGES   --chunksize 50
```

### Some results obtained:

```python
(img_storage_venv) (base) ben@master:~/Desktop/mongo_image_store/mongo_project$ python manage.py upload_images   --csv /home/ben/Desktop/Store_image_in_mongodb/synthetic_final_cleaned_new_dataset.csv   --images /home/ben/Desktop/Store_image_in_mongodb/NE
W_IMAGES   --chunksize 10
🔹 Processing chunk 1 (10 rows)
🔹 Processing chunk 2 (10 rows)
🔹 Processing chunk 3 (10 rows)
🔹 Processing chunk 4 (10 rows)
🔹 Processing chunk 5 (10 rows)
🔹 Processing chunk 6 (10 rows)
🔹 Processing chunk 7 (10 rows)
🔹 Processing chunk 8 (10 rows)
🔹 Processing chunk 9 (10 rows)
🔹 Processing chunk 10 (10 rows)
🔹 Processing chunk 11 (10 rows)
🔹 Processing chunk 12 (10 rows)
🔹 Processing chunk 13 (10 rows)
🎉 DONE | Uploaded=130 Skipped=0 Missing=0
(img_storage_venv) (base) ben@master:~/Desktop/mongo_image_store/mongo_project$ python manage.py upload_images   --csv /home/ben/Desktop/Store_image_in_mongodb/synthetic_final_cleaned_new_dataset.csv   --images /home/ben/Desktop/Store_image_in_mongodb/NEW_IMAGES   --chunksize 5
🔹 Processing chunk 1 (5 rows)
🔹 Processing chunk 2 (5 rows)
🔹 Processing chunk 3 (5 rows)
🔹 Processing chunk 4 (5 rows)
🔹 Processing chunk 5 (5 rows)
🔹 Processing chunk 6 (5 rows)
🔹 Processing chunk 7 (5 rows)
🔹 Processing chunk 8 (5 rows)
🔹 Processing chunk 9 (5 rows)
🔹 Processing chunk 10 (5 rows)
🔹 Processing chunk 11 (5 rows)
🔹 Processing chunk 12 (5 rows)
🔹 Processing chunk 13 (5 rows)
🔹 Processing chunk 14 (5 rows)
🔹 Processing chunk 15 (5 rows)
🔹 Processing chunk 16 (5 rows)
🔹 Processing chunk 17 (5 rows)
🔹 Processing chunk 18 (5 rows)
🔹 Processing chunk 19 (5 rows)
🔹 Processing chunk 20 (5 rows)
🔹 Processing chunk 21 (5 rows)
🔹 Processing chunk 22 (5 rows)
🔹 Processing chunk 23 (5 rows)
🔹 Processing chunk 24 (5 rows)
🔹 Processing chunk 25 (5 rows)
🔹 Processing chunk 26 (5 rows)
🎉 DONE | Uploaded=130 Skipped=0 Missing=0
(img_storage_venv) (base) ben@master:~/Desktop/mongo_image_store/mongo_project$ python manage.py upload_images   --csv /home/ben/Desktop/Store_image_in_mongodb/synthetic_final_cleaned_new_dataset.csv   --images /home/ben/Desktop/Store_image_in_mongodb/NEW_IMAGES   --chunksize 50
🔹 Processing chunk 1 (50 rows)
🔹 Processing chunk 2 (50 rows)
🔹 Processing chunk 3 (30 rows)
🎉 DONE | Uploaded=130 Skipped=0 Missing=0
(img_storage_venv) (base) ben@master:~/Desktop/mongo_image_store/mongo_project$ python manage.py upload_images   --csv /home/ben/Desktop/Store_image_in_mongodb/synthetic_final_cleaned_new_dataset.csv   --images /home/ben/Desktop/Store_image_in_mongodb/NEW_IMAGES   --chunksize 130
🔹 Processing chunk 1 (130 rows)
🎉 DONE | Uploaded=130 Skipped=0 Missing=0

(img_storage_venv) (base) ben@master:~/Desktop/mongo_image_store/mongo_project$ python manage.py upload_images   --csv /home/ben/Desktop/Store_image_in_mongodb/synthetic_final_cleaned_new_dataset.csv   --images /home/ben/Desktop/Store_image_in_mongodb/NEW_IMAGES   --chunksize 12
🔹 Processing chunk 1 (12 rows)
🔹 Processing chunk 2 (12 rows)
🔹 Processing chunk 3 (12 rows)
🔹 Processing chunk 4 (12 rows)
🔹 Processing chunk 5 (12 rows)
🔹 Processing chunk 6 (12 rows)
🔹 Processing chunk 7 (12 rows)
🔹 Processing chunk 8 (12 rows)
🔹 Processing chunk 9 (12 rows)
🔹 Processing chunk 10 (12 rows)
🔹 Processing chunk 11 (10 rows)
🎉 DONE | Uploaded=130 Skipped=0 Missing=0
(img_storage_venv) (base) ben@master:~/Desktop/mongo_image_store/mongo_project$ 
```



