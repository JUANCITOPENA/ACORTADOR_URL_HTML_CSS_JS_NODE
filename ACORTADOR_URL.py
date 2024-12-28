import streamlit as st
import pymongo
import certifi
import random
import string
from dotenv import load_dotenv
import os
import validators
import datetime
from urllib.parse import quote_plus

# Load environment variables
load_dotenv()

# Escape username and password for MongoDB URI
username = quote_plus("JUANCITOPENA")
password = quote_plus("P@$$word_1234@&$@JDDLM#*mK2T6vpG&B")

# Construct MongoDB URI with escaped characters
MONGO_URI = f"mongodb+srv://{username}:{password}@acortadorurl.y6l52.mongodb.net/?retryWrites=true&w=majority"

# Initialize MongoDB connection as a global variable
@st.cache_resource
def init_db():
    try:
        # Use certifi to provide the CA file for SSL connections
        client = pymongo.MongoClient(
            MONGO_URI, 
            tls=True, 
            tlsCAFile=certifi.where(), 
            tlsAllowInvalidCertificates=True  # Allows connection even with certificate issues (not recommended for production)
        )
        db = client.url_shortener
        # Test the connection
        client.admin.command('ping')
        st.success("Connected to MongoDB!")
        return db.urls
    except Exception as e:
        st.error(f"Error connecting to MongoDB: {str(e)}")
        return None

# Initialize collection globally
collection = init_db()

def generate_short_id(length=6):
    """Generate a random short ID for the URL."""
    characters = string.ascii_letters + string.digits
    return ''.join(random.choice(characters) for _ in range(length))

def is_valid_url(url):
    """Validate if the provided URL is correct."""
    return validators.url(url)

def get_base_url():
    """Get the base URL of the Streamlit app."""
    if 'base_url' not in st.session_state:
        # Set a default base URL for local testing or production
        st.session_state.base_url = os.getenv('BASE_URL', 'http://localhost:8501')
    return st.session_state.base_url

def shorten_url(long_url):
    """Create a shortened URL and store it in MongoDB."""
    if collection is None:
        st.error("Database connection not available")
        return None

    try:
        # Check if URL already exists
        existing_url = collection.find_one({"long_url": long_url})
        if existing_url:
            base_url = get_base_url()
            return f"{base_url}?short_id={existing_url['short_id']}"
        
        # Create new short URL
        short_id = generate_short_id()
        while collection.find_one({"short_id": short_id}):  # Ensure unique short_id
            short_id = generate_short_id()
        
        base_url = get_base_url()
        short_url = f"{base_url}?short_id={short_id}"
        
        url_data = {
            "long_url": long_url,
            "short_id": short_id,
            "created_at": datetime.datetime.utcnow()
        }
        
        collection.insert_one(url_data)
        return short_url
    except Exception as e:
        st.error(f"Error saving URL: {str(e)}")
        return None

def get_long_url(short_id):
    """Retrieve the original URL from MongoDB using the short ID."""
    if collection is None:
        st.error("Database connection not available")
        return None

    try:
        url_data = collection.find_one({"short_id": short_id})
        return url_data["long_url"] if url_data else None
    except Exception as e:
        st.error(f"Error retrieving URL: {str(e)}")
        return None

# Streamlit UI
def main():
    st.title("🔗 URL Shortener")
    st.write("Convert your long URLs into short, manageable links!")
    
    # Check if database is connected
    if collection is None:
        st.error("Cannot connect to database. Please check your connection settings.")
        return
    
    # Display current base URL
    st.sidebar.write("Current Base URL:", get_base_url())
    
    # URL Input
    long_url = st.text_input("Enter your long URL:", placeholder="https://example.com/very/long/url")
    
    if st.button("Shorten URL"):
        if not long_url:
            st.warning("Please enter a URL.")
            return
            
        if not is_valid_url(long_url):
            st.error("Please enter a valid URL.")
            return
            
        with st.spinner("Generating short URL..."):
            short_url = shorten_url(long_url)
            if short_url:
                st.success("URL shortened successfully!")
                
                # Create columns for better layout
                col1, col2 = st.columns([3, 1])
                
                with col1:
                    st.code(short_url)
                    st.caption("This is your shortened URL. Click the button to copy it.")
                
                with col2:
                    if st.button("📋 Copy", key="copy_button"):
                        st.write("✅ Copied!")
                        st.session_state['clipboard'] = short_url
                
                # Show statistics
                st.divider()
                st.subheader("URL Information")
                st.write("Original URL:", long_url)
                st.write("Short URL:", short_url)
                st.write("Created at:", datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"))

    # Handle redirects
    if "short_id" in st.query_params:
        short_id = st.query_params["short_id"]
        long_url = get_long_url(short_id)
        if long_url:
            st.info(f"Redirecting to: {long_url}")
            st.markdown(f'<meta http-equiv="refresh" content="0;url={long_url}">', unsafe_allow_html=True)
        else:
            st.error("URL not found.")

if __name__ == "__main__":
    main()
