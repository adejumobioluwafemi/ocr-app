import streamlit as st
import requests
from PIL import Image
import io
import time
import os

# Page configuration
st.set_page_config(
    page_title="OCR MVP",
    page_icon="🔍",
    layout="centered"
)

# Custom CSS for better styling
st.markdown("""
<style>
    .main-header {
        font-size: 2.5rem;
        color: #1f77b4;
        text-align: center;
        margin-bottom: 2rem;
    }
    .success-box {
        background-color: #d4edda;
        border: 1px solid #c3e6cb;
        border-radius: 5px;
        padding: 20px;
        margin: 10px 0;
    }
    .error-box {
        background-color: #f8d7da;
        border: 1px solid #f5c6cb;
        border-radius: 5px;
        padding: 20px;
        margin: 10px 0;
    }
    .info-box {
        background-color: #d1ecf1;
        border: 1px solid #bee5eb;
        border-radius: 5px;
        padding: 15px;
        margin: 10px 0;
    }
</style>
""", unsafe_allow_html=True)

def get_backend_url():
    """Get backend URL from environment variable or use default"""
    return os.getenv('BACKEND_URL', 'http://localhost:8000/api/v1')

def test_backend_connection(backend_url):
    """Test if backend is reachable"""
    try:
        response = requests.get(f"{backend_url}/health", timeout=5)
        return response.status_code == 200, response.json() if response.status_code == 200 else None
    except Exception:
        return False, None

