# Data Dictionary: Retail Sales & Features Dataset

This document defines every column used across the retail sales dataset that
powers this knowledge base and the store performance profiles.

## Sales records

- **Store** — numeric store identifier (1–45).
- **Dept** — numeric department identifier within a store (e.g. 1, 5, 20).
  Departments represent product categories; the same Dept number refers to
  the same category across every store.
- **Date** — the first day (a Friday) of the sales week.
- **Weekly_Sales** — total sales revenue for that store/department/week, in
  dollars.
- **IsHoliday** — whether the week contains a major holiday (Super Bowl,
  Labor Day, Thanksgiving, or Christmas).

## Store attributes

- **Type** — store format classification, A/B/C. Roughly corresponds to
  store size tier: A stores are typically the largest-format stores, B are
  mid-size, and C are the smallest.
- **Size** — the store's square footage.

## External / economic features

- **Temperature** — average regional temperature (°F) for the week.
- **Fuel_Price** — average regional fuel price ($/gallon) for the week.
- **CPI** — Consumer Price Index for the region that week, a general measure
  of price-level inflation.
- **Unemployment** — regional unemployment rate (%) for the week.
- **MarkDown1** through **MarkDown5** — dollar amount of five anonymized
  promotional markdown events run that week. Only populated from
  mid-November 2011 onward; earlier weeks have no markdown data because the
  promotions program had not started yet.

## Derived / engineered fields

- **MarkdownsSum** — sum of MarkDown1–5 for the week; a single combined
  measure of promotional activity.
- **SuperBowlWeek / LaborDay / Thanksgiving / Christmas** — boolean flags
  derived from the calendar week number, used to let a forecasting model
  learn holiday-specific effects separately rather than treating all
  holidays as identical.
- **WMAE (Weighted Mean Absolute Error)** — the evaluation metric used for
  this dataset. It is a standard MAE, except holiday weeks are weighted 5x
  as heavily as non-holiday weeks, because getting holiday-week forecasts
  right matters disproportionately for staffing and inventory decisions.
