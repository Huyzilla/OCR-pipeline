#!/usr/bin/env python3
"""
Convert existing OCR outputs from old structure (outputs_marker_single) 
to new structure (outputs/) without re-running OCR.

This allows us to demonstrate the new structure and prepare for chunking
while the full batch OCR runs separately.
"""
import argparse
import shutil
import re
from pathlib import Path


def extract_pdf_folder_name(folder_path: Path) -> str:
    """Extract clean folder name from old structure folder name."""
    base_name = folder_path.name
    # Remove _cropped suffix if present
    if base_name.endswith("_cropped"):
        base_name = base_name[:-len("_cropped")]
    return base_name


def format_pdf_header(folder_name: str) -> str:
    """Convert folder name to markdown header format."""
    match = re.match(r"^([A-Za-z]+)(\d+)$", folder_name)
    if match:
        prefix, number = match.groups()
        return f"# {prefix}_{number}"
    return f"# {folder_name}"


def replace_image_placeholders(md_text: str, folder_path: Path) -> str:
    """Replace image references with correct format."""
    # Find the folder - check if it exists and has images
    image_files = list(folder_path.glob("*.jpeg")) + list(folder_path.glob("*.jpg")) + list(folder_path.glob("*.png"))
    image_count = len(image_files)
    
    if image_count == 0:
        return md_text
    
    # Replace image reference patterns in markdown
    image_pattern = r"!\[.*?\]\(.*?\)"
    images = re.findall(image_pattern, md_text)
    
    for i, _ in enumerate(images[:image_count], 1):
        if i <= len(images):
            md_text = md_text.replace(images[i-1], f"![](images/image{i}.jpg)", 1)
    
    return md_text


def convert_folder_structure(old_folder: Path, new_output_root: Path) -> bool:
    """
    Convert single folder from old structure to new structure.
    
    Old structure: output_marker_single/Public283_cropped/Public283_cropped.md
    New structure: outputs/Public283/main.md
    """
    try:
        # Get clean folder name
        clean_name = extract_pdf_folder_name(old_folder)
        
        # Create new output folder structure
        new_folder = new_output_root / clean_name
        new_folder.mkdir(parents=True, exist_ok=True)
        
        # Create images subdirectory
        images_dir = new_folder / "images"
        images_dir.mkdir(exist_ok=True)
        
        # Find markdown file
        md_files = list(old_folder.glob("*.md"))
        if not md_files:
            print(f"  ⚠️  No markdown file found in {old_folder.name}")
            return False
        
        md_file = md_files[0]
        
        # Read and process markdown
        with open(md_file, "r", encoding="utf-8") as f:
            md_text = f.read()
        
        # Replace image references
        md_text = replace_image_placeholders(md_text, old_folder)
        
        # Add header
        header = format_pdf_header(clean_name)
        final_md = f"{header}\n\n{md_text}"
        
        # Save to main.md
        output_md = new_folder / "main.md"
        with open(output_md, "w", encoding="utf-8") as f:
            f.write(final_md)
        
        # Copy images to images/ folder
        for image_file in old_folder.glob("*.*"):
            if image_file.suffix.lower() in [".jpeg", ".jpg", ".png", ".gif"]:
                dest_image = images_dir / image_file.name
                shutil.copy2(image_file, dest_image)
        
        return True
    except Exception as e:
        print(f"  ❌ Error: {e}")
        return False


def convert_batch(old_root: Path, new_root: Path) -> None:
    """Convert all folders from old to new structure."""
    old_root = Path(old_root)
    new_root = Path(new_root)
    
    if not old_root.exists():
        print(f"❌ Source directory not found: {old_root}")
        return
    
    new_root.mkdir(parents=True, exist_ok=True)
    
    # Get all old structure folders
    old_folders = sorted([f for f in old_root.iterdir() if f.is_dir()])
    if not old_folders:
        print(f"❌ No folders found in {old_root}")
        return
    
    print(f"📁 Source: {old_root}")
    print(f"📁 Target: {new_root}")
    print(f"📄 Converting {len(old_folders)} folders...")
    print()
    
    success = 0
    failed = 0
    
    for i, old_folder in enumerate(old_folders, 1):
        print(f"[{i:03d}/{len(old_folders):03d}] {old_folder.name}", end=" -> ")
        if convert_folder_structure(old_folder, new_root):
            print(f"✅")
            success += 1
        else:
            print(f"❌")
            failed += 1
    
    print("\n" + "="*60)
    print(f"📊 CONVERSION SUMMARY")
    print("="*60)
    print(f"✅ Success: {success}")
    print(f"❌ Failed:  {failed}")
    print(f"📈 Total:   {success + failed}")


def main():
    parser = argparse.ArgumentParser(
        description="Convert OCR outputs from old to new folder structure"
    )
    parser.add_argument(
        "--old_root",
        default="/media/data3/users/huytq/huy/outputs_marker_single",
        help="Source folder with old structure",
    )
    parser.add_argument(
        "--new_root",
        default="/media/data3/users/huytq/huy/outputs_converted",
        help="Target folder for new structure",
    )
    args = parser.parse_args()
    
    convert_batch(args.old_root, args.new_root)


if __name__ == "__main__":
    main()
