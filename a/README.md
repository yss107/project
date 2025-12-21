# Data Analyst Assignment - Excel Data Analysis

## Overview
This project contains a Python script that performs comprehensive data analysis on an Excel file with order data. The script uses **actual Excel formulas** to fill columns and calculate results, ensuring that the Excel file remains dynamic and editable.

## ⚠️ IMPORTANT: Data Quality Issue
The dataset contains **2 duplicate rows** (Order O080 and O100), which cause discrepancies between formula-based calculations and pivot table results:
- **With duplicates** (formula-based): West = ₹1,858,965, East = ₹1,104,235
- **Without duplicates** (pivot table): West = ₹1,836,405, East = ₹1,089,985
- **Difference**: ₹36,810 total

The completed Excel file includes:
- An **"Analysis Notes"** sheet explaining the issue
- **"DUPLICATE"** markers in column Z of the orders sheet
- Detailed explanations in the Questions sheet answers

## Files
- `Data Analyst Assignment Data.xlsx` - Original Excel file with order data and questions
- `Data Analyst Assignment Data_COMPLETED.xlsx` - Output file with Excel formulas and answers
- `data_analysis_script.py` - Python script that inserts Excel formulas for all analyses

## Tasks Completed

### Task 1: Data Anomalies Identified
1. **Duplicate Rows**: 2 duplicate rows found affecting count and revenue accuracy
2. **Missing Salesperson Names**: 1 order with missing salesperson affecting performance tracking
3. **Data Type Issues**: Unit Price stored as object (string) and Order Date as object instead of proper numeric/datetime types

### Task 2: Revenue Calculations
- **Revenue Formula (Excel)**: `=Quantity*Unit_Price` (for all orders)
- **Net Revenue Formula (Excel)**: `=IF(Payment_Status="Paid",Quantity*Unit_Price*(1-Discount%/100),"")` (for Paid orders only)
- Excel formulas inserted for all 126 rows
- Formulas automatically calculate values when Excel file is opened

### Task 3: Regional Analysis
Created pivot table showing Net Revenue by Region:

**⚠️ IMPORTANT - Duplicate Row Impact:**
- **Formula calculation (includes duplicates):**
  - West: ₹1,858,965.00 (Highest)
  - North: ₹1,329,260.00
  - South: ₹1,312,220.00
  - East: ₹1,104,235.00

- **Pivot table (excluding duplicates):**
  - West: ₹1,836,405.00 (Highest)
  - North: ₹1,329,260.00
  - South: ₹1,312,220.00
  - East: ₹1,089,985.00

The difference of ₹36,810 is due to 2 duplicate orders (O080 and O100) that appear twice in the dataset.

### Task 4: Total Revenue
**Total Revenue Formula (Excel)**: `=SUM(Revenue_Column)`
Added at the bottom of orders sheet with formula for dynamic calculation

### Task 5: Payment Status Analysis
**Unpaid/Pending Orders Formula (Excel)**: `=(COUNTIF(Status,"Unpaid")+COUNTIF(Status,"Pending"))/COUNTA(Status)*100&"%"`
Added at the bottom of orders sheet with formulas for dynamic calculation

### Task 6: Time-based Product Analysis
- **Month Column Formula (Excel)**: `=TEXT(Order_Date,"MMMM")` - Extracts month name
- **Products Sold Summary**: Created new sheet with `SUMIFS` formulas for monthly product quantities
- **Formulas**: `=SUMIFS(Quantity,Product,Product_Name,Month,Month_Name)` for each product-month combination
- **Highest Selling Product**: Mobile (145 units total, calculated by Excel)
- **Peak Sales**: Mobile in March (58 units, calculated by Excel)

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
1. **orders sheet**: Original data with **Excel formulas** in Revenue, Net Revenue, and Month columns
2. **Questions sheet**: All 7 questions with detailed answers
3. **Products sold sheet**: Monthly product quantity summary using **SUMIFS formulas**
4. **Summary section**: Total Revenue and Payment Status formulas at bottom of orders sheet

## Technical Details

### Excel Formula Implementation
- Uses `openpyxl` library to insert actual Excel formulas (not calculated values)
- **Revenue**: Direct multiplication formula `=Quantity*Unit_Price`
- **Net Revenue**: Conditional formula with IF statement for Paid orders only
- **Month**: TEXT function to extract month name from date
- **Products Sold**: SUMIFS formulas for cross-tabulation by product and month
- **Summary Statistics**: SUM, COUNTIF, and COUNTA formulas for totals and percentages

### Data Processing
- Maintains original Excel data types and formatting
- Inserts formulas that calculate dynamically when Excel file is opened
- Conditional logic implemented via Excel IF statements
- All formulas follow Excel syntax and best practices

### Key Advantages
- **Dynamic**: Values update automatically if source data changes
- **Transparent**: Users can see and understand the formulas
- **Editable**: Formulas can be modified directly in Excel
- **Standard**: Uses native Excel functions (no macros or VBA)

## Results Summary
✅ All 7 tasks completed successfully using Excel formulas  
✅ Data anomalies identified and documented  
✅ Revenue calculations performed with Excel formulas (not static values)  
✅ Regional and temporal analyses completed with dynamic formulas  
✅ Statistical insights on discount effectiveness provided  
✅ Output Excel file generated with fully functional formulas  
✅ All calculations update automatically when data changes  
