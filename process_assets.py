import os
import json
import shutil
from PIL import Image

def process_assets(input_dir, output_xcassets):
    if os.path.exists(output_xcassets):
        shutil.rmtree(output_xcassets)
    os.makedirs(output_xcassets)

    # Info.json for the root xcassets
    with open(os.path.join(output_xcassets, "Contents.json"), "w") as f:
        json.dump({"info": {"version": 1, "author": "xcode"}}, f)

    for root, dirs, files in os.walk(input_dir):
        for file in files:
            if file.lower().endswith(('.png', '.jpg', '.jpeg', '.pdf')):
                file_path = os.path.join(root, file)
                
                # Determine asset name and scale
                # Example: MyImage@2x.png -> name="MyImage", scale="2x"
                base_name = os.path.splitext(file)[0]
                extension = os.path.splitext(file)[1]
                
                scale = "1x"
                asset_name = base_name
                if "@2x" in base_name:
                    scale = "2x"
                    asset_name = base_name.replace("@2x", "")
                elif "@3x" in base_name:
                    scale = "3x"
                    asset_name = base_name.replace("@3x", "")

                # Create imageset directory
                imageset_dir = os.path.join(output_xcassets, f"{asset_name}.imageset")
                if not os.path.exists(imageset_dir):
                    os.makedirs(imageset_dir)
                
                # Resize image to 1x1
                try:
                    with Image.open(file_path) as img:
                        resized_img = img.resize((1, 1))
                        resized_filename = file # Keep original filename
                        resized_img.save(os.path.join(imageset_dir, resized_filename))
                        print(f"Processed: {file} -> 1x1")
                except Exception as e:
                    print(f"Failed to process {file}: {e}")
                    continue

                # Update or create Contents.json for the imageset
                contents_path = os.path.join(imageset_dir, "Contents.json")
                if os.path.exists(contents_path):
                    with open(contents_path, "r") as f:
                        contents = json.load(f)
                else:
                    contents = {
                        "images": [],
                        "info": {"version": 1, "author": "xcode"}
                    }
                
                # Add this image to the contents if not already there
                if not any(img["filename"] == resized_filename for img in contents["images"]):
                    contents["images"].append({
                        "idiom": "universal",
                        "filename": resized_filename,
                        "scale": scale
                    })
                
                with open(contents_path, "w") as f:
                    json.dump(contents, f, indent=2)

if __name__ == "__main__":
    import sys
    if len(sys.argv) < 3:
        print("Usage: python process_assets.py <input_dir> <output_xcassets>")
        sys.exit(1)
    
    process_assets(sys.argv[1], sys.argv[2])
