# End-to-End (E2E) Testing SOP

## Objective
Validate critical user workflows from request submission to review result retrieval.

## Critical path scenarios
1. Submit review request.
2. Observe lifecycle progression (`queued` -> `running` -> terminal state).
3. Retrieve review result and findings.
4. Submit feedback record.

## Preconditions
- Running service instance
- Test tenant/context headers if required
- Stable test dataset / known repository inputs

## Procedure
1. Start with a clean test context.
2. Execute critical path API flow using scripted requests.
3. Validate response contracts and persisted lifecycle outcomes.
4. Capture logs for failures and correlate with job IDs.

## Pass/Fail criteria
- All critical path scenarios complete successfully.
- Terminal state is correct (`completed` for happy path).
- Findings payload and feedback recording are retrievable.

## Release gate
- Required for release candidates and production promotions.
- Fail release on critical-path E2E regression.
