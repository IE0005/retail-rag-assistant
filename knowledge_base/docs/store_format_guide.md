# Store Format Guide: Types A, B, and C

This reference explains the three store format types used across the chain
and what operationally distinguishes them.

## Type A — Large format

Type A stores are the largest-format stores in the chain, typically well
over 150,000 square feet. They carry the broadest assortment across every
department, run the widest range of markdown and promotional events, and
generally post the highest absolute weekly sales. Because of their scale,
small percentage forecasting errors at a Type A store translate into large
absolute dollar swings, so forecast accuracy matters disproportionately
here.

## Type B — Mid-size format

Type B stores range roughly from 35,000 to 150,000 square feet. They carry
a narrower assortment than Type A, with department-level sales more
concentrated in a smaller number of high-performing categories. Markdown
events tend to have a visibly larger *relative* impact on weekly sales at
Type B stores than at Type A stores, since a promotion represents a bigger
share of the store's total volume.

## Type C — Small format

Type C stores are the smallest format, generally under 40,000 square feet.
They carry the most limited assortment, concentrated in essentials and the
highest-velocity categories only. Type C stores show the most volatile
week-to-week percentage swings in the dataset, simply because their
absolute sales base is small enough that normal demand noise looks large
in percentage terms.

## Why format matters for forecasting and anomaly detection

Store format (Type and Size) is one of the strongest predictors of a
department's baseline sales level, which is why both the demand-forecasting
model and the anomaly-detection logic condition on it. An anomaly threshold
calibrated on a Type A store's sales distribution would flag almost every
normal week at a Type C store as "anomalous," because the two store formats
have fundamentally different baseline variance. Any analysis comparing
stores should always account for format before comparing raw sales
numbers.
