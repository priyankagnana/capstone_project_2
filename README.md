# LendingClub Default Risk Analysis and Portfolio Optimization

## Project Overview
This project analyzes loan-level data from LendingClub to identify key drivers of loan default risk and propose data-driven strategies to improve underwriting decisions and portfolio performance.

The project includes:
- Python-based ETL pipeline
- Exploratory Data Analysis (EDA)
- Statistical modeling using logistic regression
- Tableau dashboard for visualization
- Business insights and recommendations

---

## Problem Statement
Identify the main drivers of loan default risk and recommend strategies to reduce expected defaults while maintaining revenue.

---

## Repository Structure

```
data/
├── raw/
│   └── loan.csv
├── processed/
│   ├── clean_lendingclub.csv
│   ├── tableau_loans.csv
│   └── kpi_summary.csv

notebooks/
├── 01_extraction.ipynb
├── 02_cleaning.ipynb
├── 03_eda.ipynb
├── 04_statistical.ipynb
└── 05_final_load_prep.ipynb

reports/
├── figures/
└── model_top_coefficients.csv

tableau/
├── screenshots/
└── dashboard_links.md

docs/
├── data_dictionary.md
└── team_contribution_plan.md

README.md
```



---

## Dataset Information

- Source: LendingClub Loan Data (Kaggle)
- Number of records: 2,260,668
- Format: CSV

### Key Features
- Loan amount  
- Interest rate  
- Term  
- Grade and sub-grade  
- Debt-to-income ratio (DTI)  
- Annual income  
- Loan purpose  
- Verification status  
- State  
- Issue date  

### Target Variable
- is_default (derived from loan_status)

---

## ETL Methodology

Data preprocessing was implemented using Python.

### Steps
- Standardized column names  
- Parsed issue date into year and month  
- Derived features such as term_months and emp_length_years  
- Cleaned and normalized categorical variables  
- Created binary target variable is_default  

### Tools Used
- Python  
- Pandas  
- NumPy  

---

## KPI Framework

- Default Rate = Defaults / Total Loans  
- Exposure Proxy = Total Loan Amount  
- Average Interest Rate  

### Observed KPIs
- Default Rate: 12.58%  
- Average Interest Rate: 13.09  
- Average Loan Amount: 15046.93  

---

## Exploratory Data Analysis

Key analyses include:
- Default rate trend over time  
- Default rate by grade  
- Default rate by loan purpose  
- Relationship between loan term and default  

Visualizations are available in the reports directory.

---

## Statistical Analysis

### Model
Logistic Regression

### Performance
- ROC-AUC: 0.680  
- Average Precision: 0.389  

### Key Drivers
- Loan grade  
- Term  
- Debt-to-income ratio  
- Interest rate  

---

## Tableau Dashboard

The dashboard enables interactive exploration of loan performance.

### Features
- Filters: Year, grade, term, purpose, state  
- Visualizations: Trends, segment comparisons, portfolio distribution  

Dashboard link:
(To be updated)

Screenshots are available in tableau/screenshots.

---

## Key Insights

1. Default risk is concentrated in lower credit grades  
2. Longer loan terms increase default probability  
3. High DTI borrowers are riskier  
4. Certain loan purposes drive higher defaults  
5. Interest rate does not fully offset risk  
6. Geographic variation affects default rates  
7. Verification status influences borrower reliability  
8. Missing data correlates with higher risk  
9. A small subset of segments drives most defaults  
10. Portfolio composition impacts overall risk  

---

## Business Recommendations

- Restrict high-risk grade and long-term loan combinations  
- Introduce DTI-based thresholds for approvals  
- Optimize portfolio mix toward lower-risk segments  
- Strengthen verification processes  
- Implement monitoring dashboards  

---

## Impact Estimation

Reducing exposure to high-risk segments by 10% can lower overall default rates by approximately 2 to 3 percent.

Improved DTI filtering can reduce risk while maintaining loan volume.

---

## Limitations

- Target variable is derived from loan_status  
- Observational dataset with no causal inference  
- Logistic regression provides moderate predictive power  

---

## Future Scope

- Use advanced models such as XGBoost or Random Forest  
- Build expected loss models  
- Perform model calibration  
- Conduct A/B testing for policy changes  

---

## Contribution Matrix

| Member Name | Contribution |
|------------|-------------|
| Gnana Priyanka | EDA, analysis |
| Divyanjali | ETL pipeline, insights |
| G Jaya Geethika | Report, insights |
| Spruha Perumalla  | Tableau dashboard |
| Khyati Kapil  | Tableau dashboard |

---

## Tech Stack

- Python (Pandas, NumPy, Scikit-learn)  
- Jupyter Notebook  
- Tableau Public  
- Git and GitHub  

---

## Acknowledgements

- LendingClub for dataset  
- Kaggle for data hosting  

---

