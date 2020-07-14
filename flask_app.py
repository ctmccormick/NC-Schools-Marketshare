from flask import Flask, render_template, url_for
import os
import time
import psycopg2
import pandas as pd
import json
from queries import market_share_query, profile_results, state_market_share_query, tip_leas_raw, parent_leas

app = Flask(__name__)

os.environ["TZ"] = "America/New_York"
time.tzset()

with open("ncschools/static/tableau_links.json", "r") as fp:
    tableau_links = json.load(fp)

c_port = <port>
c_host = <hostname>
c_user = <username>
c_pass = <password>
c_db = <dbname>

conn = psycopg2.connect(host=c_host, port=c_port, dbname=c_db, user=c_user, password=c_pass)


@app.route('/')
def hello_world():
    return 'Hello from Flask!'


data = {'leas': {}}

for result in profile_results:
    lea_name = result[0]
    adm = result[1]
    needy_pct = result[2]
    num_pub_schools = result[3]
    num_charter_schools = result[4]
    names_charter_schools = result[5]
    num_private_schools = result[6]
    num_homeschools = result[7]

    data['leas'][lea_name] = {}
    data['leas'][lea_name]['adm'] = adm
    data['leas'][lea_name]['needy'] = needy_pct
    data['leas'][lea_name]['pub_schools'] = num_pub_schools
    data['leas'][lea_name]['private_schools'] = num_private_schools
    data['leas'][lea_name]['homeschools'] = num_homeschools
    data['leas'][lea_name]['num_charter_schools'] = num_charter_schools
    data['leas'][lea_name]['names_charter_schools'] = names_charter_schools

marketshare = pd.read_sql(market_share_query, con=conn)
marketshare = marketshare.fillna('-')

state_marketshare = pd.read_sql(state_market_share_query, con=conn)

# create and clean state data to match
state_marketshare['order'] = 1
state_marketshare['lea_name'] = 'State'

pct_cols = ['adm_pct', 'charter_pct', 'private_pct', 'home_pct']
for col in state_marketshare.columns:
    if col in pct_cols:
        state_marketshare[col] = state_marketshare[col].apply(lambda x: x * 100)

cols_in_order = ['lea_name', 'total_adm', 'adm_pct', 'charter_enrollment', 'charter_pct', 'private_enrollment'
    , 'private_pct', 'home_enrollment', 'home_pct', 'school_year', 'total_enrollment', 'order']
state_marketshare = state_marketshare[cols_in_order]

all_leas = marketshare['lea_name'].unique()

all_alphabet = 'ABCDEFGHIJKLMNOPQRSTUVWXYZ'

tip_leas = []
for item in tip_leas_raw:
    tip_leas.append(item[0])

tip_alphabet = []
for item in sorted(tip_leas):
    if item[0] not in tip_alphabet:
        tip_alphabet.append(item[0])
    else:
        pass


@app.route("/districts")
def market_share():
    return render_template("lea_links.html", all_leas=all_leas
                           , tip_leas=tip_leas
                           , tip_alphabet=tip_alphabet
                           , all_alphabet=all_alphabet
                           , landing_def='district_profile')


@app.route("/districts/<lea>")
def district_profile(lea):
    if lea in parent_leas:
        child_df = marketshare.loc[marketshare['lea_name'] == lea].copy()
        child_df['order'] = 2

        parent = parent_leas[lea]
        parent_df = marketshare.loc[marketshare['lea_name'] == parent].copy()
        parent_df['order'] = 3

        df = pd.concat([child_df, parent_df, state_marketshare])
        df = df.sort_values(by=['school_year', 'order'], ascending=[False, True])

    else:
        lea_df = marketshare.loc[marketshare['lea_name'] == lea].copy()

        df = pd.concat([lea_df, state_marketshare])
        df = df.sort_values(by=['school_year', 'order'], ascending=[False, True])

    df1617 = df[df['school_year'] == '2016-17']
    df1718 = df[df['school_year'] == '2017-18']
    df1819 = df[df['school_year'] == '2018-19']

    dfs = [df1819, df1718, df1617]

    return render_template("district_profile.html", dfs=dfs
                           , leas=all_leas, profile_data=data, lea=lea
                           , tableau_links=tableau_links
                           , parent_leas=parent_leas
                           )


@app.route("/homeschools/tipdistricts/<lea>")
def tip_homeschools(lea):
    return render_template('homeschool_dashboards.html', leas=tip_leas
                           , alphabet=tip_alphabet, lea=lea, tableau_links=tableau_links)


conn.close()

if __name__ == "__main__":
    app.run()
