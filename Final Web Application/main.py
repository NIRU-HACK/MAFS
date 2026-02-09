import streamlit as st
import time
from queue_manager import InferenceQueue

st.set_page_config(page_title="MAFS Inference Queue", layout="wide")

st.title("🚢 Maritime Ship Detection - FIFO Processing")
st.markdown("""
This application demonstrates a **non-blocking FIFO queue** for heavy inference tasks.
Upload images below, and they will be processed in the background without freezing the UI.
""")

# Initialize the queue in Streamlit's cache to persist across re-runs
# @st.cache_resource ensures the Queue singleton is created only once
@st.cache_resource
def get_queue():
    return InferenceQueue()

q = get_queue()

# --- Sidebar for Status ---
st.sidebar.header("System Status")
st.sidebar.success("Queue Worker: Active 🟢")

# --- Main Upload Section ---
uploaded_file = st.file_uploader("Upload an Image for Inference", type=["jpg", "png", "jpeg"])

if uploaded_file is not None:
    # We use the file name + size as a simple unique key to avoid re-adding the same file multiple times in this demo
    # In a real app, you might want to handle this differently
    file_key = f"{uploaded_file.name}_{uploaded_file.size}"
    
    if 'processing_jobs' not in st.session_state:
        st.session_state.processing_jobs = []

    # Button to submit the job
    if st.button("Add to Processing Queue"):
        # Add job to queue
        job_id = q.add_job(uploaded_file)
        
        # Track this job in the user's session
        st.session_state.processing_jobs.append(job_id)
        st.toast(f"Job {job_id[:8]} added to queue!", icon="📨")

# --- Results Section ---
st.divider()
st.subheader("Processing Queue & Results")

if 'processing_jobs' not in st.session_state or not st.session_state.processing_jobs:
    st.info("No jobs currently in session. Upload an image and add it to the queue.")
else:
    # Create a container for live updates
    status_container = st.container()
    
    # Auto-refresh mechanism (simple polling)
    # If there are any incomplete jobs, we rerun the script periodically
    needs_rerun = False
    
    with status_container:
        # Display jobs in reverse order (newest first)
        for job_id in reversed(st.session_state.processing_jobs):
            job = q.get_job(job_id)
            
            if job:
                with st.expander(f"Job: {job.id[:8]} - {job.status.upper()}", expanded=True):
                    cols = st.columns([1, 3])
                    
                    with cols[0]:
                        if job.status == 'pending':
                            st.warning("⏳ Pending...")
                            needs_rerun = True
                        elif job.status == 'processing':
                            st.info("⚙️ Processing...")
                            st.progress(50)
                            needs_rerun = True
                        elif job.status == 'completed':
                            st.success("✅ Completed")
                        elif job.status == 'failed':
                            st.error("❌ Failed")

                    with cols[1]:
                        if job.status == 'completed':
                            st.write(f"**Result:** {job.result}")
                            # In a real app, you might show the processed image here
                            # st.image(processed_image)
                        else:
                            st.write(f"Original File: {job.data.name}")

    # Rerun script to poll for updates if jobs are active
    if needs_rerun:
        time.sleep(1) # Poll every 1 second
        st.rerun()

# --- Debug/Job Inspection (Optional) ---
# st.write(q.get_all_jobs())
