# Anomaly Detection Methods Reference

This document explains the statistical approach used to flag unusual sales
weeks, and when to prefer it over alternatives.

## Z-score method (used in this project)

For a given store/department, compute the mean and standard deviation of
weekly sales over a trailing baseline window, excluding holiday weeks from
the baseline calculation (since holiday weeks are expected to be high and
would otherwise inflate the "normal" baseline). For each week, compute:

    z = (weekly_sales - baseline_mean) / baseline_std

A week is flagged as anomalous if |z| exceeds a threshold — 2.0 is a
reasonable default, flagging roughly the most extreme ~5% of weeks under a
normal distribution assumption. A positive z-score is a "spike" (unusually
high), negative is a "drop."

## Why exclude holiday weeks from the baseline

If holiday weeks were included in the baseline mean/std calculation, the
baseline would be artificially inflated and widened, which would make the
method *less* sensitive to genuine non-holiday anomalies — a real problem
during the weeks that matter most for catching unexpected demand shifts
early.

## When z-score is the wrong tool

Z-score anomaly detection assumes a roughly stable, unimodal baseline
distribution. It is a poor fit for: data with a strong ongoing trend (a
steadily climbing baseline makes old weeks look artificially low and new
weeks look artificially high, triggering false positives), very short
history (fewer than ~8-10 weeks gives an unreliable mean/std estimate), or
multimodal demand patterns (e.g. a department with two genuinely different
"normal" operating regimes, like pre- and post-renovation).

## Alternatives for more complex cases

For manufacturing-style process data with higher dimensionality or
non-stationary baselines, unsupervised methods like K-means clustering,
Gaussian Mixture Models, or Variational Autoencoders can outperform a
simple z-score — they can model multimodal or nonlinear "normal" regions
rather than assuming a single Gaussian baseline. These are more complex to
implement and tune, so the simpler z-score approach is preferred whenever
the underlying data is reasonably well-behaved, reserving the heavier
methods for cases where z-score demonstrably fails.
