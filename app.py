import streamlit as st
import pandas as pd
import io
import base64
import os
from PIL import Image

# Get the absolute path to the logo file
logo_path = os.path.join(os.path.dirname(__file__), "assets", "logo.png")

try:
    # Try to load the logo
    logo = Image.open(logo_path)
    
    # Set page config with emoji as fallback
    st.set_page_config(page_title="Vivenu & Fortress Data Merger", page_icon="📊", layout="wide")
    
    # Create columns for layout
    col1, col2 = st.columns([1, 4])
    
    # Display logo
    with col1:
        st.image(logo, width=150)
        
except Exception as e:
    # Fallback if logo can't be loaded
    st.set_page_config(page_title="Vivenu & Fortress Data Merger", page_icon="📊", layout="wide")
    st.error(f"Could not load logo: {e}")

# Display title
col1, col2 = st.columns([1, 4])
with col2:
    st.title("Vivenu & Fortress Data Merger")
    st.write("Upload your Vivenu and Fortress files to analyze attendance data.")
# Define the required columns for each file
vivenu_required_columns = ['barcode', 'ticketName', 'origin']
fortress_required_columns = ['Barcode']

# Create two columns for file uploads
col1, col2 = st.columns(2)

with col1:
    st.subheader("Vivenu File")
    uploaded_viv = st.file_uploader("Upload Vivenu file", type=["csv", "xlsx", "xls"])
    
    if uploaded_viv is not None:
        try:
            # Determine file type and read accordingly
            if uploaded_viv.name.endswith('.csv'):
                df_viv = pd.read_csv(uploaded_viv)
            else:
                df_viv = pd.read_excel(uploaded_viv)
            
            # Check if required columns exist in the Vivenu file
            missing_columns = [col for col in vivenu_required_columns if col not in df_viv.columns]
            if missing_columns:
                st.error(f"❌ The following required columns are missing from the Vivenu file: {', '.join(missing_columns)}")
                df_viv = None
            else:
                st.success("✅ Vivenu file loaded successfully!")
                st.write(f"Total records: {len(df_viv)}")
                with st.expander("Preview Vivenu Data"):
                    st.dataframe(df_viv.head())
        except Exception as e:
            st.error(f"❌ Error loading Vivenu file: {str(e)}")
            df_viv = None
    else:
        df_viv = None

with col2:
    st.subheader("Fortress File")
    uploaded_fortress = st.file_uploader("Upload Fortress file", type=["csv", "xlsx", "xls"])
    
    if uploaded_fortress is not None:
        try:
            # Determine file type and read accordingly
            if uploaded_fortress.name.endswith('.csv'):
                df_fortress = pd.read_csv(uploaded_fortress)
            else:
                df_fortress = pd.read_excel(uploaded_fortress)
            
            # Check if required columns exist in the Fortress file
            missing_columns = [col for col in fortress_required_columns if col not in df_fortress.columns]
            if missing_columns:
                st.error(f"❌ The following required columns are missing from the Fortress file: {', '.join(missing_columns)}")
                df_fortress = None
            else:
                st.success("✅ Fortress file loaded successfully!")
                st.write(f"Total records: {len(df_fortress)}")
                with st.expander("Preview Fortress Data"):
                    st.dataframe(df_fortress.head())
        except Exception as e:
            st.error(f"❌ Error loading Fortress file: {str(e)}")
            df_fortress = None
    else:
        df_fortress = None

