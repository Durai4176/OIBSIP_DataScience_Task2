import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots

# Set page configuration
st.set_page_config(page_title="Unemployment Analysis in India", layout="wide")

# Set random seed for reproducibility
np.random.seed(42)

@st.cache_data
def load_data():
    csv_path = "C:\\Users\\kumar\\OneDrive\\Desktop\\streamlit\\internship\\oasis\\Unemployment_in_India.csv"
    df = pd.read_csv(csv_path)
    
    # Clean column names by removing leading/trailing spaces
    df.columns = df.columns.str.strip()
    
    # Convert date to datetime format - handle leading spaces and use dayfirst parameter
    df['Date'] = pd.to_datetime(df['Date'].str.strip(), dayfirst=True)
    
    # Extract year and month for easier analysis
    df['Year'] = df['Date'].dt.year
    df['Month'] = df['Date'].dt.month
    df['Month_Name'] = df['Date'].dt.strftime('%b')
    
    return df

def main():
    st.title("📊 Unemployment Analysis in India")
    st.markdown("""
    This app analyzes unemployment trends in India, with a focus on the impact of Covid-19.
    Explore the data through various visualizations and insights.
    """)
    
    # Load data
    df = load_data()
    
    # Create sections for different analyses
    st.markdown("## 📈 Overview")
    
    # Overview section
    st.header("Unemployment Overview in India")
    
    # Display basic information about the dataset
    st.subheader("Dataset Information")
    col1, col2 = st.columns(2)
    with col1:
        st.write(f"Number of records: {df.shape[0]}")
        st.write(f"Time period: {df['Date'].min().strftime('%b %Y')} to {df['Date'].max().strftime('%b %Y')}")
    with col2:
        st.write(f"Number of regions: {df['Region'].nunique()}")
        st.write(f"Areas covered: {', '.join([str(area) for area in df['Area'].unique()])}")
    
    # Display first few rows of the dataset
    st.subheader("Sample Data")
    st.dataframe(df.head())
    
    # Overall unemployment trend
    st.subheader("Overall Unemployment Rate Trend")
    
    # Group by date and calculate average unemployment rate
    monthly_data = df.groupby('Date')['Estimated Unemployment Rate (%)'].mean().reset_index()
    
    # Create a line chart using Plotly
    fig = px.line(
        monthly_data, 
        x='Date', 
        y='Estimated Unemployment Rate (%)',
        title='Average Monthly Unemployment Rate in India',
        labels={'Estimated Unemployment Rate (%)': 'Unemployment Rate (%)', 'Date': 'Month-Year'},
        markers=True
    )
    
    # Add text annotation for Covid-19 lockdown
    st.markdown("**Note:** The Covid-19 lockdown in India began on March 24, 2020, which significantly impacted unemployment rates.")
    
    # Update layout
    fig.update_layout(height=500)
    st.plotly_chart(fig, use_container_width=True)
    
    # Unemployment by area (Rural vs Urban)
    st.subheader("Rural vs Urban Unemployment")
    
    # Group by date and area
    area_data = df.groupby(['Date', 'Area'])['Estimated Unemployment Rate (%)'].mean().reset_index()
    
    # Create a line chart with multiple lines
    fig = px.line(
        area_data, 
            x='Date', 
            y='Estimated Unemployment Rate (%)',
            color='Area',
            title='Rural vs Urban Unemployment Rate',
            labels={'Estimated Unemployment Rate (%)': 'Unemployment Rate (%)', 'Date': 'Month-Year'},
            markers=True
        )
        
    # Add text note about Covid-19 instead of vertical line
    st.caption("Note: The Covid-19 lockdown began on March 24, 2020")
    
    # Update layout
    fig.update_layout(height=500)
    st.plotly_chart(fig, use_container_width=True)
    
    # Distribution of unemployment rates
    st.subheader("Distribution of Unemployment Rates")
    
    col1, col2 = st.columns(2)
    
    with col1:
        # Histogram
        fig = px.histogram(
            df, 
            x='Estimated Unemployment Rate (%)',
            nbins=30,
            title='Histogram of Unemployment Rates',
            color_discrete_sequence=['#3366CC']
        )
        st.plotly_chart(fig, use_container_width=True)
        
    with col2:
        # Box plot by area
        fig = px.box(
            df, 
            x='Area', 
            y='Estimated Unemployment Rate (%)',
            title='Unemployment Rate Distribution by Area',
            color='Area'
        )
        st.plotly_chart(fig, use_container_width=True)
    
    # Regional Analysis Section
    st.markdown("## 🔍 Regional Analysis")
    st.header("Regional Unemployment Analysis")
    
    # Region selector
    all_regions = sorted([str(region) for region in df['Region'].unique()])
    selected_regions = st.multiselect(
        "Select regions to compare:",
        options=all_regions,
        default=all_regions[:5]  # Default to first 5 regions
    )
        
    if not selected_regions:
        st.warning("Please select at least one region to display.")
    else:
        # Filter data for selected regions
        filtered_df = df[df['Region'].isin(selected_regions)]
        
        # Time period selector
        time_period = st.slider(
            "Select time period:",
            min_value=df['Date'].min().to_pydatetime(),
            max_value=df['Date'].max().to_pydatetime(),
            value=(df['Date'].min().to_pydatetime(), df['Date'].max().to_pydatetime()),
            format="MMM YYYY"
        )
        
        # Filter by time period
        filtered_df = filtered_df[
            (filtered_df['Date'] >= time_period[0]) & 
            (filtered_df['Date'] <= time_period[1])
        ]
        
        # Area selector
        area_options = ['Both', 'Rural', 'Urban']
        selected_area = st.radio("Select area:", area_options, horizontal=True)
        
        if selected_area != 'Both':
            filtered_df = filtered_df[filtered_df['Area'] == selected_area]
        
        # Regional comparison
        st.subheader("Regional Unemployment Rate Comparison")
        
        # Group by region and calculate average unemployment rate
        region_data = filtered_df.groupby('Region')['Estimated Unemployment Rate (%)'].mean().reset_index()
        region_data = region_data.sort_values('Estimated Unemployment Rate (%)', ascending=False)
        
        # Create a bar chart
        fig = px.bar(
            region_data, 
            x='Region', 
            y='Estimated Unemployment Rate (%)',
            title=f'Average Unemployment Rate by Region ({selected_area})',
            color='Estimated Unemployment Rate (%)',
            color_continuous_scale='Viridis'
        )
        
        # Update layout
        fig.update_layout(height=500)
        st.plotly_chart(fig, use_container_width=True)
            
        # Regional trends over time
        st.subheader("Regional Unemployment Trends Over Time")
        
        # Group by region and date
        region_time_data = filtered_df.groupby(['Region', 'Date'])['Estimated Unemployment Rate (%)'].mean().reset_index()
        
        # Create a line chart
        fig = px.line(
            region_time_data, 
            x='Date', 
            y='Estimated Unemployment Rate (%)',
            color='Region',
            title=f'Unemployment Rate Trends by Region ({selected_area})',
            labels={'Estimated Unemployment Rate (%)': 'Unemployment Rate (%)', 'Date': 'Month-Year'},
            markers=True
        )
        
        # Add Covid-19 lockdown note
        st.caption("Note: India's COVID-19 lockdown began on March 24, 2020, significantly impacting unemployment rates.")
        
        # Update layout
        fig.update_layout(height=600)
        st.plotly_chart(fig, use_container_width=True)
            
        # Correlation with employment and labor participation
        st.subheader("Correlation Analysis")
        
        # Calculate correlation for each region
        correlation_data = []
        for region in selected_regions:
            region_df = filtered_df[filtered_df['Region'] == region]
            
            # Calculate correlations
            corr_employment = region_df['Estimated Unemployment Rate (%)'].corr(region_df['Estimated Employed'])
            corr_labor = region_df['Estimated Unemployment Rate (%)'].corr(region_df['Estimated Labour Participation Rate (%)'])
            
            correlation_data.append({
                'Region': region,
                'Correlation with Employment': corr_employment,
                'Correlation with Labor Participation': corr_labor
            })
        
        corr_df = pd.DataFrame(correlation_data)
        
        col1, col2 = st.columns(2)
        
        with col1:
            # Correlation with employment
            fig = px.bar(
                corr_df, 
                x='Region', 
                y='Correlation with Employment',
                title='Correlation between Unemployment Rate and Employment',
                color='Correlation with Employment',
                color_continuous_scale='RdBu_r'
            )
            fig.update_layout(height=400)
            st.plotly_chart(fig, use_container_width=True)
        
        with col2:
            # Correlation with labor participation
            fig = px.bar(
                corr_df, 
                x='Region', 
                y='Correlation with Labor Participation',
                title='Correlation between Unemployment Rate and Labor Participation',
                color='Correlation with Labor Participation',
                color_continuous_scale='RdBu_r'
            )
            fig.update_layout(height=400)
            st.plotly_chart(fig, use_container_width=True)
    
    # Covid-19 Impact Analysis Section
    st.markdown("## 🦠 Covid-19 Impact")
    st.header("Covid-19 Impact Analysis")
    
    # Define pre and post Covid periods
    pre_covid_start = pd.to_datetime('2019-05-01')
    pre_covid_end = pd.to_datetime('2020-02-29')
    post_covid_start = pd.to_datetime('2020-03-01')
    post_covid_end = pd.to_datetime('2020-06-30')
    
    # Filter data for pre and post Covid
    pre_covid_df = df[(df['Date'] >= pre_covid_start) & (df['Date'] <= pre_covid_end)]
    post_covid_df = df[(df['Date'] >= post_covid_start) & (df['Date'] <= post_covid_end)]
    
    # Calculate average unemployment rates
    pre_covid_avg = pre_covid_df['Estimated Unemployment Rate (%)'].mean()
    post_covid_avg = post_covid_df['Estimated Unemployment Rate (%)'].mean()
    percent_change = ((post_covid_avg - pre_covid_avg) / pre_covid_avg) * 100
    
    # Display key metrics
    st.subheader("Key Covid-19 Impact Metrics")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.metric(
            "Pre-Covid Avg. Unemployment", 
            f"{pre_covid_avg:.2f}%"
        )
    
    with col2:
        st.metric(
            "Post-Covid Avg. Unemployment", 
            f"{post_covid_avg:.2f}%", 
            f"{percent_change:.2f}%"
        )
    
    with col3:
        # Calculate most affected region
        region_impact = []
        for region in df['Region'].unique():
            pre = pre_covid_df[pre_covid_df['Region'] == region]['Estimated Unemployment Rate (%)'].mean()
            post = post_covid_df[post_covid_df['Region'] == region]['Estimated Unemployment Rate (%)'].mean()
            change = post - pre
            region_impact.append({'Region': region, 'Change': change})
        
        region_impact_df = pd.DataFrame(region_impact)
        most_affected = region_impact_df.loc[region_impact_df['Change'].idxmax()]
        
        st.metric(
            "Most Affected Region", 
            most_affected['Region'], 
            f"{most_affected['Change']:.2f}%"
        )
        
    # Pre vs Post Covid comparison
    st.subheader("Pre vs Post Covid-19 Unemployment Comparison")
    
    # Create comparison data
    comparison_data = [
        {'Period': 'Pre-Covid (May 2019 - Feb 2020)', 'Unemployment Rate': pre_covid_avg},
        {'Period': 'Post-Covid (Mar 2020 - Jun 2020)', 'Unemployment Rate': post_covid_avg}
    ]
    
    comparison_df = pd.DataFrame(comparison_data)
    
    # Create a bar chart
    fig = px.bar(
        comparison_df, 
        x='Period', 
        y='Unemployment Rate',
        title='Average Unemployment Rate: Pre vs Post Covid-19',
        color='Period',
        text_auto='.2f'
    )
    
    # Update layout
    fig.update_layout(height=400)
    st.plotly_chart(fig, use_container_width=True)
        
    # Monthly trend during Covid
    st.subheader("Monthly Unemployment Trend During Covid-19")
    
    # Filter data for the Covid period (Jan 2020 - Jun 2020)
    covid_period_df = df[(df['Date'] >= pd.to_datetime('2020-01-01')) & (df['Date'] <= post_covid_end)]
    
    # Group by date
    covid_monthly = covid_period_df.groupby('Date')['Estimated Unemployment Rate (%)'].mean().reset_index()
    
    # Create a line chart
    fig = px.line(
        covid_monthly, 
        x='Date', 
        y='Estimated Unemployment Rate (%)',
        title='Monthly Unemployment Rate During Covid-19 Period',
        labels={'Estimated Unemployment Rate (%)': 'Unemployment Rate (%)', 'Date': 'Month'},
        markers=True
    )
    
    # Add Covid-19 lockdown note
    st.caption("Note: India's COVID-19 lockdown began on March 24, 2020, significantly impacting unemployment rates.")
    
    # Update layout
    fig.update_layout(height=500)
    st.plotly_chart(fig, use_container_width=True)
        
    # Regional impact of Covid
    st.subheader("Regional Impact of Covid-19")
    
    # Calculate impact for each region
    region_impact_full = []
    for region in df['Region'].unique():
        pre = pre_covid_df[pre_covid_df['Region'] == region]['Estimated Unemployment Rate (%)'].mean()
        post = post_covid_df[post_covid_df['Region'] == region]['Estimated Unemployment Rate (%)'].mean()
        change = post - pre
        percent = (change / pre) * 100 if pre > 0 else 0
        region_impact_full.append({
            'Region': region, 
            'Pre-Covid Rate': pre, 
            'Post-Covid Rate': post, 
            'Absolute Change': change,
            'Percentage Change': percent
        })
    
    region_impact_df = pd.DataFrame(region_impact_full)
    region_impact_df = region_impact_df.sort_values('Absolute Change', ascending=False)
        
    # Create a bar chart
    fig = px.bar(
        region_impact_df.head(10), 
        x='Region', 
        y='Absolute Change',
        title='Top 10 Regions Most Affected by Covid-19 (Absolute Change in Unemployment Rate)',
        color='Absolute Change',
        color_continuous_scale='Reds',
        text_auto='.2f'
    )
    
    # Update layout
    fig.update_layout(height=500)
    st.plotly_chart(fig, use_container_width=True)
    
    # Rural vs Urban impact
    st.subheader("Rural vs Urban Covid-19 Impact")
    
    # Calculate pre and post covid averages for rural and urban areas
    rural_pre = pre_covid_df[pre_covid_df['Area'] == 'Rural']['Estimated Unemployment Rate (%)'].mean()
    rural_post = post_covid_df[post_covid_df['Area'] == 'Rural']['Estimated Unemployment Rate (%)'].mean()
    urban_pre = pre_covid_df[pre_covid_df['Area'] == 'Urban']['Estimated Unemployment Rate (%)'].mean()
    urban_post = post_covid_df[post_covid_df['Area'] == 'Urban']['Estimated Unemployment Rate (%)'].mean()
    
    # Calculate percentage changes
    rural_change_pct = ((rural_post - rural_pre) / rural_pre) * 100 if rural_pre > 0 else 0
    urban_change_pct = ((urban_post - urban_pre) / urban_pre) * 100 if urban_pre > 0 else 0
    
    # Create comparison data
    area_impact_data = [
        {'Area': 'Rural', 'Period': 'Pre-Covid', 'Rate': rural_pre},
        {'Area': 'Rural', 'Period': 'Post-Covid', 'Rate': rural_post},
        {'Area': 'Urban', 'Period': 'Pre-Covid', 'Rate': urban_pre},
        {'Area': 'Urban', 'Period': 'Post-Covid', 'Rate': urban_post}
    ]
    
    area_impact_df = pd.DataFrame(area_impact_data)
    
    # Create a grouped bar chart
    fig = px.bar(
        area_impact_df, 
        x='Area', 
        y='Rate',
        color='Period',
        barmode='group',
        title='Rural vs Urban Unemployment: Pre and Post Covid-19',
        text_auto='.2f'
    )
    
    # Update layout
    fig.update_layout(height=500)
    st.plotly_chart(fig, use_container_width=True)
    
    # Display percentage changes
    col1, col2 = st.columns(2)
    with col1:
        st.metric("Rural Unemployment Change", f"{rural_change_pct:.2f}%")
    with col2:
        st.metric("Urban Unemployment Change", f"{urban_change_pct:.2f}%")

if __name__ == "__main__":
    main()