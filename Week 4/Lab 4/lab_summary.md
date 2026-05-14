# Lab Summary: Error Handling and Scheduled Workflows

## Error Handling Approach

The **Daily Data Fetcher** workflow uses n8n's built-in **Error Trigger** node combined with the HTTP Request node's native **Retry on Failure** setting (3 retries, 5-second delay) to handle transient failures such as timeouts and 5xx server errors. When a failure occurs after all retries are exhausted, the Error Trigger captures the full error context — including the failing node name, error message, and timestamp — and formats it into a human-readable notification string ready to be sent via email, Slack, or Discord. This two-layer approach (retry for transient issues, Error Trigger for permanent failures) ensures that minor network hiccups never surface as failures while genuine problems are surfaced immediately.

## Idempotency Strategy

The **Daily Summary Generator** workflow ensures idempotency by storing a list of already-processed dates in n8n's workflow static data. Before saving any new record, a **Code node** checks whether today's ISO date (`YYYY-MM-DD`) already exists in that list; an **IF node** then routes execution either to the save branch (new record) or a skip branch (duplicate suppressed). In a production setup, this local static data store would be replaced by a Google Sheets read-before-write pattern or a database `UPSERT`, using the `date` field as the unique key — ensuring that even if the scheduler fires multiple times or a manual test run occurs, no duplicate rows are ever created.

## Schedule Choice

The workflow is scheduled to run **daily at 9:00 AM** using the n8n Schedule Trigger's built-in daily interval with hour/minute precision. This time was chosen because it captures overnight GitHub activity (stars, forks, open issues) and delivers the summary at the start of the working day, giving teams actionable data before their morning standup. The Error Trigger is also attached to the scheduled workflow so any unhandled failure during an automated run immediately produces a formatted alert, eliminating silent failures in unattended execution.
