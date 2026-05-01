# AGenNext CodeReview Desktop Test Cases

This desktop surface is currently scaffolded. The cases below define the minimum validation set for implementation and QA.

## Assumptions
- Desktop app uses existing backend API from `src/codereviewer/api/app.py`.
- Desktop app authenticates to backend (or runs in trusted local mode).
- Desktop app can select a local repository and submit review jobs.

## Test Cases

### DSK-001 Launch and Shell Initialization
- Precondition: Desktop app is installed.
- Steps:
  1. Launch the desktop app.
  2. Wait for initial UI load.
- Expected:
  - App opens without crash.
  - Home view renders navigation, runtime profile selector, and review submission form.

### DSK-002 Backend Connectivity Check
- Precondition: Backend is running and reachable.
- Steps:
  1. Open settings.
  2. Configure backend URL.
  3. Trigger connection test.
- Expected:
  - Connectivity test succeeds.
  - Provider/model metadata loads from `/api/providers` and `/api/models`.

### DSK-003 Backend Unavailable Handling
- Precondition: Backend URL is invalid or service is offline.
- Steps:
  1. Start app with invalid backend endpoint.
  2. Try to load runtime profiles.
- Expected:
  - App shows non-blocking error message.
  - Retry action is available.
  - App does not crash or freeze.

### DSK-004 Runtime Profile CRUD
- Precondition: Backend is reachable.
- Steps:
  1. Create a runtime profile.
  2. Mark it default.
  3. Reload the app.
- Expected:
  - Profile is persisted.
  - Default profile remains selected after reload.

### DSK-005 Repository Context Selection
- Precondition: Local git repository exists.
- Steps:
  1. Select repository path from desktop file picker.
  2. Choose branch and changed files.
- Expected:
  - App captures repository metadata.
  - Invalid path is rejected with clear error.

### DSK-006 Review Submission Happy Path
- Precondition: Valid runtime profile and repository selection.
- Steps:
  1. Submit a review request with at least one code patch.
  2. Observe job progress and result.
- Expected:
  - Job transitions through `queued -> running -> completed`.
  - Findings and summary are displayed.

### DSK-007 Review Failure Handling
- Precondition: Submit malformed payload or backend error.
- Steps:
  1. Trigger a failing request.
  2. Observe UI state.
- Expected:
  - Job marked `failed`.
  - Error reason shown.
  - User can retry with corrected input.

### DSK-008 Feedback Submission
- Precondition: Completed review exists.
- Steps:
  1. Mark one finding as false positive.
  2. Submit reason text.
- Expected:
  - Feedback persists through `/api/feedback`.
  - Feedback appears in review history or audit section.

### DSK-009 Persistence Across Restart
- Precondition: App has existing configured backend/profile.
- Steps:
  1. Close app.
  2. Reopen app.
- Expected:
  - Saved preferences are restored.
  - No data corruption in local app state.

### DSK-010 Security - Secret Redaction
- Precondition: Review result contains potential secret text.
- Steps:
  1. Open results and export/share action.
  2. Inspect output payload.
- Expected:
  - Sensitive credentials/tokens are redacted where policy requires.
  - No plaintext secret leaks in logs/UI export.

### DSK-011 Large Diff Performance
- Precondition: Repository with large diff (e.g., > 1,000 changed lines).
- Steps:
  1. Submit review.
  2. Observe UI responsiveness and completion time.
- Expected:
  - UI remains responsive.
  - Progress indicator updates.
  - Request completes within defined SLO.

### DSK-012 Offline Recovery
- Precondition: App connected to backend.
- Steps:
  1. Disconnect network during review.
  2. Restore network.
- Expected:
  - App reports disconnected state.
  - Queued action retries or guides user to retry safely.

## Automation Priority
1. P0: DSK-001, DSK-002, DSK-003, DSK-006, DSK-007
2. P1: DSK-004, DSK-005, DSK-008, DSK-009
3. P2: DSK-010, DSK-011, DSK-012
