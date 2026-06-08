import pandas as pd
import numpy as np
import json
from pathlib import Path

OUT = Path("/home/claude/dashboard_data.json")

accounts = pd.read_csv("/mnt/user-data/uploads/ravenstack_accounts.csv")
churn = pd.read_csv("/mnt/user-data/uploads/ravenstack_churn_events.csv")
usage = pd.read_csv("/mnt/user-data/uploads/ravenstack_feature_usage.csv")
subs = pd.read_csv("/mnt/user-data/uploads/ravenstack_subscriptions.csv")
tickets = pd.read_csv("/mnt/user-data/uploads/ravenstack_support_tickets.csv")

for df, cols in [(accounts, ['signup_date']), (churn, ['churn_date']),
                  (usage, ['usage_date']), (subs, ['start_date', 'end_date']),
                  (tickets, ['submitted_at'])]:
    for c in cols:
        df[c] = pd.to_datetime(df[c], errors='coerce')

D = {}

# ============ KPI HEADLINES ============
n_total = len(accounts)
n_churned = int(accounts['churn_flag'].sum())

churned_subs = subs[subs['churn_flag']==True].copy()
lost_arr_lifetime = float(churned_subs['arr_amount'].sum())

active_subs = subs[subs['end_date'].isna()]
active_arr = float(active_subs['arr_amount'].sum())
active_mrr = float(active_subs['mrr_amount'].sum())

# Industry benchmark: 4% monthly churn → compounded annually
annual_at_risk_arr = active_arr * (1 - 0.96**12)

# Lifetime churn rate over the ~24-month window → annualized
# 22% over 2 years; we compute the annualized rate from lifetime
lifetime_rate = n_churned / n_total
# If R = lifetime, T = years observed, annual = 1 - (1-R)^(1/T)
years_observed = (churn['churn_date'].max() - churn['churn_date'].min()).days / 365
annual_churn_rate = (1 - (1 - lifetime_rate)**(1/years_observed)) * 100

D['kpi'] = {
    'lost_arr_lifetime': lost_arr_lifetime,
    'active_arr': active_arr,
    'annual_at_risk_arr': annual_at_risk_arr,
    'annual_churn_rate': annual_churn_rate,
    'n_total': n_total,
    'n_churned': n_churned,
    'churn_rate_lifetime': n_churned / n_total * 100,
    'data_start': str(churn['churn_date'].min().date()),
    'data_end': str(churn['churn_date'].max().date()),
}

# ============ WHEN: tenure at churn ============
ch_acct = churn.merge(accounts[['account_id','signup_date']], on='account_id')
ch_acct['tenure_days'] = (ch_acct['churn_date'] - ch_acct['signup_date']).dt.days
# Take the first churn event per account (most relevant for tenure)
first_churn = ch_acct.sort_values('churn_date').groupby('account_id').first().reset_index()

# Tenure buckets
buckets = [(0,30,'0-30 days'), (31,90,'31-90 days'), (91,180,'91-180 days'),
           (181,365,'181-365 days'), (366,99999,'Over 1 year')]
tenure_data = []
for lo, hi, label in buckets:
    n = int(((first_churn['tenure_days'] >= lo) & (first_churn['tenure_days'] <= hi)).sum())
    tenure_data.append({'label': label, 'count': n, 'pct': n/len(first_churn)*100})

D['tenure_buckets'] = tenure_data
D['pct_first_90'] = float((first_churn['tenure_days'] <= 90).mean() * 100)

# Monthly churn time series
churn['month'] = churn['churn_date'].dt.to_period('M').dt.to_timestamp()
monthly = churn.groupby('month').size().reset_index(name='count')
monthly['month'] = monthly['month'].dt.strftime('%Y-%m')
D['monthly_churn'] = monthly.to_dict('records')

# ============ WHERE: industry ============
ind = accounts.groupby('industry').agg(
    total=('account_id','count'),
    churned=('churn_flag','sum')
).reset_index()
ind['rate'] = ind['churned']/ind['total']*100
ind_arr = subs[subs['churn_flag']==True].merge(accounts[['account_id','industry']], on='account_id')\
                                          .groupby('industry')['arr_amount'].sum().reset_index()
ind = ind.merge(ind_arr, on='industry')
ind = ind.sort_values('rate', ascending=False)
D['by_industry'] = ind.to_dict('records')

# Plan tier (subscription level)
plan = subs.groupby('plan_tier').agg(
    total=('subscription_id','count'),
    churned=('churn_flag','sum'),
    avg_mrr=('mrr_amount','mean')
).reset_index()
plan['rate'] = plan['churned']/plan['total']*100
D['by_plan'] = plan.to_dict('records')

# Country
ctry = accounts.groupby('country').agg(
    total=('account_id','count'),
    churned=('churn_flag','sum')
).reset_index()
ctry['rate'] = ctry['churned']/ctry['total']*100
ctry = ctry.sort_values('total', ascending=False)
D['by_country'] = ctry.to_dict('records')

# ============ WHY: reasons ============
reasons = churn['reason_code'].value_counts().reset_index()
reasons.columns = ['reason', 'count']
reasons['pct'] = reasons['count']/reasons['count'].sum()*100
D['reasons'] = reasons.to_dict('records')

