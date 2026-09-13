# Model comparison — predict job role from skills

- Rows: **2502**  |  Roles (classes): **42**  |  Features: TF-IDF over skills (max 3000, 1-2 grams)
- Best model: **Logistic Regression** (accuracy 0.9820, macro-F1 0.9813)

| model                   |   accuracy |   macro_f1 |   train_time_s | file                           |
|:------------------------|-----------:|-----------:|---------------:|:-------------------------------|
| Logistic Regression     |     0.982  |     0.9813 |          0.399 | logistic_regression.joblib     |
| K-Nearest Neighbors     |     0.98   |     0.9794 |          0.002 | k-nearest_neighbors.joblib     |
| Random Forest           |     0.98   |     0.9792 |          0.889 | random_forest.joblib           |
| Linear SVM              |     0.978  |     0.9772 |          0.078 | linear_svm.joblib              |
| Multinomial Naive Bayes |     0.976  |     0.9748 |          0.008 | multinomial_naive_bayes.joblib |
| Gradient Boosting       |     0.9541 |     0.9564 |         80.136 | gradient_boosting.joblib       |
| Decision Tree           |     0.8902 |     0.8897 |          0.204 | decision_tree.joblib           |
