import zipfile
import os

# Function to extract a GAE file to a folder
def extract_gae_file(gae_file_path):
    with zipfile.ZipFile(gae_file_path, 'r') as gae_zip:
        # Get the base filename without the extension
        file_name = os.path.splitext(os.path.basename(gae_file_path))[0]
        # Create a folder for extraction
        extraction_folder = os.path.join("Extracted", file_name)
        os.makedirs(extraction_folder, exist_ok=True)

        # Extract the contents of the GAE file to the extraction folder
        gae_zip.extractall(extraction_folder)
        print(f"GAE file '{gae_file_path}' extracted to '{extraction_folder}'")

if __name__ == "__main__":
    gae_file_path = input("Enter the path to the GAE file: ")
    if os.path.isfile(gae_file_path) and gae_file_path.lower().endswith(".gae"):
        extract_gae_file(gae_file_path)
    else:
        print("Invalid GAE file path. Make sure the file exists and has a .gae extension.")
