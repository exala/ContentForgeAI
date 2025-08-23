import streamlit as st
import pandas as pd
import os

# --- Import Your Existing Modules ---
from modules import prompt_orchestrator, generate_content, post_processor, article_storage_manager
from modules.wordpress_publisher import create_wordpress_post, upload_image_to_wordpress

# --- Page Configuration ---
st.set_page_config(
    page_title="ContentForgeAI",
    page_icon="🤖",
    layout="wide"
)

# --- Main Application ---
st.title("🤖 ContentForgeAI")
st.markdown("Your AI-powered content creation and publishing assistant.")

# --- Sidebar ---
with st.sidebar:
    # --- NEW: Download Database Section ---
    st.header("Export Data")
    db_file_path = 'articles.db'  # Assuming the DB is in the root directory
    # Check if the database file exists before showing the button
    if os.path.exists(db_file_path):
        # Read the file content in binary mode
        with open(db_file_path, 'rb') as f:
            db_bytes = f.read()

        st.download_button(
            label="Download articles.db",
            data=db_bytes,
            file_name="articles.db",
            mime="application/octet-stream"  # A generic mime type for binary files
        )
    else:
        st.info("No database file found. Generate an article first to create it.")

    st.markdown("---")  # Visual separator

    st.header("Credentials & Settings")
    st.markdown("Enter your credentials here. They will be stored for the current session.")

    api_key = st.text_input("OpenAI/Gemini API Key", type="password", key="api_key")
    wp_url = st.text_input("WordPress URL", key="wp_url", placeholder="https://yourdomain.com")
    wp_user = st.text_input("WordPress Username", key="wp_user")
    wp_password = st.text_input("WordPress Password", type="password", key="wp_password")

    # Set credentials as environment variables
    # if api_key: os.environ['API_KEY'] = api_key  <-- OLD
    if api_key: os.environ['GOOGLE_API_KEY'] = api_key # <-- NEW, matches generation.py
    if wp_url: os.environ['WP_URL'] = wp_url
    if wp_user: os.environ['WP_USER'] = wp_user
    if wp_password: os.environ['WP_PASSWORD'] = wp_password

    st.info("Your modules should read these credentials, for example, using `os.getenv('API_KEY')`")

    # --- END of new section ---

# --- Main Content Area with Tabs ---
tab1, tab2 = st.tabs(["Single Topic Generation", "Excel Bulk Processing"])

# (The rest of your code for the tabs remains exactly the same)
# ...
# --- Single Topic Tab ---
with tab1:
    st.header("Generate a Single Article")

    topic = st.text_input("Enter the main topic or keyword", placeholder="e.g., 'Benefits of Solar Energy'")
    publish_to_wp = st.checkbox("Publish directly to WordPress", key="single_publish")

    generate_button = st.button("Generate Article")

    if generate_button and topic:
        # Check for credentials if publishing
        if publish_to_wp and not all([wp_url, wp_user, wp_password]):
            st.error("Please provide all WordPress credentials in the sidebar to publish.")
        else:
            with st.spinner("Generating content... Please wait."):
                try:
                    # 1. Generate Content
                    prompt = prompt_orchestrator(topic)
                    raw_content = generate_content(prompt)
                    title, html_content = post_processor(raw_content)

                    # 2. Store in Database
                    article_storage_manager(title, html_content, topic)
                    st.success("Article generated and stored in the database!")

                    # 3. Display Result
                    with st.container(border=True):
                        st.subheader(title)
                        st.markdown(html_content, unsafe_allow_html=True)
                        st.caption(f"Word Count: {len(html_content.split())}")

                    # 4. Publish to WordPress
                    if publish_to_wp:
                        with st.spinner("Publishing to WordPress..."):
                            try:
                                # NOTE: Hardcoded image path from your original code.
                                # Consider adding a file uploader for this in the future.
                                image_path = "/home/runner/workspace/font.PNG" # Adjust the location or link of your image here
                                featured_media_id = None
                                if os.path.exists(image_path):
                                    featured_media_id = upload_image_to_wordpress(image_path, title)

                                success = create_wordpress_post(title, html_content, "publish", featured_media_id)
                                if success:
                                    st.success("✅ Successfully published to WordPress!")
                                else:
                                    st.error("❌ Failed to publish to WordPress.")
                            except Exception as wp_error:
                                st.error(f"WordPress publishing error: {wp_error}")

                except Exception as e:
                    st.error(f"An error occurred during generation: {e}")

# --- Excel Bulk Processing Tab ---
with tab2:
    st.header("Generate Articles in Bulk from Excel")

    uploaded_file = st.file_uploader("Upload an Excel file (.xlsx, .xls)", type=["xlsx", "xls"])

    if uploaded_file is not None:
        try:
            df = pd.read_excel(uploaded_file)
            st.success(f"Successfully uploaded `{uploaded_file.name}` with {len(df)} rows.")

            with st.expander("Preview Data", expanded=True):
                st.dataframe(df.head())

            # Column selection
            column_name = st.selectbox("Select the column containing the topics:", df.columns)

            publish_bulk_to_wp = st.checkbox("Publish all articles to WordPress", key="bulk_publish")

            process_button = st.button("Generate All Articles from Excel")

            if process_button:
                if publish_bulk_to_wp and not all([wp_url, wp_user, wp_password]):
                    st.error("Please provide all WordPress credentials in the sidebar to publish.")
                else:
                    topics = df[column_name].dropna().tolist()
                    st.info(f"Starting to process {len(topics)} topics...")

                    results_container = st.container()
                    progress_bar = st.progress(0)

                    for i, topic in enumerate(topics):
                        try:
                            # 1. Generate
                            prompt = prompt_orchestrator(topic)
                            raw_content = generate_content(prompt)
                            title, html_content = post_processor(raw_content)

                            # 2. Store
                            article_storage_manager(title, html_content, topic)

                            result_msg = f"✅ **{topic}**: Generated '{title}' ({len(html_content.split())} words)."

                            # 3. Publish
                            if publish_bulk_to_wp:
                                try:
                                    # NOTE: Using the same hardcoded image path
                                    image_path = "/home/runner/workspace/font.PNG"
                                    featured_media_id = None
                                    if os.path.exists(image_path):
                                        featured_media_id = upload_image_to_wordpress(image_path, title)

                                    success = create_wordpress_post(title, html_content, "publish", featured_media_id)
                                    if success:
                                        result_msg += " Published to WordPress."
                                    else:
                                        result_msg += " WP publishing failed."
                                except Exception as wp_e:
                                    result_msg += f" WP Error: {wp_e}"

                            results_container.markdown(result_msg)

                        except Exception as e:
                            results_container.error(f"❌ **{topic}**: Failed with error - {e}")

                        # Update progress bar
                        progress_bar.progress((i + 1) / len(topics))

        except Exception as e:
            st.error(f"Error processing Excel file: {e}")