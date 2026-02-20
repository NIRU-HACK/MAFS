import streamlit as st
import time
from queue_manager import InferenceQueue

st.set_page_config(page_title="MAFS Inference Queue", layout="wide")

st.title("🚢 Maritime Ship Detection - Land Masking & Band Selection")
st.markdown("""
This application demonstrates **VV/VH Band Selection** and **Land Masking Visualization** using a non-blocking FIFO queue.
""")

# Initialize the queue in Streamlit's cache to persist across re-runs
@st.cache_resource
def get_queue():
    return InferenceQueue()

q = get_queue()

# --- Sidebar for Status & Config ---
st.sidebar.header("Configuration")
band_selection = st.sidebar.radio("SAR Band Selection", ["VV", "VH", "Dual (Grayscale)"])
st.sidebar.divider()
st.sidebar.header("System Status")
st.sidebar.success("Queue Worker: Active 🟢")

# --- Main Upload Section ---
uploaded_file = st.file_uploader("Upload an Image for Inference", type=["jpg", "png", "jpeg"])

if uploaded_file is not None:
    # Display the original image
    st.subheader("Original Image")
    st.image(uploaded_file, caption="Input Data", width=400)
    
    if 'processing_jobs' not in st.session_state:
        st.session_state.processing_jobs = []

    # Button to submit the job
    if st.button("Add to Processing Queue"):
        # Safely read file bytes to pass to the thread
        uploaded_file.seek(0)
        file_bytes = uploaded_file.read()
        
        # Add job to queue with selected band
        params = {"band": band_selection.split()[0]}
        job_id = q.add_job(file_bytes, params)
        
        # Track this job in the user's session
        st.session_state.processing_jobs.append(job_id)
        st.toast(f"Job {job_id[:8]} added to queue (Band: {params['band']})!", icon="📨")

# --- Results Section ---
st.divider()
st.subheader("Processing Queue & Results")

if 'processing_jobs' not in st.session_state or not st.session_state.processing_jobs:
    st.info("No jobs currently in session. Upload an image and add it to the queue.")
else:
    # Create a container for live updates
    status_container = st.container()
    
    # Auto-refresh mechanism
    needs_rerun = False
    
    with status_container:
        # Display jobs in reverse order (newest first)
        for job_id in reversed(st.session_state.processing_jobs):
            job = q.get_job(job_id)
            
            if job:
                with st.expander(f"Job: {job.id[:8]} - {job.status.upper()} ({job.params.get('band')})", expanded=True):
                    if job.status == 'pending':
                        st.warning("⏳ Pending...")
                        needs_rerun = True
                    elif job.status == 'processing':
                        st.info("⚙️ Processing (Applying Land Masking & Band Selection)...")
                        st.progress(50)
                        needs_rerun = True
                    elif job.status == 'completed':
                        st.success("✅ Completed")
                        result = job.result
                        
                        st.write(f"**Status:** {result['message']}")
                        
                        cols = st.columns([1, 1])
                        with cols[0]:
                            st.image(result['processed_image'], caption="Final Masked Image", use_container_width=True)
                        with cols[1]:
                            st.image(result['mask'], caption="Land Mask", use_container_width=True)
                        
                        # Visualization of steps
                        if "steps" in result:
                            st.divider()
                            st.subheader("Land Masking Visualization")
                            step_names = list(result['steps'].keys())
                            tabs = st.tabs(step_names)
                            for i, name in enumerate(step_names):
                                with tabs[i]:
                                    st.image(result['steps'][name], caption=f"Step: {name}", use_container_width=True)

                    elif job.status == 'failed':
                        st.error("❌ Failed")
                        st.write(f"Error: {job.result}")

    # Rerun script to poll for updates if jobs are active
    if needs_rerun:
        time.sleep(1) # Poll every 1 second
        st.rerun()
