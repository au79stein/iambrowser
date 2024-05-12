#!/usr/bin/env python3

import sys
import pyperclip
import boto3
from botocore.exceptions import ClientError
from pprint import pprint
from pick import pick
import policy as P

RESET  = "\033[0m"
RED    = "\033[0;31m"
GREEN  = "\033[0;32m"
YELLOW = "\033[0;33m"
CYAN   = "\033[0;36m"

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
      #gn.show()
      return gn
  return None


def print_list(policyList, msg=""):
  '''print any list of objects we have created 
     by calling show() method'''
  if msg:
    title = GREEN+msg+RESET
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
  

def add_groups_to_user(username):
  '''list groups to which a user belongs
     and add those groups to users list'''
  #linenum = 1
  un = locate_user_by_name(username)
  iam = boto3.client('iam', region_name=region)
  paginator = iam.get_paginator('list_groups_for_user')
  group_params = {'UserName': username}
  try:
    for response in paginator.paginate(**group_params):
      for group in response['Groups']:
        gn = locate_group_by_name(group['GroupName'])
        if gn:
          un.groups.append(gn)
        #print(f"{linenum: 4d}: ", end="")
        #print(f"GroupName: {group['GroupName']},  GroupId: {group['GroupId']}", end="")
        #print()
        #linenum = linenum + 1
  except ClientError:
    print("couldn't list groups for {}".format(username))


def add_users_into_group(groupname):
  '''get users in a group and add them to the group membership list'''
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


######################################
# add_group_inline_policies_to_users #
######################################
# 1. get members of the group
# 2. get policies for the group
# 3. for each member, add policies 
######################################
def add_group_inline_policies_to_users(groupname):
  group_members = []


############################
# add user_inline_policies #
############################
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


def test_get_policy_document():
  get_policy_document('arn:aws:iam::aws:policy/PowerUserAccess', 'v5')


def test_update_policy_data():
  update_policy_data('arn:aws:iam::aws:policy/PowerUserAccess')


def test_get_groups_for_user():
  ############################
  # test get groups for user #
  ############################
  for u in users:
    print(f"Username = {u.username}")
    add_groups_to_user(u.username)
    u.show_groups()
    print()
  

def test_inline_and_attached_policies():
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
    print(f"!! {u.username}")
    add_user_attached_policies(u.username)
    u.show_attached_policies()


def test_lookup_groups(test_group_names):
  #test_group_names = ['devops-beginner', 'admin']
  #test_lookup_groups(test_group_names)

  for g in test_group_names:
    testgrp = locate_group_by_name(g)
    if testgrp:
      testgrp.show()
    else:
      print(f"group {n} not found")


def test_lookup_policies(test_policy_names, test_policy_arns):
  #test_policy_names = ['terraform-stagin-only']
  #test_policy_arns  = ['arn:aws:iam::aws:policy/PowerUserAccess']
  #test_lookup_policies(test_policy_names, test_policy_arns)

  for n in test_policy_names:
    testpol = locate_policy_by_name(n)
    if testpol:
      testpol.show()
    else:
      print(f"named policy {n} not found")

  for a in test_policy_arns:
    testarn = locate_policy_by_arn(a)
    if testarn:
      testarn.show()
    else:
      print(f"policy arn {a} not found")


def test_lookup_users(test_users):
  for u in test_users:
    testuser = locate_user_by_name(u)
    if testuser:
      testuser.show()
    else:
      print(f"user {u}not found")


def add_users_to_groups():
  ''' go thru the list of groups
      get the users in each group
      update the group with the names of each user
      that is a member'''
  for g in groups:
    gn = locate_group_by_name(g.groupname)
    add_users_into_group(g.groupname)
    gn.show_users()


def add_groups_to_users():
  ''' loop through list of users
      get list of groups to which they belong
      add these groups to the users list
      already have func to do this for one user'''
  for u in users:
    print(f"adding groups to {u.username}...")
    add_groups_to_user(u.username)
    u.show_groups()
    print(f"done! \n")


def init_build_lists():
  ##########################
  # build users and groups #
  ##########################
  build_list_of_users(users)
  build_list_of_groups(groups)

  #########################################################
  # build list of policies that are being used (attached) #
  #########################################################
  build_attached_policies_list(attachedPolicyList)

  ##########################
  # print users and groups #
  ##########################
  print_list(users, msg="List of Users")
  print_list(groups, msg="List of Groups")
  print_list(attachedPolicyList, msg="List of Attached Policies")

  add_groups_to_users()


def main():

  ########################
  # initialize and setup #
  ########################
  init_build_lists()

  

if __name__ == "__main__":
  main()

