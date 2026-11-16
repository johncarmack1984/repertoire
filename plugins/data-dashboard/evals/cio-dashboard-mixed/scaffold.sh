#!/usr/bin/env bash
# Few's CIO dashboard situation (chapter 8) as CSVs. Planted: Data Warehouse availability is critical
# (3.8 points under its acceptable level, and down right now), Network and ERP are warnings (0.4 and
# 0.6 under), CPU is a warning (79%), the Budgeting system milestone is 13 days past due (critical),
# and the data warehouse cutover rehearsal is 3 days past due (warning). Nothing else crosses a rule.
set -euo pipefail

mkdir -p it

cat > it/NOTES.md <<'EOF'
# IT data for the CIO's dashboard

**Who reads it.** Priya Raman, our CIO. She keeps it open all day on her desktop monitor (1920 by 1080, browser full screen) and glances at it between meetings. At a glance she needs to know whether any system is in trouble right now, how the systems and hardware have held up, and whether the budget, satisfaction, and projects are on track.

**As of.** Friday, November 13, 2026, 3:35 PM Pacific Standard Time (2026-11-13T15:35:00-08:00). Today is November 13, 2026. `systems_now.csv` is live as of that moment; the other files come from the 3:00 PM refresh.

**What counts as a problem.** These are IT's service levels:

- Right now: a system whose status in `systems_now.csv` is anything but `up` is critical.
- Availability: each system has its own acceptable level in `availability.csv`. A system whose availability over the last 30 days is below its acceptable level is a warning; more than 2 points below it is critical.
- Hardware capacity: under 70% used is good, 70% to 85% is excessive (a warning), and over 85% is critical.
- Response time: each system has an acceptable time in `response_limits.csv`. A system is fine while at least 90% of today's samples are within it, and a warning below that.
- Expenses: at or under the YTD budget is good, up to 5% over is a warning, and more than 5% over is critical.
- Customer satisfaction (our internal survey, scored 1 to 4, target 3.50): 3.40 or higher is fine, below 3.40 is a warning, and below 3.20 is critical.
- Level 1 problems (the most severe incidents) YTD: 110 or fewer is fine, 111 to 130 is a warning, and more than 130 is critical.
- Project milestones: an open milestone past its due date is a warning, and more than 7 days past due is critical. A completed milestone is done, whatever its dates.

**Files.**

- `systems_now.csv`: each system's status right now, and when a problem began.
- `availability.csv`: each system's availability over the last 30 days and its acceptable level, in percent.
- `availability_monthly.csv`: each system's availability for the last 12 closed months.
- `capacity.csv`: CPU (the cluster average over the last 15 minutes) and storage, in percent of capacity used.
- `cpu_today.csv`: CPU used in each complete hour today. `storage_monthly.csv`: storage used at the end of each of the last 12 months.
- `network_hourly.csv`: network traffic in each hour of yesterday, in gigabytes, with the mean for that hour over the last 7 days and over the last 6 months.
- `response_times.csv`: today's response-time samples for four systems, in seconds. `response_limits.csv`: each one's acceptable time.
- `non_system_metrics.csv`: expenses, customer satisfaction, and level 1 problems YTD, each against its target or budget. `non_system_monthly.csv`: the same three for each month this year.
- `milestones.csv`: major project milestones with due dates; `completed_on` is empty while a milestone is open.
- `project_queue.csv`: projects waiting to start, with priority (1 is highest). Priya wants the top five.
- `events.csv`: critical events on the change calendar. Priya wants the ones in the next 14 days.
EOF

cat > it/systems_now.csv <<'EOF'
system,status,since
Network,up,
ERP,up,
Data Warehouse,down,2026-11-13T14:50:00-08:00
Web Site,up,
Email,up,
HR,up,
Problem Tracking,up,
EOF

cat > it/availability.csv <<'EOF'
system,availability_last_30_days_pct,acceptable_pct
Network,98.6,99.0
ERP,97.9,98.5
Data Warehouse,93.2,97.0
Web Site,99.4,99.0
Email,99.7,99.5
HR,96.7,95.0
Problem Tracking,94.7,94.0
EOF