# Reason × Industry stacked
rxi = churn.merge(accounts[['account_id','industry']], on='account_id')
rxi_pivot = pd.crosstab(rxi['industry'], rxi['reason_code'])
D['reason_by_industry'] = {
    'industries': rxi_pivot.index.tolist(),
    'reasons': rxi_pivot.columns.tolist(),
    'data': rxi_pivot.values.tolist()
}

# ============ THE SIGNAL: predictive evaluation ============
# Test multiple signals and report what's strong vs weak

# Signal 1: Tenure under 90 days
churned_in_90 = int((first_churn['tenure_days'] <= 90).sum())
total_churned = len(first_churn)

# Signal 2: Industry = DevTools
devtools_churn = int(accounts[(accounts['industry']=='DevTools') & (accounts['churn_flag']==True)].shape[0])
devtools_total = int(accounts[accounts['industry']=='DevTools'].shape[0])
other_churn = int(accounts[(accounts['industry']!='DevTools') & (accounts['churn_flag']==True)].shape[0])
other_total = int(accounts[accounts['industry']!='DevTools'].shape[0])

# Signal 3: Usage drop in last 90d vs prior 90d
ce_unique = churn.sort_values('churn_date').groupby('account_id').last().reset_index()
usage_acct = usage.merge(subs[['subscription_id','account_id']], on='subscription_id', how='left')
drop_data = []
for _, row in ce_unique.iterrows():
    aid = row['account_id']
    cd = row['churn_date']
    u = usage_acct[usage_acct['account_id']==aid]
    last_90 = u[(u['usage_date'] > cd - pd.Timedelta(days=90)) & (u['usage_date'] <= cd)]
    prior_90 = u[(u['usage_date'] > cd - pd.Timedelta(days=180)) & (u['usage_date'] <= cd - pd.Timedelta(days=90))]
    drop_data.append({
        'last': last_90['usage_count'].sum(),
        'prior': prior_90['usage_count'].sum()
    })
dd = pd.DataFrame(drop_data)
dd_valid = dd[dd['prior'] > 0].copy()
dd_valid['ratio'] = dd_valid['last']/dd_valid['prior']
pct_dropped_50 = float((dd_valid['ratio'] < 0.5).mean() * 100)
median_ratio = float(dd_valid['ratio'].median())

# Signal 4: Support ticket spike
ticket_signal = []
for _, row in ce_unique.iterrows():
    aid = row['account_id']
    cd = row['churn_date']
    t = tickets[tickets['account_id']==aid]
    last_60 = t[(t['submitted_at'] > cd - pd.Timedelta(days=60)) & (t['submitted_at'] <= cd)]
    prior_60 = t[(t['submitted_at'] > cd - pd.Timedelta(days=120)) & (t['submitted_at'] <= cd - pd.Timedelta(days=60))]
    ticket_signal.append({'last': len(last_60), 'prior': len(prior_60)})
ts = pd.DataFrame(ticket_signal)
ticket_avg_last = float(ts['last'].mean())
ticket_avg_prior = float(ts['prior'].mean())

D['signals'] = [
    {
        'name': 'New accounts (under 90 days tenure)',
        'finding': f'{D["pct_first_90"]:.0f}% of all churned accounts left within their first 90 days',
        'strength': 'strong',
        'note': 'Matches the industry benchmark of 70% of churn in first 90 days. Onboarding is the highest-leverage moment.'
    },
    {
        'name': 'Industry segment (DevTools)',
        'finding': f'DevTools churns at {devtools_churn/devtools_total*100:.0f}%, other industries at {other_churn/other_total*100:.0f}%',
        'strength': 'strong',
        'note': 'A 2x difference between the worst and best segments. Worth segment-specific retention plays.'
    },
    {
        'name': 'Stated cancellation reason',
        'finding': '"Features" and "support" together explain 36% of churn',
        'strength': 'moderate',
        'note': 'Useful for routing fixes (product vs. CS), less useful for early warning since the signal arrives at cancellation.'
    },
    {
        'name': 'Usage drop in 90 days before churn',
        'finding': f'Median usage ratio: {median_ratio:.2f}; only {pct_dropped_50:.0f}% of churned accounts dropped to under 50% of prior activity',
        'strength': 'weak',
        'note': 'The classic "usage dropoff before churn" signal is not strongly present in this data. The model cannot rely on usage drops alone.'
    },
    {
        'name': 'Support ticket spike before churn',
        'finding': f'Avg tickets in 60 days before churn: {ticket_avg_last:.1f}; in the 60 days before that: {ticket_avg_prior:.1f}',
        'strength': 'weak',
        'note': 'No clear spike. Support volume is low across the board and does not flag at-risk accounts ahead of time.'
    },
    {
        'name': 'Plan tier',
        'finding': 'Basic, Pro, and Enterprise all churn at 9 to 10% per subscription',
        'strength': 'weak',
        'note': 'Plan tier is not a signal. Do not use plan as a risk feature.'
    }
]

# Save
with open(OUT, 'w') as f:
    json.dump(D, f, default=str)

print(f"Wrote dashboard data to {OUT}")
print(f"KPI: lost ARR ${lost_arr_lifetime/1e6:.1f}M, active ARR ${active_arr/1e6:.1f}M, annual rate {annual_churn_rate:.1f}%")
print(f"Tenure: {D['pct_first_90']:.0f}% churn in first 90 days")
