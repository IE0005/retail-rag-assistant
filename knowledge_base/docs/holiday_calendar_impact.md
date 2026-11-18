# Holiday Calendar & Sales Impact

Four holiday weeks are tracked separately in the sales calendar because each
one affects demand differently, and treating them as identical would hide
important patterns.

## Super Bowl week

Falls in early-to-mid February. Produces a moderate, broad-based lift
concentrated in food, beverage, and electronics departments. The lift is
short — essentially a single elevated week with little carryover into the
following week.

## Labor Day

Early September. Produces the smallest lift of the four tracked holidays
in most departments, but is still tracked separately because it marks the
start of back-to-school and early-autumn merchandising transitions that
affect markdown timing on summer inventory.

## Thanksgiving

Late November. The single largest demand event of the year in this
dataset. Sales in the Thanksgiving week itself and the following week
(which typically absorbs Black Friday / early holiday shopping) can run
2–3x a store's normal weekly volume, concentrated heavily in general
merchandise and seasonal departments. Because of this scale, a forecasting
error during Thanksgiving week carries much more operational risk than the
same percentage error on a typical week.

## Christmas

Mid-to-late December. A second, slightly smaller demand peak building
through the weeks leading up to the holiday, followed by a sharp drop-off
immediately after. Unlike Thanksgiving, the Christmas peak is often spread
across two to three elevated weeks rather than concentrated in one.

## Why holiday weeks are weighted 5x in evaluation

The standard evaluation metric for this dataset (WMAE — Weighted Mean
Absolute Error) weights holiday weeks five times as heavily as non-holiday
weeks. This reflects the real operational cost structure: an inventory
shortfall during Thanksgiving or Christmas week is far more expensive — in
lost sales, stockouts, and customer experience — than the same dollar
error on an ordinary week in March. A model that is accurate on average but
systematically wrong on holiday weeks would score poorly under this metric
even if its overall MAE looked reasonable.
