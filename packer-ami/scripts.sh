sleep 30

sudo apt-get update
sudo apt-get install python3
sudo apt-get -y install python3-pip
sudo pip install flask==2
sudo pip install psycopg==3
sudo pip install bcrypt==4
sudo pip install Flask-Bcrypt==1
sudo pip install requests
sudo pip install flask-sqlalchemy==1
sudo pip install sqlalchemy==1
sudo pip install sqlalchemy_utils
sudo pip install psycopg2-binary
sudo pip install boto3
sudo chmod 777 /home/ubuntu/main.py

sleep 30
sudo mv /tmp/webapplication.service /etc/systemd/system/webapplication.service

sudo yum install amazon-cloudwatch-agent -y
sudo /opt/aws/amazon-cloudwatch-agent/bin/amazon-cloudwatch-agent-ctl -a fetch-config -m ec2 -c file:/home/ubuntu/AmazonCloudWatch-agent-config.json -s