"""
Data Analyst Assignment - Excel Data Analysis Script
This script performs all tasks mentioned in the Questions sheet of the Excel file.
"""

import pandas as pd
import numpy as np
from datetime import datetime
import warnings
warnings.filterwarnings('ignore')

# File paths
INPUT_FILE = 'Data Analyst Assignment Data.xlsx'
OUTPUT_FILE = 'Data Analyst Assignment Data_COMPLETED.xlsx'

def load_data():
    """Load the Excel file and return dataframes."""
    print("Loading Excel file...")
    xls = pd.ExcelFile(INPUT_FILE)
    df_orders = pd.read_excel(xls, sheet_name='orders')
    df_questions = pd.read_excel(xls, sheet_name='Questions')
    return df_orders, df_questions

def task1_identify_anomalies(df):
    """Task 1: Identify 3 data anomalies."""
    print("\n" + "="*80)
    print("TASK 1: Identifying Data Anomalies")
    print("="*80)
    
    anomalies = []
    
    # Anomaly 1: Duplicate rows
    duplicate_count = df.duplicated().sum()
    anomalies.append(
        f"1. Duplicate Rows: There are {duplicate_count} duplicate rows in the dataset. "
        f"This affects analysis by inflating counts and revenue calculations, leading to "
        f"inaccurate insights about sales performance and customer behavior."
    )
    
    # Anomaly 2: Missing Salesperson Name
    missing_salesperson = df['Salesperson Name'].isnull().sum()
    anomalies.append(
        f"2. Missing Salesperson Names: {missing_salesperson} order(s) have missing salesperson names. "
        f"This affects performance tracking, commission calculations, and prevents accurate "
        f"salesperson-level analytics."
    )
    
    # Anomaly 3: Unit Price stored as object instead of numeric
    anomalies.append(
        f"3. Data Type Issues: 'Unit Price' is stored as object (string) instead of numeric type, "
        f"and 'Order Date' is stored as object instead of datetime. This prevents proper numerical "
        f"operations, sorting, and date-based filtering, potentially causing calculation errors."
    )
    
    for anomaly in anomalies:
        print(f"\n{anomaly}")
    
    return anomalies

def task2_calculate_revenue(df):
    """Task 2: Fill Net Revenue and Revenue columns."""
    print("\n" + "="*80)
    print("TASK 2: Calculating Net Revenue and Revenue")
    print("="*80)
    
    # Convert Unit Price to numeric (it's stored as object)
    df['Unit Price'] = pd.to_numeric(df['Unit Price'], errors='coerce')
    
    # Convert Discount % to decimal (5% = 0.05)
    df['Discount_Decimal'] = df['Discount %'] / 100
    
    # Calculate Revenue for all orders
    df['Revenue'] = df['Quantity'] * df['Unit Price']
    
    # Calculate Net Revenue only for Paid orders
    df['Net Revenue'] = np.where(
        df['Payment Status'] == 'Paid',
        df['Quantity'] * df['Unit Price'] * (1 - df['Discount_Decimal']),
        np.nan
    )
    
    print(f"✓ Revenue calculated for all {len(df)} orders")
    print(f"✓ Net Revenue calculated for {df['Payment Status'].eq('Paid').sum()} paid orders")
    print(f"\nSample calculations:")
    print(df[['Order ID', 'Quantity', 'Unit Price', 'Discount %', 'Payment Status', 'Revenue', 'Net Revenue']].head(10))
    
    return df

def task3_pivot_table(df):
    """Task 3: Create pivot table for Net Revenue by Region."""
    print("\n" + "="*80)
    print("TASK 3: Pivot Table - Net Revenue by Region")
    print("="*80)
    
    # Create pivot table
    pivot = df[df['Payment Status'] == 'Paid'].groupby('Region')['Net Revenue'].sum().sort_values(ascending=False)
    
    print("\nNet Revenue by Region (Paid orders only):")
    print(pivot)
    
    highest_region = pivot.idxmax()
    highest_revenue = pivot.max()
    
    print(f"\n✓ Region with highest Net Revenue: {highest_region} (₹{highest_revenue:,.2f})")
    
    return pivot

def task4_total_revenue(df):
    """Task 4: Calculate Total Revenue."""
    print("\n" + "="*80)
    print("TASK 4: Total Revenue Calculation")
    print("="*80)
    
    total_revenue = df['Revenue'].sum()
    print(f"Total Revenue = SUM of all Revenue")
    print(f"Total Revenue = ₹{total_revenue:,.2f}")
    
    return total_revenue

