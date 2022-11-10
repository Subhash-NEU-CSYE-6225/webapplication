sleep 30
#! /bin/sh
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
sudo pip install statsd
sudo chmod 755 /home/ubuntu
sudo chmod 777 /home/ubuntu/main.py
sudo mkdir -p /home/ubuntu/logs
sudo chmod 755 /home/ubuntu/logs
sudo chmod 777 /home/ubuntu/logs

sleep 30
sudo mv /tmp/webapplication.service /etc/systemd/system/webapplication.service

sudo curl -o /root/amazon-cloudwatch-agent.deb https://s3.amazonaws.com/amazoncloudwatch-agent/debian/amd64/latest/amazon-cloudwatch-agent.deb
sudo dpkg -i -E /root/amazon-cloudwatch-agent.deb
sudo /opt/aws/amazon-cloudwatch-agent/bin/amazon-cloudwatch-agent-ctl -a fetch-config -m ec2 -c file:/home/ubuntu/AmazonCloudWatch-agent-config.json -s