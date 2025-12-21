# Data Analyst Assignment - Excel Data Analysis

## Overview
This project contains a Python script that performs comprehensive data analysis on an Excel file with order data. The script addresses all questions from the "Questions" sheet and generates a complete analysis report.

## Files
- `Data Analyst Assignment Data.xlsx` - Original Excel file with order data and questions
- `Data Analyst Assignment Data_COMPLETED.xlsx` - Output file with all calculations and answers
- `data_analysis_script.py` - Python script that performs all analyses

## Tasks Completed

### Task 1: Data Anomalies Identified
1. **Duplicate Rows**: 2 duplicate rows found affecting count and revenue accuracy
2. **Missing Salesperson Names**: 1 order with missing salesperson affecting performance tracking
3. **Data Type Issues**: Unit Price stored as object (string) and Order Date as object instead of proper numeric/datetime types

### Task 2: Revenue Calculations
- **Revenue Formula**: Quantity × Unit Price (for all orders)
- **Net Revenue Formula**: Quantity × Unit Price × (1 - Discount%) (for Paid orders only)
- All 126 orders have Revenue calculated
- 108 Paid orders have Net Revenue calculated

### Task 3: Regional Analysis
Created pivot table showing Net Revenue by Region:
- **West**: ₹1,858,965.00 (Highest)
- **North**: ₹1,329,260.00
- **South**: ₹1,312,220.00
- **East**: ₹1,104,235.00

### Task 4: Total Revenue
**Total Revenue** = ₹7,429,500.00

### Task 5: Payment Status Analysis
**Unpaid/Pending Orders**: 14.29% (18 out of 126 orders)

### Task 6: Time-based Product Analysis
- **Month Column**: Extracted month names from Order Date
- **Products Sold Summary**: Created new sheet with monthly product quantities
- **Highest Selling Product**: Mobile (145 units total)
- **Peak Sales**: Mobile in March (58 units)

### Task 7: Discount Impact Analysis
**Key Findings**:
- Correlation between Discount % and Net Revenue: 0.1028 (weak positive)
- Orders with high discounts (>5%) have higher average net revenue (₹63,503.54) compared to low discounts (₹42,608.50)
- High discount orders generated ₹3,048,170.00 vs ₹2,556,510.00 for low discount orders
- **Conclusion**: Higher discounts are associated with higher revenue, suggesting they may be applied to higher-value products or bulk orders

## How to Run

### Prerequisites
```bash
pip install pandas openpyxl
```

### Execution
```bash
cd /home/runner/work/project/project/a
python3 data_analysis_script.py
```

### Output
The script generates `Data Analyst Assignment Data_COMPLETED.xlsx` with:
1. **orders sheet**: Original data with calculated Revenue, Net Revenue, and Month columns
2. **Questions sheet**: All 7 questions with detailed answers
3. **Products sold sheet**: Monthly product quantity summary

## Technical Details

### Data Processing
- Converted Unit Price from object to numeric type
- Converted Order Date to datetime for month extraction
- Handled missing values appropriately (NaN for non-paid orders in Net Revenue)
- Applied conditional logic for Payment Status-based calculations

### Analysis Methods
- Pandas groupby for aggregations
- Pivot tables for dimensional analysis
- Statistical correlation analysis
- Comprehensive data quality assessment

## Results Summary
✅ All 7 tasks completed successfully  
✅ Data anomalies identified and documented  
✅ Revenue calculations performed with proper formulas  
✅ Regional and temporal analyses completed  
✅ Statistical insights on discount effectiveness provided  
✅ Output Excel file generated with all answers  
