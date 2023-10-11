import pandas as pd
import numpy as np
import itertools
import networkx as nx
import streamlit as st
import matplotlib.pyplot as plt
from networkx.readwrite import json_graph
from networkx.drawing.nx_agraph import write_dot
from calendar import month_name

# Data creation
# digital_xlsx = pd.ExcelFile('C:\\Users\\vipul.srivastava01\\Desktop\\graph_analysis\\Smart View Customer 360\\data\\Digital.xlsx')
# financial_xlsx = pd.ExcelFile('C:\\Users\\vipul.srivastava01\\Desktop\\graph_analysis\\Smart View Customer 360\\data\\Financial.xlsx')
customer_info_df = pd.read_pickle('customer_info.pkl')
interaction_data_df = pd.read_pickle('interaction_data.pkl')
score_type_df = pd.read_pickle('score_type.pkl')
transaction_utility_df = pd.read_pickle('transaction_utility.pkl')
account_data_df = pd.read_pickle('account_data.pkl')
my_table_df = pd.read_pickle('my_table.pkl')
my_table2_df = pd.read_pickle('my_table2.pkl')
# score_type_df = pd.read_excel(digital_xlsx, 'Score Type')
# st.write(customer_info_df)

# product_data = pd.read_excel(xlsx, 'Product')
# product_payment_schedule_data = pd.read_excel(xlsx, 'Product Payment Schedule')
# transaction_date = pd.read_excel(xlsx, 'Transaction Dates')
# monthly_transaction_history = pd.read_excel(xlsx, 'Monthly Transaction History')

# datetime2string = []
# for i in range(len(transaction_date)):
#     convert2string = transaction_date['Start Date'][i].strftime('%A, %B %d, %Y')
#     datetime2string.append(convert2string)

# transaction_date['Start Date'] = datetime2string

# demographic_data.drop(['Customer ID','Co-Borrower Information'], axis = 'columns', inplace = True)
# st.write(demographic_data)
# st.write(product_data)
# st.write(product_payment_schedule_data)
# st.write(monthly_transaction_history)

# demographic_data.dropna(inplace = True)
# product_data.dropna(inplace = True)
# product_payment_schedule_data.dropna(inplace = True)
# transaction_date.dropna(inplace = True)

# merge_data1 = demographic_data.merge(product_data.dropna(), on = 'Customer ID')
# merge_data2 = merge_data1.merge(product_payment_schedule_data.dropna(), on = 'Customer ID')
# merge_data_3 = merge_data2.merge(product_payment_schedule_data.dropna(), on = 'Customer ID')
# merge_data_4 = merge_data_3.merge(transaction_date.dropna(), on = 'Customer ID')
# merge_data_final = merge_data_4.merge(monthly_transaction_history.dropna(), on = 'Customer ID')

# st.write(merge_data_final)

# merge_data_df = demographic_data.merge(monthly_transaction_history, on = 'Customer ID')
# st.write(merge_data_df)

# Set page configuration
st.set_page_config(
    page_title = 'Graph Analysis (Behavioral Profile)',
    layout = 'wide',
    # initial_sidebar_state = 'expanded'
)

# Define the SessionState class
class SessionState:
    def __init__(self, **kwargs):
        self.__dict__.update(kwargs)

# Define function to get the data with caching
@st.cache_data
def get_data():
    return [customer_info_df, interaction_data_df, score_type_df, transaction_utility_df, account_data_df, my_table_df, my_table2_df]
    # return [demographic_data, product_data, product_payment_schedule_data, transaction_date, monthly_transaction_history]
    # return merge_data_final

# Get the data using the caching function
# demographic_data_df = get_data()[0]
# product_data_df = get_data()[1]
# product_payment_schedule_data_df = get_data()[2]
# transaction_date_df = get_data()[3]
# monthly_transaction_history_df = get_data()[4]
customer_info_df = get_data()[0]
interaction_data_df = get_data()[1]
score_type_df = get_data()[2]
transaction_utility_df = get_data()[3]
account_data_df = get_data()[4]
my_table_df = get_data()[5]
my_table2_df = get_data()[6]

