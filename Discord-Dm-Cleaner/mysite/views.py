from django.shortcuts import render
from django.views.decorators.http import require_http_methods
from django.http import JsonResponse
import threading
import sys
import os

sys.path.append(os.path.dirname(os.path.abspath(__file__)))
from cleaner import run_bot

active_bots = {}
log_messages = []

def service(request):
    if request.method == "POST":
        token = request.POST.get("token", "").strip()
        target_id = request.POST.get("target_id", "").strip()

        if not token or not target_id:
            return JsonResponse({"status": "error", "message": "Token and Target ID cannot be empty."})
        elif not target_id.isdigit():
            return JsonResponse({"status": "error", "message": "Target ID must be a number."})
        else:
            try:
                log_messages.clear()
                t = threading.Thread(
                    target=run_bot,
                    args=(token, target_id, active_bots, log_messages),
                    daemon=True
                )
                t.start()
                return JsonResponse({"status": "started"})
            except Exception as e:
                return JsonResponse({"status": "error", "message": str(e)})

    return render(request, "service.html")

def stop(request):
    if request.method == "POST":
        token = request.POST.get("token", "").strip()
        if token in active_bots:
            try:
                client = active_bots[token]
                import asyncio
                future = asyncio.run_coroutine_threadsafe(client.close(), client.loop)
                future.result(timeout=5)
                del active_bots[token]
                log_messages.append("Service stopped by user.")
                return JsonResponse({"status": "stopped"})
            except Exception as e:
                return JsonResponse({"status": "error", "message": str(e)})
        return JsonResponse({"status": "not_found"})
    return JsonResponse({"status": "error"})

def get_logs(request):
    return JsonResponse({"logs": list(log_messages)})

def index(request):
    return render(request, "index.html")

def howtowork(request):
    return render(request, "howtowork.html")