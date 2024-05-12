#!/usr/bin/env python3

import sys
import pyperclip
import boto3
from botocore.exceptions import ClientError
from pprint import pprint
from pick import pick
import policy as P

profile = "mfa"
region  = "us-east-2"
service = "iam"

attachedPolicyList = []
users = []
groups = []


def locate_policy_by_arn(policyarn):
  '''lookup a policy by arn'''
  for a in attachedPolicyList:
    if a.arn == policyarn:
      #a.show()
      return a
  return None


def locate_policy_by_name(policyname):
  '''lookup a policy by name '''
  for p in attachedPolicyList:
    if p.policyname == policyname:
      #p.show()
      return p
  return None


def locate_user_by_name(username):
  '''lookup a user seaching by name'''
  for u in users:
    if u.username == username:
      #print(f"found {username}")
      #u.show()
      return u
  return None


def locate_group_by_name(groupname):
  '''lookup a group by its groupname'''
  for gn in groups:
    if gn.groupname == groupname:
      gn.show()
      return gn
  return None


def print_list(policyList, msg=""):
  '''print any list of objects we have created 
     by calling show() method'''
  if msg:
    title = msg
  else:
    title = "-----"
  print(f"-----{title}-----")

  linenum = 1
  for apl in policyList:
    print(f"{linenum: 4d}: ", end="")
    apl.show()
    linenum = linenum + 1


def build_list_of_users(userList):
  '''creates a list of user objects'''
  iam = boto3.client('iam', region_name=region)
  paginator = iam.get_paginator('list_users')
  for response in paginator.paginate():
    for user in response["Users"]:
      createdate = user['CreateDate'].strftime('%m/%d/%Y')
      if "PasswordLastUsed" in user:
        pwdate = user['PasswordLastUsed'].strftime('%m/%d/%Y')
      else:
        pwdate = "Never"
      userList.append(P.User(user['UserName'], user['UserId'], user['Arn'], createdate, pwdate))


def build_list_of_groups(groupList):
  '''create a list of group objects'''
  iam = boto3.client('iam', region_name=region)
  paginator = iam.get_paginator('list_groups')
  for response in paginator.paginate():
    for group in response['Groups']:
      groupList.append(P.Group(group['GroupName'], group['GroupId'], group['Arn']))

  
def build_attached_policies_list(policyList):
  '''creates a list of attached policies
     attached policies are a subset of all policies
     but are actually attached to something'''
  iam = boto3.client('iam', region_name=region)
  paginator = iam.get_paginator('list_policies')
  policy_params = {'OnlyAttached': True}
  for response in paginator.paginate(**policy_params):
    for policy in response["Policies"]:
      policyList.append(P.Policy(policy['PolicyName'], policy['PolicyId'], policy['Arn']))


def update_policy_data(policyarn):
  '''update a policy object with attachment count and version id'''
  iam = boto3.client('iam', region_name=region)
  response = iam.get_policy(PolicyArn=policyarn)['Policy']
  p = locate_policy_by_name(response['PolicyName'])
  if p:
    p.attachmentcount  =  response['AttachmentCount']
    p.defaultversionid =  response['DefaultVersionId']
    p.show()


def get_policy_document(policyarn, versionid):
  '''get the policy document using policyarn and versionid'''
  pa = locate_policy_by_arn(policyarn)
  if pa:
    iam = boto3.client('iam', region_name=region)
    response = iam.get_policy_version(PolicyArn=policyarn, VersionId=versionid)['PolicyVersion']
    pa.document = response['Document']
    pa.show_document()
  else:
    print(f"policy arn {policyarn} not found")
  

def add_users_in_group(groupname):
  gn = locate_group_by_name(groupname)
  iam = boto3.client('iam', region_name=region)
  paginator = iam.get_paginator('get_group')
  group_params = {'GroupName': groupname}
  try:
    for response in paginator.paginate(**group_params):
      for user in response['Users']:
        un = locate_user_by_name(user['UserName'])
        if un:
          gn.users.append(un)
  except ClientError:
    print("couldn't get users for {}".format(groupname))

  
def add_user_attached_policies(username):
  '''get user attached policies'''
  u = locate_user_by_name(username)
  iam = boto3.client('iam', region_name=region)
  paginator = iam.get_paginator('list_attached_user_policies')
  policy_params = {'UserName': username}
  try:
    for response in paginator.paginate(**policy_params):
      for policy in response['AttachedPolicies']:
        p = locate_policy_by_name(policy['PolicyName'])
        if p:
          u.attached_policies.append(p)
  except ClientError:
    print("couldn't list attached policies for {}".format(username))

'''
============================
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

============================
'''

def add_user_inline_policies(username):
  '''get user inline policies'''
  u = locate_user_by_name(username)
  iam = boto3.client('iam', region_name=region)
  paginator = iam.get_paginator('list_user_policies')
  policy_params = {'UserName': username}
  try:
    for response in paginator.paginate(**policy_params):
      for policy in response['PolicyNames']:
        p = locate_policy_by_name(policy)
        if p:
          u.inline_policies.append(p)
          u.show_policies()
  except ClientError:
    print("couldn't list inline policies for {}".format(username))


def main():
  build_attached_policies_list(attachedPolicyList)
  print_list(attachedPolicyList, msg="List of Attached Policies")

  build_list_of_users(users)
  print_list(users, msg="List of Users")

  build_list_of_groups(groups)
  print_list(groups, msg="List of Groups")

  rich = locate_user_by_name('rgoldstein')
  if rich:
    rich.show()
  else:
    print("user not found")

  pol = locate_policy_by_name('terraform-staging-only')
  if pol:
    pol.show()
  else:
    print("policy not found")

  update_policy_data('arn:aws:iam::aws:policy/PowerUserAccess')

  polarn = locate_policy_by_arn('arn:aws:iam::aws:policy/PowerUserAccess')
  if polarn:
    polarn.show()
  else:
    print("policy arn not found")

  get_policy_document('arn:aws:iam::aws:policy/PowerUserAccess', 'v5')

  gn = locate_group_by_name('devops-beginner')
  add_users_in_group('devops-beginner')
  gn.show_users()

  gn = locate_group_by_name('admin')
  add_users_in_group('admin')
  gn.show_users()


  #################################################
  ### testing user inline and attached policies ###
  #################################################
  '''
  for u in users:
    print(f">> {u.username}")
    add_user_inline_policies(u.username)
    u.show_inline_policies()

  for u in users:
    print(f"!! {u.username}")
    add_user_attached_policies(u.username)
    u.show_attached_policies()
  '''
  for u in users:
    print(f">> {u.username}")
    add_user_inline_policies(u.username)
    u.show_inline_policies()
    add_user_attached_policies(u.username)
    u.show_attached_policies()


if __name__ == "__main__":
  main()

