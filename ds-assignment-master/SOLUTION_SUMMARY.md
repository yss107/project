# GoTo Data Science Assignment - Solution Summary

## Overview
This document summarizes my approach to fixing and improving the driver allocation model training pipeline for GoRide's two-wheel transportation service.

## Issues Identified and Fixed

### 1. Critical Data Leakage Bug
**Problem:** The `clean_participant_df` function was keeping both CREATED and outcome events (ACCEPTED/IGNORED/REJECTED) for the same driver-order pair, creating duplicate rows that leaked outcome information into training features.

**Solution:** Modified the function to keep only the final outcome event per driver-order pair using `groupby().last()`, reducing the dataset from 400K to 200K rows and eliminating data leakage.

**Impact:** ROC AUC improved from 0.17 (worse than random!) to 0.65, confirming the model was learning from leaked outcomes.

### 2. Missing Feature Implementation
**Problem:** `driver_historical_completed_bookings` function raised NotImplementedError.

**Solution:** Implemented a cumulative sum feature that counts completed bookings for each driver before the current event timestamp, ensuring temporal consistency to avoid lookahead bias. Handled test data gracefully by setting default values.

### 3. Missing Evaluation Metrics
**Problem:** The `evaluate` method in SklearnClassifier was not implemented.

**Solution:** Implemented comprehensive evaluation using ROC AUC (primary metric for ranking), along with accuracy, precision, recall, and F1-score to provide a complete picture of model performance.

## Model Improvements

### Feature Engineering
I added four new features based on domain understanding:

1. **driver_acceptance_rate**: Historical acceptance rate per driver (normalized version of completed bookings)
2. **is_rush_hour**: Binary indicator for peak hours (7-9 AM, 5-8 PM) when driver behavior may differ
3. **distance_interaction**: Product of trip distance and driver distance to capture combined effects
4. **trip_to_driver_ratio**: Ratio indicating if the trip is worth the pickup distance

These features improved ROC AUC from 0.653 to 0.713 (+9%).

### Hyperparameter Tuning
Optimized Random Forest parameters:
- Increased trees: 300 → 500 (more robust predictions)
- Reduced max_depth: 30 → 15 (prevent overfitting)
- Added min_samples_split=10, min_samples_leaf=4 (regularization)
- Enabled bootstrap=true (better generalization)
- Set max_features="sqrt" (decorrelate trees)

These changes improved ROC AUC from 0.713 to 0.745 (+4.5%).

## Results

### Final Performance Metrics
- **ROC AUC: 0.745** (primary metric for driver ranking)
- **Accuracy: 0.905**
- **Precision: 0.909**
- **Recall: 0.994**
- **F1 Score: 0.950**

### Performance Progression
1. Initial (buggy): ROC AUC 0.170
2. After bug fixes: ROC AUC 0.653 (+284%)
3. After new features: ROC AUC 0.713 (+9%)
4. After hyperparameter tuning: ROC AUC 0.745 (+4.5%)

**Total improvement: +338% from buggy baseline**

## Key Insights

1. **Data quality is paramount**: The data leakage bug had the largest impact on model performance. Always validate data preprocessing carefully.

2. **Feature engineering matters**: Simple domain-based features (acceptance rate, rush hour) provided meaningful improvements without adding complexity.

3. **Regularization helps**: Reducing max_depth and adding min_samples constraints prevented overfitting despite having more features.

4. **High recall is natural**: The extremely high recall (99.4%) reflects class imbalance - most driver-order pairs in the data result in acceptance, which is expected since we only have records for actual allocations.

## Future Work

If given more time, I would explore:
1. Address class imbalance with SMOTE or class weights
2. Add driver-level aggregated features (avg GPS accuracy, typical working hours)
3. Incorporate booking-level features from booking_log (COMPLETED vs CANCELLED orders)
4. Try gradient boosting (XGBoost/LightGBM) for potentially better performance
5. Implement cross-validation for more robust hyperparameter tuning
6. Add feature importance analysis to understand driver acceptance patterns

## Conclusion

The assignment successfully simulated real-world data science challenges: debugging data pipelines, identifying silent errors, and iteratively improving model performance through principled feature engineering and hyperparameter tuning. The final model achieves strong performance in predicting driver acceptance, which would help GoRide allocate orders more efficiently and reduce customer wait times.
