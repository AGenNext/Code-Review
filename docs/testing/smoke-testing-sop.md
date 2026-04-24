# Smoke Testing SOP

## Objective
Quickly confirm the deployed service is alive and critical endpoints respond.

## When to run
- Immediately after deploy
- After rollback
- During incident recovery verification

## Procedure
1. Health endpoint
```bash
curl -i https://<domain>/healthz
```
Expected: `HTTP 200` and JSON status payload.

2. Landing/UI route
```bash
curl -i https://<domain>/
curl -i https://<domain>/app
```
Expected: `HTTP 200`.

3. Basic API reachability
```bash
curl -i https://<domain>/api/reviews
```
Expected: non-5xx response (auth behavior may vary by environment).

## Pass/Fail criteria
- Health endpoint passes.
- Core routes are reachable.
- No crash-looping container/process.

## Incident note
If smoke fails, halt rollout and trigger rollback SOP.