# Process data only if both files are loaded
if df_viv is not None and df_fortress is not None:
    st.subheader("Analysis Results")
    
    # Merge the dataframes
    with st.spinner("Processing data..."):
        df = pd.merge(df_viv, df_fortress, left_on='barcode', right_on='Barcode', how='left')
        df['Entered to the game?'] = df['Barcode'].apply(lambda x: 'X' if pd.isnull(x) else 'V')

        df_V = df[df['Entered to the game?'] == 'V']
        df_X = df[df['Entered to the game?'] == 'X']

        df_V_not_manui = df_V[~df_V['ticketName'].str.contains('מנוי', na=False)]
        df_V_manui = df_V[df_V['ticketName'].str.contains('מנוי', na=False)]
        df_X_not_manui = df_X[~df_X['ticketName'].str.contains('מנוי', na=False)]
        df_X_manui = df_X[df_X['ticketName'].str.contains('מנוי', na=False)]

        # Calculate metrics
        fans = len(df_fortress)
        V_manui = len(df_fortress[df_fortress['Barcode'].isna()])
        V_not_manui_trans = len(df_V_not_manui)
        V_manui_trans = len(df_V_manui)
        X_not_manui_trans = len(df_X_not_manui)
        X_manui_trans = len(df_X_manui)
        free_tickets = len(df_viv[df_viv['origin'].isna()])

    # Display results in a more appealing layout
    metric_col1, metric_col2, metric_col3 = st.columns(3)
    
    with metric_col1:
        st.metric("כמות צופים", fans)
        st.metric("הזמנות", free_tickets)
    
    with metric_col2:
        st.metric("מנויים שנכנסו למשחק עם המנוי", V_manui)
        st.metric("כרטיסים שנכנסו למשחק", V_not_manui_trans)
        st.metric("כרטיסים ממנוי שנכנסו למשחק", V_manui_trans)
    
    with metric_col3:
        st.metric("כרטיסים שלא נכנסו למשחק", X_not_manui_trans)
        st.metric("כרטיסים ממנוי שלא נכנסו למשחק", X_manui_trans)
    
    # Create a formatted text for clipboard
    analysis_text = f"""כמות צופים
{fans}

הזמנות
{free_tickets}

מנויים שנכנסו למשחק עם המנוי
{V_manui}

כרטיסים שנכנסו למשחק
{V_not_manui_trans}

כרטיסים ממנוי שנכנסו למשחק
{V_manui_trans}

כרטיסים שלא נכנסו למשחק
{X_not_manui_trans}

כרטיסים ממנוי שלא נכנסו למשחק
{X_manui_trans}"""
    
    # Create a download button for the analysis results
    st.subheader("Copy Analysis Results")
    
    # Create a downloadable text file for the analysis results with UTF-8-sig encoding
    b64 = base64.b64encode(analysis_text.encode('utf-8-sig')).decode()
    href = f'<a href="data:file/txt;base64,{b64}" download="analysis_results.txt" id="download_link" target="_blank">Download Analysis Results as Text File</a>'
    
    # Add a clickable button that looks nicer
    button_html = f"""
    <style>
    .download-button {{
        display: inline-block;
        padding: 0.5em 1em;
        background-color: #ADD8E6;
        color: black;
        text-align: center;
        text-decoration: none;
        font-size: 16px;
        border-radius: 4px;
        border: none;
        cursor: pointer;
        margin: 10px 0;
    }}
    .download-button:hover {{
        background-color: #FFFF00;
    }}
    </style>
    
    <a href="data:file/txt;base64,{b64}" download="analysis_results.txt" class="download-button">
        Copy Analysis Results (Download as Text)
    </a>
    """
    
    st.markdown(button_html, unsafe_allow_html=True)
    st.info("Click the button above to download the analysis results as a text file that you can open and copy.")
    
    # Data exploration section
    st.subheader("Merged Data Explorer")
    with st.expander("View Merged Data"):
        st.dataframe(df)
    
    # Download options
    st.subheader("Download Options")
    
    # Modified function to create a download link with UTF-8-sig encoding
    def get_table_download_link(df, filename, link_text):
        # Use StringIO to create a buffer and write CSV with UTF-8-sig encoding
        csv_buffer = io.StringIO()
        df.to_csv(csv_buffer, index=False, encoding='utf-8-sig')
        csv_str = csv_buffer.getvalue()
        
        # Encode the CSV string to base64
        b64 = base64.b64encode(csv_str.encode('utf-8-sig')).decode()
        href = f'<a href="data:file/csv;base64,{b64}" download="{filename}.csv">{link_text}</a>'
        return href
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown(get_table_download_link(df, "merged_data", "Download Merged Data"), unsafe_allow_html=True)
    
    with col2:
        download_format = st.selectbox("Download specific segment:", [
            "All Data", 
            "Entered Tickets", 
            "Not Entered Tickets",
            "Entered Subscription Tickets",
            "Not Entered Subscription Tickets"
        ])
        
        if download_format == "All Data":
            download_df = df
            filename = "all_data"
        elif download_format == "Entered Tickets":
            download_df = df_V
            filename = "entered_tickets"
        elif download_format == "Not Entered Tickets":
            download_df = df_X
            filename = "not_entered_tickets"
        elif download_format == "Entered Subscription Tickets":
            download_df = df_V_manui
            filename = "entered_subscription_tickets"
        elif download_format == "Not Entered Subscription Tickets":
            download_df = df_X_manui
            filename = "not_entered_subscription_tickets"
        
        st.markdown(get_table_download_link(download_df, filename, f"Download {download_format}"), unsafe_allow_html=True)

else:
    if uploaded_viv is None and uploaded_fortress is None:
        st.info("Please upload both Vivenu and Fortress files to begin analysis.")
    elif uploaded_viv is None:
        st.warning("Vivenu file is missing. Please upload to proceed.")
    elif uploaded_fortress is None:
        st.warning("Fortress file is missing. Please upload to proceed.")
    else:
        st.error("There was an error processing one or both files. Please check the error messages above.")

# Add footer
st.markdown("---")
st.markdown("Developed for Vivenu and Fortress data analysis")