cat > it/availability_monthly.csv <<'EOF'
month,system,availability_pct
2025-11,Network,99.4
2025-12,Network,99.3
2026-01,Network,99.5
2026-02,Network,99.2
2026-03,Network,99.4
2026-04,Network,99.1
2026-05,Network,99.3
2026-06,Network,99.0
2026-07,Network,98.9
2026-08,Network,99.1
2026-09,Network,98.8
2026-10,Network,98.7
2025-11,ERP,98.9
2025-12,ERP,98.7
2026-01,ERP,98.8
2026-02,ERP,99.0
2026-03,ERP,98.6
2026-04,ERP,98.9
2026-05,ERP,98.4
2026-06,ERP,98.7
2026-07,ERP,98.5
2026-08,ERP,98.2
2026-09,ERP,98.3
2026-10,ERP,98.0
2025-11,Data Warehouse,98.1
2025-12,Data Warehouse,97.8
2026-01,Data Warehouse,98.0
2026-02,Data Warehouse,97.6
2026-03,Data Warehouse,97.9
2026-04,Data Warehouse,97.4
2026-05,Data Warehouse,97.1
2026-06,Data Warehouse,96.8
2026-07,Data Warehouse,96.2
2026-08,Data Warehouse,95.7
2026-09,Data Warehouse,95.1
2026-10,Data Warehouse,94.4
2025-11,Web Site,99.5
2025-12,Web Site,99.2
2026-01,Web Site,99.6
2026-02,Web Site,99.4
2026-03,Web Site,99.7
2026-04,Web Site,99.3
2026-05,Web Site,99.5
2026-06,Web Site,99.6
2026-07,Web Site,99.2
2026-08,Web Site,99.4
2026-09,Web Site,99.5
2026-10,Web Site,99.3
2025-11,Email,99.8
2025-12,Email,99.9
2026-01,Email,99.7
2026-02,Email,99.8
2026-03,Email,99.9
2026-04,Email,99.6
2026-05,Email,99.8
2026-06,Email,99.9
2026-07,Email,99.7
2026-08,Email,99.8
2026-09,Email,99.9
2026-10,Email,99.8
2025-11,HR,97.1
2025-12,HR,96.8
2026-01,HR,97.3
2026-02,HR,96.9
2026-03,HR,97.0
2026-04,HR,96.5
2026-05,HR,96.8
2026-06,HR,97.2
2026-07,HR,96.6
2026-08,HR,96.9
2026-09,HR,97.1
2026-10,HR,96.8
2025-11,Problem Tracking,95.3
2025-12,Problem Tracking,95.0
2026-01,Problem Tracking,94.8
2026-02,Problem Tracking,95.2
2026-03,Problem Tracking,94.9
2026-04,Problem Tracking,95.1
2026-05,Problem Tracking,94.6
2026-06,Problem Tracking,95.0
2026-07,Problem Tracking,94.8
2026-08,Problem Tracking,94.5
2026-09,Problem Tracking,94.9
2026-10,Problem Tracking,94.6
EOF

cat > it/capacity.csv <<'EOF'
resource,pct_used_now
CPU,79
Storage,63
EOF

cat > it/cpu_today.csv <<'EOF'
hour,cpu_pct
00:00,41
01:00,38
02:00,36
03:00,35
04:00,37
05:00,44
06:00,52
07:00,61
08:00,70
09:00,74
10:00,77
11:00,78
12:00,76
13:00,80
14:00,81
15:00,79
EOF

cat > it/storage_monthly.csv <<'EOF'
month,storage_used_pct
2025-11,51
2025-12,52
2026-01,53
2026-02,54
2026-03,55
2026-04,56
2026-05,57
2026-06,58
2026-07,59
2026-08,60
2026-09,61
2026-10,62
EOF

