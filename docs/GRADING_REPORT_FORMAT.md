# Grading Report Format

## Overview
The grading system now produces professional, structured reports with clear visual hierarchy and total grade calculations.

## Report Structure

### 1. 📊 Grade Summary (Top Priority)
The most important section showing overall performance:

```markdown
| Metric | Value |
|:-------|------:|
| Total Score | 85 / 100 points |
| Percentage | 85.0% |
| Grade Status | Pass |
```

**Key Features:**
- **Total Score** calculated automatically by summing all section scores
- **Percentage** calculated as (Total Score / Max Points) × 100
- **Status** indicates pass/fail or grade level

### 2. 📋 Section Scores (Detailed Breakdown)
Shows performance across all grading sections:

```markdown
| Section | AI Score | Human Score | Max Points | Δ | Status |
|:--------|-------:|-----------:|---------:|:--:|:-----:|
| History of Present Illness | 25 | 24 | 30 | +1 | ✅ |
| Review of Systems | 18 | 20 | 25 | -2 | ⚠️ |
| Physical Exam | 22 | 22 | 25 | 0 | ✅ |
| Assessment & Plan | 20 | 18 | 20 | +2 | ⚠️ |
| **TOTALS** | **85** | **84** | **100** | **-** | **-** |
```

**Key Features:**
- Individual section scores with AI vs Human comparison
- Delta (Δ) shows difference between AI and Human scores
- Status emoji: ✅ perfect (±0-1), ⚠️ close (±2-5), ❌ large gap (±6+)
- **TOTALS row** at bottom for easy reference

### 3. ✓ Rubric Items (Itemized Checklist)
Shows which specific rubric items were checked:

```markdown
| Item | Checked | Points |
|:-----|:-------:|-------:|
| Chief complaint clearly stated | ✓ | 5 |
| Duration of symptoms documented | ✓ | 5 |
| Associated symptoms listed | ✗ | 0 |
| Past medical history complete | ✓ | 5 |
```

**Key Features:**
- ✓ = Item was checked/present
- ✗ = Item was not checked/absent
- Points awarded per item

### 4. ℹ️ Additional Notes
Any special notes, ignored items, or missing requirements:

```markdown
- Ignored items: Comments section (not scored)
- Missing: Student signature
- Special notes: Late submission penalty applied
```

## Multiple Students

When grading multiple students, each student receives a **complete separate report** with:
- Clear student identification header
- Individual Grade Summary
- Individual Section Scores
- Individual Rubric Items
- Separated by horizontal rules for easy distinction

## Visual Hierarchy

The formatting uses emoji and markdown to create clear visual hierarchy:

- **📊** Grade Summary (highest priority - overall performance)
- **📋** Section Scores (detailed breakdown)
- **✓** Rubric Items (itemized checklist)
- **ℹ️** Additional Notes (supplementary information)
- **Bold** for all totals and important values
- Right-aligned numbers for easy comparison
- Horizontal rules (---) between major sections

## Example Complete Report

```markdown
# STUDENT GRADING REPORT
**Student:** John Doe  
**Date:** 2024-11-17

---

## 📊 GRADE SUMMARY

| Metric | Value |
|:-------|------:|
| Total Score | 85 / 100 points |
| Percentage | 85.0% |
| Grade Status | Pass (B) |

---

## 📋 SECTION SCORES

| Section | AI Score | Human Score | Max Points | Δ | Status |
|:--------|-------:|-----------:|---------:|:--:|:-----:|
| History of Present Illness | 25 | 24 | 30 | +1 | ✅ |
| Review of Systems | 18 | 20 | 25 | -2 | ⚠️ |
| Physical Exam | 22 | 22 | 25 | 0 | ✅ |
| Assessment & Plan | 20 | 18 | 20 | +2 | ⚠️ |
| **TOTALS** | **85** | **84** | **100** | **-** | **-** |

---

## ✓ RUBRIC ITEMS

| Item | Checked | Points |
|:-----|:-------:|-------:|
| Chief complaint clearly stated | ✓ | 5 |
| Duration of symptoms documented | ✓ | 5 |
| Associated symptoms listed | ✗ | 0 |
| Past medical history complete | ✓ | 5 |
| ... | ... | ... |

---

## ℹ️ ADDITIONAL NOTES

- All required sections completed
- Minor discrepancy in ROS scoring
- Overall strong performance
```

## Benefits

1. **Clear Total Grade** - Immediately shows overall performance
2. **Structured Layout** - Easy to scan and understand
3. **Visual Hierarchy** - Emoji and formatting guide the eye
4. **Detailed Breakdown** - Section scores provide context
5. **Itemized Feedback** - Rubric items show exactly what was assessed
6. **Professional Presentation** - Ready for export or presentation
7. **Multi-Student Support** - Clean separation for batch grading

## Usage

The formatting agent automatically applies this structure when processing grading results. No manual formatting needed - just submit your grading data and receive a professionally formatted report.
