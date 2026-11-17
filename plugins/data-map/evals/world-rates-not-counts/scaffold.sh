#!/usr/bin/env bash
# Measles cases and population by country for a static newsletter figure. Planted: India has the most
# cases but a modest rate; Kyrgyzstan has the highest rate among populous countries; the Falkland Islands
# (population 3,398) top the raw rates from 4 cases; North Korea, Eritrea, and Turkmenistan did not report;
# the rates are strongly right-skewed. The boundaries come from the plugin's bundled Natural Earth file.
set -euo pipefail

mkdir -p data

cp "$(dirname "$0")/../../skills/data-map/assets/geo/world-110m.json" data/countries.geojson

cat > data/NOTES.md <<'EOF'
# Measles 2025, by country

**What it's for.** The lead figure in our December newsletter, Measles Watch Monthly. It goes out as an image in the email and on the website, about 640 px wide in the email.

**Files.**

- `measles_2025.csv`: one row per country. `iso3` matches the `id` of each feature in `countries.geojson`. `cases` is laboratory-confirmed and epidemiologically linked measles cases reported for January to October 2025. `population` is the mid-year estimate we divide by, the same figure as `pop_est` in the boundaries file. A blank `cases` means the country did not report for 2025; it does not mean zero. A `0` is a reported zero.
- `countries.geojson`: Natural Earth 1:110m country boundaries (public domain). Antarctica and the French Southern and Antarctic Lands have no resident population and no row in the CSV.

**Source line we use.** Measles Watch analysis of national surveillance reports, January to October 2025 (provisional). Boundaries: Natural Earth.
EOF

