# Formula vs Pivot Mismatch - Root Cause Analysis

## Problem Reported
"the output derived from formula and pivot derived is not matching, tried via different approaches but not getting same"

## Root Cause: Duplicate Rows
The dataset contains 2 duplicate orders that appear twice:

### Duplicate #1: Order O080
- **Location**: Rows 82 & 94 in orders sheet
- **Details**: East region, Office Chair, 2 units, ₹7,500 each, 5% discount, PAID
- **Net Revenue per occurrence**: ₹14,250
- **Impact**: +₹14,250 when counting duplicates

### Duplicate #2: Order O100
- **Location**: Rows 47 & 103 in orders sheet  
- **Details**: West region, Printer, 2 units, ₹12,000 each, 6% discount, PAID
- **Net Revenue per occurrence**: ₹22,560
- **Impact**: +₹22,560 when counting duplicates

## The Discrepancy Explained

### Calculation Method 1: Excel Formulas (All Rows)
Excel formulas process every row individually, including duplicates:
```
Regional Net Revenue:
├── West:  ₹1,858,965.00 ← includes duplicate O100
├── North: ₹1,329,260.00
├── South: ₹1,312,220.00
└── East:  ₹1,104,235.00 ← includes duplicate O080
```

### Calculation Method 2: Pivot Table (Unique Rows)
Pivot tables typically identify and handle duplicates:
```
Regional Net Revenue:
├── West:  ₹1,836,405.00 ← correct (O100 counted once)
├── North: ₹1,329,260.00
├── South: ₹1,312,220.00
└── East:  ₹1,089,985.00 ← correct (O080 counted once)
```

### Total Difference
```
West:  ₹1,858,965 - ₹1,836,405 = ₹22,560 (1 duplicate O100)
East:  ₹1,104,235 - ₹1,089,985 = ₹14,250 (1 duplicate O080)
                                  ─────────
TOTAL DISCREPANCY:                 ₹36,810
```

## Solution Implemented

### 1. Analysis Notes Sheet (First Sheet)
- Comprehensive explanation of duplicate row issue
- Side-by-side comparison of both calculation methods
- Clear recommendation to remove duplicates for accurate analysis

### 2. Visual Marking in Orders Sheet
- Column Z: "DUPLICATE" text label for affected rows
- Yellow highlighting on duplicate rows (47, 82, 94, 103)
- Easy identification at a glance

### 3. Updated Question Answers
- Task 1: Detailed duplicate row analysis with exact row numbers
- Task 3: Both calculation results provided with clear explanation
- All answers acknowledge the duplicate row impact

### 4. Documentation
- README.md updated with duplicate row warning
- Clear explanation of why different methods yield different results

## How to Fix for Accurate Analysis

### Option A: Remove Duplicates in Excel
1. Select all data in orders sheet
2. Go to Data → Remove Duplicates
3. Select all columns
4. This will remove rows 94 and 103 (keeping 82 and 47)
5. Formulas will automatically recalculate

### Option B: Use Unique Records in Pivot Table
1. When creating pivot table, ensure "Count" is on unique Order IDs
2. Or manually exclude duplicate rows before pivot analysis

### Option C: Python Data Cleaning
```python
import pandas as pd
df = pd.read_excel('file.xlsx')
df_clean = df.drop_duplicates()  # Removes 2 rows
# Now calculations will match pivot tables
```

## Verification
After implementing this solution, users can:
1. Open 'Analysis Notes' sheet to understand the issue
2. See yellow-highlighted duplicates in orders sheet
3. Check column Z for "DUPLICATE" markers
4. Read detailed explanations in Questions sheet
5. Choose their preferred handling method

## Key Takeaway
**The formulas are working correctly** - they process all rows as intended. 
The "mismatch" occurs because:
- Excel formulas include all rows (data quality issue exposed)
- Pivot tables can identify/exclude duplicates (data cleaning applied)

Both are correct for their respective approaches. The root issue is the 
presence of duplicate data that should have been cleaned during data entry 
or preprocessing.
