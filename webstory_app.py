"""Streamlit application for News Webstory Generator."""

import os
import streamlit as st
import uuid
import json
from datetime import datetime
from dotenv import load_dotenv

from image_generator import InfographicGenerator
from storage import StorageManager

# Load environment variables
load_dotenv()

# Initialize components
image_generator = InfographicGenerator()
storage_manager = StorageManager()

# Set up the Streamlit page
st.set_page_config(page_title="News Webstory Generator", layout="wide")

# App title and description
st.title("News Webstory Generator")
st.markdown(
    """Create mobile-friendly webstories from news articles. 
    Enter your article title and bullet points below to generate a webstory!"""
)

# Initialize session state for storing generated images and webstory data
if "webstory_images" not in st.session_state:
    st.session_state.webstory_images = []

if "webstory_html_url" not in st.session_state:
    st.session_state.webstory_html_url = ""

if "webstory_id" not in st.session_state:
    st.session_state.webstory_id = str(uuid.uuid4())

# Create form for user input
with st.form("webstory_form"):
    # Article title input
    article_title = st.text_input("News Article Title", help="Enter the title of your news article")
    
    # Bullet points input
    st.subheader("Summary Bullet Points")
    st.markdown("Enter up to 5 bullet points summarizing the article")
    
    bullet_points = []
    for i in range(5):
        bullet = st.text_area(f"Bullet Point {i+1}", key=f"bullet_{i}", height=100)
        if bullet.strip():
            bullet_points.append(bullet.strip())
    
    # Submit button
    submitted = st.form_submit_button("Generate Webstory")

# Process form submission
if submitted:
    if not article_title:
        st.error("Please enter an article title")
    elif not bullet_points:
        st.error("Please enter at least one bullet point")
    else:
        with st.spinner("Generating webstory images..."):
            try:
                # Clear previous images
                st.session_state.webstory_images = []
                
                # Generate title image
                title_image_url = image_generator.generate_infographic(article_title)
                title_image_storage_url = storage_manager.save_image(title_image_url, f"title_{article_title}")
                st.session_state.webstory_images.append({
                    "type": "title",
                    "text": article_title,
                    "image_url": title_image_storage_url
                })
                
                # Generate images for each bullet point
                for i, bullet in enumerate(bullet_points):
                    bullet_image_url = image_generator.generate_infographic(bullet)
                    bullet_image_storage_url = storage_manager.save_image(bullet_image_url, f"bullet_{i}_{article_title}")
                    st.session_state.webstory_images.append({
                        "type": "bullet",
                        "text": bullet,
                        "image_url": bullet_image_storage_url
                    })
                
                # Generate and save webstory HTML
                webstory_html = generate_webstory_html(article_title, st.session_state.webstory_images)
                st.session_state.webstory_html_url = save_webstory_html(webstory_html, article_title)
                
                st.success("Webstory generated successfully!")
                
            except Exception as e:
                st.error(f"Error generating webstory: {str(e)}")

# Display generated webstory if available
if st.session_state.webstory_images:
    st.subheader("Generated Webstory")
    
    # Display carousel of images
    col1, col2, col3 = st.columns([1, 10, 1])
    
    with col1:
        if st.button("◀", key="prev_button"):
            if "current_image_index" not in st.session_state or st.session_state.current_image_index <= 0:
                st.session_state.current_image_index = len(st.session_state.webstory_images) - 1
            else:
                st.session_state.current_image_index -= 1
    
    with col3:
        if st.button("▶", key="next_button"):
            if "current_image_index" not in st.session_state:
                st.session_state.current_image_index = 1
            elif st.session_state.current_image_index >= len(st.session_state.webstory_images) - 1:
                st.session_state.current_image_index = 0
            else:
                st.session_state.current_image_index += 1
    
    # Initialize current image index if not set
    if "current_image_index" not in st.session_state:
        st.session_state.current_image_index = 0
    
    # Display current image
    with col2:
        current_image = st.session_state.webstory_images[st.session_state.current_image_index]
        st.image(current_image["image_url"], use_column_width=True)
        st.markdown(f"**{current_image['text']}**")
        st.markdown(f"Page {st.session_state.current_image_index + 1} of {len(st.session_state.webstory_images)}")
    
    # Display webstory link
    if st.session_state.webstory_html_url:
        st.markdown("---")
        st.markdown(f"[🌐 View Full Webstory]({st.session_state.webstory_html_url})")
        st.markdown(f"[💾 Download Webstory HTML]({st.session_state.webstory_html_url})")

