from __future__ import annotations

import os

try:
    import opik
except Exception:  # pragma: no cover
    opik = None


class OpikTracer:
    def __init__(self, enabled: bool, project_name: str, use_local: bool = False) -> None:
        self.enabled = False
        self.project_name = project_name
        self.client = None

        if not enabled:
            return

        if opik is None:
            print("Warning: Opik is not installed. Tracing is disabled.")
            return

        api_key = os.getenv("OPIK_API_KEY") or os.getenv("COMET_API_KEY")
        if not api_key and not use_local:
            print(
                "Warning: OPIK_API_KEY/COMET_API_KEY not found. "
                "Tracing is disabled. Set API key or use --opik_use_local."
            )
            return

        try:
            if use_local:
                opik.configure(use_local=True)
            self.client = opik.Opik(project_name=project_name, _show_misconfiguration_message=False)
            self.enabled = True
            print(f"Opik tracing enabled (project={project_name})")
        except Exception as e:
            print(f"Warning: cannot initialize Opik tracer ({e}). Tracing disabled.")

    def start_trace(self, name: str, input_data: dict, metadata: dict) -> object | None:
        if not self.enabled or self.client is None:
            return None
        try:
            return self.client.trace(name=name, input=input_data, metadata=metadata, project_name=self.project_name)
        except Exception as e:
            print(f"Warning: Opik start_trace failed ({e}). Disabling Opik for this session.")
            self.enabled = False
            return None

    def start_span(self, trace_obj: object | None, name: str, span_type: str, input_data: dict, metadata: dict) -> object | None:
        if not self.enabled or self.client is None or trace_obj is None:
            return None
        try:
            trace_id = getattr(trace_obj, "id", None)
            if not trace_id:
                return None
            return self.client.span(
                trace_id=trace_id,
                name=name,
                type=span_type,
                input=input_data,
                metadata=metadata,
                project_name=self.project_name,
            )
        except Exception as e:
            print(f"Warning: Opik start_span failed ({e}). Disabling Opik for this session.")
            self.enabled = False
            return None

    def update(self, obj: object | None, output_data: dict | None = None, metadata: dict | None = None) -> None:
        if obj is None:
            return
        try:
            kwargs = {}
            if output_data is not None:
                kwargs["output"] = output_data
            if metadata is not None:
                kwargs["metadata"] = metadata
            if kwargs:
                obj.update(**kwargs)
        except Exception as e:
            print(f"Warning: Opik update failed ({e})")

    def end(self, obj: object | None) -> None:
        if obj is None:
            return
        try:
            obj.end()
        except Exception as e:
            print(f"Warning: Opik end failed ({e})")