# merge_data = demographic_data_df.merge(transaction_date_df, on = 'Customer ID')
# customer_data_df = merge_data.merge(monthly_transaction_history_df, on = 'Customer ID')

# df = get_data()

# st.write(customer_data_df.dtypes)

session_state = SessionState(
                              customer_id = [],
                              score_type = [],
                              product_type = [],
                              month_name = []
                            )

header_left, header_mid, header_right = st.columns([0.5, 2, 0.5], gap = 'large')

with header_mid:
    st.markdown("<h1 style = 'font-size: 21px; text-align: center; padding-bottom: 5px;'><b>Graph Analysis</b></h1>", unsafe_allow_html = True)
st.divider()

# c1, c2 = st.columns([1, 3], gap = 'large')

with st.sidebar:
    customer_id = st.multiselect(
        label = 'Select Customer ID',
        options = sorted(customer_info_df['Customer ID'].dropna().unique()),
        default = sorted(customer_info_df['Customer ID'].dropna().unique())[0]
    )
    session_state.customer_id = customer_id

    score_type_list = sorted(score_type_df['Score Type'].dropna().unique())
    score_type_keep_list = ['Churn Score', 'Sentiment Score', 'NPS Score', 'Credit Score']
    score_type_final_list = [ele for ele in score_type_list if ele in score_type_keep_list]
    score_type = st.multiselect(
        label = 'Select Score Type',
        options =  score_type_final_list,
        default = score_type_final_list[0]
    )
    session_state.score_type = score_type

    transaction_utility_list = sorted(transaction_utility_df['Product Type'].dropna().unique())
    transaction_utility_keep_list = ['Checking Account', 'Credit Card']
    transaction_utility_final_list = [ele for ele in transaction_utility_list if ele in transaction_utility_keep_list]
    product_type = st.multiselect(
        label = 'Select Product Type',
        options = transaction_utility_final_list,
        default = transaction_utility_final_list[0]
    )
    session_state.product_type = product_type


filtered_data_customer_info = customer_info_df.query('`Customer ID` in @customer_id')
filtered_data_score_type = score_type_df.query('`Customer ID` in @customer_id and `Score Type` in @score_type')
filtered_data_transaction_utility = transaction_utility_df.query('`Customer ID` in @customer_id and `Product Type` in @product_type')
filtered_data_account_data = account_data_df.query('`Customer ID` in @customer_id')
# st.write(filtered_data_account_data)
# st.write(filtered_data_account_data.dtypes)

def convert_int2currency(variable_name):
    rounded_currency = float(format(variable_name, ".2f"))
    currency_format = '{:,}'.format(rounded_currency)
    currency = '$' + str(currency_format)
    return currency

# Card value for Score Profile
churn_score_list = ['Churn Score']
filtered_data_churn_score_type = score_type_df.query('`Customer ID` in @customer_id and `Score Type` in @churn_score_list')
max_churn_score = filtered_data_churn_score_type['Score Value'].max()

sentiment_score_list = ['Sentiment Score']
filtered_data_sentiment_score_type = score_type_df.query('`Customer ID` in @customer_id and `Score Type` in @sentiment_score_list')
max_sentiment_score = filtered_data_sentiment_score_type['Score Value'].max()

nps_score_list = ['NPS Score']
filtered_data_nps_score_type = score_type_df.query('`Customer ID` in @customer_id and `Score Type` in @nps_score_list')
max_nps_score = filtered_data_score_type['Score Value'].max()

credit_score_list = ['Credit Score']
filtered_data_credit_score_type = score_type_df.query('`Customer ID` in @customer_id and `Score Type` in @credit_score_list')
max_credit_score = filtered_data_score_type['Score Value'].max()

