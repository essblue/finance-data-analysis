import streamlit as st
import plotly.express as px
import pandas as pd
import os
import warnings

warnings.filterwarnings ('ignore')

st.set_page_config(page_title="KPI Dashboard", page_icon=":bar_chart:",layout="wide")
st.title(":bar_chart: Sample")
st.markdown('<style> div.block-container{padding-top:1erm;}<style>', unsafe_allow_html=True)

#file Uploader
fl= st.file_uploader(":file_folder: Upload a file ", type=(["csv","txt","xlxs","xls"]))

default_file = r"C:\Users\essbl\Downloads\Sample - Superstore.csv"
if fl:
    df = pd.read_csv(fl, encoding="ISO-8859-1",sep=";", on_bad_lines='warn')
    st.write(f"Using uploaded file: {fl.name}")
elif os.path.exists(default_file):  # ✅ Check if the file actually exists
    df = pd.read_csv(default_file, encoding="ISO-8859-1", sep=";",on_bad_lines='warn')
    st.write("Using default file: Sample - Superstore.csv")
else:
    st.error("No file uploaded, and default file not found!")
    df = None


#if fl is not None:
   # filename = fl.name
    #st.write(filename)
    #df = pd.read_csv(filename, encoding="ISO-8859-1")
#else:
#    os.chdir (r"C:\Users\essbl\OneDrive\Documents\Streamlit")
#    df = pd.read_csv( "Superstore.csv" , encoding="ISO-8859-1")
#st.write("Columns in dataset:", df.columns.tolist())  # Debug column names
# Proceed only if DataFrame is loaded
if df is not None:
    #st.write("Columns in dataset:", df.columns.tolist())  # Debugging

    # Standardize column names
    df.columns = df.columns.str.strip()  # Remove spaces
    df.columns = df.columns.str.lower()  # Convert to lowercase

    # Check for 'order date' column
    if "order date" in df.columns:
        #st.write("Unique values in Order Date column:", df["order date"].unique())  # Debugging

        # Remove non-date values
        df = df[df["order date"].astype(str).str.match(r"\d{1,2}/\d{1,2}/\d{4}", na=False)]

        # Convert Order Date to datetime
        df["order date"] = pd.to_datetime(df["order date"].astype(str), dayfirst=True, errors="coerce")
    else:
        st.error("❌ 'Order Date' column not found!")

    # Display DataFrame
    #st.write(df.head())
#Date Picker
col1, col2 = st.columns((2))
df["order date"] = pd.to_datetime(df["order date"].astype(str), dayfirst=True, errors ="coerce")

# Getting the min and the max date 
startDate = pd.to_datetime (df["order date"]).min()
endDate = pd.to_datetime(df["order date"]).max()

with col1:
     date1 = pd.to_datetime(st.date_input("Start Date", startDate))

with col2:
     date2 = pd.to_datetime(st.date_input ("End Date",endDate ))

df = df[(df["order date"]>= date1) & (df["order date"]<= date2)]. copy()

#Create for Region
st.sidebar.header ("Choose your filter: ")
region = st.sidebar.multiselect("Select Region", df["region"].unique())
if not region:
     df2 = df.copy()
else:
     df2 = df[df["region"].isin(region)]

#Create for State
state = st.sidebar.multiselect("Select State", df2["state"].unique())
if not state:
     df3 = df2.copy()
else:
     df3 = df2[df["state"].isin(state)]

#Create for City 

city = st.sidebar.multiselect("Select City", df3["city"].unique())
# Filter the data based on Region, State and City

if not region and not state and not city:
     filtered_df = df
elif not state and not city:
     filtered_df = df[df["region"].isin(region)]
elif not region and not city:
     filtered_df = df[df["state"].isin(state)]
elif state and city:
     filtered_df = df3[df["state"].isin(state)& df3["city"].isin(city)]
elif region and city:
     filtered_df = df3[df["rzgion"].isin(region)& df3["city"].isin(city)]
elif region and state:
     filtered_df = df3[df["region"].isin(region)& df3["state"].isin(state)]
elif city:
     filtered_df = df3[df3["city"].isin(city)]
else:
     filtered_df = df3[df3["region"].isin(region)& df3["state"].isin(state)&df3["city"].isin(city)]



# Replace commas with dots to correctly interpret decimal values
filtered_df["sales"] = filtered_df["sales"].str.replace(",", ".")

# Convert to numeric
filtered_df["sales"] = pd.to_numeric(filtered_df["sales"], errors="coerce").fillna(0)

category_df = filtered_df.groupby(by =["category"], as_index= False)["sales"].sum()

# Convert the 'sales' column to numeric if it isn't already
category_df["sales"] = pd.to_numeric(category_df["sales"], errors="coerce")

