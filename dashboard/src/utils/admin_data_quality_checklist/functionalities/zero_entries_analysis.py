import json
import os
import sys
import traceback
import streamlit as st
import pandas as pd
import requests
import plotly.express as px
from dotenv import load_dotenv
from src.utils.admin_data_quality_checklist.helpers.graph_functions import plot_pie_chart

load_dotenv()

# Add the parent directory to the Python path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

API_BASE_URL = os.getenv("API_BASE_URL")

ZERO_ENTRIES_ENDPOINT = f"{API_BASE_URL}/zero_entries"

def zero_entries_analysis(uploaded_file, df):
    st.session_state.drop_export_rows_complete = False
    st.session_state.drop_export_entries_complete = False
    st.subheader("Zero Entries Analysis")
    st.write("The function returns the count and percentage of zero values for a variable, with optional filtering and grouping by a categorical variable.")
    with st.expander("ℹ️ Info"):
        st.markdown("""
        - Analyzes zero entries in a specified column of the dataset.
        - Options:
        - Select a column to analyze
        - Optionally group by a categorical variable
        - Optionally filter by a categorical variable
        - Provides the count and percentage of zero entries.
        - Displays a table of rows with zero entries.
        - Valid input format: CSV file
        """)

    column_to_analyze = st.selectbox("Select column to analyze", df.columns.tolist())
    group_by = st.selectbox("Group by (optional): Analyze missing entries within distinct categories of another column. This is useful if you want to understand how missing values are distributed across different groups.", ["None"] + df.columns.tolist())
    filter_by_col = st.selectbox("Filter by (optional): Focus on a specific subset of your data by selecting a specific value in another column. This is helpful when you want to analyze missing entries for a specific condition.", ["None"] + df.columns.tolist())

    if filter_by_col != "None":
        filter_by_value = st.selectbox("Filter value", df[filter_by_col].unique().tolist())

    if st.button("Analyze Zero Entries"):
        with st.spinner("Analyzing zero entries..."):
            try:
                uploaded_file.seek(0)  # Reset file pointer
                files = {"file": ("uploaded_file.csv", uploaded_file, "text/csv")}
                payload = {
                    "column_to_analyze": column_to_analyze,
                    "group_by": group_by if group_by != "None" else None,
                    "filter_by": {filter_by_col: filter_by_value} if filter_by_col != "None" else None
                }
                response = requests.post(
                    ZERO_ENTRIES_ENDPOINT,
                    files=files,
                    data={"input_data": json.dumps(payload)}
                )
                
                if response.status_code == 200:
                    result = response.json()
                    st.success("Analysis complete!")
                    
                    if result["grouped"]:
                        st.write("Zero entries by group:")
                        group_column_name = group_by  # Use the selected group-by column name
                        grouped_data = [{group_column_name: group, "Zero Count": count, "Zero Percentage": f"{percentage:.2f}%"}
                                        for group, (count, percentage) in result["analysis"].items()]
                        grouped_df = pd.DataFrame(grouped_data)
                        grouped_df = grouped_df.sort_values("Zero Count", ascending=False)
                        st.dataframe(grouped_df, use_container_width=True)
                        
                        data = pd.DataFrame([(group, percentage, 100-percentage) for group, (count, percentage) in result["analysis"].items()],
                                            columns=[group_column_name, 'Zero', 'Non-Zero'])
                        data = data.sort_values('Zero', ascending=False)
                        fig = px.bar(data, x=group_column_name, y=['Zero', 'Non-Zero'], 
                                    title=f"Zero vs Non-Zero Entries by {group_column_name}",
                                    labels={'value': 'Percentage', 'variable': 'Entry Type'},
                                    color_discrete_map={'Zero': '#1f77b4', 'Non-Zero': '#ff7f0e'})
                        fig.update_layout(barmode='relative', yaxis_title='Percentage')
                        fig.update_traces(texttemplate='%{y:.1f}%', textposition='inside')
                        st.plotly_chart(fig)
                    else:
                        count, percentage = result["analysis"]
                        analysis_df = pd.DataFrame([{"Zero Count": count, "Zero Percentage": f"{percentage:.2f}%"}])
                        st.dataframe(analysis_df, use_container_width=True)
                        
                        labels = ['Zero', 'Non-Zero']
                        values = [percentage, 100-percentage]
                        fig = plot_pie_chart(labels, values, "Zero vs Non-Zero Entries (%)")
                        st.plotly_chart(fig)
                    
                    if result["filtered"]:
                        st.info(f"Results are filtered by {filter_by_col} = {filter_by_value}")
                    
                    # Display the table of zero entries
                    if "zero_entries_table" in result:
                        zero_entries_df = pd.DataFrame(result["zero_entries_table"])
                        if column_to_analyze in zero_entries_df.columns:
                            zero_entries_df = zero_entries_df.sort_values(column_to_analyze, ascending=False)
                        else:
                            st.warning(f"Column '{column_to_analyze}' not found in the zero entries table. Displaying unsorted data.")
                        st.write("Rows with Zero Entries:")
                        st.dataframe(zero_entries_df, use_container_width=True)
                else:
                    st.error(f"Error: {response.status_code} - {response.text}")
            except Exception as e:
                st.error(f"An error occurred: {str(e)}")
                st.write("Traceback:", traceback.format_exc())