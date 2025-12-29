import streamlit as st
import requests
import base64
from PIL import Image
import io
import re

# Page configuration
st.set_page_config(
    page_title="Vehicle Damage Detector",
    page_icon="🚗",
    layout="wide"
)

# Custom CSS for better styling
st.markdown("""
    <style>
    .main {
        background: linear-gradient(to bottom right, #f0f9ff, #e0e7ff);
    }
    .stButton>button {
        width: 100%;
        background: linear-gradient(to right, #2563eb, #4f46e5);
        color: white;
        font-weight: bold;
        padding: 0.75rem;
        border-radius: 0.5rem;
        border: none;
    }
    .stButton>button:hover {
        background: linear-gradient(to right, #1d4ed8, #4338ca);
    }
    .damage-section {
        background-color: #f0fdf4;
        border-left: 4px solid #22c55e;
        padding: 1rem 1.5rem;
        margin: 1rem 0;
        border-radius: 0.5rem;
    }
    .error-box {
        background-color: #fef2f2;
        border: 2px solid #fca5a5;
        border-radius: 0.5rem;
        padding: 1rem;
        margin-top: 1rem;
    }
    .section-title {
        color: #166534;
        font-weight: bold;
        font-size: 1.2rem;
        margin-bottom: 0.5rem;
    }
    .damage-item {
        margin-left: 1.5rem;
        margin-bottom: 0.5rem;
    }
    </style>
""", unsafe_allow_html=True)

# Title and description
st.markdown("# 🚗 Vehicle Damage Detector")
st.markdown("### Powered by Groq AI - Fast & Accurate Analysis")
st.markdown("---")

# Initialize session state
if 'analysis_result' not in st.session_state:
    st.session_state.analysis_result = None
if 'uploaded_image' not in st.session_state:
    st.session_state.uploaded_image = None

# Sidebar for API key and instructions
with st.sidebar:
    st.markdown("## ⚙️ Configuration")
    api_key = st.text_input(
        "Groq API Key",
        type="password",
        placeholder="Enter your API key (gsk_...)",
        help="Get your free API key from console.groq.com"
    )
    
    st.markdown("---")
    st.markdown("## 📋 How to Use")
    st.markdown("""
    1. **Get API Key**: Sign up at [console.groq.com](https://console.groq.com)
    2. **Enter Key**: Paste your API key above
    3. **Upload Image**: Choose a vehicle photo
    4. **Analyze**: Click the button to detect damage
    5. **Review**: Check the detailed report
    """)
    
    st.markdown("---")
    st.markdown("## 🎯 Features")
    st.markdown("""
    - ✅ Damage detection
    - ✅ Severity assessment
    - ✅ Location identification
    - ✅ Repair recommendations
    - ✅ Cost estimates
    - ✅ Safety concerns
    """)

# Main content area
col1, col2 = st.columns([1, 1])

with col1:
    st.markdown("### 📤 Upload Vehicle Image")
    uploaded_file = st.file_uploader(
        "Choose an image...",
        type=['png', 'jpg', 'jpeg'],
        help="Upload a clear photo of the vehicle showing any damage"
    )
    
    if uploaded_file is not None:
        st.session_state.uploaded_image = uploaded_file
        image = Image.open(uploaded_file)
        st.image(image, caption="Uploaded Image", use_container_width=True)

with col2:
    st.markdown("### 🔍 Analysis")
    
    if st.session_state.uploaded_image is not None:
        st.info("✅ Image ready for analysis")
    else:
        st.warning("⚠️ Please upload an image to begin")
    
    if not api_key:
        st.warning("⚠️ Please enter your Groq API key in the sidebar")

# Function to convert image to base64
def image_to_base64(image_file):
    """Convert uploaded image to base64 string with compression"""
    image_file.seek(0)
    
    # Open and resize image if too large
    img = Image.open(image_file)
    
    # Convert RGBA to RGB if necessary
    if img.mode == 'RGBA':
        img = img.convert('RGB')
    
    # Resize if image is too large (max 2048x2048)
    max_size = 2048
    if img.width > max_size or img.height > max_size:
        img.thumbnail((max_size, max_size), Image.Resampling.LANCZOS)
    
    # Save to bytes
    buffered = io.BytesIO()
    img.save(buffered, format="JPEG", quality=85)
    img_bytes = buffered.getvalue()
    
    return base64.b64encode(img_bytes).decode('utf-8')

# Function to parse and format the analysis result
def format_damage_report(text):
    """Parse the AI response and format it beautifully"""
    
    # Split by numbered sections
    sections = re.split(r'\n\d+\.\s+\*\*', text)
    
    if len(sections) > 1:
        # Format each section
        for i, section in enumerate(sections[1:], 1):
            # Extract section title and content
            parts = section.split('**:', 1)
            if len(parts) == 2:
                title = parts[0].strip()
                content = parts[1].strip()
                
                # Create expandable section
                with st.expander(f"**{i}. {title}**", expanded=True):
                    # Split content by lines and format
                    lines = content.split('\n')
                    for line in lines:
                        line = line.strip()
                        if line.startswith('-'):
                            st.markdown(f"• {line[1:].strip()}")
                        elif line:
                            st.markdown(line)
    else:
        # If parsing fails, display as is with better formatting
        st.markdown(text)

