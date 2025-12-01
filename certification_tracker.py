# python3 -m pip install streamlit pandas
# python -m streamlit run certification_tracker.py
import streamlit as st
import json
import os
import pandas as pd
from datetime import datetime

# --- Configuration (FIXED PATH for reliable saving) ---
JSON_FILENAME = 'certifications.json' 
# Calculates the absolute path to ensure the file is saved next to the script
JSON_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), JSON_FILENAME) 

# --- JSON Data Management Functions ---

def load_certs():
    """Loads certification data from the JSON file."""
    if not os.path.exists(JSON_FILE):
        return []
    with open(JSON_FILE, 'r') as f:
        try:
            data = json.load(f)
            if isinstance(data, list):
                # Ensure all required keys are present for DataFrame compatibility
                required_keys = ['cert_id', 'date', 'expires', 'fee', 'renewal_frequency']
                for cert in data:
                    for key in required_keys:
                        if key not in cert:
                            cert[key] = "" if key not in ['fee'] else 0.00
            return data if isinstance(data, list) else []
        except (json.JSONDecodeError, FileNotFoundError):
            return [] 

def save_certs(certs):
    """Saves the current list of certifications to the JSON file."""
    for cert in certs:
        # Date: Convert datetime/Timestamp objects if present
        date_val = cert.get('date')
        if isinstance(date_val, (datetime, pd.Timestamp)):
            cert['date'] = date_val.strftime('%Y-%m-%d')

        # Expires: Handle None, NaT, or empty strings by converting to "N/A"
        expires_val = cert.get('expires')
        if expires_val is None or str(expires_val).upper() in ["N/A", "NAT", "NONE", ""]:
            cert['expires'] = "N/A"
        elif isinstance(expires_val, (datetime, pd.Timestamp)):
            cert['expires'] = expires_val.strftime('%Y-%m-%d')
        
        # Ensure fee is saved as a float
        fee_val = cert.get('fee')
        try:
            cert['fee'] = float(fee_val) if fee_val else 0.00
        except (TypeError, ValueError):
            cert['fee'] = 0.00
            
        # Ensure cert_id is saved as a string 
        cert['cert_id'] = str(cert.get('cert_id', ''))

    try:
        with open(JSON_FILE, 'w') as f:
            json.dump(certs, f, indent=4)
    except Exception as e:
        # Display error if saving fails
        st.error(f"FATAL SAVE ERROR: Could not write to file! Details: {e}")


# --- Streamlit UI Components ---

def add_certification(certs_list):
    """Streamlit form to add a new certification."""
    st.subheader("➕ Add New Certification")
    
    with st.form("add_cert_form", clear_on_submit=True):
        new_cert = {}
        
        # Required fields
        new_cert['name'] = st.text_input("Certification Name", key="name_input")
        new_cert['issuer'] = st.text_input("Issuing Organization", key="issuer_input")
        
        # New field
        new_cert['cert_id'] = st.text_input("Certificate ID# (Optional)", key="cert_id_input") 
        
        date_achieved = st.date_input("Date Achieved", key="date_input", 
                                        min_value=datetime(2000, 1, 1), 
                                        max_value=datetime.now())
        new_cert['date'] = date_achieved.strftime('%Y-%m-%d')
        
        expires_date = st.date_input("Expiration Date (Optional)", key="expires_input", 
                                        min_value=datetime.now(), value=None)
        new_cert['expires'] = expires_date.strftime('%Y-%m-%d') if expires_date else "N/A"
        
        st.markdown("---")
        st.markdown("**Renewal/Financial Details (AMF)**")
        new_cert['fee'] = st.number_input("Renewal/Annual Fee (USD)", 
                                            min_value=0.00, 
                                            value=0.00, 
                                            step=10.00, 
                                            format="%.2f", 
                                            key="fee_input")

        new_cert['renewal_frequency'] = st.selectbox("Renewal Frequency", 
                                                    ['None/One-Time', 'Annual', 'Biennial (Every 2 years)', 'Triennial (Every 3 years)', 'Other'], 
                                                    key="frequency_input")
        
        submitted = st.form_submit_button("Add Certification")

        if submitted:
            if new_cert['name'] and new_cert['issuer']:
                certs_list.append(new_cert)
                save_certs(certs_list)
                st.success(f"Added **{new_cert['name']}**! Changes applied.")
                st.rerun() 
            else:
                st.error("Certification Name and Issuer are required.")

