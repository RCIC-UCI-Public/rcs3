# Grafana Configuration
# These values should come from the infra module's outputs:
grafana_username = "admin"
grafana_url      = "https://backup-metrics-prod-grafana-alb-414120755.us-west-2.elb.amazonaws.com"

# Path to dashboard JSON files
dashboards_path = "../../dashboards"

# Admin users (will be created with admin privileges)
admin_users = ["scottl","ppapadop","lopez","santucci"]

# Common dashboards available to all users
common_dashboards = ["cost-estimates.json", "cost-estimates-improved.json"]

# Define teams and their bucket access permissions
bucket_teams = {
"Team blsemler" = {
members = ["blsemler"]
buckets = ["blsemler-littlebird-uci-p-bkup-bucket"]
},
"Team cestark" = {
members = ["cestark"]
buckets = ["cestark- bmc-uci-p-bkup-bucket",
"cestark-fibre-data-uci-p-bkup-bucket",
"cestark-hippocampus-uci-p-bkup-bucket"]
},
"Team fmarango" = {
members = ["fmarango"]
buckets = ["fmarango-f-ivm-uci-p-bkup-bucket"]
},
"Team kbeier" = {
members = ["kbeier","ronp" ]
buckets = ["kbeier-apollon-uci-p-bkup-bucket",
"kbeier-balbina-uci-p-bkup-bucket",
"kbeier-beier1-uci-p-bkup-bucket",
"kbeier-csaba-uci-p-bkup-bucket",
"kbeier-emem-uci-p-bkup-bucket",
"kbeier-faye-uci-p-bkup-bucket"]
},
"Team kngreen" = {
members = ["kngreen"]
buckets = ["kngreen-model-ad-uci-p-bkup-bucket"]
},
"Team lewell" = {
members = ["lewell"]
buckets = ["lewell-cedar-uci-p-bkup-bucket"]
},
"Team lwagar" = {
members = ["lwagar"]
buckets = ["lwagar-wagarlab-uci-p-bkup-bucket"]
},
"Team macharya" = {
members = ["macharya"]
buckets = ["macharya-mmanas-uci-p-bkup-bucket"]
},
"Team medhap" = {
members = ["medhap"]
buckets = ["medhap-rivendell-uci-p-bkup-bucket"]
},
"Team mfrose" = {
members = ["mfrose"]
buckets = ["mfrose-morandi1-uci-p-bkup-bucket"]
},
"Team middlebj" = {
members = ["middlebj"]
buckets = ["middlebj-middlab-uci-p-bkup-bucket"]
},
"Team mingt" = {
members = ["mingt"]
buckets = ["mingt-chlamydia-uci-p-bkup-bucket"]
},
"Team piomelli" = {
members = ["piomelli"]
buckets = ["piomelli-piomellinas-uci-p-bkup-bucket"]
},
"Team rcic-admin" = {
members = ["rcic-admin"]
buckets = ["rcic-admin-crsp-uci-p-bkup-bucket"]
},
"Team rfrostig" = {
members = ["rfrostig"]
buckets = ["rfrostig-cortex-uci-p-bkup-bucket",
"rfrostig-sharat-uci-p-bkup-bucket"]
},
"Team xiangmix" = {
members = ["xiangmix","ronp"]
buckets = ["xiangmix-brain-uci-p-bkup-bucket",
"xiangmix-cncm2-uci-p-bkup-bucket",
"xiangmix-cncm-uci-p-bkup-bucket",
"xiangmix-cncmviruscore-uci-p-bkup-bucket",
"xiangmix-xu160-uci-p-bkup-bucket",
"xiangmix-xuisebnas-uci-p-bkup-bucket",
"xiangmix-xulabtissuecyte-uci-p-bkup-bucket",
"xiangmix-xuoffice-uci-p-bkup-bucket"]
}
}

# Default password for all users (can be overridden)
default_user_password = "ChangeMe123!"
