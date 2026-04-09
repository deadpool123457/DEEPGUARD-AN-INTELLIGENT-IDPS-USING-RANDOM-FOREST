import urllib.request
import os

# The direct link to the raw data
url = "https://raw.githubusercontent.com/defcom17/NSL_KDD/master/KDDTrain%2B.txt"
filename = "KDDTrain+.txt"

print(f"Downloading {filename} from GitHub...")
print("This is about 19MB, so it might take 10-20 seconds...")

try:
    # This downloads the file and saves it in your folder
    urllib.request.urlretrieve(url, filename)
    print("\n[SUCCESS] File downloaded successfully!")
    print(f"Saved as: {os.path.abspath(filename)}")
except Exception as e:
    print(f"\n[ERROR] Download failed: {e}")