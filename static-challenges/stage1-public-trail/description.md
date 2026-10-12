# STAGE-01 — The Public Trail

**Category:** OSINT / Reconnaissance · **Difficulty:** Easy

An ActionLK employee's profile photo was flagged during initial breach
triage. Something they posted, without realising it, is the
investigation's first lead. Download the attached image and take a closer
look at what it's carrying besides pixels.

**Attach in CTFd:** `profile.jpg`
**Flag format:** `ACTIONLK{...}`

**Hints (suggested point deductions):**
- (-5) Images carry more than pixels.
- (-10) Try a metadata tool, e.g. `exiftool profile.jpg`.

**Implementation note (for the viva, not for players):** the note is stored
in the JPEG's COM marker segment, which `exiftool` surfaces under the
`Comment` tag — this is the field most CTFs mean by "EXIF Comment" even
though it's technically a JPEG comment segment rather than an Exif IFD tag.
If you'd rather it be a strictly-EXIF `UserComment` tag (0x9286) instead,
swap the COM-segment write in `generate_assets.py` for a Pillow
`Image.Exif()` write — worth mentioning if a marker asks about the
distinction.
