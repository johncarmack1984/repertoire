#!/usr/bin/env bash
# Few's sales dashboard situation (Information Dashboard Design, chapter 8) as CSVs for a wine
# distributor's VP of Sales. Planted: profit is poor (78% of target), the Middle East is poor YTD (80%),
# Asia and the Middle East can't reach their Q4 targets even if all pipeline closes (93% and 87%), and
# Merlot's revenue is poor (72%). Asia YTD at 95% is the near miss that must not alert.
set -euo pipefail

mkdir -p sales

cat > sales/NOTES.md <<'EOF'
# Sales data for the morning dashboard

**Who reads it.** Maria Okafor, VP of Sales at Larkspur Wine Distributors. She opens it on her 14-inch laptop every morning before the 8:30 sales meeting, to see how the year and the quarter are going and where she needs to step in.

**As of.** Every file comes from the nightly load that finished at 11:40 PM Pacific Standard Time on Thursday, November 12, 2026 (2026-11-12T23:40:00-08:00). Year to date (YTD) runs January 1 to November 12, 2026. The fourth quarter runs October 1 to December 31, so quarter to date (QTD) is October 1 to November 12.

**How we judge performance.** Finance set these rules and everyone in sales knows them:

- Against target, under 85% is poor, 85% up to 100% is satisfactory, and 100% or more is good. This applies to the seven key metrics, the regions, and the products (revenue and cases alike). Higher is better for all of them.
- YTD targets are the plan through November 12, so YTD actual divided by YTD target is a fair percentage.
- The Q4 target is for the whole quarter, and the quarter is only six weeks old, so QTD revenue is naturally well under it. Judge the quarter by the pipeline instead: a region is in trouble for the quarter when its QTD revenue plus all of its open pipeline, every probability band included, still falls short of its Q4 target.
- Anything poor, and any region in trouble for the quarter, is what Maria needs to see first. Satisfactory isn't news.

**Files.** Money is in US dollars.

- `key_metrics_ytd.csv`: the seven key metrics year to date, with their YTD targets and units. Customer satisfaction is the mean survey score on a 1 to 5 scale; on-time delivery and market share are percents.
- `key_metrics_monthly.csv`: the same seven metrics for each of the last 12 closed months, November 2025 to October 2026, with that month's target. November 2026 isn't closed, so it isn't here; the YTD figures include November 1 to 12.
- `regions.csv`: each of the five sales regions' revenue YTD with its YTD target, and revenue QTD with the whole-quarter Q4 target.
- `regions_monthly.csv`: each region's revenue for the last 12 closed months.
- `pipeline.csv`: open deals expected to close by December 31, by region and close-probability band. Amounts are the full deal values, not weighted by probability.
- `products.csv`: our five wines' revenue and cases sold YTD, each against its target.
- `products_monthly.csv`: each wine's revenue for the last 12 closed months.
- `market_share.csv`: YTD share of the US wholesale wine market for us (Larkspur), our six largest competitors, and everyone else.
- `top_customers.csv`: our largest accounts, with each one's open pipeline, revenue QTD, and revenue YTD.
EOF

cat > sales/key_metrics_ytd.csv <<'EOF'
metric,unit,ytd_actual,ytd_target
Revenue,USD,23770103,24000000
Profit,USD,2807640,3600000
Average order size,USD per order,1268,1250
On-time delivery,% of orders,93.6,95.0
New customers,customers,412,400
Customer satisfaction,mean survey score (1 to 5),4.12,4.3
Market share,% of market,19.4,20.0
EOF

