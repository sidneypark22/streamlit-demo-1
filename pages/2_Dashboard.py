import streamlit as st
import duckdb
# import sys
# import os
import plotly.express as px
import pandas as pd
# import io
import streamlit_authenticator as stauth
import extra_streamlit_components as stx
import yaml
from yaml.loader import SafeLoader
# from streamlit.web.server.websocket_headers import _get_websocket_headers 
# import json
from st_pages import show_pages, hide_pages, Page

# buffer = io.BytesIO()

# headers = _get_websocket_headers()
# st.write(headers)

st.set_page_config(
    initial_sidebar_state='auto',
    layout='wide',
)

show_pages(
    [
        Page("Home.py", "Home", "🏠"),
        Page("./pages/2_Dashboard.py", "Dashboard"),
        Page("./pages/3_Contact_Us.py", "Contact Us"),
        Page('./pages/99_Login.py', 'Login'),
    ]
)
hide_pages(['Login'])

ss = st.session_state

@st.cache_resource(experimental_allow_widgets=True)
def get_manager():    
    return stx.CookieManager(key='streamlit-demo-1-cookies')
cookie_manager = get_manager()

with st.container(border=False, height=1):
    cookie_manager.set('last_page', './pages/2_Dashboard.py')

cookies = cookie_manager.get_all()

with open('config.yaml') as file:
    config = yaml.load(file, Loader=SafeLoader)

    authenticator = stauth.Authenticate(
        config['credentials'],
        config['cookie']['name'],
        config['cookie']['key'],
        config['cookie']['expiry_days'],
        config['pre-authorized']
    )

authenticator.login()

if ss.get("authentication_status") is None:
    st.switch_page('./pages/99_Login.py')
elif st.session_state["authentication_status"] is False:
    st.error('Username or password is incorrect')
else:
    with st.sidebar.container():
        authenticator.logout()

    if 'base_df' not in ss:
        ss.base_df = duckdb.sql(
            """with cte_car_prices as (
                select *, try_strptime(substring(saledate, 1, 33), '%a %b %d %Y %H:%M:%S %Z') as sale_date
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
        ).df()

    df = ss.base_df.copy()

    # st.markdown(
    #     """
    #     <style>
    #         section[data-testid="stSidebar"] {
    #             width: 300px !important; # Set the width to your desired value
    #         }
    #     </style>
    #     """,
    #     unsafe_allow_html=True,
    # )

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
    
    with st.container(border=False, height=1):
        for fc in filter_columns:
            # st.write(cookie_manager.get(cookie=f'filter_{fc}'))
            # ss[f'filter_{fc}'] = cookie_manager.get(cookie=f'filter_{fc}')
            if f'filter_{fc}' not in ss:
                ss[f'filter_{fc}'] = cookies.get(f'filter_{fc}', [])
            else:
                cookie_manager.set(f'filter_{fc}', ss[f'filter_{fc}'], f'set_cookie_filter_{fc}')
                # cookies[f'filter_{fc}'] = ss[f'filter_{fc}']
            if len(ss[f'filter_{fc}']) == 0:
                pass
            elif 'All' in ss[f'filter_{fc}']:
                pass
            elif None in ss[f'filter_{fc}']:
                pass
            else:
                df = df[df[fc].isin(ss[f'filter_{fc}'])]
                # st.caption(f"Filter applied - {fc.capitalize()}: {ss[f'filter_{fc}']}")
        # cookie_manager.batch_set(cookies)
        # st.write(cookies)
        # st.write(cookie_manager.get_all(key="get_all_2"))
        # st.write(ss.filter_year, ss.filter_make)
    with st.sidebar.form(
        key='form_filter',
        clear_on_submit=False,
        border=False,
    ) as form_filter:
        with st.expander('Filters', expanded=False):
            st.form_submit_button(label='Apply Filters')
            for filter_column in filter_columns:
                filter_key=f'filter_{filter_column}'
                ss[f'{filter_key}_selected'] = ss.get(filter_key, [])
                st.multiselect(
                    label=filter_column.capitalize(),
                    options=['All'] + list(df[filter_column].sort_values().unique()),
                    key=filter_key,
                    default=ss[f'{filter_key}_selected'],
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
            if ss.get('filter_bar_chart_x_axis', None) is not None:
                x_axis_column = ss['filter_bar_chart_x_axis']
                bar_chart_df = duckdb.sql(
                    f"""select {x_axis_column}, sum(selling_price) as selling_price
                    from df
                    --group by {x_axis_column}
                    group by all
                    order by selling_price desc"""
                ).df()
                
                fig_bar = px.bar(
                    bar_chart_df, 
                    x=x_axis_column,
                    y='selling_price',
                )
                fig_bar.update_xaxes(tickangle=270)
                fig_bar.update_layout(xaxis_type='category')
                fig_bar.update_layout(xaxis_title=x_axis_column.capitalize(), yaxis_title='Total Selling Prices')
                st.write(fig_bar)

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
            if ss.add_category_to_line_chart == 'Yes':
                st.selectbox(
                    label='Choose a column for category',
                    key='filter_line_chart_category',
                    options=[c for c in filter_columns if c not in ['year', 'month', 'week', 'year_month']],
                )

        with col2:
            # if ss.get('filter_line_chart_category', None) is not None:
            x_axis_column = 'year_month'
            if ss.add_category_to_line_chart == 'Yes':
                category_column = ss['filter_line_chart_category']
                line_chart_df = duckdb.sql(
                    f"""select {x_axis_column}, {category_column}, sum(selling_price) as selling_price
                    from df
                    group by all
                    order by 1,2
                    """
                ).df()
            else:
                category_column = None
                line_chart_df = duckdb.sql(
                    f"""select {x_axis_column}, sum(selling_price) as selling_price
                    from df
                    group by all
                    order by 1
                    """
                ).df()
                
            fig_line = px.line(
                line_chart_df, 
                x=x_axis_column,
                y='selling_price',
                color=category_column,
            )
            fig_line.update_xaxes(tickangle=270)
            # fig.update_layout(xaxis_type='category')
            fig_line.update_layout(xaxis_title=x_axis_column.replace('_', ' ').capitalize(), yaxis_title='Total Selling Prices')
            st.write(fig_line)


    with st.container():
        st.radio(
            label='Show dataset',
            key='radio_show_dataset',
            options=['No', 'Yes']
        )
        if ss.radio_show_dataset == 'Yes':
            st.dataframe(df)
            with st.expander(
                label='Expand to download data',
            ):
                st.radio(
                    label='Download data',
                    key='radio_download_data',
                    options=['No', 'Yes'],
                )
                if ss.radio_download_data == 'Yes':
                    st.radio(
                        label="Choose output file format",
                        key="radio_choose_output_file_format",
                        options=['CSV', 'Excel'],
                    )
                    if ss.radio_choose_output_file_format == "CSV":
                        st.download_button(
                            label='Download data above',
                            key='download_button_df',
                            data=df.to_csv(index=False, encoding='utf-8'),
                            file_name='output_download.csv',
                            mime='text/csv,'
                        )
                    elif ss.radio_choose_output_file_format == "Excel":
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