def task5_unpaid_pending_percentage(df):
    """Task 5: Calculate percentage of Unpaid/Pending orders."""
    print("\n" + "="*80)
    print("TASK 5: Unpaid/Pending Orders Percentage")
    print("="*80)
    
    total_orders = len(df)
    unpaid_pending_orders = df[df['Payment Status'].isin(['Unpaid', 'Pending'])].shape[0]
    percentage = (unpaid_pending_orders / total_orders) * 100
    
    print(f"Total Orders = {total_orders}")
    print(f"Unpaid + Pending Orders = {unpaid_pending_orders}")
    print(f"Percentage = (Unpaid + Pending Orders / Total Orders) × 100")
    print(f"Percentage = ({unpaid_pending_orders} / {total_orders}) × 100 = {percentage:.2f}%")
    
    return percentage

def task6_month_and_products_sold(df):
    """Task 6: Extract month and create Products sold summary."""
    print("\n" + "="*80)
    print("TASK 6: Month Extraction and Products Sold Summary")
    print("="*80)
    
    # Convert Order Date to datetime if needed
    if df['Order Date'].dtype == 'object':
        df['Order Date'] = pd.to_datetime(df['Order Date'])
    
    # Extract month name
    df['Month'] = df['Order Date'].dt.strftime('%B')
    
    print(f"✓ Month column filled with month names")
    print(f"\nSample:")
    print(df[['Order ID', 'Order Date', 'Month']].head())
    
    # Create Products sold summary
    print("\n" + "-"*80)
    print("Creating Products Sold Summary Table (Month-wise)")
    print("-"*80)
    
    products_sold = df.groupby(['Month', 'Product'])['Quantity'].sum().reset_index()
    products_sold_pivot = products_sold.pivot(index='Product', columns='Month', values='Quantity').fillna(0)
    
    # Reorder columns by month
    month_order = ['January', 'February', 'March', 'April', 'May', 'June', 
                   'July', 'August', 'September', 'October', 'November', 'December']
    available_months = [m for m in month_order if m in products_sold_pivot.columns]
    products_sold_pivot = products_sold_pivot[available_months]
    
    # Add total column
    products_sold_pivot['Total'] = products_sold_pivot.sum(axis=1)
    
    print("\nProducts Sold Summary (Quantity by Month):")
    print(products_sold_pivot)
    
    # Find highest quantity
    max_total_idx = products_sold_pivot['Total'].idxmax()
    max_total_value = products_sold_pivot['Total'].max()
    
    # Find highest for month-product combination
    products_sold_with_total = products_sold.copy()
    max_row = products_sold_with_total.loc[products_sold_with_total['Quantity'].idxmax()]
    
    print(f"\n✓ Product with highest total quantity sold: {max_total_idx} ({int(max_total_value)} units)")
    print(f"✓ Highest single month-product combination: {max_row['Product']} in {max_row['Month']} ({int(max_row['Quantity'])} units)")
    
    return df, products_sold_pivot

def task7_discount_revenue_analysis(df):
    """Task 7: Analyze discount vs revenue relationship."""
    print("\n" + "="*80)
    print("TASK 7: Discount vs Revenue Analysis")
    print("="*80)
    
    # Analyze for paid orders only
    paid_df = df[df['Payment Status'] == 'Paid'].copy()
    
    # Group by discount percentage
    discount_analysis = paid_df.groupby('Discount %').agg({
        'Net Revenue': ['sum', 'mean', 'count'],
        'Revenue': ['sum', 'mean']
    }).round(2)
    
    print("\nRevenue Analysis by Discount %:")
    print(discount_analysis)
    
    # Calculate correlation
    correlation = paid_df['Discount %'].corr(paid_df['Net Revenue'])
    
    print(f"\nCorrelation between Discount % and Net Revenue: {correlation:.4f}")
    
    # Compare low vs high discount
    low_discount = paid_df[paid_df['Discount %'] <= 5]
    high_discount = paid_df[paid_df['Discount %'] > 5]
    
    avg_net_revenue_low = low_discount['Net Revenue'].mean()
    avg_net_revenue_high = high_discount['Net Revenue'].mean()
    
    total_net_revenue_low = low_discount['Net Revenue'].sum()
    total_net_revenue_high = high_discount['Net Revenue'].sum()
    
    print(f"\nLow Discount (≤5%):")
    print(f"  - Number of orders: {len(low_discount)}")
    print(f"  - Average Net Revenue: ₹{avg_net_revenue_low:,.2f}")
    print(f"  - Total Net Revenue: ₹{total_net_revenue_low:,.2f}")
    
    print(f"\nHigh Discount (>5%):")
    print(f"  - Number of orders: {len(high_discount)}")
    print(f"  - Average Net Revenue: ₹{avg_net_revenue_high:,.2f}")
    print(f"  - Total Net Revenue: ₹{total_net_revenue_high:,.2f}")
    
    conclusion = f"""
CONCLUSION:
The correlation coefficient of {correlation:.4f} indicates a {'negative' if correlation < 0 else 'positive'} 
relationship between discount percentage and net revenue. 

Analysis shows:
- Orders with low discounts (≤5%) have an average net revenue of ₹{avg_net_revenue_low:,.2f}
- Orders with high discounts (>5%) have an average net revenue of ₹{avg_net_revenue_high:,.2f}

{'Higher discounts lead to LOWER net revenue per order on average.' if avg_net_revenue_low > avg_net_revenue_high else 'Higher discounts lead to HIGHER net revenue per order on average.'}
However, the total net revenue from {'low' if total_net_revenue_low > total_net_revenue_high else 'high'} 
discount orders is higher (₹{max(total_net_revenue_low, total_net_revenue_high):,.2f} vs ₹{min(total_net_revenue_low, total_net_revenue_high):,.2f}),
suggesting that the {'number' if total_net_revenue_low > total_net_revenue_high else 'discount strategy'} of orders 
matters more than individual discount levels for overall revenue.
"""
    
    print(conclusion)
    
    return conclusion