rfm_score_list = ['RFM Score']
filtered_data_rfm_score_type = score_type_df.query('`Customer ID` in @customer_id and `Score Type` in @rfm_score_list')
avg_rfm_score = int(filtered_data_rfm_score_type['Score Value'].mean())

default_propensity_score_list = ['Default Propensity Score']
filtered_data_default_propensity_score_type = score_type_df.query('`Customer ID` in @customer_id and `Score Type` in @default_propensity_score_list')
# st.write(score_type_df)
avg_default_propensity_score = int(filtered_data_default_propensity_score_type['Score Value'].mean())

# Card value for Behavioral Profile
mortgage_product_list = ['Mortgage']
filtered_data_mortgage_type = transaction_utility_df.query('`Customer ID` in @customer_id and `Product Type` in @mortgage_product_list')
mortgage_digital_persona = filtered_data_mortgage_type['Digital Persona'].tolist()[-1]
max_mortgage_late_payment = str(int(filtered_data_mortgage_type['Late Payment'].max())) + ' days'

checking_account_product_list = ['Checking Account']
filtered_data_checking_account_type = transaction_utility_df.query('`Customer ID` in @customer_id and `Product Type` in @checking_account_product_list')
checking_account_digital_persona = filtered_data_checking_account_type['Digital Persona'].tolist()[-1]

credit_card_product_list = ['Credit Card']
filtered_data_credit_card_type = transaction_utility_df.query('`Customer ID` in @customer_id and `Product Type` in @credit_card_product_list')
credit_card_digital_persona = filtered_data_credit_card_type['Digital Persona'].tolist()[-1]

personal_loans_product_list = ['Personal Loans']
filtered_data_personal_loans_type = transaction_utility_df.query('`Customer ID` in @customer_id and `Product Type` in @personal_loans_product_list')
personal_loans_digital_persona = filtered_data_personal_loans_type['Digital Persona'].tolist()[-1]
max_personal_loans_late_payment = str(int(filtered_data_personal_loans_type['Late Payment'].max())) + ' days'

tab1, tab2, tab3, tab5 = st.tabs(['General Info', 'Banking Profile', 'Events', 'AI Recommendation'])

# st.write(G.nodes())

# score_type_list = ['Churn Score', 'Sentiment Score', 'NPS Score', 'Credit Score']
# for i in range(len(filtered_data_score_type)):
#     if filtered_data_score_type['Score Type'][i] == 'Churn Score' or filtered_data_score_type['Score Type'][i] == 'Sentiment Score' or filtered_data_score_type['Score Type'][i] == 'NPS Score' or filtered_data_score_type['Score Type'][i] == 'Credit Score':
#         if filtered_data_score_type['Score Type'][i] not in score_type_list:
#             score_type_list.append(filtered_data_score_type['Score Type'][i])

# st.write(score_type_list)
# st.write(month_name_list)
# avg_score_value_list = []
# for i in range(len(score_type_list)):
#     for j in range(len(month_name_list)):
#         score_type = score_type_list[i]
#         month_name = month_name_list[j]
#         filtered_data_score_type_month = filtered_data_score_type.query('`Month Name Score Type` in @month_name and `Score Type` in @score_type')
#         avg_score_value_list.append(int(filtered_data_score_type_month['Score Value'].mean()))

# st.write(avg_score_value_list)
# G.add_node(filtered_data_customer_info['Name'].tolist()[0])

# edge_dict = {'Churn Score': ['April', 'August', 'December', 'February', 'January', 'July', 'June', 'March', 'May', 'November', 'October', 'September'], 'Sentiment Score': ['April', 'August', 'December', 'February', 'January', 'July', 'June', 'March', 'May', 'November', 'October', 'September'], 'NPS Score': ['April', 'August', 'December', 'February', 'January', 'July', 'June', 'March', 'May', 'November', 'October', 'September'], 'Credit Score': ['April', 'August', 'December', 'February', 'January', 'July', 'June', 'March', 'May', 'November', 'October', 'September']}

