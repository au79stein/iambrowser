#!/usr/bin/env python3

import sys
import pyperclip
import boto3
from botocore.exceptions import ClientError
from pprint import pprint
from pick import pick


RESET  = "\033[0m"
RED    = "\033[0;31m"
GREEN  = "\033[0;32m"
YELLOW = "\033[0;33m"
CYAN   = "\033[0;36m"


profile = "mfa"
region  = "us-east-2"
service = "iam"

def list_policies():
  linenum = 1
  iam = boto3.client('iam', region_name=region)
  paginator = iam.get_paginator('list_policies')
  policy_params = {'OnlyAttached': True}
  for response in paginator.paginate(**policy_params):
    for policy in response["Policies"]:
      print(f"{linenum: 4d}: ", end="")
      print(f"PolicyId: {policy['PolicyId']}, PolicyName: {policy['PolicyName']}", end="")
      print(f"PolicyArn: {policy['Arn']}", end="")
      print()
      linenum = linenum + 1
  
def list_users():
  linenum = 1
  iam = boto3.client('iam', region_name=region)
  paginator = iam.get_paginator('list_users')
  for response in paginator.paginate():
    for user in response["Users"]:
      print(f"{linenum: 4d}: ", end="")
      print(f"Username: {user['UserName']}, Arn: {user['Arn']}, Created: {user['CreateDate'].strftime('%m/%d/%Y')}", end="")
      if "PasswordLastUsed" in user:
        print(f" PasswordLastUsed: {user['PasswordLastUsed'].strftime('%m/%d/%Y')}", end="")
      else:
        print(f" PasswordLastUsed: Never", end="")
      print()
      linenum = linenum + 1


def get_policy_version(policyarn, versionid):
  iam = boto3.client('iam', region_name=region)
  response = iam.get_policy_version(PolicyArn=policyarn, VersionId=versionid)['PolicyVersion']
  print(f"VersionId: {response['VersionId']}, \n")
  print(f"{response['Document']}", end="")
  print()
  pprint(response['Document'])


def get_policy(policyarn):
  iam = boto3.client('iam', region_name=region)
  response = iam.get_policy(PolicyArn=policyarn)['Policy']
  print(f"PolicyName: {response['PolicyName']}, PolicyId: {response['PolicyId']}, AttachmentCount: {response['AttachmentCount']}, DefaultVersionId: {response['DefaultVersionId']}, Arn: {response['Arn']}", end="")
  print()
  print("temporarily added call here to get_policy_version to display document also")
  versionid = response['DefaultVersionId']
  get_policy_version(policyarn, versionid)


def get_group(groupname):
  linenum = 1
  iam = boto3.client('iam', region_name=region)
  paginator = iam.get_paginator('get_group')
  group_params = {'GroupName': groupname}
  try:
    for response in paginator.paginate(**group_params):
      for user in response['Users']:
        print(f"{linenum: 4d}: ", end="")
        print(f"UserName: {user['UserName']}", end="")
        print()
        linenum = linenum + 1
  except ClientError:
    print("couldn't list users for {}".format(groupname))


def list_user_policies(username):
  linenum = 1
  iam = boto3.client('iam', region_name=region)
  paginator = iam.get_paginator('list_user_policies')
  policy_params = {'UserName': username}
  try:
    for response in paginator.paginate(**policy_params):
      for policy in response['PolicyNames']:
        print(f"{linenum: 4d}: ", end="")
        print(f"PolicyName: {policy}", end="")
        print()
        linenum = linenum + 1
  except ClientError:
    print("couldn't list policies for {}".format(username))


def list_groups_for_user(username):
  linenum = 1
  iam = boto3.client('iam', region_name=region)
  paginator = iam.get_paginator('list_groups_for_user')
  group_params = {'UserName': username}
  try:
    for response in paginator.paginate(**group_params):
      for group in response['Groups']:
        print(f"{linenum: 4d}: ", end="")
        print(f"GroupName: {group['GroupName']},  GroupId: {group['GroupId']}", end="")
        print()
        linenum = linenum + 1
  except ClientError:
    print("couldn't list groups for {}".format(username))


def list_groups():
  linenum = 1
  iam = boto3.client('iam', region_name=region)
  paginator = iam.get_paginator('list_groups')
  for response in paginator.paginate():
    for group in response['Groups']:
      print(f"{linenum: 4d}: ", end="")
      print(f"GroupName: {group['GroupName']},  GroupId: {group['GroupId']}", end="")
      print()
      linenum = linenum + 1


def list_attached_user_policies(username):
  linenum = 1
  iam = boto3.client('iam', region_name=region)
  paginator = iam.get_paginator('list_attached_user_policies')
  policy_params = {'UserName': username}
  try:
    for response in paginator.paginate(**policy_params):
      for policy in response['AttachedPolicies']:
        print(f"{linenum: 4d}: ", end="")
        print(f"PolicyName: {policy['PolicyName']}", end="")
        print()
        linenum = linenum + 1
  except ClientError:
    print("couldn't list attached policies for {}".format(username))


def list_group_policies(groupname):
  linenum = 1
  iam = boto3.client('iam', region_name=region)
  paginator = iam.get_paginator('list_group_policies')
  group_params = {'GroupName': groupname}
  try:
    for response in paginator.paginate(**group_params):
      for policy in response['PolicyNames']:
        print(f"{linenum: 4d}: ", end="")
        print(f"PolicyName: {policy}", end="")
        print()
        linenum = linenum + 1
  except ClientError:
    print("couldn't list attached policies for {}".format(groupname))


def list_attached_group_policies(groupname):
  linenum = 1
  iam = boto3.client('iam', region_name=region)
  paginator = iam.get_paginator('list_attached_group_policies')
  group_params = {'GroupName': groupname}
  try:
    for response in paginator.paginate(**group_params):
      for policy in response['AttachedPolicies']:
        print(f"{linenum: 4d}: ", end="")
        print(f"PolicyName: {policy['PolicyName']}", end="")
        print()
        linenum = linenum + 1
  except ClientError:
    print("couldn't list attached policies for {}".format(groupname))


def menu():
  title = "make a selection..."
  options = ['list users', 'list groups', 'list groups for user', 'get users in group', 'list user policies', 'list policies', 'list attached user policies', 'list group policies', 'list attached group policies', 'get policy', 'exit']
  selected = pick(options, title, multiselect=False, min_selection_count=1)
  print(f"you picked: {selected[1]} -> {selected[0]}")
  return selected[1]


def main():
  while True:
    sel = menu()
    if sel == 0:   list_users()
    elif sel == 1: list_groups()
    elif sel == 2: 
      username = input('enter user name: ')
      list_groups_for_user(username)
    elif sel == 3: 
      groupname = input('enter group name: ')
      get_group(groupname)
    elif sel == 4: 
      username = input('enter user name: ')
      list_user_policies(username)
    elif sel == 5: list_policies()
    elif sel == 6: 
      username = input('enter user name: ')
      list_attached_user_policies(username)
    elif sel == 7: 
      groupname = input('enter group name: ')
      list_group_policies(groupname)
    elif sel == 8: 
      groupname = input('enter group name: ')
      list_attached_group_policies(groupname)
    elif sel == 9: 
      policyarn = input('enter policy arn: ')
      get_policy(policyarn)
    elif sel == 10: exit()
    else:
      print("invalid selection")
      break
    input("hit ENTER to continue")

  #list_attached_group_policies()


if __name__ == '__main__':
  main()
