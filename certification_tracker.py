# python3 -m pip install streamlit pandas
# streamlit run certification_tracker.py
import streamlit as st
import json
import os
import pandas as pd
from datetime import datetime

# --- Configuration ---
JSON_FILE = 'certifications.json'

# --- JSON Data Management Functions ---

def load_certs():
    """Loads certification data from the JSON file."""
    if not os.path.exists(JSON_FILE):
        return []
    with open(JSON_FILE, 'r') as f:
        try:
            data = json.load(f)
            return data if isinstance(data, list) else []
        except (json.JSONDecodeError, FileNotFoundError):
            return [] 

def save_certs(certs):
    """Saves the current list of certifications to the JSON file."""
    for cert in certs:
        if isinstance(cert.get('date'), (datetime, pd.Timestamp)):
             cert['date'] = cert['date'].strftime('%Y-%m-%d')
        if isinstance(cert.get('expires'), (datetime, pd.Timestamp)):
             cert['expires'] = cert['expires'].strftime('%Y-%m-%d')
        
        if cert.get('expires') is None or cert.get('expires') == "":
             cert['expires'] = "N/A"
        
        if isinstance(cert.get('fee'), (int, float)):
             cert['fee'] = float(cert['fee'])

    with open(JSON_FILE, 'w') as f:
        json.dump(certs, f, indent=4)

# --- Streamlit UI Components ---

def add_certification(certs):
    """Streamlit form to add a new certification."""
    st.subheader("➕ Add New Certification")
    
    with st.form("add_cert_form", clear_on_submit=True):
        new_cert = {}
        
        new_cert['name'] = st.text_input("Certification Name", key="name_input")
        new_cert['issuer'] = st.text_input("Issuing Organization", key="issuer_input")
        
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
                certs.append(new_cert)
                save_certs(certs)
                st.success(f"Added **{new_cert['name']}**! Changes applied.")
                st.rerun() 
            else:
                st.error("Certification Name and Issuer are required.")

def display_certifications_table(certs):
    """Displays all current certifications in a non-editable table, sorted by the selector."""
    st.subheader("📜 Current Certifications (Sorted Table)")
    
    if not certs:
        st.info("No certifications found. Add one using the form.")
        return 
    
    # Data is already sorted in the main function
    df = pd.DataFrame(certs) 
    
    # Define column types for display formatting (not editing)
    column_config = {
        "fee": st.column_config.NumberColumn("Renewal/Annual Fee (USD)", format="$%0.2f"),
        "date": st.column_config.DateColumn("Date Achieved", format="YYYY-MM-DD"),
        "expires": st.column_config.DateColumn("Expiration Date", format="YYYY-MM-DD"),
        "renewal_frequency": "Renewal Frequency" # Simple rename
    }

    # Use st.dataframe for guaranteed display of the pre-sorted data
    st.dataframe(
        df, 
        use_container_width=True, 
        hide_index=True, 
        column_config=column_config,
        # IMPORTANT: rely only on the Python sort.
    )

def display_due_soon_block(certs):
    """Filters and displays certifications ordered by their expiration date."""
    st.markdown("---")
    st.subheader("🗓️ Certifications Due Soon (Next 180 Days)")
    
    today = datetime.now().date()
    due_soon_certs = []
    
    for cert in certs:
        expiry_val = cert.get('expires')
        
        if expiry_val is None or expiry_val == "N/A":
            continue

        try:
            if isinstance(expiry_val, datetime):
                expiry_date = expiry_val.date()
            elif isinstance(expiry_val, str):
                expiry_date = datetime.strptime(expiry_val, '%Y-%m-%d').date()
            else:
                continue
            
            days_left = (expiry_date - today).days
            
            if 0 <= days_left <= 180:
                due_soon_certs.append({
                    'Certification': cert['name'],
                    'Issuer': cert['issuer'],
                    'Expiration Date': expiry_date.strftime('%Y-%m-%d'), 
                    'Renewal Fee': f"${cert.get('fee', 0.00):.2f}",
                    'Days Left': days_left
                })
        except ValueError:
            continue

    if due_soon_certs:
        # Convert to DataFrame and sort by Days Left (ascending) - default for urgency
        due_soon_df = pd.DataFrame(due_soon_certs).sort_values(by='Days Left', ascending=True)
        
        st.warning("These certifications require attention for renewal or CE credits!")
        
        st.dataframe(
            due_soon_df, 
            hide_index=True, 
            use_container_width=True,
            column_order=('Certification', 'Expiration Date', 'Days Left', 'Renewal Fee', 'Issuer')
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
        
        if frequency == 'Annual':
            total_annual_fee += float(fee) if fee else 0
        elif frequency == 'Biennial (Every 2 years)':
            total_annual_fee += (float(fee) / 2.0) if fee else 0
        elif frequency == 'Triennial (Every 3 years)':
            total_annual_fee += (float(fee) / 3.0) if fee else 0
            
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
    
    # 1. Load data
    certs_list = load_certs()
    
    # --- Data Type Conversion and Preparation ---
    if certs_list:
        df = pd.DataFrame(certs_list)
        df['date'] = pd.to_datetime(df['date'], errors='coerce')
        df['expires'] = pd.to_datetime(df['expires'], errors='coerce')
        certs = df.to_dict('records')
    else:
        certs = [] 
    
    # --------------------------------------------------------------------------
    
    # --- Layout ---
    col1, col2 = st.columns([1, 2])
    
    # 2. Add Certification form
    with col1:
        add_certification(certs)

    # 3. Sorting Selector (Guaranteed Sorting)
    if certs:
        # These are the columns available for sorting
        sort_options = ['date', 'expires', 'name', 'issuer', 'fee']
        st.markdown("---")
        
        sort_col, check_col = st.columns([1, 1])
        
        with sort_col:
            sort_by = st.selectbox("Sort Table By:", sort_options, 
                                format_func=lambda x: x.replace('_', ' ').title(), 
                                index=1) # Default to sorting by EXPIRES
        
        with check_col:
            st.markdown("<br>", unsafe_allow_html=True)
            # Default to ascending for dates/expires (earliest first) and descending for fees/names
            sort_ascending = st.checkbox('Sort Ascending', value=True if sort_by in ['date', 'expires'] else False) 

        # Apply the explicit Python sort
        df_to_sort = pd.DataFrame(certs)
        df_to_sort = df_to_sort.sort_values(by=sort_by, ascending=sort_ascending, na_position='last')
        certs = df_to_sort.to_dict('records') # Update the main list with sorted data

    # 4. Display Table (Non-Editable)
    with col2:
        display_certifications_table(certs)

    # 5. Display the CE/Expiration Due Soon Block 
    display_due_soon_block(certs)
    
    # 6. Display Summary Metrics
    display_summary(certs)

if __name__ == "__main__":
    main()