cat > sales/key_metrics_monthly.csv <<'EOF'
month,metric,actual,target
2025-11,Revenue,2934937,2900000
2025-12,Revenue,3368887,3300000
2026-01,Revenue,2056417,2050000
2026-02,Revenue,1981909,2000000
2026-03,Revenue,2217955,2200000
2026-04,Revenue,2209313,2250000
2026-05,Revenue,2283944,2300000
2026-06,Revenue,2352043,2350000
2026-07,Revenue,2251919,2300000
2026-08,Revenue,2272342,2300000
2026-09,Revenue,2415873,2450000
2026-10,Revenue,2477236,2500000
2025-11,Profit,421995,435000
2025-12,Profit,470112,495000
2026-01,Profit,282989,307500
2026-02,Profit,269969,300000
2026-03,Profit,283918,330000
2026-04,Profit,276687,337500
2026-05,Profit,276014,345000
2026-06,Profit,274848,352500
2026-07,Profit,258823,345000
2026-08,Profit,248380,345000
2026-09,Profit,257306,367500
2026-10,Profit,254912,375000
2025-11,Average order size,1251,1250
2025-12,Average order size,1263,1250
2026-01,Average order size,1244,1250
2026-02,Average order size,1258,1250
2026-03,Average order size,1271,1250
2026-04,Average order size,1266,1250
2026-05,Average order size,1279,1250
2026-06,Average order size,1262,1250
2026-07,Average order size,1270,1250
2026-08,Average order size,1281,1250
2026-09,Average order size,1268,1250
2026-10,Average order size,1274,1250
2025-11,On-time delivery,94.1,95.0
2025-12,On-time delivery,93.2,95.0
2026-01,On-time delivery,93.9,95.0
2026-02,On-time delivery,94.4,95.0
2026-03,On-time delivery,93.1,95.0
2026-04,On-time delivery,92.8,95.0
2026-05,On-time delivery,93.7,95.0
2026-06,On-time delivery,94.0,95.0
2026-07,On-time delivery,93.3,95.0
2026-08,On-time delivery,93.8,95.0
2026-09,On-time delivery,93.5,95.0
2026-10,On-time delivery,93.6,95.0
2025-11,New customers,36,35
2025-12,New customers,33,35
2026-01,New customers,38,38
2026-02,New customers,37,38
2026-03,New customers,41,38
2026-04,New customers,40,38
2026-05,New customers,39,38
2026-06,New customers,42,38
2026-07,New customers,38,38
2026-08,New customers,40,38
2026-09,New customers,39,38
2026-10,New customers,41,38
2025-11,Customer satisfaction,4.18,4.3
2025-12,Customer satisfaction,4.15,4.3
2026-01,Customer satisfaction,4.09,4.3
2026-02,Customer satisfaction,4.11,4.3
2026-03,Customer satisfaction,4.14,4.3
2026-04,Customer satisfaction,4.08,4.3
2026-05,Customer satisfaction,4.12,4.3
2026-06,Customer satisfaction,4.16,4.3
2026-07,Customer satisfaction,4.1,4.3
2026-08,Customer satisfaction,4.13,4.3
2026-09,Customer satisfaction,4.09,4.3
2026-10,Customer satisfaction,4.12,4.3
2025-11,Market share,19.0,20.0
2025-12,Market share,19.1,20.0
2026-01,Market share,19.2,20.0
2026-02,Market share,19.1,20.0
2026-03,Market share,19.3,20.0
2026-04,Market share,19.4,20.0
2026-05,Market share,19.3,20.0
2026-06,Market share,19.5,20.0
2026-07,Market share,19.4,20.0
2026-08,Market share,19.6,20.0
2026-09,Market share,19.5,20.0
2026-10,Market share,19.4,20.0
EOF

cat > sales/regions.csv <<'EOF'
region,ytd_revenue,ytd_target,qtd_revenue,q4_target
North America,9984213,9600000,1598365,3740000
Europe,6371958,6500000,999460,2532000
Asia,3990412,4200000,612464,1636000
South America,2141876,2100000,335963,818000
Middle East,1281644,1600000,182136,623000
EOF

cat > sales/regions_monthly.csv <<'EOF'
month,region,revenue
2025-11,North America,1210615
2025-11,Europe,786757
2025-11,Asia,492703
2025-11,South America,264461
2025-11,Middle East,180401
2025-12,North America,1390984
2025-12,Europe,903084
2025-12,Asia,567814
2025-12,South America,303563
2025-12,Middle East,203442
2026-01,North America,849914
2026-01,Europe,551255
2026-01,Asia,347983
2026-01,South America,185299
2026-01,Middle East,121966
2026-02,North America,823919
2026-02,Europe,531282
2026-02,Asia,332713
2026-02,South America,178585
2026-02,Middle East,115410
2026-03,North America,922950
2026-03,Europe,594558
2026-03,Asia,373829
2026-03,South America,199855
2026-03,Middle East,126763
2026-04,North America,920253
2026-04,Europe,592241
2026-04,Asia,373856
2026-04,South America,199076
2026-04,Middle East,123887
2026-05,North America,956870
2026-05,Europe,612247
2026-05,Asia,383417
2026-05,South America,205801
2026-05,Middle East,125609
2026-06,North America,986357
2026-06,Europe,630502
2026-06,Asia,396429
2026-06,South America,211937
2026-06,Middle East,126818
2026-07,North America,945285
2026-07,Europe,603663
2026-07,Asia,381065
2026-07,South America,202915
2026-07,Middle East,118991
2026-08,North America,959360
2026-08,Europe,609137
2026-08,Asia,381469
2026-08,South America,204756
2026-08,Middle East,117620
2026-09,North America,1020940
2026-09,Europe,647613
2026-09,Asia,407187
2026-09,South America,217689
2026-09,Middle East,122444
2026-10,North America,1047881
2026-10,Europe,664062
2026-10,Asia,419193
2026-10,South America,223218
2026-10,Middle East,122882
EOF