# Function to generate webstory HTML
def generate_webstory_html(title, images):
    """Generate HTML for the webstory.
    
    Args:
        title (str): The title of the webstory.
        images (list): List of image data dictionaries.
        
    Returns:
        str: HTML content for the webstory.
    """
    html = f"""
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>{title} - Webstory</title>
        <style>
            body, html {{margin: 0; padding: 0; height: 100%; overflow: hidden;}}
            .webstory-container {{height: 100vh; position: relative;}}
            .webstory-slide {{height: 100%; width: 100%; position: absolute; top: 0; left: 0; display: none; flex-direction: column; justify-content: flex-end; background-size: cover; background-position: center;}}
            .webstory-slide.active {{display: flex;}}
            .webstory-text {{padding: 20px; background: rgba(0,0,0,0.7); color: white; font-family: Arial, sans-serif;}}
            .webstory-nav {{position: absolute; top: 0; height: 100%; width: 50%; z-index: 10;}}
            .webstory-nav.prev {{left: 0;}}
            .webstory-nav.next {{right: 0;}}
            .progress-bar {{position: absolute; top: 0; left: 0; right: 0; height: 4px; display: flex;}}
            .progress-segment {{height: 100%; flex: 1; margin: 0 2px; background: rgba(255,255,255,0.3);}}
            .progress-segment.active {{background: white;}}
        </style>
    </head>
    <body>
        <div class="webstory-container">
            <div class="progress-bar">
    """
    
    # Add progress segments
    for i in range(len(images)):
        html += f'<div class="progress-segment" id="progress-{i}"></div>'
    
    html += "</div>"
    
    # Add slides
    for i, img_data in enumerate(images):
        active_class = "active" if i == 0 else ""
        html += f"""
            <div class="webstory-slide {active_class}" id="slide-{i}" style="background-image: url('{img_data['image_url']}');">
                <div class="webstory-text">
                    <h2>{img_data['text']}</h2>
                </div>
            </div>
        """
    
    # Add navigation
    html += """
            <div class="webstory-nav prev" onclick="prevSlide()"></div>
            <div class="webstory-nav next" onclick="nextSlide()"></div>
        </div>
        
        <script>
            let currentSlide = 0;
            const slides = document.querySelectorAll('.webstory-slide');
            const progressSegments = document.querySelectorAll('.progress-segment');
            const totalSlides = slides.length;
            
            // Mark first progress segment as active
            progressSegments[0].classList.add('active');
            
            function showSlide(index) {
                // Hide all slides
                slides.forEach(slide => slide.classList.remove('active'));
                progressSegments.forEach(segment => segment.classList.remove('active'));
                
                // Show the selected slide
                slides[index].classList.add('active');
                progressSegments[index].classList.add('active');
                currentSlide = index;
            }
            
            function nextSlide() {
                let nextIndex = currentSlide + 1;
                if (nextIndex >= totalSlides) nextIndex = 0;
                showSlide(nextIndex);
            }
            
            function prevSlide() {
                let prevIndex = currentSlide - 1;
                if (prevIndex < 0) prevIndex = totalSlides - 1;
                showSlide(prevIndex);
            }
            
            // Auto-advance slides every 5 seconds
            setInterval(nextSlide, 5000);
        </script>
    </body>
    </html>
    """
    
    return html

# Function to save webstory HTML to BytePlus object storage
def save_webstory_html(html_content, title):
    """Save the webstory HTML to BytePlus object storage.
    
    Args:
        html_content (str): The HTML content to save.
        title (str): The title of the webstory.
        
    Returns:
        str: URL of the saved HTML in object storage.
    """
    try:
        # Generate a unique object key based on timestamp and title
        timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
        # Clean title to use as part of the filename
        clean_title = ''.join(c if c.isalnum() else '_' for c in title)[:50]
        object_key = f"{storage_manager.object_key_prefix}/webstories/{timestamp}_{clean_title}.html"
        
        # Create a temporary file with the HTML content
        import tempfile
        with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix=".html") as temp_file:
            temp_file_path = temp_file.name
            temp_file.write(html_content)
        
        try:
            # Upload the HTML to BytePlus Object Storage
            storage_manager.client.put_object_from_file(
                storage_manager.bucket_name,
                object_key,
                temp_file_path
            )
            
            # Generate a URL for the uploaded HTML
            storage_url = f"https://{storage_manager.bucket_name}.{storage_manager.endpoint}/{object_key}"
            
            return storage_url
            
        finally:
            # Clean up the temporary file
            if os.path.exists(temp_file_path):
                os.unlink(temp_file_path)
                
    except Exception as e:
        raise Exception(f"Failed to save webstory HTML: {str(e)}")

# Instructions in the sidebar
with st.sidebar:
    st.header("How to use")
    st.markdown(
        """1. Enter a news article title in the input field"""
    )
    st.markdown(
        """2. Add up to 5 bullet points summarizing the article"""
    )
    st.markdown(
        """3. Click 'Generate Webstory' to create your webstory"""
    )
    st.markdown(
        """4. Use the carousel to navigate through the generated images"""
    )
    st.markdown(
        """5. Click on the webstory link to view or download the full webstory"""
    )
    
    st.header("About")
    st.markdown(
        """News Webstory Generator uses the following BytePlus genAI technologies:"""
    )
    st.markdown(
        """- BytePlus text-to-image Vision model to generate contextual images"""
    )
    st.markdown(
        """- BytePlus Cloud Object Storage to store and serve generated images and webstories"""
    )