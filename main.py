from fastapi import FastAPI, Query
import psutil
from typing import List
import time

app = FastAPI()

# check is the process running
def process_exists(process_name:str) -> bool:
    for proc in psutil.process_iter():
        try:
            if process_name.lower() in proc.name().lower():
                return True
        except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
            pass
    return False

# check os disk usage
def disk_usage() -> dict:
    disk = psutil.disk_usage('/')
    return {
        "total": disk.total,
        "used": disk.used,
        "free": disk.free,
        "percent": disk.percent,
    }

# check cpu usage, list all cores
def cpu_usage() -> dict:
    return {
        "cpu": psutil.cpu_percent(),
        "cores": psutil.cpu_percent(percpu=True),
        "total": psutil.cpu_count(),
    }

# check memory usage
def memory_usage() -> dict:
    return {
        "total": psutil.virtual_memory().total,
        "available": psutil.virtual_memory().available,
        "percent": psutil.virtual_memory().percent,
        "used": psutil.virtual_memory().used,
        "free": psutil.virtual_memory().free,
        "used_gb": psutil.virtual_memory().used / 1024 / 1024 / 1024,
        "free_gb": psutil.virtual_memory().free / 1024 / 1024 / 1024,
    }

# get the os uptime in hours
def uptime_boot() -> dict:
    return {
        "uptime": time.time() - psutil.boot_time(),
        "uptime_readable": time.strftime('%H:%M:%S', time.gmtime(time.time() - psutil.boot_time()))
    }

@app.get("/disk")
async def disk():
    return disk_usage()

@app.get("/cpu")
async def cpu():
    return cpu_usage()

# check system up time, covert to readable format
@app.get("/uptime")
async def uptime():
    return uptime_boot()

# return memory usage
@app.get("/memory")
async def memory():
    return memory_usage()

# overall system health
@app.get("/system")
async def system():
    return {
        "disk": disk_usage(),
        "cpu": cpu_usage(),
        "memory": memory_usage(),
        "uptime": uptime_boot()
    }

#take query input of arrays of process name
@app.get("/health")
async def health(q: List[str] = Query(max_length=20)) -> List[dict]:
    return_array = []
    
   # loop the array of process name
    for i in q:
        if process_exists(i):
            return_array.append({i: "running"})
        else:
            return_array.append({i: "failed"})
        
    return return_array

