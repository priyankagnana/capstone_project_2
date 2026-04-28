from __future__ import annotations

import argparse
import re
from dataclasses import dataclass
from pathlib import Path
from typing import Iterable, Optional

import pandas as pd


PROJECT_ROOT = Path(__file__).resolve().parents[1]
DATA_DIR = PROJECT_ROOT / "data"
RAW_DIR = DATA_DIR / "raw"
PROCESSED_DIR = DATA_DIR / "processed"


RAW_LOANS_CSV = RAW_DIR / "loan.csv"
OUT_CLEAN = PROCESSED_DIR / "clean_lendingclub.csv"
OUT_TABLEAU = PROCESSED_DIR / "tableau_loans.csv"
OUT_KPI = PROCESSED_DIR / "kpi_summary.csv"


DEFAULT_STATUSES = {
    "Charged Off",
    "Default",
    "Does not meet the credit policy. Status:Charged Off",
    "Does not meet the credit policy. Status:Default",
}


@dataclass(frozen=True)
class PipelineOutputs:
    clean_path: Path
    tableau_path: Path
    kpi_path: Path


def _parse_term_months(term: pd.Series) -> pd.Series:
    # Typical values: " 36 months", " 60 months"
    return (
        term.astype(str)
        .str.extract(r"(\d+)", expand=False)
        .astype("float64")
    )


def _parse_int_rate(int_rate: pd.Series) -> pd.Series:
    # Raw values are sometimes numeric already; sometimes "13.56%"
    s = int_rate.astype(str).str.strip()
    s = s.str.replace("%", "", regex=False)
    return pd.to_numeric(s, errors="coerce")


def _parse_emp_length_years(emp_length: pd.Series) -> pd.Series:
    # Typical values: "10+ years", "1 year", "< 1 year", "n/a"
    s = emp_length.astype(str).str.strip().str.lower()
    # Use NaN (not pd.NA) because dtype=float cannot hold NAType scalars
    out = pd.Series(float("nan"), index=s.index, dtype="float64")

    out.loc[s.str.contains(r"10\+", regex=True, na=False)] = 10.0
    out.loc[s.str.contains(r"<\s*1", regex=True, na=False)] = 0.5

    m = s.str.extract(r"(\d+)", expand=False)
    out = out.fillna(pd.to_numeric(m, errors="coerce"))
    return out


def _parse_issue_date(issue_d: pd.Series) -> pd.Series:
    # Typical LC format: "Dec-2018"
    return pd.to_datetime(issue_d, format="%b-%Y", errors="coerce")


def _bucket_dti(dti: pd.Series) -> pd.Series:
    dti_num = pd.to_numeric(dti, errors="coerce")
    bins = [0, 10, 20, 30, 40, 50, float("inf")]
    labels = ["0-10", "10-20", "20-30", "30-40", "40-50", "50+"]
    return pd.cut(dti_num, bins=bins, labels=labels, right=False)


def load_raw_loans(path: Path = RAW_LOANS_CSV) -> pd.DataFrame:
    if not path.exists():
        raise FileNotFoundError(f"Missing raw file: {path}")

    usecols = [
        "id",
        "loan_amnt",
        "term",
        "int_rate",
        "installment",
        "grade",
        "sub_grade",
        "emp_length",
        "home_ownership",
        "annual_inc",
        "verification_status",
        "issue_d",
        "loan_status",
        "purpose",
        "addr_state",
        "dti",
    ]

    df = pd.read_csv(path, usecols=lambda c: c in set(usecols), low_memory=False)
    return df


