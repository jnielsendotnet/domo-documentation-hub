# Image Path Validation and Fix Summary

## Overview

Fixed 276 broken image references across the documentation (68% improvement).

## Results

| Metric | Before | After | Change |
|--------|--------|-------|--------|
| **Total Images** | 810 | 810 | - |
| **Valid Images** | 189 | 465 | +276 |
| **Broken Images** | 408 | 132 | -276 ✓ |
| **External URLs** | 213 | 213 | - |

## What Was Fixed

### Phase 1: Stoplight API Path Migration (408 → 211)
**Fixed:** 197 images  
**Script:** `scripts/fix_image_paths.py`

Updated old Stoplight API paths to new structure:
- **OLD:** `/images/dev/stoplight.io/api/v1/projects/{id}/branches/{id}/images/assets/images/FILE`
- **NEW:** `/images/dev/stoplight.io/images/FILE`

**Files Modified:** 28 files with 202 path changes

### Phase 2: Relative Path Fixes (211 → 137)
**Fixed:** 74 images  
**Script:** `scripts/fix_relative_image_paths.py`

Fixed incorrect relative and absolute paths:
- `../../assets/images/file.png` → `/images/dev/stoplight.io/images/file.png`
- `../../../../assets/images/file.png` → `/images/dev/stoplight.io/images/file.png`
- `/images/dev/file.png` → `/images/dev/stoplight.io/images/file.png`
- `/assets/images/file.png` → `/images/dev/stoplight.io/images/file.png`

**Files Modified:** 23 files with 101 path changes

### Phase 3: Copy Missing Images (137 → 132)
**Fixed:** 5 images (43 copied, 38 weren't referenced yet)  
**Script:** `scripts/copy_missing_images.py`

Copied 43 missing images from `../domo-developer-portal/assets/images/`:
- App Catalyst images (AC_Picture1-12.png)
- SIEM integration images (siem1-11.png)
- Advanced form images
- Auth page images
- Manifest/mapping tutorial images
- And more...

**Images Copied:** 43 files to `images/dev/stoplight.io/images/`

## Remaining Broken Images (132)

### Categories of Still-Broken Images

1. **URL-Encoded Filenames** (~30 images)
   - Example: `Screenshot%202024-03-22%20at%2010.05.58%20AM.png`
   - Issue: Filename has `%20` instead of spaces or hyphens
   - Files exist but with different names

2. **Placeholder/Example Images** (~8 images)
   - `example.jpg` (2 refs)
   - `infographic.png` (4 refs)
   - `chapter_divider.png` (6 refs)
   - Action: Replace with actual images or remove references

3. **Deleted Screenshots** (~10 images)
   - `Screenshot-2024-01-02-at-8.50.40-AM.png`
   - Action: May need to recreate or remove

4. **Malformed Paths** (~15 images)
   - `image-(1` (missing extension/closing paren)
   - `33137` (app store image ID without context)
   - Action: Fix the MDX references

5. **API Endpoints** (~6 images - ACCEPTABLE)
   - `/domo/avatars/v2/USER/...` (dynamic avatar URLs)
   - Action: None needed - these are dynamic endpoints

6. **Truly Missing** (~63 images)
   - Images that don't exist in either repo
   - Action: Need to recreate, find in backups, or remove references

## Scripts Created

1. **`scripts/validate_images.py`**
   - Validates all image paths in MDX files
   - Generates comprehensive reports
   - Output: `image_validation_report.json`, `broken_images.txt`, `image_summary.txt`

2. **`scripts/fix_image_paths.py`**
   - Fixes old Stoplight API paths
   - Automatically updates to new structure

3. **`scripts/fix_relative_image_paths.py`**
   - Fixes relative and incorrect absolute paths
   - Redirects to correct stoplight directory

4. **`scripts/copy_missing_images.py`**
   - Finds missing images in domo-developer-portal
   - Copies them to the correct location
   - Reports truly missing images

## Next Steps

### Immediate Actions Needed

1. **Fix URL-Encoded Filenames**
   - Rename files or update references to match
   - Create a script to handle URL encoding

2. **Handle Placeholder Images**
   - Replace `example.jpg`, `infographic.png`, `chapter_divider.png`
   - Or remove these references if not needed

3. **Fix Malformed References**
   - Review MDX files with broken image syntax
   - Correct the markdown/HTML image tags

### Optional Actions

4. **Review Deleted Screenshots**
   - Determine if these are still needed
   - Recreate or remove references

5. **Document Image Best Practices**
   - Use absolute paths: `/images/dev/stoplight.io/images/file.png`
   - Avoid spaces in filenames
   - Use descriptive names

## Files Modified

See git status for complete list of modified files. Key changes:
- ~51 portal MDX files with image path fixes
- 43 new image files copied to `images/dev/stoplight.io/images/`
- 4 new validation/fix scripts in `scripts/`

## Validation Reports

All validation data available in:
- `scripts/output/image_validation_report.json`
- `scripts/output/broken_images.txt`
- `scripts/output/image_summary.txt`
- `scripts/output/truly_missing_images.json`