with col1:
     st.subheader("Sales Category")
     fig = px.bar(category_df, x = "category", y = "sales", text=[f'$ {x :,.2f}' for x in category_df["sales"]], 
                  template = "seaborn")
     st.plotly_chart(fig, use_container_width= True, height=200)
with col1:
     st.subheader("Regional Sales")
     fig = px.pie(filtered_df, values = "sales", names ="region", hole = 0.5)
     fig.update_traces(text = filtered_df["region"], textposition = "outside")
     st.plotly_chart(fig, use_container_width= True)

# Download Data
cl1, cl2 = st.columns((2))
with cl1:
    with st.expander("Category_ViewData"):
        st.write(category_df.style.background_gradient(cmap="Blues"))
        csv = category_df.to_csv(index = False).encode('utf-8')
        st.download_button("Download Data", data = csv, file_name = "Category.csv", mime = "text/csv",
                            help = 'Click here to download the data as a CSV file')

with cl2:
    with st.expander("Region_ViewData"):
        region = filtered_df.groupby(by = "region", as_index = False)["sales"].sum()
        st.write(region.style.background_gradient(cmap="Oranges"))
        csv = region.to_csv(index = False).encode('utf-8')
        st.download_button("Download Data", data = csv, file_name = "Region.csv", mime = "text/csv",
                        help = 'Click here to download the data as a CSV file')
# Time Series Analysis

filtered_df["month_year"] = filtered_df["order date"].dt.to_period("M")
st.subheader('Time Series Analysis')

linechart = pd.DataFrame(filtered_df.groupby(filtered_df["month_year"].dt.strftime("%Y : %b"))["sales"].sum()).reset_index()
fig2 = px.line(linechart, x = "month_year", y = "sales", labels = {"sales" : "amount"}, height = 500, width = 1000, template = "gridon")
st.plotly_chart(fig2, use_container_width= True)

with st.expander ("View Data of Time Series:"):
     st.write(linechart.T.style.background_gradient(cmap="Blues"))
     csv = linechart.to_csv(index=False).encode("utf-8")
     st.download_button('Download Data', data =csv, file_name = "TimeSeies.csv", mime = 'text/csv')
# Create a Tree map based on region, category and sub-category 
st.subheader("Hierarchal View of Sales Using Treemap ")
fig3 = px.treemap(filtered_df, path = ["region", "category", "sub-category"], values ="sales", hover_data = ["sales"], 
                  color = "sub-category")
fig3.update_layout(width= 800, height= 650)
st.plotly_chart(fig3, use_container_width=True)

#Include Segments
chart1, chart2 = st.columns((2))
with chart1:
     st.subheader('Sales by Segment')
     fig = px.pie(filtered_df, values = "sales", names = "segment", template = "plotly_dark")
     fig.update_traces(text = filtered_df["segment"], textposition = "inside")
     st.plotly_chart(fig, use_container_width=True)

with chart2:
     st.subheader('Sales by Category')
     fig = px.pie(filtered_df, values = "sales", names = "category", template = "gridon")
     fig.update_traces(text = filtered_df["category"], textposition = "inside")
     st.plotly_chart(fig, use_container_width=True)

import plotly.figure_factory as ff
st.subheader(":point_right: Monthly Sub-category Sales Summary")
with st.expander("Summary_table"):
     df_sample = df[0:5][["region", "state", "city", "category", "sales", "profit", "quantity"]]
     fig = ff.create_table(df_sample, colorscale = "Cividis")
     st.plotly_chart(fig, use_container_width=True)

     st.markdown("Monthly Sales Sub-category Table")
     filtered_df["month"] = filtered_df["order date"].dt.month_name()
     sub_category_Year = pd.pivot_table(data = filtered_df, values = "sales", index =["sub-category"], columns= "month")
     st.write (sub_category_Year.style.background_gradient(cmap="Blues"))
#Create a Scatter Plot
data1 = px.scatter(filtered_df, x ="sales", y = "profit", size = "quantity")

data1.update_layout(
    title=dict(text="Sales vs Profits Scatter Plot", font=dict(size=20)),  
    xaxis=dict(title=dict(text="Sales", font=dict(size=19))), 
    yaxis=dict(title=dict(text="Profit", font=dict(size=19)))  
)

st.plotly_chart(data1,use_container_width=True)

with st.expander("View Data"):
     st.write (filtered_df.iloc[:500, 1:20:2].style.background_gradient(cmap="Oranges"))

#Download Original Data
csv = df.to_csv(index = False).encode('utf-8')
st.download_button('Download Data', data = csv, file_name = "Data.csv", mime = "text/csv")