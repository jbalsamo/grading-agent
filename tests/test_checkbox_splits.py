"""
Unit tests for the fix_checkbox_splits function.

This function post-processes MarkItDown output to rejoin checkbox lines
that were incorrectly split by commas during conversion.
"""
import pytest
import sys
import os

# Add parent directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app import fix_checkbox_splits


@pytest.mark.unit
class TestFixCheckboxSplits:
    """Test the fix_checkbox_splits function."""
    
    def test_simple_split(self):
        """Test rejoining a simple split checkbox line."""
        input_md = "- [ ] Diabetes,\n- [ ] Type 2"
        expected = "- [ ] Diabetes, Type 2"
        assert fix_checkbox_splits(input_md) == expected
    
    def test_multi_line_split(self):
        """Test rejoining multiple consecutive split lines."""
        input_md = "- [ ] Hypertension,\n- [ ] Stage 1,\n- [ ] controlled"
        expected = "- [ ] Hypertension, Stage 1, controlled"
        assert fix_checkbox_splits(input_md) == expected
    
    def test_no_split_needed(self):
        """Test that normal checkbox lines are unchanged."""
        input_md = "- [ ] Normal item without comma"
        expected = "- [ ] Normal item without comma"
        assert fix_checkbox_splits(input_md) == expected
    
    def test_multiple_checkboxes_no_split(self):
        """Test multiple separate checkboxes remain separate."""
        input_md = "- [ ] Item one\n- [ ] Item two\n- [ ] Item three"
        expected = "- [ ] Item one\n- [ ] Item two\n- [ ] Item three"
        assert fix_checkbox_splits(input_md) == expected
    
    def test_mixed_content(self):
        """Test mixed content with some splits and some normal lines."""
        input_md = """# Conditions
- [ ] Diabetes,
- [ ] Type 2
- [ ] Hypertension
- [ ] Heart disease,
- [ ] coronary"""
        expected = """# Conditions
- [ ] Diabetes, Type 2
- [ ] Hypertension
- [ ] Heart disease, coronary"""
        assert fix_checkbox_splits(input_md) == expected
    
    def test_checked_boxes_split(self):
        """Test that checked boxes with [x] that end with comma are rejoined."""
        input_md = "- [x] Radiology,\n- [x] MRI and x-ray"
        expected = "- [x] Radiology, MRI and x-ray"
        assert fix_checkbox_splits(input_md) == expected
    
    def test_checked_boxes_no_split(self):
        """Test that checked boxes without trailing comma remain separate."""
        input_md = "- [x] Completed item\n- [ ] Pending item"
        expected = "- [x] Completed item\n- [ ] Pending item"
        assert fix_checkbox_splits(input_md) == expected
    
    def test_checked_multi_line_split(self):
        """Test rejoining multiple consecutive checked split lines."""
        input_md = "- [x] Radiology,\n- [x] MRI,\n- [x] x-ray and CT"
        expected = "- [x] Radiology, MRI, x-ray and CT"
        assert fix_checkbox_splits(input_md) == expected
    
    def test_plain_bullet_split(self):
        """Test rejoining plain bullet lines split by comma."""
        input_md = "- Radiology,\n- MRI and x-ray"
        expected = "- Radiology, MRI and x-ray"
        assert fix_checkbox_splits(input_md) == expected
    
    def test_plain_bullet_multi_line_split(self):
        """Test rejoining multiple consecutive plain bullet split lines."""
        input_md = "- Radiology,\n- MRI,\n- x-ray and CT"
        expected = "- Radiology, MRI, x-ray and CT"
        assert fix_checkbox_splits(input_md) == expected
    
    def test_empty_string(self):
        """Test handling of empty string input."""
        assert fix_checkbox_splits("") == ""
    
    def test_no_checkboxes(self):
        """Test content with no checkboxes is unchanged."""
        input_md = "# Header\n\nSome regular text\n\n- Regular list item"
        expected = "# Header\n\nSome regular text\n\n- Regular list item"
        assert fix_checkbox_splits(input_md) == expected
    
    def test_long_medical_diagnosis(self):
        """Test real-world medical diagnosis split across lines."""
        input_md = """- [ ] Chronic obstructive pulmonary disease,
- [ ] with acute exacerbation,
- [ ] severe"""
        expected = "- [ ] Chronic obstructive pulmonary disease, with acute exacerbation, severe"
        assert fix_checkbox_splits(input_md) == expected
    
    def test_preserves_other_markdown(self):
        """Test that other markdown elements are preserved."""
        input_md = """# Patient Info

**Name:** John Doe

## Diagnoses
- [ ] Diabetes,
- [ ] Type 2

## Notes
Regular paragraph text here."""
        
        result = fix_checkbox_splits(input_md)
        
        # Check checkbox was fixed
        assert "- [ ] Diabetes, Type 2" in result
        # Check other elements preserved
        assert "# Patient Info" in result
        assert "**Name:** John Doe" in result
        assert "## Diagnoses" in result
        assert "## Notes" in result
        assert "Regular paragraph text here." in result
