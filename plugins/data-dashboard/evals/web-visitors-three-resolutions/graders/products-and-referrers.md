---
type: llm
focus: { source: file, path: web-analysis.html }
weight: 2
---
You are reading the source of an HTML analysis dashboard of web visitors and sales. The data gives the top 10 products by revenue this month, each with its share of revenue and its share of product page views. One stands out: "Pleated skirt, beige" earns 3.1% of revenue but draws 14.8% of views, the most viewed of all. It also gives the top 10 referring sites with referrals, share of all referrals, change since a year ago (google.com +18%, reddit.com +112%, facebook.com −22%, and so on), and average revenue per referral, plus two ranked lists of product pairs: often bought together but never shown together (27% down to 10%), and shown together but rarely bought together (3% down to 0%).

PASS only if all of these hold:

1. Each product's revenue share and view share are drawn on one shared scale in the same row (for example a bar for revenue and a tick for views), so the pleated skirt's gap shows at a glance.
2. Referrers appear as a table or graphical table with all four measures, and the change since a year ago keeps its sign.
3. Both lists of product pairs appear, ranked by their percentage.
4. The products and referrers keep the order the data gives (by revenue and by referrals), with numbers right-aligned or drawn to scale.

FAIL otherwise, and name the first rule that was broken.
