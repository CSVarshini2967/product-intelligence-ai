from app.modules.deduplication.service import deduplicate
from app.modules.extraction.service import extract_attributes

# Test extraction
rows = [{'part_desc': '5" P120 Grinding Disc 10pc', 'mfg_part_num': 'ABC-123', 'brand_name': '3M', 'part_desc_normalized': '5" P120 Grinding Disc 10pc'}]
result = extract_attributes(rows)
print('Extraction OK:', result[0].get('extracted_attributes', [])[:2])

# Test deduplication
rows2 = [
    {'mfg_part_num': 'ABC-123', 'part_desc': '5in disc'},
    {'mfg_part_num': 'ABC-123', 'part_desc': '5in disc'},
]
result2 = deduplicate(rows2)
print('Deduplication OK:', result2[1]['duplicate_info'])
print('All tests passed.')