# dict_list = []
# for i in range(len(score_type_list)):
#     # if len(dict_list) > 0:
#     #     edge_list[score_type_list[i]] = dict_list
#         for j in range(len(month_name_list)): 
#             G.add_node(score_type_list[i])
#             G.add_node(month_name_list[j])
#             dict_list.append(month_name_list[j])
#         edge_list[score_type_list[i]] = dict_list  
# for k in range(len(avg_score_value_list)):
#     G.add_node(avg_score_value_list[k])
#     edge_list.append(avg_score_value_list[k])
    # score_type_node_list.append(score_type_list[i])

# st.write(edge_dict)
# for key, value in edge_dict:
#     for i in value:
#             G.add_edge(filtered_data_customer_info['Name'].tolist()[0], edge_dict[key])
#             G.add_edge(edge_dict[key], value[i])

# st.write(score_type_node_list)
# month_name_node_list = []
# for i in range(len(month_name_list)):
#     G.add_node(month_name_list[i])
#     month_name_node_list.append(month_name_list[i])
# st.write(month_name_node_list)
# avg_score_value_node_list = []
# for i in range(len(avg_score_value_list)):
#     G.add_node(avg_score_value_list[i])
#     avg_score_value_node_list.append(avg_score_value_list[i])
# st.write(avg_score_value_node_list)
# for i in range(len(score_type_node_list)):
#     score_type_edge = score_type_node_list[i]
#     G.add_edge(filtered_data_customer_info['Name'].tolist()[0], score_type_edge)

# for i in range(len(month_name_node_list)):
#     month_name_edge = month_name_node_list[i]
#     G.add_edge(score_type_edge, month_name_edge)

# for i in range(len(avg_score_value_node_list)):
#     avg_score_value_edge = avg_score_value_node_list[i]
#     G.add_edge(month_name_edge, avg_score_value_edge)

# st.write(G.nodes())