def transform_clean_loans(raw: pd.DataFrame) -> pd.DataFrame:
    df = raw.copy()

    df["loan_amnt"] = pd.to_numeric(df.get("loan_amnt"), errors="coerce")
    df["int_rate"] = _parse_int_rate(df.get("int_rate"))
    df["term_months"] = _parse_term_months(df.get("term"))
    df["emp_length_years"] = _parse_emp_length_years(df.get("emp_length"))
    df["annual_inc"] = pd.to_numeric(df.get("annual_inc"), errors="coerce")
    df["dti"] = pd.to_numeric(df.get("dti"), errors="coerce")

    df["issue_date"] = _parse_issue_date(df.get("issue_d"))
    df["issue_year"] = df["issue_date"].dt.year.astype("Int64")
    df["issue_month"] = df["issue_date"].dt.to_period("M").astype(str)

    loan_status = df.get("loan_status").astype(str).str.strip()
    df["loan_status"] = loan_status
    df["is_default"] = loan_status.isin(DEFAULT_STATUSES).astype("int64")

    out = df[
        [
            "id",
            "loan_amnt",
            "int_rate",
            "term_months",
            "grade",
            "sub_grade",
            "emp_length_years",
            "home_ownership",
            "annual_inc",
            "verification_status",
            "purpose",
            "addr_state",
            "dti",
            "issue_date",
            "issue_year",
            "issue_month",
            "loan_status",
            "is_default",
        ]
    ].copy()

    return out


def transform_tableau_loans(clean: pd.DataFrame) -> pd.DataFrame:
    out = clean[
        [
            "loan_amnt",
            "int_rate",
            "term_months",
            "grade",
            "purpose",
            "addr_state",
            "issue_year",
            "is_default",
            "dti",
        ]
    ].copy()
    out["dti_bucket"] = _bucket_dti(out["dti"]).astype("string")
    out = out.drop(columns=["dti"])
    return out


def compute_kpi_summary(clean: pd.DataFrame) -> pd.DataFrame:
    df = clean.copy()
    df = df.dropna(subset=["issue_year", "grade"])

    agg = (
        df.groupby(["issue_year", "grade"], dropna=False)
        .agg(
            loans=("id", "size"),
            exposure=("loan_amnt", "sum"),
            default_rate=("is_default", "mean"),
            avg_int_rate=("int_rate", "mean"),
            avg_loan_amnt=("loan_amnt", "mean"),
        )
        .reset_index()
        .sort_values(["issue_year", "grade"], ascending=[True, True])
    )
    return agg


def ensure_dirs() -> None:
    PROCESSED_DIR.mkdir(parents=True, exist_ok=True)


def run_pipeline(
    raw_path: Path = RAW_LOANS_CSV,
    out_clean: Path = OUT_CLEAN,
    out_tableau: Path = OUT_TABLEAU,
    out_kpi: Path = OUT_KPI,
) -> PipelineOutputs:
    ensure_dirs()

    raw = load_raw_loans(raw_path)
    clean = transform_clean_loans(raw)
    tableau = transform_tableau_loans(clean)
    kpi = compute_kpi_summary(clean)

    clean.to_csv(out_clean, index=False)
    tableau.to_csv(out_tableau, index=False)
    kpi.to_csv(out_kpi, index=False)

    return PipelineOutputs(clean_path=out_clean, tableau_path=out_tableau, kpi_path=out_kpi)


def main(argv: Optional[Iterable[str]] = None) -> int:
    parser = argparse.ArgumentParser(description="Capstone ETL pipeline")
    parser.add_argument("--raw", type=Path, default=RAW_LOANS_CSV, help="Path to raw loan.csv")
    parser.add_argument("--out-clean", type=Path, default=OUT_CLEAN, help="Output cleaned dataset CSV")
    parser.add_argument("--out-tableau", type=Path, default=OUT_TABLEAU, help="Output Tableau-friendly CSV")
    parser.add_argument("--out-kpi", type=Path, default=OUT_KPI, help="Output KPI summary CSV")
    args = parser.parse_args(list(argv) if argv is not None else None)

    outputs = run_pipeline(
        raw_path=args.raw,
        out_clean=args.out_clean,
        out_tableau=args.out_tableau,
        out_kpi=args.out_kpi,
    )

    print(f"Wrote: {outputs.clean_path}")
    print(f"Wrote: {outputs.tableau_path}")
    print(f"Wrote: {outputs.kpi_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
