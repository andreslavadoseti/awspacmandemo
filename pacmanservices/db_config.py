import os
import boto3
import urllib.request
from app import app
from flaskext.mysql import MySQL
#import configparser
#config = configparser.ConfigParser()
#config.read('pacmandb.properties')
#props = config['DEFAULT']
mysql = MySQL()

ssm = boto3.client('ssm', 'us-east-1')
ec2 = boto3.client('ec2', 'us-east-1')
instanceId = urllib.request.urlopen('http://169.254.169.254/latest/meta-data/instance-id').read().decode()

def getAttrValue(objList, attribute, val):
        return next((x['Value'] for x in objList if x[attribute] == val), None)

ec2Response = ec2.describe_tags(
    Filters=[
        {
            'Name': 'resource-id',
            'Values': [instanceId]
        },
    ],
)

projectName = getAttrValue(ec2Response['Tags'], 'Key', 'ProjectName')
environment = getAttrValue(ec2Response['Tags'], 'Key', 'Environment') 

# Find DB Connection in Parameter Store
response = ssm.get_parameters(
	Names=[projectName+'_'+environment+'_DB_USER', projectName+'_'+environment+'_DB_PASS', projectName+'_'+environment+'_DB_NAME', projectName+'_'+environment+'_DB_HOST', projectName+'_'+environment+'_DB_PORT'],
	WithDecryption=True
)

# MySQL configurations
app.config['MYSQL_DATABASE_USER'] = getAttrValue(response['Parameters'], 'Name', projectName+'_'+environment+'_DB_USER')
app.config['MYSQL_DATABASE_PASSWORD'] = getAttrValue(response['Parameters'], 'Name', projectName+'_'+environment+'_DB_PASS')
app.config['MYSQL_DATABASE_DB'] = getAttrValue(response['Parameters'], 'Name', projectName+'_'+environment+'_DB_NAME')
app.config['MYSQL_DATABASE_HOST'] = getAttrValue(response['Parameters'], 'Name', projectName+'_'+environment+'_DB_HOST')
#app.config['MYSQL_DATABASE_PORT'] = int(getAttrValue(response['Parameters'], 'Name', projectName+'_'+environment+'_DB_PORT'))
mysql.init_app(app)

# Create Player table if not exist
try:
	conn = mysql.connect()
	cursor = conn.cursor()
	cursor.execute("CREATE TABLE IF NOT EXISTS player ( user_id bigint(20) NOT NULL AUTO_INCREMENT, user_name varchar(45) COLLATE utf8_unicode_ci DEFAULT NULL, score bigint(20) DEFAULT 0, level bigint(20) DEFAULT 0, PRIMARY KEY (user_id)) ENGINE=InnoDB AUTO_INCREMENT=2 DEFAULT CHARSET=utf8 COLLATE=utf8_unicode_ci")
	conn.commit()
except Exception as e:
	print(e)
finally:
	cursor.close()
	conn.close()
