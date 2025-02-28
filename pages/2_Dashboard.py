import streamlit as st
import duckdb
import plotly.express as px
import pandas as pd
import io
import streamlit_authenticator as stauth
import extra_streamlit_components as stx
import yaml
from yaml.loader import SafeLoader
import requests

buffer = io.BytesIO()

st.set_page_config(
    initial_sidebar_state='auto',
    layout='wide',
)

filter_columns = [
    'year',
    'month',
    'week',
    'make',
    'model',
    'trim',
    'body',
    'transmission',
    'vin',
    'state',
    'condition',
    'odometer',
    'color',
    'interior',
    'seller'
]

def get_cookie_manager(key: str = 'init') -> stx.CookieManager:
    @st.cache_resource(experimental_allow_widgets=True)
    def get_manager():
        return stx.CookieManager(key=key)
    cookie_manager = get_manager()
    return cookie_manager

def set_cookie(cookie_manager: stx.CookieManager, cookie: str, value: str) -> bool:
    with st.container(border=False, height=1):
        cookie_manager.set(cookie, value)
        # cookie_manager.set('last_page', './pages/2_Dashboard.py')

def check_authentication(auth_config_file_name: str = 'config.yaml'):
    with open(auth_config_file_name) as file:
        config = yaml.load(file, Loader=SafeLoader)

        authenticator = stauth.Authenticate(
            config['credentials'],
            config['cookie']['name'],
            config['cookie']['key'],
            config['cookie']['expiry_days'],
        )

    authenticator.login()

    if st.session_state["authentication_status"] is None:
        st.switch_page('Home.py')
    else:
        with st.sidebar.container():
            authenticator.logout()
        return True

def get_base_df():
    base_df = duckdb.sql(
        """with cte_car_prices as (
            select *, try_strptime(substring(saledate, 1, 33), '%a %b %d %Y %H:%M:%S GMT%z') as sale_date
            from read_csv('pages/files/car_prices.csv')
            --limit 1000
        )
        select 
            cast(year as string) as year,
            strftime(sale_date, '%m') as month,
            strftime(sale_date, '%d') as week,
            strftime(sale_date, '%Y-%m') as year_month,
            cast(sale_date as timestamp) as sale_date,
            coalesce(make, '') as make,
            coalesce(model, '') as model,
            coalesce(trim, '') as trim,
            coalesce(body, '') as body,
            coalesce(transmission, '') as transmission,
            coalesce(vin, '') as vin,
            coalesce(state, '') as state,
            coalesce(condition, -1) as condition,
            case 
                when odometer is null then 'Unknown'
                when odometer < 50000 then '-50000'
                when odometer >= 50000 and odometer < 100000 then '50000-100000'
                when odometer >= 100000 and odometer < 150000 then '100000-150000'
                when odometer >= 150000 and odometer < 200000 then '150000-200000'
                when odometer >= 200000 and odometer < 250000 then '200000-250000'
                when odometer >= 250000 and odometer < 300000 then '250000-300000'
                when odometer >= 300000 then '300000-'
                else 'Unknown'
            end as odometer,
            odometer as odometer_raw,
            coalesce(color, '') as color,
            coalesce(interior, '') as interior,
            coalesce(seller, '') as seller,
            mmr,
            sellingprice as selling_price
        from cte_car_prices
        """
    )

    return base_df

