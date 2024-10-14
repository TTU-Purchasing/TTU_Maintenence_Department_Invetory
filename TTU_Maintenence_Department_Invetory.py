import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
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
    df['Department Relation'] = df['Department Relation'].fillna('No Description')
    
    # Sidebar filters (excluding the URL column)
    department_filter = st.sidebar.multiselect('Department Relation', df['Department Relation'].unique())
    item_description_filter = st.sidebar.multiselect('Item Description', df['Name'].unique())
    item_type_filter = st.sidebar.multiselect('Item Type', df['Type'].unique())
    vendor_name_filter = st.sidebar.multiselect('Vendor Name', df['Vendor'].unique())
        
    # Apply filters
    filtered_df = df.copy().reset_index(drop=True)
    # Move 'Secondary Vendor (Higher Price)' column to the last position
    if 'Secondary Vendor (Higher Price)' in filtered_df.columns:
        cols = [col for col in filtered_df.columns if col != 'Secondary Vendor (Higher Price)'] + ['Secondary Vendor (Higher Price)']
        filtered_df = filtered_df[cols]

    if department_filter:
        filtered_df = filtered_df[filtered_df['Department Relation'].isin(department_filter)]

    if item_description_filter:
        filtered_df = filtered_df[filtered_df['Name'].isin(item_description_filter)]

    if item_type_filter:
        filtered_df = filtered_df[filtered_df['Type'].isin(item_type_filter)]

    if vendor_name_filter:
        filtered_df = filtered_df[filtered_df['Vendor'].isin(vendor_name_filter)]
    
    # Display the filtered data
    if filtered_df.empty:
        st.write('No search criteria met.')
    else:
        st.dataframe(filtered_df, height=min(400, 50 + len(filtered_df) * 35))
        st.caption(f"Total records displayed: {len(filtered_df)}")
    
    # Additional info
    st.caption(f"Total records displayed: {len(filtered_df)}")
    
    # Interactive Plot for quantity of items per vendor
    if filtered_df['Vendor'].nunique() > 0:
        vendor_counts = filtered_df['Vendor'].value_counts().reset_index()
        vendor_counts.columns = ['Vendor', 'Quantity']
        fig = px.bar(vendor_counts, x='Quantity', y='Vendor', orientation='h', title='Quantity of Items per Vendor', color='Vendor', color_discrete_sequence=px.colors.qualitative.Light24)
        fig.update_layout(yaxis=dict(tickmode='linear', categoryorder='total ascending'), height=600, width=1000)
        fig.update_yaxes(tickangle=0, tickfont=dict(size=12))
        fig.update_traces(marker_line_width=1.5, hoverinfo='all')
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.write('No search criteria met for Vendor chart.')
    
        
    # 3. Heatmap of Correlations (if numerical columns exist)
    if filtered_df.select_dtypes(include=['number']).shape[1] > 1:
        st.subheader("Correlation Heatmap")
        fig = px.imshow(filtered_df.corr(), text_auto=True, color_continuous_scale='coolwarm', title='Correlation Heatmap')
        fig.update_layout(height=500)
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.write('No numerical data available for correlation heatmap.')
    
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