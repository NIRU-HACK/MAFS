import queue
import threading
import time
import uuid
import io
import numpy as np
from PIL import Image
from dataclasses import dataclass
from typing import Any, Dict, Optional
import land_masking

# Define a simple job structure
@dataclass
class Job:
    id: str
    data: Any  # The image bytes
    status: str  # 'pending', 'processing', 'completed', 'failed'
    params: Dict[str, Any] # Parameters like 'band'
    result: Optional[Any] = None
    created_at: float = 0.0

class InferenceQueue:
    def __init__(self):
        self._queue = queue.Queue()
        self._results: Dict[str, Job] = {}
        self._stop_event = threading.Event()
        self._worker_thread = threading.Thread(target=self._worker_process, daemon=True)
        self._worker_thread.start()

    def add_job(self, data: Any, params: Dict[str, Any]) -> str:
        """Add a job to the queue and return its ID."""
        job_id = str(uuid.uuid4())
        job = Job(id=job_id, data=data, status='pending', params=params, created_at=time.time())
        self._results[job_id] = job
        self._queue.put(job_id)
        return job_id

    def get_job(self, job_id: str) -> Optional[Job]:
        """Get the status and result of a job."""
        return self._results.get(job_id)

    def _worker_process(self):
        """Background worker that processes jobs from the queue."""
        print("Worker thread started...")
        while not self._stop_event.is_set():
            try:
                job_id = self._queue.get(timeout=1)
                
                if job_id in self._results:
                    job = self._results[job_id]
                    job.status = 'processing'
                    
                    try:
                        print(f"Processing job {job_id} with params {job.params}...")
                        
                        # Load image from bytes
                        image = Image.open(io.BytesIO(job.data)).convert("RGB")
                        img_array = np.array(image)
                        
                        # --- BAND SELECTION ---
                        band = job.params.get('band', 'VV')
                        if band == 'VV':
                            # Assume channel 0 is VV (Red in common RGB representations of SAR)
                            gray_img = img_array[:,:,0]
                        elif band == 'VH':
                            # Assume channel 1 is VH (Green)
                            gray_img = img_array[:,:,1]
                        else:
                            # Default to average/grayscale
                            gray_img = cv2.cvtColor(img_array, cv2.COLOR_RGB2GRAY)
                        
                        # --- LAND MASKING ---
                        final_masked, mask, steps = land_masking.process_image(gray_img, return_steps=True)
                        
                        # Simulate some heavy processing
                        time.sleep(1) 
                        
                        # Store result
                        job.result = {
                            "message": f"Processed successfully using {band} band.",
                            "processed_image": Image.fromarray(final_masked),
                            "mask": Image.fromarray(mask),
                            "steps": {name: Image.fromarray(img) for name, img in steps.items()},
                            "original_size": image.size
                        }
                        job.status = 'completed'
                        print(f"Finished job {job_id}")
                        
                    except Exception as e:
                        print(f"Error processing job {job_id}: {e}")
                        import traceback
                        traceback.print_exc()
                        job.status = 'failed'
                        job.result = str(e)
                
                self._queue.task_done()
                
            except queue.Empty:
                continue
            except Exception as e:
                print(f"Worker Error: {e}")

    def stop(self):
        """Stop the worker thread gracefully."""
        self._stop_event.set()
        self._worker_thread.join()
