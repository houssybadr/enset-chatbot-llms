"""Appels Ollama et mesures réelles partagés par l'application et l'étude."""
import shutil
import subprocess
import threading
import time
import statistics

import ollama
import psutil


def resources():
    memory = psutil.virtual_memory()
    result = {"cpu_pct": psutil.cpu_percent(interval=0.1), "ram_gb": memory.used / 1024**3,
              "ram_pct": memory.percent}
    if shutil.which("nvidia-smi"):
        try:
            output = subprocess.check_output(
                ["nvidia-smi", "--query-gpu=utilization.gpu,memory.used,memory.total",
                 "--format=csv,noheader,nounits"], timeout=3,
                creationflags=getattr(subprocess, "CREATE_NO_WINDOW", 0), text=True)
            values = output.strip().splitlines()[0].split(",")
            result.update(gpu_pct=float(values[0]), vram_mb=float(values[1]),
                          vram_total_mb=float(values[2]))
        except (OSError, subprocess.SubprocessError, ValueError):
            pass
    return result


def generate(model, messages, options, on_text=None):
    samples, stop = [], threading.Event()

    def sample():
        psutil.cpu_percent()
        while not stop.is_set():
            samples.append(resources())
            stop.wait(0.4)

    worker = threading.Thread(target=sample, daemon=True)
    worker.start()
    start = time.perf_counter()
    first, text, final = None, "", None
    try:
        for chunk in ollama.chat(model=model, messages=messages, options=options, stream=True):
            content = chunk.message.content or ""
            if content:
                if first is None:
                    first = time.perf_counter() - start
                text += content
                if on_text:
                    on_text(text)
            final = chunk
        elapsed = time.perf_counter() - start
    finally:
        stop.set()
        worker.join(timeout=5)
    if final is None or not final.done:
        raise RuntimeError("Le flux Ollama s'est terminé sans réponse complète.")
    tokens, duration = final.eval_count, final.eval_duration
    metrics = {"Modèle": model, "Temps (s)": elapsed, "Tokens": tokens,
               "Tokens/s": tokens / (duration / 1e9) if tokens is not None and duration else None,
               "TTFT (s)": first}
    for key in ("cpu_pct", "ram_gb", "ram_pct", "gpu_pct", "vram_mb"):
        values = [s[key] for s in samples if key in s]
        metrics[key + "_mean"] = statistics.mean(values) if values else None
        metrics[key + "_max"] = max(values) if values else None
    return text, metrics
