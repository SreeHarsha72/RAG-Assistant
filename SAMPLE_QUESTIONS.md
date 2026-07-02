# Sample Questions and Expected Behavior

Use these questions to demo the project in GitHub, interviews, or a screen recording.

## Metric Definition

```text
What does net_revenue mean?
```

Expected behavior: The assistant should retrieve metric definition or data dictionary chunks and explain the meaning of `net_revenue` with source files.

## Metric Formula

```text
How is net_revenue calculated?
```

Expected behavior: The assistant should return the formula if it exists in the indexed files and cite the source document.

## Pipeline Failure Diagnosis

```text
Why did the orders pipeline fail?
```

Expected behavior: The assistant should retrieve pipeline logs and dbt run logs, identify the failed model, explain the root cause, mention business impact, and recommend a fix.

## SLA Question

```text
What is the SLA for the daily orders pipeline?
```

Expected behavior: The assistant should retrieve internal SOP or documentation chunks and answer with the SLA if available.

## Lineage / Dependency Question

```text
Which dashboard depends on the failed pipeline?
```

Expected behavior: The assistant should retrieve documentation or notes that mention dependent dashboards or downstream impact.

## Data Dictionary Question

```text
Where is customer_segment defined?
```

Expected behavior: The assistant should retrieve the relevant CSV data dictionary chunk and explain the column.

## No-Answer Test

```text
What is the company's vacation policy?
```

Expected behavior: If vacation policy information is not present in the indexed documents, the assistant should say it could not find enough information instead of inventing an answer.