with tab1: # General Info 
    # try:
        general_info_e1 = nx.from_pandas_edgelist(df = filtered_data_customer_info, source = 'Name', target = 'Customer ID')
        general_info_e2 = nx.from_pandas_edgelist(df = filtered_data_customer_info, source = 'Name', target = 'Address')
        general_info_e3 = nx.from_pandas_edgelist(df = filtered_data_customer_info, source = 'Address', target = 'City')
        general_info_e4 = nx.from_pandas_edgelist(df = filtered_data_customer_info, source = 'City', target = 'Country')
        general_info_e5 = nx.from_pandas_edgelist(df = filtered_data_customer_info, source = 'Name', target = 'Gender')
        general_info_e6 = nx.from_pandas_edgelist(df = filtered_data_customer_info, source = 'Name', target = 'Income')
        general_info_e7 = nx.from_pandas_edgelist(df = filtered_data_customer_info, source = 'Name', target = 'Dependents')
        general_info_e8 = nx.from_pandas_edgelist(df = filtered_data_customer_info, source = 'Name', target = 'Email')
        general_info_e9 = nx.from_pandas_edgelist(df = filtered_data_customer_info, source = 'Name', target = 'Loyality')
        general_info_e10 = nx.from_pandas_edgelist(df = filtered_data_customer_info, source = 'Name', target = 'Age')

        general_info_e1.add_nodes_from(nodes_for_adding = filtered_data_customer_info['Name'].tolist())
        general_info_e2.add_nodes_from(nodes_for_adding = filtered_data_customer_info['Name'].tolist())
        general_info_e3.add_nodes_from(nodes_for_adding = filtered_data_customer_info['Address'].tolist())
        general_info_e4.add_nodes_from(nodes_for_adding = filtered_data_customer_info['City'].tolist())
        general_info_e5.add_nodes_from(nodes_for_adding = filtered_data_customer_info['Name'].tolist())
        general_info_e6.add_nodes_from(nodes_for_adding = filtered_data_customer_info['Name'].tolist())
        general_info_e7.add_nodes_from(nodes_for_adding = filtered_data_customer_info['Name'].tolist())
        general_info_e8.add_nodes_from(nodes_for_adding = filtered_data_customer_info['Name'].tolist())
        general_info_e9.add_nodes_from(nodes_for_adding = filtered_data_customer_info['Name'].tolist())
        general_info_e10.add_nodes_from(nodes_for_adding = filtered_data_customer_info['Name'].tolist())

        general_info_graph = nx.Graph([tuple(general_info_e1.nodes()), tuple(general_info_e2.nodes()), tuple(general_info_e3.nodes()), tuple(general_info_e4.nodes()), tuple(general_info_e5.nodes()), tuple(general_info_e6.nodes()), tuple(general_info_e7.nodes()), tuple(general_info_e8.nodes()), tuple(general_info_e9.nodes()), tuple(general_info_e10.nodes())])
        
        # F = nx.compose(G, H)

        # st.write(F.nodes)
        # st.write(F.edges)
        # st.write(tuple(customer_details_g1.nodes))
        # st.write(tuple(customer_details_g1.nodes()))
        # data = json_graph.tree_data(G, root = list(g1.nodes)[0])

        # H = json_graph.tree_graph(data)
        # pos = {0:(10, 10), 1:(7.5, 7.5), 2:(12.5, 7.5), 3:(6, 6), 4:(9, 6)}
        # st.pyplot(H)
        # G.add_edges_from([tuple(g1.nodes()), tuple(g2.nodes()), tuple(g3.nodes())])
        # pos = hierarchy_pos(G, )
        # pos = nx.flow_hierarchy(G)
        # nx.tree_graph()
        fig, ax = plt.subplots(figsize = [15, 10])
        pos = nx.spring_layout(general_info_graph, scale = 0.1)     
        # pos = nx.nx_pydot.pydot_layout(G, prog="dot")
        nx.draw_networkx(general_info_graph, pos = pos, node_color = 'Beige', font_size = 7, node_size = 3000, with_labels = True)
        nx.draw_networkx_edge_labels(general_info_graph, pos = pos, edge_labels = {tuple(general_info_e1.nodes()): 'Customer ID', tuple(general_info_e2.nodes()): 'Locality', tuple(general_info_e3.nodes()): 'City', tuple(general_info_e4.nodes()): 'Country', tuple(general_info_e5.nodes()): 'Gender', tuple(general_info_e6.nodes()): 'Annual Income', tuple(general_info_e7.nodes()): 'Dependent', tuple(general_info_e8.nodes()): 'Email', tuple(general_info_e9.nodes()): 'Loyalty', tuple(general_info_e10.nodes()): 'Age'}, font_color = 'blue', font_size = 7)
        # fig, ax = plt.subplots()
        # # draw(nx.ego_graph(G = G, n = 1, radius = 3))
        st.pyplot(fig, use_container_width = True)
    # except:
        # st.write('Please select 1 Customer Name')

