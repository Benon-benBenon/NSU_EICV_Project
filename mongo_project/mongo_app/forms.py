from django import forms

class UploadSingleImageForm(forms.Form):
    enumerator = forms.CharField(max_length=50)
    seqnum = forms.CharField(max_length=50)
    b_code_produit_unite = forms.CharField(max_length=50)
    b_group = forms.CharField(max_length=100)
    b_products = forms.CharField(max_length=100)
    b_nsu = forms.CharField(max_length=50)
    bq3 = forms.CharField(max_length=10)
    bq5 = forms.CharField(max_length=10)
    bq6 = forms.CharField(max_length=10)
    bq7 = forms.CharField(max_length=10)
    province_id = forms.CharField(max_length=10)
    Province = forms.CharField(max_length=50)
    district_id = forms.CharField(max_length=10)
    District = forms.CharField(max_length=50)
    sector_id = forms.CharField(max_length=10)
    Sector = forms.CharField(max_length=50)
    combined_id = forms.CharField(max_length=50)

    image_file = forms.ImageField()
