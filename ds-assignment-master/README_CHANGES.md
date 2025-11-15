# Changes Made to Fix and Improve Pipeline

## Summary
Successfully fixed all bugs in the driver allocation model training pipeline and improved model performance from ROC AUC 0.17 to 0.75 (+342% improvement).

## Files Modified

### 1. src/data/make_dataset.py
- **Fixed:** `clean_participant_df()` function to remove data leakage
- **Issue:** Was keeping both CREATED and outcome (ACCEPTED/IGNORED/REJECTED) events for same driver-order pair
- **Fix:** Keep only the last event per driver-order pair using `groupby().last()`

### 2. src/features/transformations.py
- **Implemented:** `driver_historical_completed_bookings()` - counts historical completed bookings per driver
- **Added:** `driver_acceptance_rate()` - historical acceptance rate per driver
- **Added:** `time_based_features()` - rush hour indicator
- **Added:** `distance_interaction_features()` - distance-based interaction terms

### 3. src/features/build_features.py
- **Updated:** `apply_feature_engineering()` to include all new feature transformations

### 4. src/models/classifier.py
- **Implemented:** `evaluate()` method with ROC AUC, accuracy, precision, recall, and F1 score

### 5. config.toml
- **Updated:** Feature list to include new features
- **Tuned:** Random Forest hyperparameters for better performance and generalization

### 6. .gitignore
- **Added:** Patterns to exclude large data files from git

## Results

### Submission Files Generated
- `submission/metrics.json` - Model evaluation metrics
- `submission/results.csv` - Driver predictions (10,000 orders)

### Final Metrics
- ROC AUC: 0.751
- Accuracy: 0.906
- Precision: 0.910
- Recall: 0.994
- F1 Score: 0.950

### How to Run
```bash
make run
```

This will execute the full pipeline: data processing → feature engineering → model training → predictions → tests