def main():
    # Header
    st.markdown('<h1 class="main-header">🔍 OCR Text Extractor</h1>', unsafe_allow_html=True)
    
    # Sidebar
    with st.sidebar:
        st.header("Configuration")
        
        # Backend URL configuration
        default_backend_url = get_backend_url()
        backend_url = st.text_input(
            "Backend URL",
            value=default_backend_url,
            help="URL of your FastAPI backend (e.g., http://localhost:8000)"
        )
        
        # Test connection
        st.markdown("---")
        st.subheader("Connection Status")
        
        if st.button("Test Connection"):
            with st.spinner("Testing connection..."):
                is_connected, health_data = test_backend_connection(backend_url)
                
                if is_connected:
                    st.success("✅ Backend connected successfully!")
                    if health_data:
                        st.write(f"Status: {health_data.get('status', 'Unknown')}")
                        st.write(f"OCR Engine: {health_data.get('ocr_engine', 'Unknown')}")
                else:
                    st.error("❌ Cannot connect to backend")
                    st.write("Please check:")
                    st.write("1. Backend server is running")
                    st.write("2. URL is correct")
                    st.write("3. No firewall blocking the connection")
        
        st.markdown("---")
        st.markdown("### About")
        st.markdown("""
        This MVP extracts text from images using EasyOCR.
        
        **Supported formats:**
        - PNG, JPG, JPEG
        
        **Tips:**
        - Use clear, high-contrast images
        - Ensure text is legible
        - Avoid blurry or rotated text
        """)
    
    # Main content
    col1, col2 = st.columns([1, 1])
    
    with col1:
        st.subheader("Upload Image")
        
        # File uploader
        uploaded_file = st.file_uploader(
            "Choose an image file",
            type=['png', 'jpg', 'jpeg'],
            help="Select a PNG, JPG, or JPEG image containing text"
        )
        
        if uploaded_file is not None:
            # Display uploaded image
            image = Image.open(uploaded_file)
            st.image(image, caption="Uploaded Image", use_container_width=True)
            
            # Image information
            st.markdown('<div class="info-box">', unsafe_allow_html=True)
            st.write(f"**Image Info:**")
            st.write(f"- Format: {uploaded_file.type}")
            st.write(f"- Size: {image.size[0]} x {image.size[1]} pixels")
            st.write(f"- File size: {len(uploaded_file.getvalue()) // 1024} KB")
            st.markdown('</div>', unsafe_allow_html=True)
    
    with col2:
        st.subheader("Extracted Text")
        
        if uploaded_file is not None:
            # First test connection
            is_connected, _ = test_backend_connection(backend_url)
            
            if not is_connected:
                st.markdown('<div class="error-box">', unsafe_allow_html=True)
                st.error("🔌 Backend Connection Required")
                st.write("Please ensure:")
                st.write(f"1. Backend is running at: `{backend_url}`")
                st.write("2. Click 'Test Connection' in sidebar to verify")
                st.write("3. Check the backend URL is correct")
                st.markdown('</div>', unsafe_allow_html=True)
                return
            
            # Process button
            if st.button("Extract Text", type="primary", use_container_width=True):
                with st.spinner("Processing image..."):
                    try:
                        # Prepare the file for upload
                        files = {"image": (uploaded_file.name, uploaded_file.getvalue(), uploaded_file.type)}
                        
                        # Make API request with timeout
                        start_time = time.time()
                        response = requests.post(
                            f"{backend_url}/predict",
                            files=files,
                            timeout=30
                        )
                        processing_time = time.time() - start_time
                        
                        if response.status_code == 200:
                            result = response.json()
                            
                            if result.get("success"):
                                # Success case
                                st.markdown('<div class="success-box">', unsafe_allow_html=True)
                                st.success("✅ Text extracted successfully!")
                                
                                # Display extracted text
                                st.text_area(
                                    "Extracted Text",
                                    result["text"],
                                    height=200,
                                    key="extracted_text"
                                )
                                
                                # Display metadata
                                st.write("**Details:**")
                                st.write(f"- Confidence: {result.get('confidence', 'N/A')}")
                                st.write(f"- Words detected: {result.get('word_count', 0)}")
                                st.write(f"- Processing time: {processing_time:.2f}s")
                                st.write(f"- Image size: {result.get('image_size', 'N/A')}")
                                
                                st.markdown('</div>', unsafe_allow_html=True)
                                
                            else:
                                # OCR processing failed
                                st.markdown('<div class="error-box">', unsafe_allow_html=True)
                                st.error("❌ Failed to extract text")
                                st.write(f"Error: {result.get('error', 'Unknown error')}")
                                st.markdown('</div>', unsafe_allow_html=True)
                                
                        elif response.status_code == 404:
                            st.markdown('<div class="error-box">', unsafe_allow_html=True)
                            st.error("🔍 Endpoint Not Found (404)")
                            st.write(f"The endpoint `/predict` was not found at `{backend_url}`")
                            st.write("Please check:")
                            st.write("1. Backend is running the correct version")
                            st.write("2. API routes are properly configured")
                            st.write("3. Try accessing the backend directly:")
                            st.code(f"curl -X GET {backend_url}/health")
                            st.markdown('</div>', unsafe_allow_html=True)
                            
                        else:
                            # API error
                            try:
                                error_detail = response.json().get('detail', 'Unknown error')
                            except:
                                error_detail = response.text
                                
                            st.markdown('<div class="error-box">', unsafe_allow_html=True)
                            st.error(f"❌ API Error (Status: {response.status_code})")
                            st.write(f"Detail: {error_detail}")
                            st.markdown('</div>', unsafe_allow_html=True)
                            
                    except requests.exceptions.ConnectionError:
                        st.markdown('<div class="error-box">', unsafe_allow_html=True)
                        st.error("🔌 Connection Error")
                        st.write(f"Cannot connect to backend at: `{backend_url}`")
                        st.write("Please check:")
                        st.write("1. The backend server is running")
                        st.write("2. The backend URL is correct")
                        st.write("3. No firewall blocking the connection")
                        st.markdown('</div>', unsafe_allow_html=True)
                        
                    except requests.exceptions.Timeout:
                        st.markdown('<div class="error-box">', unsafe_allow_html=True)
                        st.error("⏰ Request Timeout")
                        st.write("The request took too long. Try with a smaller image.")
                        st.markdown('</div>', unsafe_allow_html=True)
                        
                    except Exception as e:
                        st.markdown('<div class="error-box">', unsafe_allow_html=True)
                        st.error("💥 Unexpected Error")
                        st.write(f"An unexpected error occurred: {str(e)}")
                        st.markdown('</div>', unsafe_allow_html=True)
        
        else:
            # No file uploaded
            st.info("👈 Upload an image to extract text")
            
            # Connection status
            is_connected, health_data = test_backend_connection(backend_url)
            if is_connected:
                st.success("✅ Backend is connected and ready")
            else:
                st.warning("⚠️ Backend not connected - check configuration")

    st.markdown("---")
    st.markdown(
        "**MVP Version 1.0** | Built with Streamlit & FastAPI"
    )

if __name__ == "__main__":
    main()