cat > it/network_hourly.csv <<'EOF'
hour,yesterday_gb,mean_last_7_days_gb,mean_last_6_months_gb
00:00,66.7,67.4,59.4
01:00,65.9,65.5,57.7
02:00,65.0,63.6,56.1
03:00,69.7,67.4,59.4
04:00,68.9,65.5,57.7
05:00,63.0,63.6,56.1
06:00,65.9,65.5,57.7
07:00,93.7,92.6,81.6
08:00,120.2,118.3,104.3
09:00,156.3,141.4,124.6
10:00,173.0,160.7,141.6
11:00,189.6,175.1,154.4
12:00,200.3,184.1,162.3
13:00,204.6,187.2,165.0
14:00,202.3,184.1,162.3
15:00,188.6,175.1,154.4
16:00,174.0,160.7,141.6
17:00,142.0,141.4,124.6
18:00,120.2,118.3,104.3
19:00,95.7,92.6,81.6
20:00,64.9,65.5,57.8
21:00,67.7,67.4,59.4
22:00,66.9,65.5,57.7
23:00,66.0,63.6,56.1
EOF

cat > it/response_times.csv <<'EOF'
system,sampled_at,seconds
Data Warehouse,2026-11-13T08:00:00-08:00,1.4
Data Warehouse,2026-11-13T08:13:00-08:00,1.9
Data Warehouse,2026-11-13T08:26:00-08:00,2.2
Data Warehouse,2026-11-13T08:39:00-08:00,1.6
Data Warehouse,2026-11-13T08:52:00-08:00,2.8
Data Warehouse,2026-11-13T09:05:00-08:00,1.8
Data Warehouse,2026-11-13T09:18:00-08:00,2.1
Data Warehouse,2026-11-13T09:31:00-08:00,2.5
Data Warehouse,2026-11-13T09:44:00-08:00,1.7
Data Warehouse,2026-11-13T09:57:00-08:00,2.0
Data Warehouse,2026-11-13T10:10:00-08:00,2.3
Data Warehouse,2026-11-13T10:23:00-08:00,2.6
Data Warehouse,2026-11-13T10:36:00-08:00,1.5
Data Warehouse,2026-11-13T10:49:00-08:00,1.9
Data Warehouse,2026-11-13T11:02:00-08:00,2.4
Data Warehouse,2026-11-13T11:15:00-08:00,2.9
Data Warehouse,2026-11-13T11:28:00-08:00,2.2
Data Warehouse,2026-11-13T11:41:00-08:00,1.8
Data Warehouse,2026-11-13T11:54:00-08:00,2.0
Data Warehouse,2026-11-13T12:07:00-08:00,2.7
Data Warehouse,2026-11-13T12:20:00-08:00,6.1
Data Warehouse,2026-11-13T12:33:00-08:00,2.1
Data Warehouse,2026-11-13T12:46:00-08:00,1.6
Data Warehouse,2026-11-13T12:59:00-08:00,2.3
Data Warehouse,2026-11-13T13:12:00-08:00,4.8
Data Warehouse,2026-11-13T13:25:00-08:00,1.9
Data Warehouse,2026-11-13T13:38:00-08:00,2.5
Data Warehouse,2026-11-13T13:51:00-08:00,2.2
Data Warehouse,2026-11-13T14:04:00-08:00,1.7
Data Warehouse,2026-11-13T14:17:00-08:00,2.0
ERP,2026-11-13T08:00:00-08:00,0.9
ERP,2026-11-13T08:13:00-08:00,1.1
ERP,2026-11-13T08:26:00-08:00,1.3
ERP,2026-11-13T08:39:00-08:00,1.0
ERP,2026-11-13T08:52:00-08:00,1.4
ERP,2026-11-13T09:05:00-08:00,1.2
ERP,2026-11-13T09:18:00-08:00,0.8
ERP,2026-11-13T09:31:00-08:00,1.6
ERP,2026-11-13T09:44:00-08:00,1.1
ERP,2026-11-13T09:57:00-08:00,1.3
ERP,2026-11-13T10:10:00-08:00,1.0
ERP,2026-11-13T10:23:00-08:00,1.5
ERP,2026-11-13T10:36:00-08:00,1.2
ERP,2026-11-13T10:49:00-08:00,0.9
ERP,2026-11-13T11:02:00-08:00,1.7
ERP,2026-11-13T11:15:00-08:00,1.1
ERP,2026-11-13T11:28:00-08:00,1.3
ERP,2026-11-13T11:41:00-08:00,1.0
ERP,2026-11-13T11:54:00-08:00,2.6
ERP,2026-11-13T12:07:00-08:00,1.2
ERP,2026-11-13T12:20:00-08:00,1.4
ERP,2026-11-13T12:33:00-08:00,1.1
ERP,2026-11-13T12:46:00-08:00,0.9
ERP,2026-11-13T12:59:00-08:00,1.3
ERP,2026-11-13T13:12:00-08:00,1.2
ERP,2026-11-13T13:25:00-08:00,1.0
ERP,2026-11-13T13:38:00-08:00,1.5
ERP,2026-11-13T13:51:00-08:00,1.1
ERP,2026-11-13T14:04:00-08:00,1.8
ERP,2026-11-13T14:17:00-08:00,1.2
Web Site,2026-11-13T08:00:00-08:00,0.6
Web Site,2026-11-13T08:13:00-08:00,0.8
Web Site,2026-11-13T08:26:00-08:00,0.7
Web Site,2026-11-13T08:39:00-08:00,0.9
Web Site,2026-11-13T08:52:00-08:00,0.5
Web Site,2026-11-13T09:05:00-08:00,1.1
Web Site,2026-11-13T09:18:00-08:00,0.7
Web Site,2026-11-13T09:31:00-08:00,0.8
Web Site,2026-11-13T09:44:00-08:00,0.6
Web Site,2026-11-13T09:57:00-08:00,1.0
Web Site,2026-11-13T10:10:00-08:00,0.7
Web Site,2026-11-13T10:23:00-08:00,0.9
Web Site,2026-11-13T10:36:00-08:00,1.2
Web Site,2026-11-13T10:49:00-08:00,0.8
Web Site,2026-11-13T11:02:00-08:00,0.6
Web Site,2026-11-13T11:15:00-08:00,0.7
Web Site,2026-11-13T11:28:00-08:00,0.9
Web Site,2026-11-13T11:41:00-08:00,0.8
Web Site,2026-11-13T11:54:00-08:00,1.3
Web Site,2026-11-13T12:07:00-08:00,0.7
Web Site,2026-11-13T12:20:00-08:00,0.6
Web Site,2026-11-13T12:33:00-08:00,0.8
Web Site,2026-11-13T12:46:00-08:00,1.0
Web Site,2026-11-13T12:59:00-08:00,0.7
Web Site,2026-11-13T13:12:00-08:00,0.9
Web Site,2026-11-13T13:25:00-08:00,0.8
Web Site,2026-11-13T13:38:00-08:00,0.6
Web Site,2026-11-13T13:51:00-08:00,1.1
Web Site,2026-11-13T14:04:00-08:00,0.7
Web Site,2026-11-13T14:17:00-08:00,0.8
HR,2026-11-13T08:00:00-08:00,0.7
HR,2026-11-13T08:13:00-08:00,0.9
HR,2026-11-13T08:26:00-08:00,1.0
HR,2026-11-13T08:39:00-08:00,0.8
HR,2026-11-13T08:52:00-08:00,1.2
HR,2026-11-13T09:05:00-08:00,0.9
HR,2026-11-13T09:18:00-08:00,0.7
HR,2026-11-13T09:31:00-08:00,1.1
HR,2026-11-13T09:44:00-08:00,0.8
HR,2026-11-13T09:57:00-08:00,1.0
HR,2026-11-13T10:10:00-08:00,0.9
HR,2026-11-13T10:23:00-08:00,1.3
HR,2026-11-13T10:36:00-08:00,0.8
HR,2026-11-13T10:49:00-08:00,0.7
HR,2026-11-13T11:02:00-08:00,1.0
HR,2026-11-13T11:15:00-08:00,0.9
HR,2026-11-13T11:28:00-08:00,1.1
HR,2026-11-13T11:41:00-08:00,0.8
HR,2026-11-13T11:54:00-08:00,1.2
HR,2026-11-13T12:07:00-08:00,0.9
HR,2026-11-13T12:20:00-08:00,1.0
HR,2026-11-13T12:33:00-08:00,0.8
HR,2026-11-13T12:46:00-08:00,0.7
HR,2026-11-13T12:59:00-08:00,1.1
HR,2026-11-13T13:12:00-08:00,0.9
HR,2026-11-13T13:25:00-08:00,1.4
HR,2026-11-13T13:38:00-08:00,0.8
HR,2026-11-13T13:51:00-08:00,1.0
HR,2026-11-13T14:04:00-08:00,0.9
HR,2026-11-13T14:17:00-08:00,0.8
EOF

