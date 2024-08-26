import streamlit as st

def initialize_states():
    if "analysis_complete" not in st.session_state:
        st.session_state.analysis_complete = False
    if "num_duplicates" not in st.session_state:
        st.session_state.num_duplicates = 0
    if "duplicates_removed" not in st.session_state:
        st.session_state.duplicates_removed = False
    if "deduplicated_data_ready" not in st.session_state:
        st.session_state.deduplicated_data_ready = False
    if "previous_uploaded_file" not in st.session_state:
        st.session_state.previous_uploaded_file = None
    if "navbar_selection" not in st.session_state:
        st.session_state.navbar_selection = "Unique ID Verifier"
    if "drop_export_complete" not in st.session_state:
        st.session_state.drop_export_complete = False
    if "previous_file_option" not in st.session_state:
        st.session_state.previous_file_option = None
    if "uploaded_file" not in st.session_state:
        st.session_state.uploaded_file = None
    if "uploaded_file_id" not in st.session_state:
        st.session_state.uploaded_file_id = None

def reset_session_states():
    st.session_state.analysis_complete = False
    st.session_state.num_duplicates = 0
    st.session_state.duplicates_removed = False
    st.session_state.deduplicated_data_ready = False

def reset_upload():
    st.session_state.reset_upload = False
    st.session_state.analysis_complete = False
    st.session_state.num_duplicates = 0
    st.session_state.duplicates_removed = False
    st.session_state.deduplicated_data_ready = False
    st.session_state.previous_uploaded_file = None