cat > data/measles_2025.csv <<'EOF'
iso3,country,cases,population
AFG,Afghanistan,1516,38041754
AGO,Angola,6937,31825295
ALB,Albania,48,2854191
ARE,United Arab Emirates,245,9770529
ARG,Argentina,27,44938712
ARM,Armenia,144,2957731
AUS,Australia,133,25364307
AUT,Austria,61,8877067
AZE,Azerbaijan,224,10023318
BDI,Burundi,1992,11530580
BEL,Belgium,71,11484055
BEN,Benin,3459,11801151
BFA,Burkina Faso,3467,20321378
BGD,Bangladesh,19040,163046161
BGR,Bulgaria,1182,6975761
BHS,Bahamas,1,389482
BIH,Bosnia and Herz.,82,3301000
BLR,Belarus,557,9466856
BLZ,Belize,0,390353
BOL,Bolivia,7,11513100
BRA,Brazil,421,211049527
BRN,Brunei,17,433285
BTN,Bhutan,29,763092
BWA,Botswana,44,2303697
CAF,Central African Rep.,1018,4745185
CAN,Canada,61,37589262
CHE,Switzerland,58,8574832
CHL,Chile,17,18952038
CHN,China,5733,1397715000
CIV,Côte d'Ivoire,1235,25716544
CMR,Cameroon,5773,25876380
COD,Dem. Rep. Congo,17661,86790567
COG,Congo,823,5380508
COL,Colombia,183,50339443
CRI,Costa Rica,7,5047561
CUB,Cuba,5,11333483
CYN,N. Cyprus,18,326000
CYP,Cyprus,54,1198575
CZE,Czechia,1091,10669709
DEU,Germany,558,83132799
DJI,Djibouti,46,973560
DNK,Denmark,11,5818553
DOM,Dominican Rep.,13,10738958
DZA,Algeria,866,43053054
ECU,Ecuador,22,17373662
EGY,Egypt,3124,100388073
ERI,Eritrea,,6081196
ESH,W. Sahara,7,603253
ESP,Spain,141,47076781
EST,Estonia,2,1326590
ETH,Ethiopia,16528,112078730
FIN,Finland,15,5520314
FJI,Fiji,6,889953
FLK,Falkland Is.,4,3398
FRA,France,228,67059887
GAB,Gabon,239,2172579
GBR,United Kingdom,202,66834405
GEO,Georgia,253,3720382
GHA,Ghana,4472,30417856
GIN,Guinea,2059,12771246
GMB,Gambia,232,2347706
GNB,Guinea-Bissau,125,1920922
GNQ,Eq. Guinea,194,1355986
GRC,Greece,36,10716322
GRL,Greenland,0,56225
GTM,Guatemala,22,16604026
GUY,Guyana,2,782766
HND,Honduras,12,9746117
HRV,Croatia,135,4067500
HTI,Haiti,25,11263077
HUN,Hungary,323,9769949
IDN,Indonesia,19852,270625568
IND,India,62855,1366417754
IRL,Ireland,15,4941444
IRN,Iran,6680,82913906
IRQ,Iraq,1227,39309783
ISL,Iceland,1,361313
ISR,Israel,396,9053300
ITA,Italy,168,60297396
JAM,Jamaica,2,2948279
JOR,Jordan,162,10101694
JPN,Japan,598,126264931
KAZ,Kazakhstan,11293,18513930
KEN,Kenya,22579,52573973
KGZ,Kyrgyzstan,6224,6456900
KHM,Cambodia,154,16486542
KOR,South Korea,328,51709098
KOS,Kosovo,24,1794248
KWT,Kuwait,115,4207083
LAO,Laos,61,7169455
LBN,Lebanon,175,6855713
LBR,Liberia,832,4937374
LBY,Libya,256,6777452
LKA,Sri Lanka,217,21803000
LSO,Lesotho,67,2125268
LTU,Lithuania,7,2786844
LUX,Luxembourg,3,619896
LVA,Latvia,28,1912789
MAR,Morocco,885,36471769
MDA,Moldova,55,2657637
MDG,Madagascar,3370,26969307
MEX,Mexico,405,127575529
MKD,North Macedonia,14,2083459
MLI,Mali,2976,19658031
MMR,Myanmar,478,54045420
MNE,Montenegro,25,622137
MNG,Mongolia,34,3225167
MOZ,Mozambique,3089,30366036
MRT,Mauritania,173,4525696
MWI,Malawi,1751,18628747
MYS,Malaysia,411,31949777
NAM,Namibia,63,2494530
NCL,New Caledonia,2,287800
NER,Niger,1846,23310715
NGA,Nigeria,35057,200963599
NIC,Nicaragua,9,6545502
NLD,Netherlands,68,17332850
NOR,Norway,11,5347896
NPL,Nepal,961,28608710
NZL,New Zealand,35,4917000
OMN,Oman,70,4974986
PAK,Pakistan,9806,216565318
PAN,Panama,2,4246439
PER,Peru,148,32510453
PHL,Philippines,7776,108116615
PNG,Papua New Guinea,114,8776109
POL,Poland,1452,37970874
PRI,Puerto Rico,2,3193694
PRK,North Korea,,25666161
PRT,Portugal,98,10269417
PRY,Paraguay,43,7044636
PSE,Palestine,238,4685306
QAT,Qatar,39,2832067
ROU,Romania,490,19356544
RUS,Russia,8781,144373535
RWA,Rwanda,918,12626950
SAU,Saudi Arabia,1205,34268528
SDN,Sudan,337,42813238
SEN,Senegal,696,16296364
SLB,Solomon Is.,9,669823
SLE,Sierra Leone,308,7813215
SLV,El Salvador,5,6453553
SOL,Somaliland,355,5096159
SOM,Somalia,1020,10192317
SRB,Serbia,37,6944975
SSD,S. Sudan,435,11062113
SUR,Suriname,1,581363
SVK,Slovakia,196,5454073
SVN,Slovenia,6,2087946
SWE,Sweden,16,10285453
SWZ,eSwatini,5,1148130
SYR,Syria,1827,17070135
TCD,Chad,2522,15946876
TGO,Togo,1863,8082366
THA,Thailand,1290,69625582
TJK,Tajikistan,5033,9321018
TKM,Turkmenistan,,5942089
TLS,Timor-Leste,18,1293119
TTO,Trinidad and Tobago,3,1394973
TUN,Tunisia,165,11694719
TUR,Turkey,4034,83429615
TWN,Taiwan,99,23568378
TZA,Tanzania,8119,58005463
UGA,Uganda,20572,44269594
UKR,Ukraine,752,44385155
URY,Uruguay,5,3461734
USA,United States of America,735,328239523
UZB,Uzbekistan,15636,33580650
VEN,Venezuela,33,28515829
VNM,Vietnam,6609,96462106
VUT,Vanuatu,1,299882
YEM,Yemen,1395,29161922
ZAF,South Africa,1390,58558270
ZMB,Zambia,1147,17861030
ZWE,Zimbabwe,1314,14645468
EOF
