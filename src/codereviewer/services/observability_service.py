from __future__ import annotations

import os

from fastapi import FastAPI


def _is_enabled(value: str | None) -> bool:
    return (value or "").strip().lower() in {"1", "true", "yes", "on"}


def configure_signoz(app: FastAPI) -> None:
    if not _is_enabled(os.getenv("SIGNOZ_ENABLED")):
        return

    try:
        from opentelemetry import trace
        from opentelemetry.exporter.otlp.proto.http.trace_exporter import OTLPSpanExporter
        from opentelemetry.instrumentation.fastapi import FastAPIInstrumentor
        from opentelemetry.sdk.resources import Resource
        from opentelemetry.sdk.trace import TracerProvider
        from opentelemetry.sdk.trace.export import BatchSpanProcessor
    except Exception:
        # Keep app startup resilient when observability deps are unavailable.
        return

    service_name = os.getenv("SIGNOZ_SERVICE_NAME", "code-reviewer")
    traces_endpoint = os.getenv("SIGNOZ_OTLP_TRACES_ENDPOINT", "http://localhost:4318/v1/traces")

    provider = TracerProvider(resource=Resource.create({"service.name": service_name}))
    provider.add_span_processor(BatchSpanProcessor(OTLPSpanExporter(endpoint=traces_endpoint)))
    trace.set_tracer_provider(provider)

    FastAPIInstrumentor.instrument_app(app, tracer_provider=provider)
