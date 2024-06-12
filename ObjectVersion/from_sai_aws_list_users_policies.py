import boto3
import json
#client = boto3.client('iam',aws_access_key_id="XXXX",aws_secret_access_key="YYY")
client = boto3.client('iam')
users = client.list_users()
user_list = []

print()
print()
print()
print ("Paste the output below into https://data.page/json/csvget CSV format")
print()
print()
print()

#print ('{"Users":')
#print ('[')

for key in users['Users']:
    result = {}
    Policies = []
    Groups=[]
 
    result['userName']=key['UserName']

    List_of_Policies =  client.list_user_policies(UserName=key['UserName'])

    result['Policies'] = List_of_Policies['PolicyNames']

    List_of_Groups =  client.list_groups_for_user(UserName=key['UserName'])

    for Group in List_of_Groups['Groups']:
        Groups.append(Group['GroupName'])
    result['Groups'] = Groups

   #result_updated = result.replace("'",'"')
    user_list.append(result)


for key in user_list:
    print (json.dumps(key))