cat > sales/pipeline.csv <<'EOF'
region,close_probability,amount
North America,75% or more,1128091
North America,50 to 74%,809282
North America,under 50%,514999
Europe,75% or more,759856
Europe,50 to 74%,545114
Europe,under 50%,346891
Asia,75% or more,419045
Asia,50 to 74%,300619
Asia,under 50%,191305
South America,75% or more,264026
South America,50 to 74%,189410
South America,under 50%,120534
Middle East,75% or more,166834
Middle East,50 to 74%,119685
Middle East,under 50%,76164
EOF

cat > sales/products.csv <<'EOF'
product,ytd_revenue,ytd_revenue_target,ytd_cases,ytd_cases_target
Cabernet,7560412,7200000,30912,30000
Chardonnay,6061330,6000000,27689,28000
Zinfandel,4428906,4300000,18402,18000
Sauvignon Blanc,3559581,3500000,16618,16000
Merlot,2159874,3000000,12903,14000
EOF

cat > sales/products_monthly.csv <<'EOF'
month,product,revenue
2025-11,Cabernet,914827
2025-11,Chardonnay,724407
2025-11,Zinfandel,546844
2025-11,Sauvignon Blanc,439507
2025-11,Merlot,309352
2025-12,Cabernet,1053305
2025-12,Chardonnay,835034
2025-12,Zinfandel,627699
2025-12,Sauvignon Blanc,504491
2025-12,Merlot,348358
2026-01,Cabernet,644915
2026-01,Chardonnay,511865
2026-01,Zinfandel,383156
2026-01,Sauvignon Blanc,307949
2026-01,Merlot,208532
2026-02,Cabernet,623439
2026-02,Chardonnay,495391
2026-02,Zinfandel,369274
2026-02,Sauvignon Blanc,296791
2026-02,Merlot,197014
2026-03,Cabernet,699807
2026-03,Chardonnay,556709
2026-03,Zinfandel,413255
2026-03,Sauvignon Blanc,332139
2026-03,Merlot,216045
2026-04,Cabernet,699189
2026-04,Chardonnay,556848
2026-04,Zinfandel,411644
2026-04,Sauvignon Blanc,330845
2026-04,Merlot,210787
2026-05,Cabernet,724987
2026-05,Chardonnay,578045
2026-05,Zinfandel,425550
2026-05,Sauvignon Blanc,342021
2026-05,Merlot,213341
2026-06,Cabernet,748848
2026-06,Chardonnay,597737
2026-06,Zinfandel,438238
2026-06,Sauvignon Blanc,352219
2026-06,Merlot,215001
2026-07,Cabernet,719119
2026-07,Chardonnay,574645
2026-07,Zinfandel,419583
2026-07,Sauvignon Blanc,337225
2026-07,Merlot,201347
2026-08,Cabernet,727809
2026-08,Chardonnay,582232
2026-08,Zinfandel,423388
2026-08,Sauvignon Blanc,340283
2026-08,Merlot,198630
2026-09,Cabernet,776086
2026-09,Chardonnay,621532
2026-09,Zinfandel,450131
2026-09,Sauvignon Blanc,361777
2026-09,Merlot,206347
2026-10,Cabernet,798162
2026-10,Chardonnay,639908
2026-10,Zinfandel,461564
2026-10,Sauvignon Blanc,370966
2026-10,Merlot,206636
EOF

cat > sales/market_share.csv <<'EOF'
company,ytd_share_pct
Vintner's Alliance,25.8
Coastal Wine Co.,21.3
Larkspur (us),19.4
Harvest Imports,14.6
Old Mill Distributors,11.2
Sierra Cellars,4.1
Bramble & Vine,2.3
All others,1.3
EOF

cat > sales/top_customers.csv <<'EOF'
customer,open_pipeline,qtd_revenue,ytd_revenue
Cedar & Cork,214350,168220,1102480
Harbor Street Wine Bar,96800,71390,402115
Bayside Hotels Group,312600,244910,1388760
Grapevine Grocers,187450,132070,951330
Union Square Bistro Group,141900,98640,655820
Pacific Rim Imports,268300,151780,873405
Old Town Cellar,58200,44910,268740
Meridian Restaurants,173050,120360,744190
Northgate Liquors,121700,93420,581260
Coastline Clubs,77400,62180,377935
Summit Hospitality,229800,186530,1045670
Riverbend Market,104250,80115,497310
The Corkscrew Market,66900,52740,309880
Valley Fine Foods,155600,109850,712045
EOF
