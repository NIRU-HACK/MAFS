import queue
import threading
import time
import uuid
import io
import numpy as np
import cv2
from PIL import Image
from dataclasses import dataclass
from typing import Any, Dict, Optional
from ultralytics import YOLO
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
        
        # Initialize YOLOv11m
        print("Initializing YOLOv11m model...")
        try:
            # We use yolo11m.pt as specified in the plan. 
            # Ultralytics will auto-download it if not found.
            self.model = YOLO("yolo11m.pt") 
        except Exception as e:
            print(f"Warning: Could not load YOLOv11m: {e}")
            self.model = None

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
                            # Assume channel 0 is VV
                            gray_img = img_array[:,:,0]
                        elif band == 'VH':
                            # Assume channel 1 is VH
                            gray_img = img_array[:,:,1]
                        else:
                            # Default to average/grayscale
                            gray_img = cv2.cvtColor(img_array, cv2.COLOR_RGB2GRAY)
                        
                        # --- LAND MASKING ---
                        final_masked, mask, steps = land_masking.process_image(gray_img, return_steps=True)
                        
                        # --- YOLO INFERENCE ---
                        detections = []
                        result_img_with_boxes = Image.fromarray(final_masked).convert("RGB")
                        
                        if self.model:
                            # Run inference on the masked image
                            # Note: YOLO expects a 3-channel image typically, so we convert back
                            inference_img = cv2.cvtColor(final_masked, cv2.COLOR_GRAY2RGB)
                            results = self.model.predict(inference_img, conf=0.25)
                            
                            if results:
                                res = results[0]
                                # Get detection summary
                                for box in res.boxes:
                                    detections.append({
                                        "box": box.xyxy[0].tolist(), # [x1, y1, x2, y2]
                                        "conf": float(box.conf[0]),
                                        "cls": int(box.cls[0]),
                                        "name": res.names[int(box.cls[0])]
                                    })
                                
                                # Generate plotted image
                                plotted_bgr = res.plot()
                                result_img_with_boxes = Image.fromarray(cv2.cvtColor(plotted_bgr, cv2.COLOR_BGR2RGB))
                        
                        # Store result
                        job.result = {
                            "message": f"Processed successfully using {band} band. Found {len(detections)} vessels.",
                            "processed_image": Image.fromarray(final_masked),
                            "detection_image": result_img_with_boxes,
                            "detections": detections,
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
