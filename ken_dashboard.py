#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon Jan 12 14:42:40 2026

@author: michaelmixon
"""

# Import relevant libraries (visualization, dashboard, data manipulation)
import pandas as pd 
import numpy as np 
import plotly.graph_objects as go
import plotly.express as px
import streamlit as st
from datetime import datetime

#Define Functions 
def style_values(v, props=''):
    """Style positive values green, negative values red"""
    try:
        if v > 0:
            return 'color:green;'
        elif v < 0:
            return 'color:red;'
        else:
            return None
    except:
        pass   
    
def audience_simple(country):
    """Show top represented countries"""
    if country == 'US':
        return 'USA'
    elif country == 'IN':
        return 'India'
    else:
        return 'Other'

###############################################################################
# SECTION 1: DATA LOADING AND INITIAL PROCESSING
###############################################################################
# Load the main aggregated video metrics CSV and skip the first row (header row issue)
df_agg = pd.read_csv('Aggregated_Metrics_By_Video.csv').iloc[1:,:]

# Manually set column names to be more descriptive and consistent
df_agg.columns = ['Video','Video title','Video publish time','Comments added','Shares','Dislikes','Likes',
                  'Subscribers lost','Subscribers gained','RPM(USD)','CPM(USD)','Average % viewed','Average view duration',
                  'Views','Watch time (hours)','Subscribers','Your estimated revenue (USD)','Impressions','Impressions ctr(%)']

# Convert the 'Video publish time' column from string to datetime format
# format='mixed' allows pandas to automatically detect various date formats
# dayfirst=False specifies that dates are in month-day-year format (e.g., "Nov 12, 2020")
df_agg['Video publish time'] = pd.to_datetime(df_agg['Video publish time'], format='mixed', dayfirst=False)

# Convert 'Average view duration' from string format (HH:MM:SS) to datetime object
df_agg['Average view duration'] = df_agg['Average view duration'].apply(lambda x: datetime.strptime(x,'%H:%M:%S'))

# Create a new column that converts average view duration to total seconds
# This makes it easier to perform calculations and comparisons
df_agg['Avg_duration_sec'] = df_agg['Average view duration'].apply(lambda x: x.second + x.minute*60 + x.hour*3600)

# Calculate engagement ratio: total engagements divided by views
# Higher ratio indicates more viewer interaction per view
df_agg['Engagement_ratio'] = (df_agg['Comments added'] + df_agg['Shares'] + df_agg['Dislikes'] + df_agg['Likes']) / df_agg.Views

# Calculate efficiency metric: how many views needed to gain one subscriber
# Lower number is better (fewer views needed per new subscriber)
df_agg['Views / sub gained'] = df_agg['Views'] / df_agg['Subscribers gained']

# Sort videos by publish date, newest first
df_agg.sort_values('Video publish time', ascending=False, inplace=True)   

# Load additional datasets for more detailed analysis
df_agg_sub = pd.read_csv('Aggregated_Metrics_By_Country_And_Subscriber_Status.csv')
df_comments = pd.read_csv('All_Comments_Final.csv')
df_time = pd.read_csv('Video_Performance_Over_Time.csv')

# Convert the date column in time series data to datetime format
# dayfirst=True because this dataset uses day-first format (e.g., "30 Sept 2021")
df_time['Date'] = pd.to_datetime(df_time['Date'], format='mixed', dayfirst=True)


###############################################################################
# SECTION 2: CALCULATE BASELINE METRICS (12-MONTH MEDIAN)
###############################################################################
# Create a copy of the dataframe to calculate percentage differences from median
df_agg_diff = df_agg.copy()

# Calculate the date that is 12 months before the most recent video
metric_date_12mo = df_agg_diff['Video publish time'].max() - pd.DateOffset(months=12)

# Calculate the median values for all numeric columns over the last 12 months
# numeric_only=True explicitly tells pandas to only calculate median for numeric columns
# This avoids errors with text columns like 'Video' and 'Video title'
median_agg = df_agg_diff[df_agg_diff['Video publish time'] >= metric_date_12mo].median(numeric_only=True)


###############################################################################
# SECTION 3: NORMALIZE DATA (CALCULATE PERCENTAGE DIFFERENCE FROM MEDIAN)
###############################################################################
# Identify which columns contain numeric data (float or integer types)
# This creates a boolean array: True for numeric columns, False for non-numeric
numeric_cols = np.array((df_agg_diff.dtypes == 'float64') | (df_agg_diff.dtypes == 'int64'))

# Calculate percentage difference from median for each numeric column
# Formula: (value - median) / median gives percentage above/below median
# Example: If median Views = 1000 and a video has 1500 views, result = (1500-1000)/1000 = 0.5 (50% above median)
# .astype('float64') explicitly converts to float to avoid future pandas warnings about dtype incompatibility
df_agg_diff.iloc[:,numeric_cols] = (df_agg_diff.iloc[:,numeric_cols] - median_agg).div(median_agg).astype('float64')


###############################################################################
# SECTION 4: ENGINEER DATA FOR TREND CHART
###############################################################################

#merge daily data with publish data to get delta 
df_time_diff = pd.merge(df_time, df_agg.loc[:,['Video','Video publish time']], left_on ='External Video ID', right_on = 'Video')
df_time_diff['days_published'] = (df_time_diff['Date'] - df_time_diff['Video publish time']).dt.days

# get last 12 months of data rather than all data 
date_12mo = df_agg['Video publish time'].max() - pd.DateOffset(months =12)
df_time_diff_yr = df_time_diff[df_time_diff['Video publish time'] >= date_12mo]

# get daily view data (first 30), median & percentiles 
views_days = pd.pivot_table(df_time_diff_yr,index= 'days_published',values ='Views', aggfunc = [np.mean,np.median,lambda x: np.percentile(x, 80),lambda x: np.percentile(x, 20)]).reset_index()
views_days.columns = ['days_published','mean_views','median_views','80pct_views','20pct_views']
views_days = views_days[views_days['days_published'].between(0,30)]
views_cumulative = views_days.loc[:,['days_published','median_views','80pct_views','20pct_views']] 
views_cumulative.loc[:,['median_views','80pct_views','20pct_views']] = views_cumulative.loc[:,['median_views','80pct_views','20pct_views']].cumsum()


###############################################################################
# SECTION 5: START BUILDING STREAMLIT APP
###############################################################################
# Create sidebar dropdown to choose between aggregate metrics or individual video analysis
add_sidebar = st.sidebar.selectbox('Aggregate or Individual Video', ('Aggregate Metrics','Individual Video Analysis'))


###############################################################################
# SECTION 6: AGGREGATE METRICS VIEW (6-MONTH COMPARISON)
###############################################################################
if add_sidebar == 'Aggregate Metrics':
    # Filter data to last 6 months for recent performance view
    df_agg_metrics = df_agg[['Video publish time','Views','Likes','Subscribers','Shares','Comments added','RPM(USD)','Average % viewed',
                              'Avg_duration_sec', 'Engagement_ratio','Views / sub gained']]
    metric_date_6mo = df_agg_metrics['Video publish time'].max() - pd.DateOffset(months=6)
    df_agg_metrics = df_agg_metrics[df_agg_metrics['Video publish time'] >= metric_date_6mo]
    
    # Calculate median values for 6-month and 12-month periods
    metric_medians6mo = df_agg_metrics.median(numeric_only=True)
    metric_medians12mo = median_agg
    
    # Define which metrics to display in the dashboard
    # These are the key performance indicators (KPIs) for the channel
    metrics_to_display = ['Views', 'Likes', 'Subscribers', 'Shares', 'Comments added', 'RPM(USD)','Average % viewed',
                              'Avg_duration_sec', 'Engagement_ratio','Views / sub gained']
    
    # Create 3 columns layout for displaying metrics
    col1, col2, col3, col4, col5 = st.columns(5)
    columns = [col1, col2, col3, col4, col5]
    
    # Loop through the metrics and display them
    for i, metric in enumerate(metrics_to_display):
        # Determine which column to place this metric in (cycle through col1, col2, col3)
        column_index = i % 5
        
        with columns[column_index]:
            # Calculate the percentage change between 6-month and 12-month medians
            # This shows if performance is improving or declining
            delta = (metric_medians6mo[metric] - metric_medians12mo[metric]) / metric_medians12mo[metric]
            
            # Display the metric using Streamlit's metric component
            # Shows current value, and color-coded change from baseline
            st.metric(
                label=metric,  # Metric name
                value=round(metric_medians6mo[metric], 1),  # Current 6-month median value
                delta="{:.2%}".format(delta)  # Percentage change, formatted as percentage
            )

    df_agg_diff['Publish date'] = df_agg_diff['Video publish time'].apply(lambda x: x.date())
    df_agg_diff_final = df_agg_diff.loc[:,['Video title','Publish date','Views','Likes','Subscribers','Avg_duration_sec','Engagement_ratio']]

    df_agg_numeric_lst = df_agg_diff_final.median(numeric_only=True).index.tolist()
    df_to_pct = {col: '{:.1%}'.format for col in df_agg_numeric_lst}

    st.dataframe(df_agg_diff_final.style.hide().map(style_values).format(df_to_pct))


###############################################################################
# SECTION 7: INDIVIDUAL VIDEO ANALYSIS VIEW
###############################################################################
if add_sidebar == 'Individual Video Analysis':
    # Create dropdown list of videos (showing title and publish date)
    videos = tuple(df_agg['Video title'])
    video_select = st.selectbox('Pick a Video:', videos)
    
    # Find the selected video in the dataframe
    agg_filtered = df_agg[df_agg['Video title'] == video_select]
    agg_sub_filtered = df_agg_sub[df_agg_sub['Video Title'] == video_select]
    agg_sub_filtered['Country'] = agg_sub_filtered['Country Code'].apply(audience_simple)
    agg_sub_filtered.sort_values('Is Subscribed', inplace= True)   
    
    fig = px.bar(agg_sub_filtered, x ='Views', y='Is Subscribed', color ='Country', orientation ='h')
    #order axis 
    st.plotly_chart(fig)

    agg_time_filtered = df_time_diff[df_time_diff['Video Title'] == video_select]
    first_30 = agg_time_filtered[agg_time_filtered['days_published'].between(0,30)]
    first_30 = first_30.sort_values('days_published')

    fig2 = go.Figure()
    fig2.add_trace(go.Scatter(x=views_cumulative['days_published'], y=views_cumulative['20pct_views'],
                    mode='lines',
                    name='20th percentile', line=dict(color='purple', dash ='dash')))
    fig2.add_trace(go.Scatter(x=views_cumulative['days_published'], y=views_cumulative['median_views'],
                        mode='lines',
                        name='50th percentile', line=dict(color='yellow', dash ='dash')))
    fig2.add_trace(go.Scatter(x=views_cumulative['days_published'], y=views_cumulative['80pct_views'],
                        mode='lines', 
                        name='80th percentile', line=dict(color='royalblue', dash ='dash')))
    fig2.add_trace(go.Scatter(x=first_30['days_published'], y=first_30['Views'].cumsum(),
                        mode='lines', 
                        name='Current Video' ,line=dict(color='firebrick',width=8)))
        
    fig2.update_layout(title='View comparison first 30 days',
                   xaxis_title='Days Since Published',
                   yaxis_title='Cumulative views')
    
    st.plotly_chart(fig2)