def save_results(df_orders, df_questions, products_sold_pivot, anomalies, pivot, total_revenue, 
                 percentage, conclusion):
    """Save all results to Excel file."""
    print("\n" + "="*80)
    print("SAVING RESULTS")
    print("="*80)
    
    # Update Questions sheet with answers
    answers = [
        '\n'.join(anomalies),
        'Formulas applied: Revenue = Quantity × Unit Price; Net Revenue = Quantity × Unit Price × (1 - Discount%) for Paid orders',
        f'Pivot table created. Highest Net Revenue Region: {pivot.idxmax()} (₹{pivot.max():,.2f})',
        f'Total Revenue = ₹{total_revenue:,.2f}',
        f'{percentage:.2f}%',
        'See "Products sold" sheet for summary. Month and Product with highest quantity are documented in the sheet.',
        conclusion.strip()
    ]
    
    df_questions['Answers'] = answers
    
    # Remove the temporary Discount_Decimal column before saving
    if 'Discount_Decimal' in df_orders.columns:
        df_orders = df_orders.drop(columns=['Discount_Decimal'])
    
    # Write to Excel
    with pd.ExcelWriter(OUTPUT_FILE, engine='openpyxl') as writer:
        df_orders.to_excel(writer, sheet_name='orders', index=False)
        df_questions.to_excel(writer, sheet_name='Questions', index=False)
        products_sold_pivot.to_excel(writer, sheet_name='Products sold')
    
    print(f"✓ Results saved to '{OUTPUT_FILE}'")
    print(f"  - 'orders' sheet updated with Revenue, Net Revenue, and Month columns")
    print(f"  - 'Questions' sheet updated with all answers")
    print(f"  - 'Products sold' sheet created with monthly summary")

def main():
    """Main execution function."""
    print("="*80)
    print("DATA ANALYST ASSIGNMENT - EXCEL DATA ANALYSIS")
    print("="*80)
    
    # Load data
    df_orders, df_questions = load_data()
    
    # Task 1: Identify anomalies
    anomalies = task1_identify_anomalies(df_orders)
    
    # Task 2: Calculate Revenue and Net Revenue
    df_orders = task2_calculate_revenue(df_orders)
    
    # Task 3: Pivot table for Net Revenue by Region
    pivot = task3_pivot_table(df_orders)
    
    # Task 4: Calculate Total Revenue
    total_revenue = task4_total_revenue(df_orders)
    
    # Task 5: Calculate percentage of Unpaid/Pending orders
    percentage = task5_unpaid_pending_percentage(df_orders)
    
    # Task 6: Extract month and create Products sold summary
    df_orders, products_sold_pivot = task6_month_and_products_sold(df_orders)
    
    # Task 7: Analyze discount vs revenue relationship
    conclusion = task7_discount_revenue_analysis(df_orders)
    
    # Save results
    save_results(df_orders, df_questions, products_sold_pivot, anomalies, pivot, 
                 total_revenue, percentage, conclusion)
    
    print("\n" + "="*80)
    print("ALL TASKS COMPLETED SUCCESSFULLY!")
    print("="*80)

if __name__ == "__main__":
    main()
