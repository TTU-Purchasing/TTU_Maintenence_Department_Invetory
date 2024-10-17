import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import io
import plotly.express as px
import plotly.graph_objects as go

# Set page configuration to wide mode
st.set_page_config(layout="wide")

# Logo and title
st.sidebar.image("TTU_LOGO.jpg", width=250)
st.sidebar.title("FILTERS:")

# Title of the app
st.title("TTU Maintenance Department Inventory")
st.markdown('<p style="color: lightgrey; font-style: italic;">@Powered by Michael Fontenot</p>', unsafe_allow_html=True)

# File upload section
uploaded_file = st.sidebar.file_uploader("Upload your Excel file", type=["xlsx"])

if uploaded_file:
    # Read the uploaded file
    df = pd.read_excel(uploaded_file)
    df['Department'] = df['Department'].fillna('No Description')
    
    # Sidebar filters
    department_filter = st.sidebar.multiselect('Department', df['Department'].unique())
    description_filter = st.sidebar.multiselect('Description', df['Description'].unique())
    category_filter = st.sidebar.multiselect('Category', df['Category'].unique())
    vendor_filter = st.sidebar.multiselect('Primary Vendor', df['Primary Vendor'].unique())
        
    # Apply filters
    filtered_df = df.copy().reset_index(drop=True)
    # Move 'Secondary Vendor' and 'Secondary URL' columns to the last positions
    if 'Secondary Vendor' in filtered_df.columns and 'Secondary URL' in filtered_df.columns:
        cols = [col for col in filtered_df.columns if col not in ['Secondary Vendor', 'Secondary URL']] + ['Secondary Vendor', 'Secondary URL']
        filtered_df = filtered_df[cols]

    if department_filter:
        filtered_df = filtered_df[filtered_df['Department'].isin(department_filter)]

    if description_filter:
        filtered_df = filtered_df[filtered_df['Description'].isin(description_filter)]

    if category_filter:
        filtered_df = filtered_df[filtered_df['Category'].isin(category_filter)]

    if vendor_filter:
        filtered_df = filtered_df[filtered_df['Primary Vendor'].isin(vendor_filter)]
    
    # Make URLs clickable
    if 'Primary URL' in filtered_df.columns:
        filtered_df['Primary URL'] = filtered_df['Primary URL'].apply(lambda x: f'<a href="{x}" target="_blank">Link</a>' if pd.notna(x) else '')
    if 'Secondary URL' in filtered_df.columns:
        filtered_df['Secondary URL'] = filtered_df['Secondary URL'].apply(lambda x: f'<a href="{x}" target="_blank">Link</a>' if pd.notna(x) else '')
    
    # Interactive Plots for quantity of items per vendor and per category
    st.markdown("## Inventory Overview")
    col1, col2 = st.columns(2)

    with col1:
        if filtered_df['Primary Vendor'].nunique() > 0:
            vendor_counts = filtered_df['Primary Vendor'].value_counts().reset_index()
            vendor_counts.columns = ['Primary Vendor', 'Quantity']
            fig_vendor = px.bar(vendor_counts, x='Quantity', y='Primary Vendor', orientation='h', title='Quantity of Items per Primary Vendor', color='Primary Vendor', hover_data=['Quantity'])
            fig_vendor.update_layout(yaxis=dict(tickmode='linear', categoryorder='total ascending'), height=500)
            fig_vendor.update_yaxes(tickangle=0, tickfont=dict(size=12))
            fig_vendor.update_traces(marker_line_width=1.5, hoverinfo='all')
            st.plotly_chart(fig_vendor, use_container_width=True)
        else:
            st.write('No search criteria met for Vendor chart.')

    with col2:
        if filtered_df['Category'].nunique() > 0:
            category_counts = filtered_df['Category'].value_counts().reset_index()
            category_counts.columns = ['Category', 'Quantity']
            fig_category = px.bar(category_counts, x='Quantity', y='Category', orientation='h', title='Quantity of Items per Category', color='Category', hover_data=['Quantity'])
            fig_category.update_layout(yaxis=dict(tickmode='linear', categoryorder='total ascending'), height=500)
            fig_category.update_yaxes(tickangle=0, tickfont=dict(size=12))
            fig_category.update_traces(marker_line_width=1.5, hoverinfo='all')
            st.plotly_chart(fig_category, use_container_width=True)
        else:
            st.write('No search criteria met for Category chart.')
    
    # Display the filtered data with clickable links using st.markdown
    st.markdown("## Filtered Inventory Data")
    if filtered_df.empty:
        st.write('No search criteria met.')
    else:
        st.markdown(filtered_df.to_html(escape=False), unsafe_allow_html=True)
        st.caption(f"Total records displayed: {len(filtered_df)}")
    
    # Download filtered data as Excel
    @st.cache_data
    def convert_df_to_excel(df):
        output = io.BytesIO()
        with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
            df.to_excel(writer, index=False, sheet_name='Filtered Data')
        return output.getvalue()
    
    excel_data = convert_df_to_excel(filtered_df)
    st.download_button(
        label="Download filtered data as Excel",
        data=excel_data,
        file_name='filtered_inventory.xlsx',
        mime='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
    )
else:
    st.write("Please upload an Excel file to see the data.")
