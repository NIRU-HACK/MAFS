import queue
import threading
import time
import uuid
from dataclasses import dataclass
from typing import Any, Dict, Optional

# Define a simple job structure
@dataclass
class Job:
    id: str
    data: Any  # The image or path to process
    status: str  # 'pending', 'processing', 'completed', 'failed'
    result: Optional[Any] = None
    created_at: float = 0.0

class InferenceQueue:
    def __init__(self):
        self._queue = queue.Queue()
        self._results: Dict[str, Job] = {}
        self._stop_event = threading.Event()
        self._worker_thread = threading.Thread(target=self._worker_process, daemon=True)
        self._worker_thread.start()

    def add_job(self, data: Any) -> str:
        """Add a job to the queue and return its ID."""
        job_id = str(uuid.uuid4())
        job = Job(id=job_id, data=data, status='pending', created_at=time.time())
        self._results[job_id] = job
        self._queue.put(job_id)
        return job_id

    def get_job(self, job_id: str) -> Optional[Job]:
        """Get the status and result of a job."""
        return self._results.get(job_id)

    def get_all_jobs(self) -> Dict[str, Job]:
        """Return all jobs."""
        return self._results

    def _worker_process(self):
        """Background worker that processes jobs from the queue."""
        print("Worker thread started...")
        while not self._stop_event.is_set():
            try:
                # Get a job ID from the queue (blocking with timeout to allow stopping)
                job_id = self._queue.get(timeout=1)
                
                if job_id in self._results:
                    job = self._results[job_id]
                    job.status = 'processing'
                    
                    # --- SIMULATE INFERENCE HERE ---
                    # In a real app, you would load your YOLO model and predict
                    # e.g., result = model(job.data)
                    print(f"Processing job {job_id}...")
                    time.sleep(3)  # Simulate heavy processing (3 seconds)
                    
                    # Create a dummy result
                    job.result = f"Detected 3 ships in {job.data.name if hasattr(job.data, 'name') else 'image'}"
                    job.status = 'completed'
                    print(f"Finished job {job_id}")
                    # -------------------------------
                
                self._queue.task_done()
                
            except queue.Empty:
                continue
            except Exception as e:
                print(f"Error processing job: {e}")
                if 'job' in locals():
                    job.status = 'failed'
                    job.result = str(e)

    def stop(self):
        """Stop the worker thread gracefully."""
        self._stop_event.set()
        self._worker_thread.join()
