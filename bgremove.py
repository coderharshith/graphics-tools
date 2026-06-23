import os
from rembg import remove

# Input folder containing images
INPUT_FOLDER = "input"

# Output folder for transparent PNGs
OUTPUT_FOLDER = "output_pngs"

os.makedirs(OUTPUT_FOLDER, exist_ok=True)

SUPPORTED_EXTENSIONS = (".jpg", ".jpeg", ".png", ".webp", ".bmp")

for root, dirs, files in os.walk(INPUT_FOLDER):
    for file in files:
        if file.lower().endswith(SUPPORTED_EXTENSIONS):
            input_path = os.path.join(root, file)

            # Preserve folder structure
            relative_path = os.path.relpath(root, INPUT_FOLDER)
            output_dir = os.path.join(OUTPUT_FOLDER, relative_path)
            os.makedirs(output_dir, exist_ok=True)

            output_file = os.path.splitext(file)[0] + ".png"
            output_path = os.path.join(output_dir, output_file)

            try:
                with open(input_path, "rb") as inp:
                    input_data = inp.read()

                output_data = remove(input_data)

                with open(output_path, "wb") as out:
                    out.write(output_data)

                print(f"✓ Processed: {input_path}")

            except Exception as e:
                print(f"✗ Error processing {input_path}: {e}")

print("\nAll images processed successfully!")