cat > it/response_limits.csv <<'EOF'
system,acceptable_seconds
Data Warehouse,3.0
ERP,2.0
Web Site,1.6
HR,1.5
EOF

cat > it/non_system_metrics.csv <<'EOF'
metric,unit,ytd_actual,ytd_target
Expenses,USD,2456500,2556000
Customer satisfaction,mean IT survey score (1 to 4),3.52,3.5
Level 1 problems,incidents,87,110
EOF

cat > it/non_system_monthly.csv <<'EOF'
month,metric,value
2026-01,Expenses,226400
2026-02,Expenses,223900
2026-03,Expenses,238300
2026-04,Expenses,233100
2026-05,Expenses,240600
2026-06,Expenses,236800
2026-07,Expenses,229700
2026-08,Expenses,244200
2026-09,Expenses,236900
2026-10,Expenses,238300
2026-01,Customer satisfaction,3.44
2026-02,Customer satisfaction,3.47
2026-03,Customer satisfaction,3.49
2026-04,Customer satisfaction,3.51
2026-05,Customer satisfaction,3.5
2026-06,Customer satisfaction,3.53
2026-07,Customer satisfaction,3.55
2026-08,Customer satisfaction,3.52
2026-09,Customer satisfaction,3.54
2026-10,Customer satisfaction,3.56
2026-01,Level 1 problems,11
2026-02,Level 1 problems,9
2026-03,Level 1 problems,10
2026-04,Level 1 problems,8
2026-05,Level 1 problems,7
2026-06,Level 1 problems,9
2026-07,Level 1 problems,8
2026-08,Level 1 problems,7
2026-09,Level 1 problems,9
2026-10,Level 1 problems,6
EOF