# Function to analyze image with Groq
def analyze_vehicle_damage(image_file, api_key):
    """Send image to Groq API for damage analysis"""
    
    # Convert image to base64
    base64_image = image_to_base64(image_file)
    
    # Prepare the API request
    url = "https://api.groq.com/openai/v1/chat/completions"
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json"
    }
    
    payload = {
        "model": "meta-llama/llama-4-scout-17b-16e-instruct",
        "messages": [
            {
                "role": "user",
                "content": [
                    {
                        "type": "text",
                        "text": """You are an expert vehicle damage assessor. Analyze this vehicle image carefully and provide a detailed damage report in the following structured format:

1. **Damage Detection**:
- List each damage with specific measurements if visible
- Include: scratches, dents, cracks, broken parts, paint damage, etc.

2. **Location**:
- Specify exact location of each damage
- Use terms like: front bumper, rear door, hood, fender, quarter panel, etc.

3. **Severity**:
- Rate each damage as: Minor, Moderate, or Severe
- Explain the severity rating

4. **Repair Recommendations**:
- Suggest specific repair methods for each damage
- Include techniques like: replacement, buffing, repainting, PDR, etc.

5. **Estimated Cost Range**:
- Provide cost estimates in USD for each repair
- Include total estimated cost range

6. **Safety Concerns**:
- Identify any damage that affects vehicle safety
- Mention visibility, structural, or operational concerns

Be thorough and specific. If no damage is visible, state that clearly in section 1."""
                    },
                    {
                        "type": "image_url",
                        "image_url": {
                            "url": f"data:image/jpeg;base64,{base64_image}"
                        }
                    }
                ]
            }
        ],
        "temperature": 0.3,
        "max_tokens": 2500
    }
    
    try:
        response = requests.post(url, headers=headers, json=payload, timeout=60)
        
        # Check for specific error codes
        if response.status_code == 400:
            error_data = response.json()
            error_message = error_data.get('error', {}).get('message', 'Bad Request')
            return f"Error 400: {error_message}. This might be due to:\n- Invalid API key format\n- Image too large or unsupported format\n- Model not available in your region\n\nPlease check your API key and try with a smaller image."
        elif response.status_code == 401:
            return "Error 401: Invalid API key. Please check your Groq API key."
        elif response.status_code == 429:
            return "Error 429: Rate limit exceeded. Please wait a moment and try again."
        
        response.raise_for_status()
        data = response.json()
        
        if 'choices' in data and len(data['choices']) > 0:
            return data['choices'][0]['message']['content']
        else:
            return "Error: No response from API"
            
    except requests.exceptions.Timeout:
        return "Error: Request timed out. Please try again with a smaller image."
    except requests.exceptions.RequestException as e:
        return f"Error: {str(e)}\n\nTroubleshooting tips:\n- Verify your API key is correct\n- Try a smaller image (under 5MB)\n- Check your internet connection"

# Analyze button
st.markdown("---")
if st.button("🔍 Detect Vehicle Damage", type="primary"):
    if not api_key:
        st.error("❌ Please enter your Groq API key in the sidebar")
    elif st.session_state.uploaded_image is None:
        st.error("❌ Please upload a vehicle image first")
    else:
        with st.spinner("🔄 Analyzing vehicle damage... Please wait..."):
            result = analyze_vehicle_damage(st.session_state.uploaded_image, api_key)
            st.session_state.analysis_result = result

# Display analysis results
if st.session_state.analysis_result:
    st.markdown("---")
    st.markdown("## 📊 Damage Assessment Report")
    
    if "Error:" in st.session_state.analysis_result:
        st.error(f"❌ {st.session_state.analysis_result}")
    else:
        # Format and display the report beautifully
        format_damage_report(st.session_state.analysis_result)
        
        st.markdown("---")
        
        # Download options
        col1, col2 = st.columns(2)
        with col1:
            st.download_button(
                label="📥 Download Full Report (TXT)",
                data=st.session_state.analysis_result,
                file_name="vehicle_damage_report.txt",
                mime="text/plain",
                use_container_width=True
            )
        
        with col2:
            # Create a formatted version for download
            formatted_text = f"""
VEHICLE DAMAGE ASSESSMENT REPORT
Generated: {st.session_state.get('timestamp', 'N/A')}
═══════════════════════════════════════════════

{st.session_state.analysis_result}

═══════════════════════════════════════════════
Report generated by AI-powered Vehicle Damage Detector
            """
            st.download_button(
                label="📄 Download Formatted Report",
                data=formatted_text,
                file_name="damage_report_formatted.txt",
                mime="text/plain",
                use_container_width=True
            )

# Footer
st.markdown("---")
st.markdown("""
<div style='text-align: center; color: #6b7280; padding: 2rem;'>
    <p>Built with ❤️ using Streamlit and Groq AI</p>
    <p style='font-size: 0.875rem;'>⚡ Ultra-fast inference powered by Groq's LPU technology</p>
</div>
""", unsafe_allow_html=True)