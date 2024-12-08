import pandas as pd
import streamlit as st

class LoadingData:
    def __init__(self, path='Case Study Data new.xlsx'):
        self.path = path

    @staticmethod
    @st.cache_data
    def load_data(path):
        """Load the data from the Excel file."""
        rides = pd.read_excel(path, sheet_name='Rides')
        routes = pd.read_excel(path, sheet_name='Routes')
        bookings = pd.read_excel(path, sheet_name='Bookings')
        BusTypes= pd.read_excel(path, sheet_name='BusTypes')
        rides['ride_timestamp'] = pd.to_datetime(rides['ride_timestamp'])
        rides['month'] = rides['ride_timestamp'].dt.month
        
        return rides, routes, bookings,BusTypes

    def get_data(self):
        return self.load_data(self.path)

class UI:
    def __init__(self, data_loader):
        self.data_loader = data_loader

    def display_filters(self):
        """Display the filtering UI and return user selections."""
        rides, routes, _,_ = self.data_loader.get_data()
        st.subheader("calculates Revenue per Month, Category, and City Pair")
        # Define columns in the layout
        col1, col2, col3, col4 = st.columns([1, 2, 2, 2])
        with col1:
            month = st.selectbox('Month', ['All'] + sorted(rides['month'].unique()))
        with col2:
            category = st.selectbox('Category', ['All'] + sorted(rides['Category'].dropna().unique()))
        with col3:
            first_city = st.selectbox('First City', ['All'] + sorted(routes['first_city'].dropna().unique()))
        with col4:
            last_city = st.selectbox('Last City', ['All'] + sorted(routes['last_city'].dropna().unique()))
        
        return month, category, first_city, last_city

class DataPreparation:
    def __init__(self, data_loader):
        self.data_loader = data_loader

    def prepare_data(self, month, category, first_city, last_city):
        """Prepare and filter the data based on user selections."""
        rides, routes, bookings,BusTypes = self.data_loader.get_data()
        
        # Merge rides and routes
        merged_data = pd.merge(routes, rides, left_on='route_id', right_on='route', how='inner')
        merged_data = merged_data[merged_data['ride_status'] == 'completed']
        
        # Merge with bookings and calculate revenue
        route_ride_booking = pd.merge(
            merged_data, bookings, left_on='ride', right_on='ride_id', how='inner'
        )
        route_ride_booking['Total Revenue'] = route_ride_booking['booking_price_local'] - route_ride_booking['promo_amount']
        route_ride_booking=route_ride_booking[route_ride_booking['booking_price_local']!=0]
        BusTypes = BusTypes.drop_duplicates(subset='bus_types', keep='last')
        route_ride_booking=pd.merge(route_ride_booking,BusTypes,left_on='bus_type',right_on='bus_types',how='inner')
        # Apply filters
        if month != 'All':
            route_ride_booking = route_ride_booking[route_ride_booking['month'] == month]
        if category != 'All':
            route_ride_booking = route_ride_booking[route_ride_booking['Category'] == category]
        if first_city != 'All':
            route_ride_booking = route_ride_booking[route_ride_booking['first_city'] == first_city]
        if last_city != 'All':
            route_ride_booking = route_ride_booking[route_ride_booking['last_city'] == last_city]

        return route_ride_booking,rides, routes, bookings 

class Calculate:
    def __init__(self, data_preparation, month, category, first_city, last_city):
        self.data_preparation = data_preparation
        self.route_ride_booking,self.rides,self.routes,self.bookings  = self.data_preparation.prepare_data(month, category, first_city, last_city)
    def revenue_summary(self):
        """Calculate and display the revenue summary."""
        
        try:
            revenue = self.route_ride_booking.pivot_table(
                values='Total Revenue',
                index=['Category', 'first_city', 'last_city'],
                columns='month',
                aggfunc='sum',
                margins=True,
                margins_name='Total'
            ).fillna(0).sort_values(by='Total', ascending=False)

            # Move the "Total" row to the end
            revenue = pd.concat([revenue.iloc[1:], revenue.iloc[[0]]])
            revenue = revenue[revenue['Total'] != 0]

            st.dataframe(revenue, use_container_width=True)
        except Exception as e:
            pass
    # UTZ
    def UTZ(self):
        st.subheader("UTZ")
        st.write("I really don't know what UTZ means exactly. Due to some circumstances, I was only able to work on this task for a few hours. However, here we can write the code.")
        pass

class App:
    def __init__(self, path='Case Study Data new.xlsx'):
        self.data_loader = LoadingData(path)
        self.ui = UI(self.data_loader)
        self.data_preparation = DataPreparation(self.data_loader)
    def run(self):
        month, category, first_city, last_city = self.ui.display_filters()
        Cal=Calculate(self.data_preparation,month, category, first_city, last_city)
        Cal.revenue_summary()
        Cal.UTZ()

if __name__ == '__main__':
    app = App()
    app.run()
