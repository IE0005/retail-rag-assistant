# Inventory Replenishment Policy (Reference SOP)

> This is a synthesized reference policy written for this project's
> knowledge base, modeled on typical retail replenishment practice. It is
> not an actual corporate policy document.

## Standard replenishment trigger

A department should be flagged for replenishment review when its trailing
4-week average sales exceed its trailing 26-week average by more than 15%,
AND the deviation is not attributable to a single anomalous week (see the
Anomaly Review Guidelines section below). This combination — sustained lift
plus a clean anomaly check — distinguishes a genuine trend shift from a
short-term spike that will revert on its own.

## Holiday-week lead time rule

For any of the four major holiday weeks (Super Bowl, Labor Day,
Thanksgiving, Christmas), replenishment orders must be placed no later than
3 weeks before the holiday week itself. Lead times for holiday-driven
demand are longer than normal-week reordering because suppliers are
managing allocation across the entire promotional calendar, not just one
store's order.

## Anomaly review guidelines

Before acting on an apparent sales trend, check whether an anomaly
detection pass (e.g. a z-score-based check against the trailing baseline)
flags any of the recent weeks as statistical outliers. A trend driven by
one unusually high week should be treated with lower confidence than a
trend where every recent week is individually unremarkable but the
sustained average has shifted. The former may revert; the latter is more
likely a genuine demand-level change.

## Safety stock during economic volatility

When regional Unemployment is rising or CPI is moving sharply (see the
Economic Indicators Glossary), safety stock levels for discretionary and
general-merchandise departments should be reviewed more frequently than
the standard quarterly cadence, since these departments are the most
sensitive to macroeconomic shifts.

## De-escalation rule

If a department was flagged for replenishment based on a holiday-week
forecast, and the two weeks immediately following the holiday come in
below the forecast's lower estimate, the replenishment order for the
*next* cycle should be scaled back rather than repeated at the same
volume — this prevents compounding an over-order into the following
holiday cycle.
