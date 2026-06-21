

import os
import shutil
import sys

# Map of category -> set of file extensions (lowercase, with the dot)
CATEGORY_MAP = {
    "Images": {".jpg", ".jpeg", ".png", ".gif", ".bmp", ".svg", ".webp", ".heic", ".tiff"},
    "Documents": {".pdf", ".doc", ".docx", ".txt", ".rtf", ".odt", ".md", ".csv", ".xlsx", ".xls", ".pptx", ".ppt"},
    "Audio": {".mp3", ".wav", ".flac", ".aac", ".ogg", ".m4a"},
    "Video": {".mp4", ".mov", ".avi", ".mkv", ".wmv", ".flv", ".webm"},
    "Archives": {".zip", ".rar", ".7z", ".tar", ".gz", ".bz2"},
    "Code": {".py", ".js", ".html", ".css", ".java", ".c", ".cpp", ".json", ".sh", ".ipynb"},
    "Executables": {".exe", ".msi", ".apk", ".dmg", ".app"},
}

OTHERS_FOLDER = "Others"


def get_category(filename):
    """Return the category folder name for a given filename based on its extension."""
    _, ext = os.path.splitext(filename)
    ext = ext.lower()
    for category, extensions in CATEGORY_MAP.items():
        if ext in extensions:
            return category
    return OTHERS_FOLDER


def unique_destination_path(dest_folder, filename):
    """
    Build a destination path for `filename` inside `dest_folder`.
    If a file with the same name already exists, append ' (1)', ' (2)', etc.
    so existing files are never overwritten.
    """
    base, ext = os.path.splitext(filename)
    candidate = os.path.join(dest_folder, filename)
    counter = 1
    while os.path.exists(candidate):
        candidate = os.path.join(dest_folder, f"{base} ({counter}){ext}")
        counter += 1
    return candidate


def organize_folder(target_folder, dry_run=False):
    """
    Organize all files directly inside `target_folder` into category subfolders.
    Subfolders are not recursed into, and the script's own category folders
    are skipped if re-run on an already-organized directory.
    Returns a summary dict of {category: count}.
    """
    if not os.path.isdir(target_folder):
        raise NotADirectoryError(f"'{target_folder}' is not a valid directory.")

    summary = {}
    known_category_folders = set(CATEGORY_MAP.keys()) | {OTHERS_FOLDER}

    entries = sorted(os.listdir(target_folder))

    for entry in entries:
        full_path = os.path.join(target_folder, entry)

        # Skip directories (including our own category folders) and hidden files
        if os.path.isdir(full_path):
            continue
        if entry.startswith("."):
            continue
        # Skip the script itself if it happens to live in the target folder
        if entry == os.path.basename(__file__):
            continue

        category = get_category(entry)
        dest_folder = os.path.join(target_folder, category)

        if not dry_run:
            os.makedirs(dest_folder, exist_ok=True)

        dest_path = unique_destination_path(dest_folder, entry)

        if dry_run:
            print(f"[Dry Run] Would move: '{entry}'  ->  '{category}/{os.path.basename(dest_path)}'")
        else:
            try:
                shutil.move(full_path, dest_path)
                print(f"Moved: '{entry}'  ->  '{category}/{os.path.basename(dest_path)}'")
            except (shutil.Error, OSError) as e:
                print(f"[Error] Could not move '{entry}': {e}")
                continue

        summary[category] = summary.get(category, 0) + 1

    return summary


def print_summary(summary):
    print("\n--- Organization Summary ---")
    if not summary:
        print("No files were moved (folder may already be organized or empty).")
        return
    total = 0
    for category, count in sorted(summary.items()):
        print(f"{category:<15} {count} file(s)")
        total += count
    print("-" * 30)
    print(f"Total files organized: {total}")


def prompt_for_folder():
    path = input("Enter the path of the folder to organize: ").strip()
    while not os.path.isdir(path):
        print(f"'{path}' is not a valid directory. Please try again.")
        path = input("Enter the path of the folder to organize: ").strip()
    return path


def main():
    args = sys.argv[1:]
    dry_run = "--dry-run" in args
    args = [a for a in args if a != "--dry-run"]

    if args:
        target_folder = args[0]
        if not os.path.isdir(target_folder):
            print(f"[Error] '{target_folder}' is not a valid directory.")
            sys.exit(1)
    else:
        print("=" * 50)
        print("      AUTOMATE FOLDER ORGANIZER")
        print("=" * 50)
        target_folder = prompt_for_folder()
        choice = input("Run as a dry run first (no files will be moved)? [y/N]: ").strip().lower()
        dry_run = choice == "y"

    print(f"\nOrganizing folder: {target_folder}")
    if dry_run:
        print("(Dry run mode - no files will actually be moved)\n")

    summary = organize_folder(target_folder, dry_run=dry_run)
    print_summary(summary)

    if dry_run:
        confirm = input("\nProceed with actually moving these files now? [y/N]: ").strip().lower()
        if confirm == "y":
            print()
            summary = organize_folder(target_folder, dry_run=False)
            print_summary(summary)


if __name__ == "__main__":
    main()
