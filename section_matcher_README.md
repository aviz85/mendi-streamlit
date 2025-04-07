# Section Matcher for Hebrew Nikud

This tool analyzes source (with nikud) and target (without nikud) DOCX files, matches corresponding sections, and prepares them for further processing with the Gemini API.

## Purpose

The section matcher serves as a preprocessing stage for the automatic nikud (vowelization) system. It:

1. Identifies sections based on Hebrew letter headers
2. Finds matching sections between source and target documents
3. Prepares section pairs for processing by the nikud service
4. Saves intermediate results for debugging and testing

## Usage

### Running the Section Matcher

```bash
python test_sections_matcher.py
```

This will:
- Process source.docx and target.docx in the root directory
- Create a temporary directory with results
- Generate section mapping and matching information

### Saving Results

To save results to a permanent location:

```bash
python copy_results.py <temp_directory> [output_name]
```

Example:
```bash
python copy_results.py /var/folders/...section_matcher_test_... source_target_match
```

## Output Structure

The tool creates the following structure:

```
/section_matcher_results/source_target_match_v1/
├── match_1/
│   ├── match_info.txt         # Basic match information
│   ├── prepared_content.json  # Data prepared for nikud processing
│   ├── source_content.txt     # Raw text of source section
│   ├── source.docx            # DOCX version of source section
│   ├── target_content.txt     # Raw text of target section
│   └── target.docx            # DOCX version of target section
├── match_mapping.json         # Summary of all matches
├── source_sections.txt        # Overview of source sections
├── summary_report.txt         # Human-readable summary
└── target_sections.txt        # Overview of target sections
```

## Nikud Processing

After section matching, each pair can be processed by the nikud service, which:

1. Identifies bold text in the target document
2. Finds corresponding words in the source document
3. Adds nikud from source words to the bold words in target
4. Preserves the original content except for adding nikud to bold words

## Model Information

The tool uses the `gemini-2.5-pro-preview-03-25` model for text processing. This model is now permanently configured in the `services/gemini_service.py` file and does not require any additional patching or modification.

## Notes

- Hebrew section headers are identified as 1-3 Hebrew letters on a line by themselves
- Section matching uses both full content similarity and first sentence similarity
- Bold tags are identified using the HTML-like pattern `<b>...</b>`
- The tool is designed to handle large documents with many sections 