with tab2: # Banking Profile 
 # try: 
        # Score Profile
        st.markdown("<h1 style = 'font-size: 19px; text-align: center; padding-bottom: 5px;'><b>Score Profile</b></h1>", unsafe_allow_html = True)

        total1, total2, total3, total4 = st.columns(4, gap = 'medium')
        total5, total6 = st.columns(2, gap = 'medium')

        with total1:
            st.markdown("<style>.metric-label, .metric-value { font-size: 16px !important; }</style>", unsafe_allow_html = True)
            # st.image('icons/Borr intend to continue.png', width = 45)
            st.metric(label = "Churn Score (1-100)", value = max_churn_score)

        with total2:
            st.markdown("<style>.metric-label, .metric-value { font-size: 16px !important; }</style>", unsafe_allow_html = True)
            # st.image('icons/UW Submitted.png', width = 45)
            st.metric(label = "Sentiment Score (1-10)", value = max_sentiment_score)

        with total3:
            st.markdown("<style>.metric-label, .metric-value { font-size: 16px !important; }</style>", unsafe_allow_html = True)
            # st.image('icons/UW Cond Approved.png', width = 35)
            st.metric(label = "NPS Score (1-100)", value = max_nps_score)

        with total4:
            st.markdown("<style>.metric-label, .metric-value { font-size: 16px !important; }</style>", unsafe_allow_html = True)
            # st.image('icons/App Approved.png', width = 45)
            st.metric(label = "Credit Score (100-900)", value = max_credit_score)

        with total5:
            st.markdown("<style>.metric-label, .metric-value { font-size: 16px !important; }</style>", unsafe_allow_html = True)
            # st.image('icons/App clear to close.png', width = 45)
            st.metric(label = "RFM Score", value = avg_rfm_score)

        with total6:
            st.markdown("<style>.metric-label, .metric-value { font-size: 16px !important; }</style>", unsafe_allow_html = True)
            # st.image('icons/App suspended.png', width = 45)
            st.metric(label = "Default Propensity Score", value = avg_default_propensity_score)

        month_name_score_type_list = list(sorted(filtered_data_score_type['Month Name'].unique()))

        avg_score_value_list = []
        for i in range(len(month_name_score_type_list)):
            month_name = month_name_score_type_list[i]
            filtered_data_score_type_month = filtered_data_score_type.query('`Month Name` in @month_name')
            avg_score_value_list.append(int(filtered_data_score_type_month['Score Value'].mean()))
        # st.write(avg_score_value_list)

        score_profile_graph = nx.Graph()

        score_profile_graph.add_node(filtered_data_score_type['Score Type'].tolist()[0])

        for i,j in zip(month_name_score_type_list, avg_score_value_list):
            # G.add_edge(filtered_data_customer_info['Name'].tolist()[0], score_type_list[i])        
            score_profile_graph.add_node(i)
            score_profile_graph.add_node(j)
            score_profile_graph.add_edge(filtered_data_score_type['Score Type'].tolist()[0], i)
            score_profile_graph.add_edge(i, j)

        # G = nx.Graph([tuple(score_type_g1.nodes()), tuple(score_type_g2.nodes())])
        # st.write(G.nodes())
        # st.write(G.nodes.items(0))
        # for i in range(len(G.nodes)):
        #     st.write(G.nodes(i))
        # st.write(G.edges)
        # F = nx.compose(G, H)

        # st.write(F.nodes)
        # st.write(F.edges)
        # st.write(tuple(customer_details_g1.nodes))
        # st.write(tuple(customer_details_g1.nodes()))
        # data = json_graph.tree_data(G, root = list(g1.nodes)[0])

        # H = json_graph.tree_graph(data)
        # pos = {0:(10, 10), 1:(7.5, 7.5), 2:(12.5, 7.5), 3:(6, 6), 4:(9, 6)}
        # st.pyplot(H)
        # G.add_edges_from([tuple(g1.nodes()), tuple(g2.nodes()), tuple(g3.nodes())])
        # pos = hierarchy_pos(G, )
        # pos = nx.flow_hierarchy(G)
        # nx.tree_graph()
        
        fig, ax = plt.subplots(figsize = [15, 10])
        pos = nx.spring_layout(score_profile_graph, scale = 0.1)     
        # pos = nx.nx_pydot.pydot_layout(G, prog="dot")
        nx.draw_networkx(score_profile_graph, pos = pos, node_color = 'Beige', font_size = 7, node_size = 3000, with_labels = True)
        
        # labels = {}
        # for i in range(len(avg_score_value_list)):
        #     labels[tuple(G.nodes(0, i+1))] = avg_score_value_list[i]
        # st.write(labels)

        # nx.draw_networkx_edge_labels(G, pos = pos, edge_labels = labels, font_color = 'blue', font_size = 7)
        # fig, ax = plt.subplots()
        # # draw(nx.ego_graph(G = G, n = 1, radius = 3))
        st.pyplot(fig, use_container_width = True)
        st.markdown("<h6 style = font-size: 3px;'>Number represents Score:</h6>", unsafe_allow_html = True)
        st.markdown("<h6 style = font-size: 3px;'>Churn Score -- (1 - 100) &emsp; NPS Score -- (1 - 100) &emsp; Sentiment Score -- (1 - 10) &emsp; Credit Score -- (100 - 900)</h6>", unsafe_allow_html = True)
        # st.markdown("<h6 style = font-size: 3px;'>Sentiment Score -- (1 - 10)</h6>", unsafe_allow_html = True)
        # st.markdown("<h6 style = font-size: 3px;'>Credit Score -- (100 - 900)</h6>", unsafe_allow_html = True)

        # Behavioral Profile

        st.markdown("<h1 style = 'font-size: 19px; text-align: center; padding-bottom: 5px;'><b>Behavioral Profile</b></h1>", unsafe_allow_html = True)

        total11, total12, total13, total14 = st.columns(4, gap = 'medium')
        total15, total16 = st.columns(2, gap = 'medium')
        with total11:
            st.markdown("<style>.metric-label, .metric-value { font-size: 16px !important; }</style>", unsafe_allow_html = True)
            # st.image('icons/Borr intend to continue.png', width = 45)
            st.metric(label = "Mortgage", value = mortgage_digital_persona)

        with total12:
            st.markdown("<style>.metric-label, .metric-value { font-size: 16px !important; }</style>", unsafe_allow_html = True)
            # st.image('icons/UW Submitted.png', width = 45)
            st.metric(label = "Checking Account", value = checking_account_digital_persona)

        with total13:
            st.markdown("<style>.metric-label, .metric-value { font-size: 16px !important; }</style>", unsafe_allow_html = True)
            # st.image('icons/UW Cond Approved.png', width = 35)
            st.metric(label = "Credit Card", value = credit_card_digital_persona)

        with total14:
            st.markdown("<style>.metric-label, .metric-value { font-size: 16px !important; }</style>", unsafe_allow_html = True)
            # st.image('icons/App Approved.png', width = 45)
            st.metric(label = "Personal Loans", value = personal_loans_digital_persona)

        with total15:
            st.markdown("<style>.metric-label, .metric-value { font-size: 16px !important; }</style>", unsafe_allow_html = True)
            # st.image('icons/App clear to close.png', width = 45)
            st.metric(label = "Mortgage Late Payments", value = max_mortgage_late_payment)

        with total16:
            st.markdown("<style>.metric-label, .metric-value { font-size: 16px !important; }</style>", unsafe_allow_html = True)
            # st.image('icons/App suspended.png', width = 45)
            st.metric(label = "Personal Loans", value = max_personal_loans_late_payment)

        month_name_transaction_utility_list = list(sorted(filtered_data_transaction_utility['Month Name'].unique()))
        digital_persona_list = list(filtered_data_transaction_utility['Digital Persona'].unique())

        sum_transaction_amount_list = []
        for i in range(len(month_name_transaction_utility_list)):
            month_name = month_name_transaction_utility_list[i]
            filtered_data_transaction_utility_month = filtered_data_transaction_utility.query('`Month Name` in @month_name')
            sum_transaction_amount = filtered_data_transaction_utility_month['Transaction Amount'].sum()
            sum_transaction_amount_format = convert_int2currency(sum_transaction_amount)
            sum_transaction_amount_list.append(sum_transaction_amount_format)

        # st.write(avg_score_value_list)

        behavioral_profile_graph = nx.Graph()

        # F.add_node(filtered_data_transaction_utility['Product Type'].tolist()[0])
        # for i in range(len(digital_persona_list)):
        #     F.add_node(digital_persona_list[i])

        for i, j in zip(month_name_transaction_utility_list, sum_transaction_amount_list):
            # G.add_edge(filtered_data_customer_info['Name'].tolist()[0], score_type_list[i])        
            # for k in range(len(digital_persona_list)):
            behavioral_profile_graph.add_node(i)
            behavioral_profile_graph.add_node(j)
            
            # F.add_node(k)
            behavioral_profile_graph.add_edge(filtered_data_transaction_utility['Product Type'].tolist()[0], i)
            # F.add_edge(k, i)
            behavioral_profile_graph.add_edge(i, j)

        st.markdown("<h1 style = 'font-size: 19px; text-align: center; padding-bottom: 5px;'><b>Behavioral Profile</b></h1>", unsafe_allow_html = True)
        fig, ax = plt.subplots(figsize = [15, 10])
        pos = nx.spring_layout(behavioral_profile_graph, scale = 0.1)     
        # pos = nx.nx_pydot.pydot_layout(G, prog="dot")
        nx.draw_networkx(behavioral_profile_graph, pos = pos, node_color = 'Beige', font_size = 7, node_size = 3000, with_labels = True)
        st.pyplot(fig, use_container_width = True)
    # except:
        # st.write('Please select 1 Customer Name')

