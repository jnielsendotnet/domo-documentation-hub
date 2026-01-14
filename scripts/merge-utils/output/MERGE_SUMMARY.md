# Documentation Merge Summary

Date: 2026-01-14
Branch: feature/merge-july-2025-updates

## Files Added/Updated

### CRITICAL Priority (Completed)

1. **NEW: portal/advanced-forms-overview.mdx**
   - Source: docs/Forms/Advanced-Forms/overview.md
   - Status: ✓ Created

2. **UPDATED: portal/3ad3f9b434b10-getting-started-with-the-pro-code-editor.mdx**
   - Fixed broken image paths pointing to stoplight.io
   - Status: ✓ Updated

3. **CHECKED: portal/d01f63a6ba662-domo-developer-portal.mdx**
   - Already up-to-date with community resources
   - Status: ✓ No changes needed

4. **CHECKED: portal/6hlzv1hinkq19-setup-and-installation.mdx**
   - Already updated with npm-only distribution
   - Status: ✓ No changes needed

### HIGH Priority (Completed)

5. **NEW: portal/advanced-forms-creating.mdx**
   - Source: docs/Forms/Advanced-Forms/creating-advanced-forms.md
   - Status: ✓ Created

6. **NEW: portal/advanced-forms-datasets.mdx**
   - Source: docs/Forms/Advanced-Forms/advanced-form-datasets.md
   - Status: ✓ Created

7. **NEW: portal/advanced-forms-editor-layout.mdx**
   - Source: docs/Forms/Advanced-Forms/advanced-form-editor-layout.md
   - Status: ✓ Created

8. **NEW: portal/advanced-forms-domo-data-features.mdx**
   - Source: docs/Forms/Advanced-Forms/domo-data-features.md
   - Status: ✓ Created

9. **NEW: portal/domo-publish-cicd.mdx**
   - Source: docs/Apps/App-Framework/Tools/domo-publish-CICD.md
   - Status: ✓ Created

10. **NEW: portal/local-development-domo-cli.mdx**
    - Source: docs/Apps/App-Framework/Guides/Local-Development-with-Domo-CLI.md
    - Status: ✓ Created

### MEDIUM Priority (Completed)

11. **NEW: portal/da-cli.mdx**
    - Source: docs/Apps/App-Framework/Tools/da-cli.md
    - Status: ✓ Created

## Images Copied

The following images were copied from ../domo-developer-portal/assets/images/ to images/dev/:

- advanced-form-build-variables.png
- advanced-form-dropdown.png
- advanced-form-overview.png
- advanced-form-set-value.png
- asset-library-tutorial.png
- pro.png
- proxyId_location.png
- thumbnail-procode.png

## Navigation Updates Needed

The following files need to be added to `docs.json` navigation:

### Advanced Forms Section (NEW)
Create a new "Advanced Forms" group under the Forms section:
```json
{
  "group": "Advanced Forms",
  "pages": [
    "portal/advanced-forms-overview",
    "portal/advanced-forms-creating",
    "portal/advanced-forms-datasets",
    "portal/advanced-forms-editor-layout",
    "portal/advanced-forms-domo-data-features"
  ]
}
```

### App Framework Tools Section
Add to the existing Tools group:
- `portal/da-cli` (Domo App Generator CLI)
- `portal/domo-publish-cicd` (CI/CD with GitHub Actions)

### App Framework Guides Section
Add to the existing Guides group:
- `portal/local-development-domo-cli` (Local Development with Domo CLI)

## Pending Updates (Not Completed)

The following files from the merge report were not updated in this merge:

### MEDIUM Priority - Manual Review Needed
- **domo.js.md** (MAJOR_UPDATE, 8 commits) - Requires careful manual review
- **AI-Service-Layer-API.md** (MINOR_UPDATE, 2 commits)
- **AI-Services.md** (MINOR_UPDATE, 2 commits)
- **domo-CLI.md** (MINOR_UPDATE, 2 commits)
- **pdf-export.md** (MINOR_UPDATE, 2 commits)

### LOW Priority (149 files)
- Mostly CONTENT_DIFF files without recent git history
- Likely due to migration formatting changes
- Can be reviewed on a case-by-case basis if specific issues arise

## Next Steps

1. **Update docs.json**: Add navigation entries for the 11 new files
2. **Test build**: Run `mintlify dev` to ensure all pages render correctly
3. **Review remaining updates**: Handle MEDIUM priority MINOR_UPDATES and MAJOR_UPDATE for domo.js
4. **Commit and push**: Create a commit with the merged content
5. **Optional**: Review and merge LOW priority content differences as needed

## Tools Created

The following analysis scripts were created in `scripts/merge-utils/`:

1. **build_inventory.py** - Scans both repositories and extracts metadata
2. **create_mapping.py** - Maps files using stoplight-id and fuzzy matching
3. **detect_changes.py** - Analyzes content differences and git history
4. **generate_merge_list.py** - Creates prioritized merge recommendations
5. **transform_markdown.py** - Transforms Stoplight markdown to Mintlify format

All analysis outputs are in `scripts/merge-utils/output/`:
- merge_report.md
- merge_recommendations.json
- file_mapping.json
- changes_detected.json
- source_inventory.json
- migrated_inventory.json