def display_certifications_table(df_certs):
    """Displays all current certifications in an EDITABLE table using st.data_editor.
       CRITICAL FIX: Uses session state to reliably detect changes to existing rows."""
    st.subheader("📝 Current Certifications (Editable)")
    
    if df_certs.empty:
        st.info("No certifications found. Add one using the form.")
        return df_certs
    
    # Define column configurations for editing and display
    column_config = {
        "fee": st.column_config.NumberColumn(
            "Renewal/Annual Fee (USD)", 
            format="$%0.2f",
            min_value=0.00,
            required=True
        ),
        "date": st.column_config.DateColumn(
            "Date Achieved", 
            format="YYYY-MM-DD",
            required=True
        ),
        "expires": st.column_config.DateColumn(
            "Expiration Date", 
            format="YYYY-MM-DD"
        ),
        "renewal_frequency": st.column_config.SelectboxColumn(
            "Renewal Frequency",
            options=['None/One-Time', 'Annual', 'Biennial (Every 2 years)', 'Triennial (Every 3 years)', 'Other'],
            required=True
        ),
        "cert_id": "Certificate ID#",
        "name": st.column_config.TextColumn("Certification Name", required=True),
        "issuer": st.column_config.TextColumn("Issuing Organization", required=True),
    }
    
    column_order = [
        'name', 'issuer', 'cert_id', 'date', 'expires', 'renewal_frequency', 'fee'
    ]

    edited_df = st.data_editor(
        df_certs, 
        use_container_width=True, 
        hide_index=True, 
        column_config=column_config,
        column_order=column_order,
        key="editable_cert_table" 
    )
    
    # --- CRITICAL FIX START: Reliable change detection via Session State ---
    changes = st.session_state.get('editable_cert_table', {})
    
    # Check for edited rows, added rows, or deleted rows
    if changes.get('edited_rows') or changes.get('added_rows') or changes.get('deleted_rows'):
        st.session_state['data_edited'] = True
    else:
        st.session_state['data_edited'] = False
    # --- CRITICAL FIX END ---
    
    return edited_df

def display_due_soon_block(certs):
    """Filters and displays certifications ordered by their expiration date."""
    st.markdown("---")
    st.subheader("🗓️ Certifications Due Soon (Next 180 Days)")
    
    today = datetime.now().date()
    due_soon_certs = []
    
    for cert in certs:
        expiry_val = cert.get('expires')
        
        # Skip if expired or marked as N/A/None/NaT
        if expiry_val is None or str(expiry_val).upper() in ["N/A", "NAT", "NONE", ""]:
            continue

        try:
            # Handle date formats from different sources 
            if isinstance(expiry_val, (datetime, pd.Timestamp)):
                expiry_date = expiry_val.date()
            elif isinstance(expiry_val, str):
                expiry_date = datetime.strptime(expiry_val, '%Y-%m-%d').date()
            else:
                continue
            
            days_left = (expiry_date - today).days
            
            if 0 <= days_left <= 180:
                due_soon_certs.append({
                    'Certification': cert['name'],
                    'Certificate ID#': cert.get('cert_id', ''), 
                    'Issuer': cert['issuer'],
                    'Expiration Date': expiry_date.strftime('%Y-%m-%d'), 
                    'Renewal Fee': f"${cert.get('fee', 0.00):.2f}",
                    'Days Left': days_left
                })
        except (ValueError, TypeError):
            continue

    if due_soon_certs:
        due_soon_df = pd.DataFrame(due_soon_certs).sort_values(by='Days Left', ascending=True)
        
        st.warning("These certifications require attention for renewal or CE credits!")
        
        st.dataframe(
            due_soon_df, 
            hide_index=True, 
            use_container_width=True,
            column_order=('Certification', 'Expiration Date', 'Days Left', 'Renewal Fee', 'Certificate ID#', 'Issuer')
        )
    else:
        st.info("No certifications are due for renewal in the next 6 months.")


def display_summary(certs):
    """Displays key financial and expiration summaries."""
    st.markdown("---")
    
    total_annual_fee = 0.00
    
    for cert in certs:
        fee = cert.get('fee', 0.00)
        frequency = cert.get('renewal_frequency', 'None/One-Time')
        
        try:
            fee = float(fee)
        except (TypeError, ValueError):
            fee = 0.00
            
        if frequency == 'Annual':
            total_annual_fee += fee
        elif frequency == 'Biennial (Every 2 years)':
            total_annual_fee += (fee / 2.0)
        elif frequency == 'Triennial (Every 3 years)':
            total_annual_fee += (fee / 3.0)
            
    col3, col4 = st.columns(2)
    
    with col3:
        st.metric(
            "Total Annual AMF Estimate",
            f"${total_annual_fee:.2f}",
            help="Estimated total fees to maintain all annual, biennial, and triennial certifications."
        )

    with col4:
        st.metric(
            "Total Certifications Tracked",
            len(certs)
        )