with tab3: # Events 
    # Life Events
    max_relationship_with_bank = filtered_data_account_data['Relationship with Bank (Years)'].max()
    relationship_with_bank = str(max_relationship_with_bank) + ' years'

    life_events_subgraph1 = nx.Graph()
    
    life_events_subgraph1.add_node(relationship_with_bank)
    life_events_subgraph1.add_edge(filtered_data_customer_info['Name'].tolist()[0], relationship_with_bank)

    life_events_e1 = nx.from_pandas_edgelist(df = filtered_data_customer_info, source = 'Name', target = 'Anniversary Date')
    life_events_e2 = nx.from_pandas_edgelist(df = filtered_data_customer_info, source = 'Name', target = 'Retirement Date')
    life_events_e3 = nx.from_pandas_edgelist(df = filtered_data_customer_info, source = 'Name', target = 'Status')
    life_events_e4 = nx.from_pandas_edgelist(df = filtered_data_customer_info, source = 'Name', target = 'DOB')
    # life_events_e5 = nx.from_pandas_edgelist(df = filtered_data_account_data, source = 'Name', target = 'Relationship with Bank (Years)')
    
    life_events_e1.add_nodes_from(nodes_for_adding = filtered_data_customer_info['Name'].tolist())
    life_events_e2.add_nodes_from(nodes_for_adding = filtered_data_customer_info['Name'].tolist())
    life_events_e3.add_nodes_from(nodes_for_adding = filtered_data_customer_info['Name'].tolist())
    life_events_e4.add_nodes_from(nodes_for_adding = filtered_data_customer_info['Name'].tolist())
    # life_events_e5.add_nodes_from(nodes_for_adding = filtered_data_account_data['Name'].tolist())
    
    life_events_subgraph2 = nx.Graph([tuple(life_events_e1.nodes()), tuple(life_events_e2.nodes()), tuple(life_events_e3.nodes()), tuple(life_events_e4.nodes())])

    life_events_graph = nx.compose(life_events_subgraph2, life_events_subgraph1)
    
    fig, ax = plt.subplots(figsize = [15, 10])
    pos = nx.spring_layout(life_events_graph, scale = 0.1)     
    # pos = nx.nx_pydot.pydot_layout(G, prog="dot")
    nx.draw_networkx(life_events_graph, pos = pos, node_color = 'Beige', font_size = 7, node_size = 3000, with_labels = True)
    nx.draw_networkx_edge_labels(life_events_graph, pos = pos, edge_labels = {tuple(life_events_e1.nodes()): 'Anniversary Date', tuple(life_events_e2.nodes()): 'Retirement Date', tuple(life_events_e3.nodes()): 'Status', tuple(life_events_e4.nodes()): 'DOB', tuple(life_events_subgraph1.nodes()): 'Relationship with Bank'}, font_color = 'blue', font_size = 7)
    # fig, ax = plt.subplots()
    # # draw(nx.ego_graph(G = G, n = 1, radius = 3))
    st.pyplot(fig, use_container_width = True)

#with tab4: # Interaction Preferences
 #   pass

with tab5: # AI Recommendation
    pass
