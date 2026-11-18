# Demand Forecasting Methodology

This document summarizes the modeling approach used for weekly demand
forecasting in this knowledge base's companion projects.

## Model selection process

Five regression models were benchmarked on an identical 90/10 train/validation
split: Random Forest, Extra Trees, XGBoost, LightGBM, and CatBoost. Extra
Trees scored highest on R² (0.984), but its serialized model file was
approximately 1.3GB — impractical to deploy on free-tier hosting (GitHub
and Streamlit Community Cloud both have file-size limits well under that).
Random Forest was selected instead, scoring a close second (R² = 0.977) at
roughly 54MB — the best accuracy-to-deployability trade-off among the five
candidates.

## Features used

The deployed model is trained on: store metadata (Type, Size), calendar
features (week, month, year, day, and the four holiday flags), and the
economic indicators (Temperature, Fuel_Price, CPI, Unemployment,
MarkdownsSum). Notably, the model does not use any lagged sales values as
input features — it predicts purely from store/calendar/economic context,
which makes it usable for genuinely novel future weeks rather than only
short-horizon extrapolation.

## Evaluation metric

Models are evaluated primarily on WMAE (Weighted Mean Absolute Error),
which weights holiday weeks 5x as heavily as non-holiday weeks — see the
Holiday Calendar & Sales Impact document for why this weighting reflects
real operational cost. R² and standard MAE/RMSE are also tracked, but WMAE
is the metric the model selection decision was ultimately based on.

## Why not just use raw historical averages

A naive forecast (e.g., "next year's Thanksgiving week will equal last
year's Thanksgiving week") ignores store-level economic drift (CPI,
unemployment changes) and doesn't generalize to new stores or departments
with limited history. The regression approach generalizes across stores
and departments by learning from store format, size, and economic context
jointly, rather than requiring enough historical data for every individual
store/department combination.