if __name__ == '__main__':
    if check_authentication():

        cookie_manager = get_cookie_manager(key='streamlit-demo-1-cookies')
        set_cookie(cookie_manager, 'last_page', './pages/2_Dashboard.py')

        if 'base_df' not in st.session_state:
            st.session_state['base_df'] = get_base_df()
        
        df = st.session_state['base_df']

        with st.container(border=False, height=1):
            for filter_column in filter_columns:
                filter_key = f'filter_{filter_column}'
                if filter_key not in st.session_state:
                    st.session_state[filter_key] = cookie_manager.get(filter_key)
                else:
                    cookie_manager.set(filter_key, st.session_state[filter_key], f'set_cookie_{filter_key}')
                if st.session_state[filter_key] is None:
                    st.session_state[filter_key] = []
                elif len(st.session_state[filter_key]) == 0:
                    pass
                elif 'All' in st.session_state[filter_key]:
                    pass
                elif None in st.session_state[filter_key]:
                    pass
                else:
                    df = df[df[filter_column].isin(st.session_state[filter_key])]
        
        with st.sidebar.form(
            key='form_filter',
            clear_on_submit=False,
            border=False,
        ) as form_filter:
            with st.expander('Filters', expanded=False):
                st.form_submit_button(label='Apply Filters')
                # sort_df = df.df() if type(df) == duckdb.duckdb.DuckDBPyRelation else df
                for filter_column in filter_columns:
                    filter_key=f'filter_{filter_column}'
                    st.multiselect(
                        label=filter_column.capitalize(),
                        options=['All'] + list(df[filter_column].sort_values().unique()),
                        key=filter_key,
                        default=st.session_state.get(filter_key, []),
                    )
        
        with st.container():
            col1, col2 = st.columns([1,3])

            with col1:
                st.subheader('Bar Chart Analysis')
                st.selectbox(
                    label='Choose a column for x-axis',
                    key='filter_bar_chart_x_axis',
                    options=filter_columns,
                )
            with col2:
                if st.session_state.get('filter_bar_chart_x_axis', None) is not None:
                    x_axis_column = st.session_state['filter_bar_chart_x_axis']
                    bar_chart_df = duckdb.sql(
                        f"""select {x_axis_column} as {x_axis_column}, sum(selling_price) as selling_price
                        -- sum(selling_price) as selling_price
                        from df
                        group by all
                        order by selling_price desc"""
                    )

                    # st.write(bar_chart_df)
                    
                    fig_bar = px.bar(
                        bar_chart_df, 
                        x=x_axis_column,
                        y='selling_price',
                    )
                    fig_bar.update_xaxes(tickangle=270)
                    fig_bar.update_layout(xaxis_type='category')
                    fig_bar.update_layout(xaxis_title=x_axis_column.capitalize(), yaxis_title='Total Selling Prices')
                    st.plotly_chart(fig_bar)

        with st.container():
            col1, col2 = st.columns([1,3])

            with col1:
                st.subheader('Time Series Line Chart Analysis')
                with st.expander(
                    label='Expand to add category'
                ):
                    st.radio(
                        label='Choose to add category',
                        key='add_category_to_line_chart',
                        options=['No', 'Yes']
                    )
                if st.session_state.add_category_to_line_chart == 'Yes':
                    st.selectbox(
                        label='Choose a column for category',
                        key='filter_line_chart_category',
                        options=[c for c in filter_columns if c not in ['year', 'month', 'week', 'year_month']],
                    )

            with col2:
                x_axis_column = 'year_month'
                if st.session_state.add_category_to_line_chart == 'Yes':
                    category_column = st.session_state['filter_line_chart_category']
                    line_chart_df = duckdb.sql(
                        f"""select {x_axis_column}, {category_column}, sum(selling_price) as selling_price
                        from df
                        group by all
                        order by 1,2
                        """
                    )
                else:
                    category_column = None
                    line_chart_df = duckdb.sql(
                        f"""select {x_axis_column}, sum(selling_price) as selling_price
                        from df
                        group by all
                        order by 1
                        """
                    )
                    
                fig_line = px.line(
                    line_chart_df, 
                    x=x_axis_column,
                    y='selling_price',
                    color=category_column,
                )
                fig_line.update_xaxes(tickangle=270)
                fig_line.update_layout(xaxis_title=x_axis_column.replace('_', ' ').capitalize(), yaxis_title='Total Selling Prices')
                st.write(fig_line)

        with st.container():
            st.radio(
                label='Show dataset',
                key='radio_show_dataset',
                options=['No', 'Yes']
            )
            if st.session_state.radio_show_dataset == 'Yes':
                st.dataframe(df)
                with st.expander(
                    label='Expand to download data',
                ):
                    st.radio(
                        label='Download data',
                        key='radio_download_data',
                        options=['No', 'Yes'],
                    )
                    if st.session_state.radio_download_data == 'Yes':
                        st.radio(
                            label="Choose output file format",
                            key="radio_choose_output_file_format",
                            options=['CSV', 'Excel'],
                        )
                        if st.session_state.radio_choose_output_file_format == "CSV":
                            st.download_button(
                                label='Download data above',
                                key='download_button_df',
                                data=df.to_csv(index=False, encoding='utf-8'),
                                file_name='output_download.csv',
                                mime='text/csv,'
                            )
                        elif st.session_state.radio_choose_output_file_format == "Excel":
                            with pd.ExcelWriter(buffer, engine='xlsxwriter') as writer:
                                df.to_excel(writer, sheet_name='Sheet1', index=False)
                                writer.close()
                                st.download_button(
                                    label='Download data above',
                                    key='download_button_df',
                                    data=buffer,
                                    file_name='output_download.xlsx',
                                    mime="application/vnd.ms-excel"
                                )
