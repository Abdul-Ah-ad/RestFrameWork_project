# 🏏 CricData API — Django REST Framework Project

A cricket stats API built using Django REST Framework. It allows importing teams and players from JSON, and provides endpoints to fetch players, teams, and best XI selections.


## ⚙️ Setup Instructions

### 🔁 Clone and Setup Environment

```bash
git clone https://github.com/Abdul-Ah-ad/RestFrameWork_project/cricdata-api.git
cd cricdata-api
git checkout ahad/feat/Cric_Api

python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

pip install -r requirements.txt  # Or manually: pip install django djangorestframework

add&config local.py 

python manage.py makemigrations
python manage.py migrate

python manage.py createsuperuser

Using Postman
1. Import API in Postman
Set base URL: http://127.0.0.1:8000

2. Admin-only Endpoint (Import JSON)
POST to: /injectTeams/import_data/

Authorization → Basic Auth → Provide Django admin credentials


Endpoint	Method	Access
/teams/	GET	✅ Public (anyone)
/teams/	POST	🔐 Admin only
/players/	GET	✅ Public (anyone)
/players/	POST	🔐 Admin only
/inject-data/import_data/	POST	Import teams and players from JSON (admin only)
/team-analysis/best/?team=Pakistan&category=odi	GET	Get best XI players by team and match type

