sleep 30

sudo apt-get install python3
sudo apt-get update
sudo apt-get -y install python3-pip
sudo pip install flask==2
sudo pip install psycopg==3
sudo pip install bcrypt==4
sudo pip install Flask-Bcrypt==1
sudo pip install requests==2
sudo pip install flask-sqlalchemy==1
sudo pip install sqlalchemy==1
sudo pip install sqlalchemy_utils
sudo apt-get -y install postgresql postgresql-contrib
sudo systemctl start postgresql.service
sudo systemctl status postgresql.service

#sleep 30
sudo mv /tmp/webapplication.service /etc/systemd/system/webapplication.service
sudo systemctl enable webapplication.service
sudo systemctl start webapplication.service
sudo systemctl status webapplication.service