cat > it/milestones.csv <<'EOF'
project,milestone,due_date,completed_on
Budgeting system,Vendor contract signed,2026-10-31,
Email migration,Pilot group moved,2026-11-02,2026-10-30
Data warehouse upgrade,Cutover rehearsal,2026-11-10,
ERP patch 4.2,User acceptance testing done,2026-11-17,
HR self-service portal,Design review,2026-11-22,
Network refresh,Core switches installed,2026-12-08,
EOF

cat > it/project_queue.csv <<'EOF'
priority,project,status,funding_approved,scheduled_start
4,Laptop fleet refresh,Vendor quotes in,yes,2027-01-11
1,Data warehouse capacity expansion,Design approved,yes,2026-12-01
7,Intranet redesign,Idea,no,2027-04-05
2,Single sign-on for vendor portals,Requirements done,yes,2026-12-14
6,Conference room AV upgrade,Scoping,no,2027-03-01
3,Backup site failover test,Scheduling,no,2027-01-04
5,Help desk chatbot,Scoping,no,2027-02-01
8,Printer consolidation,Idea,no,2027-05-03
EOF

cat > it/events.csv <<'EOF'
date,event,group_responsible
2026-11-11,Payroll system patch,HR Systems
2026-11-14,Data center generator test,Facilities
2026-11-17,ERP patch 4.2 go-live,ERP Team
2026-11-19,Quarterly security audit,Security
2026-11-21,Email cutover weekend,Messaging
2026-11-24,Holiday change freeze begins,Change Board
2026-12-02,Board IT review,Office of the CIO
2026-12-15,Year-end close support,Finance Systems
EOF