# --- Main Application Logic ---

def main():
    st.set_page_config(layout="wide", page_title="IT Certification Tracker")
    
    st.title("👨‍💻 IT Certification & Fee Tracker")
    st.markdown("Manage your professional certifications, renewal fees (AMFs), and expiration dates. Data is loaded from **`certifications.json`**.")
    
    # 1. Initialize session state for tracking edits
    if 'data_edited' not in st.session_state:
        st.session_state['data_edited'] = False
        
    # --- DEBUG BLOCK START: File path verification and initialization ---
    st.sidebar.markdown("---")
    st.sidebar.subheader("File Path Debug")
    st.sidebar.code(f"JSON File Path:\n{JSON_FILE}", language="text")
    
    # Initialize file if it doesn't exist
    if not os.path.exists(JSON_FILE):
        st.sidebar.warning("File not found! Attempting to create empty file...")
        try:
            with open(JSON_FILE, 'w') as f:
                json.dump([], f)
            st.sidebar.success("Empty file created successfully. App will now rerun.")
            st.rerun() 
        except PermissionError:
            st.sidebar.error("PERMISSION DENIED: Cannot create file at this location. Check folder permissions.")
        except Exception as e:
            st.sidebar.error(f"Error creating file: {e}")
    else:
        st.sidebar.info("File exists.")
        try:
            size_bytes = os.path.getsize(JSON_FILE)
            st.sidebar.info(f"File size: {size_bytes} bytes")
        except:
             st.sidebar.info("Could not determine file size (may be permission issue).")

    st.sidebar.markdown("---")
    # --- DEBUG BLOCK END ---
    
    # 2. Load data
    certs_list = load_certs()
    
    # --- Data Type Conversion and Preparation for DataFrame ---
    if certs_list:
        df = pd.DataFrame(certs_list)
        df['date'] = pd.to_datetime(df['date'], errors='coerce')
        df['expires'] = df['expires'].replace(['N/A', '', 'None'], pd.NaT)
        df['expires'] = pd.to_datetime(df['expires'], errors='coerce')
    else:
        df = pd.DataFrame()
    
    # --- Layout ---
    col1, col2 = st.columns([1, 2])
    
    # 3. Add Certification form 
    with col1:
        add_certification(certs_list)

    # 4. Sorting Selector 
    if not df.empty:
        sort_options = ['date', 'expires', 'name', 'issuer', 'fee', 'cert_id'] 
        st.markdown("---")
        
        sort_col, check_col = st.columns([1, 1])
        
        with sort_col:
            sort_by = st.selectbox("Sort Table By:", sort_options, 
                                format_func=lambda x: x.replace('_', ' ').title(), 
                                index=1) 
        
        with check_col:
            st.markdown("<br>", unsafe_allow_html=True)
            sort_ascending = st.checkbox('Sort Ascending', value=True if sort_by in ['date', 'expires'] else False) 

        # Apply the explicit Python sort to the DataFrame
        df = df.sort_values(by=sort_by, ascending=sort_ascending, na_position='last')
        
    # 5. Display and Capture Edits 
    with col2:
        edited_df = display_certifications_table(df)
    
    # 6. Save Edits Logic
    if st.session_state['data_edited']:
        if st.button("💾 Save Changes to JSON", type="primary"):
            
            # CRITICAL FIX: Replace Pandas NaT (Not a Time) with Python None 
            edited_df['expires'] = edited_df['expires'].replace({pd.NaT: None})
            
            updated_certs = edited_df.to_dict('records')
            
            save_certs(updated_certs)
            st.success("Changes saved successfully! Rerunning application to display updated data...")
            st.session_state['data_edited'] = False 
            st.rerun()
        
        st.warning("Click 'Save Changes to JSON' to make edits permanent.")
        
        # Use the edited data for immediate feedback in subsequent blocks
        certs_for_display = edited_df.to_dict('records')
    else:
        # Use the original (or sorted) data
        certs_for_display = df.to_dict('records')


    # 7. Display the CE/Expiration Due Soon Block 
    display_due_soon_block(certs_for_display)
    
    # 8. Display Summary Metrics
    display_summary(certs_for_display)

if __name__ == "__main__":
    main()
