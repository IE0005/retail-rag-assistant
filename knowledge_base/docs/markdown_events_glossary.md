# Markdown Events Glossary

"Markdown" events are temporary promotional price reductions run across
departments to drive volume, clear aging inventory, or compete during
high-traffic calendar windows. The dataset tracks five anonymized markdown
categories, MarkDown1 through MarkDown5, representing different kinds of
promotional spend.

## Why markdowns are anonymized

The five markdown categories are not labeled with their specific
promotional mechanics (e.g. "buy-one-get-one" vs. "percentage off") in this
dataset — they are reported only as dollar amounts per store per week. This
is common in real retail datasets shared for analysis, since the specific
promotional calendar is often commercially sensitive. For modeling
purposes, what matters is the combined signal: total promotional spend in
a given week (MarkdownsSum) is a strong predictor of a short-term sales
lift.

## Markdown timing relative to holidays

Markdown events cluster heavily around the four major holiday weeks
(Super Bowl, Labor Day, Thanksgiving, Christmas), since that is when
promotional spend generates the most volume. A week with an unusually high
MarkdownsSum value that is *not* near a holiday is worth a second look —
it may indicate a clearance event for overstocked or aging inventory rather
than a planned promotional calendar event.

## Markdown data availability

Markdown figures are only populated starting in mid-November 2011. Weeks
before that date have no markdown data at all (not zero — genuinely
missing), because the promotional tracking program had not started yet.
Any analysis or model using markdown features needs to handle this
missing-data period explicitly rather than treating it as "no promotion
ran."

## Interaction with store format

Markdown lift is proportionally larger at smaller-format stores (Type B
and Type C) than at Type A stores, since a promotion represents a bigger
share of a smaller store's total weekly volume. See the Store Format Guide
for the full breakdown by Type.
