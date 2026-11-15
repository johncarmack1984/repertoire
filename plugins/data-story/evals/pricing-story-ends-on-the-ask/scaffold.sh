#!/usr/bin/env bash
# The pricing example from Storytelling with Data (chapter 8): average retail price by year for
# five competing products, a draft slide whose headline the data doesn't support, and five
# minutes in front of the person who sets the price. Values were read off the book's chart.
set -euo pipefail

mkdir -p pricing

cat > pricing/NOTES.md <<'EOF'
# Pricing review: notes

We launch our first product next spring and have to set its retail price. Five products are already on the market, A to E. `prices.csv` has each one's average retail price for every year it has been sold.

- Thursday's pricing review is run by the VP of Product, who makes the call on our price. I have five minutes of it, presenting live, with slides on the screen.
- She knows the five products but hasn't seen their prices over time.
- Finance is comfortable with a launch price anywhere from $150 to $200, and that is what I want to recommend.

`first-slide.md` is the slide an analyst drafted last week.
EOF

cat > pricing/prices.csv <<'EOF'
product,year,avg_retail_price
A,2008,395
A,2009,420
A,2010,425
A,2011,390
A,2012,300
A,2013,270
A,2014,260
B,2008,360
B,2009,400
B,2010,410
B,2011,375
B,2012,290
B,2013,262
B,2014,250
C,2010,100
C,2011,180
C,2012,195
C,2013,240
C,2014,180
D,2011,160
D,2012,260
D,2013,220
D,2014,215
E,2013,100
E,2014,210
EOF

cat > pricing/first-slide.md <<'EOF'
# Price has declined for all products on the market since the launch of Product C in 2010

[Clustered column chart: one cluster per product, one column per year from 2008 to 2014, a different color for each year, legend along the bottom]

Average Retail Product Price per Year
EOF
