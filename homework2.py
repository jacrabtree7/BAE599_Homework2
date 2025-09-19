import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import os

st.set_page_config(page_title="Land & Crop Price Analysis - Crabtree", layout="wide")
st.title("Land and Crop Price Analysis - Crabtree")


# File paths
DATA_DIR = os.path.join(os.path.dirname(__file__), "data")
CROPLAND_FILE = os.path.join(DATA_DIR, "Cropland Value.csv")
CROP_PRICES_FILE = os.path.join(DATA_DIR, "Crop Prices.csv")
PRICE_INDEX_FILE = os.path.join(DATA_DIR, "2ABCFC8E-DCA3-3553-BFF5-B454DB37F6EC.csv")

def safe_read_csv(path):
	df = pd.read_csv(path)
	# strip whitespace from column names
	df.columns = [c.strip().strip('"') for c in df.columns]
	return df

st.header("1. Price of Land by State")
try:
	cropland_df = safe_read_csv(CROPLAND_FILE)
	# Standardize column names
	cropland_df = cropland_df.rename(columns={"Year": "Year", "State": "State", "Value": "Value"})
	# convert Year and Value (cast to str before using .str to avoid accessor errors)
	cropland_df['Year'] = pd.to_numeric(cropland_df['Year'], errors='coerce')
	cropland_df['Value'] = pd.to_numeric(cropland_df['Value'].astype(str).str.replace(',', ''), errors='coerce')

	states = ["KENTUCKY", "INDIANA", "OHIO", "TENNESSEE"]
	# Data file uses uppercase state names; make selection case-insensitive
	# ensure State is string-like before using .str
	if 'State' in cropland_df.columns:
		cropland_df['State_up'] = cropland_df['State'].astype(str).fillna('').str.upper()
	else:
		cropland_df['State_up'] = ''
	years = cropland_df['Year'].dropna().astype(int)
	min_year, max_year = int(years.min()), int(years.max())

	selected_states = st.multiselect("Select states:", states, default=states)
	year_range = st.slider("Select year range:", min_year, max_year, (1997, max_year))

	plot_df = cropland_df[(cropland_df['State_up'].isin(selected_states)) & (cropland_df['Year'].between(*year_range))]
	if plot_df.empty:
		st.info("No cropland data for the selected filters.")
	else:
		fig1 = px.line(plot_df, x="Year", y="Value", color="State_up", labels={"Value": "$ / acre", "State_up": "State"}, title="Cropland Value ($/acre) by State")
		fig1.update_layout(xaxis_title="Year", yaxis_title="Value ($/acre)")
		st.plotly_chart(fig1, use_container_width=True)
except FileNotFoundError:
	st.warning("Cropland Value data not found in data folder.")
except Exception as e:
	st.warning(f"Error processing Cropland Value data: {e}")

st.header("2. Price of Crops (National)")
try:
	crop_df = safe_read_csv(CROP_PRICES_FILE)
	# normalize column names
	crop_df = crop_df.rename(columns={"Year": "Year", "Commodity": "Commodity", "Value": "Value"})
	crop_df['Year'] = pd.to_numeric(crop_df['Year'], errors='coerce')
	# cast Value to str before .str.replace to avoid accessor errors
	crop_df['Value'] = pd.to_numeric(crop_df['Value'].astype(str).str.replace(',', ''), errors='coerce')
	# Commodity names in file appear as CORN, SOYBEANS, WHEAT uppercase; normalize
	# ensure Commodity is string-like before using .str
	if 'Commodity' in crop_df.columns:
		crop_df['Commodity_up'] = crop_df['Commodity'].astype(str).fillna('').str.upper()
	else:
		crop_df['Commodity_up'] = ''

	crops = ["WHEAT", "CORN", "SOYBEANS"]
	years2 = crop_df['Year'].dropna().astype(int)
	min_y2, max_y2 = int(years2.min()), int(years2.max())

	selected_crops = st.multiselect("Select crops:", crops, default=crops)
	year_range2 = st.slider("Select year range for crops:", min_y2, max_y2, (1975, max_y2))

	plot_df2 = crop_df[(crop_df['Commodity_up'].isin(selected_crops)) & (crop_df['Year'].between(*year_range2))]
	if plot_df2.empty:
		st.info("No crop price data for the selected filters.")
	else:
		# map commodity to nicer labels (ensure string type)
		plot_df2['Commodity_label'] = plot_df2['Commodity_up'].astype(str).fillna('').str.title()
		fig2 = px.line(plot_df2, x="Year", y="Value", color="Commodity_label", labels={"Value": "$ / bushel", "Commodity_label": "Crop"}, title="National Crop Prices ($/bushel)")
		fig2.update_layout(xaxis_title="Year", yaxis_title="Price ($/bushel)")
		st.plotly_chart(fig2, use_container_width=True)
except FileNotFoundError:
	st.warning("Crop Prices data not found in data folder.")
except Exception as e:
	st.warning(f"Error processing Crop Prices data: {e}")

st.header("3. Price Received Index Value")
try:
	index_df = safe_read_csv(PRICE_INDEX_FILE)
	index_df = index_df.rename(columns={"Year": "Year", "Commodity": "Commodity", "Value": "Value"})
	# Filter to the Food Commodities Index row
	index_df['Year'] = pd.to_numeric(index_df['Year'], errors='coerce')
	# ensure Value is string-like before using .str.replace
	index_df['Value'] = pd.to_numeric(index_df['Value'].astype(str).str.replace(',', ''), errors='coerce')
	# keep only rows where Commodity indicates FOOD COMMODITIES and Data Item is INDEX FOR PRICE RECEIVED
	# guard missing columns and ensure string operations are safe
	if 'Commodity' in index_df.columns:
		commodity_up = index_df['Commodity'].astype(str).fillna('').str.upper()
	else:
		commodity_up = pd.Series([''] * len(index_df), index=index_df.index)

	if 'Data Item' in index_df.columns:
		data_item_up = index_df['Data Item'].astype(str).fillna('').str.upper()
	else:
		data_item_up = pd.Series([''] * len(index_df), index=index_df.index)

	mask = commodity_up.str.contains('FOOD') & data_item_up.str.contains('INDEX FOR PRICE RECEIVED')
	index_clean = index_df[mask].copy()
	if index_clean.empty:
		st.info("No Price Received Index data found in file.")
	else:
		years3 = index_clean['Year'].dropna().astype(int)
		min_y3, max_y3 = int(years3.min()), int(years3.max())
		year_range3 = st.slider("Select year range for index:", min_y3, max_y3, (1990, max_y3))
		plot_df3 = index_clean[index_clean['Year'].between(*year_range3)]
		fig3 = px.line(plot_df3, x='Year', y='Value', labels={"Value": "Index (2011=100)"}, title='National Price Received Index (2011=100)')
		fig3.update_layout(xaxis_title='Year', yaxis_title='Index Value')
		st.plotly_chart(fig3, use_container_width=True)
except FileNotFoundError:
	st.warning("Price Received Index data not found in data folder.")
except Exception as e:
	st.warning(f"Error processing Price Received Index data: {e}")

