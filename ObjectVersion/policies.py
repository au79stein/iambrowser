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


def locate_policy_by_arn(policyarn):
  '''lookup a policy by arn'''
  for a in attachedPolicyList:
    if a.arn == policyarn:
      a.show()
      return a
  return None


def locate_policy_by_name(policyname):
  '''lookup a policy by name '''
  for p in attachedPolicyList:
    if p.policyname == policyname:
      #p.show()
      return p
  return None


def locate_user(username):
  '''lookup a user seaching by name'''
  for u in users:
    if u.username == username:
      print(f"found {username}")
      #u.show()
      return u
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

  #print(f"PolicyName: {response['PolicyName']}, PolicyId: {response['PolicyId']}, AttachmentCount: {response['AttachmentCount']}, DefaultVersionId: {response['DefaultVersionId']}, Arn: {response['Arn']}", end="")
  #print()
  #print("temporarily added call here to get_policy_version to display document also")
  #versionid = response['DefaultVersionId']
  #get_policy_version(policyarn, versionid)


def get_policy_document(policyarn, versionid):
  iam = boto3.client('iam', region_name=region)
  response = iam.get_policy_version(PolicyArn=policyarn, VersionId=versionid)['PolicyVersion']
  
  print(f"VersionId: {response['VersionId']}, \n")
  print(f"{response['Document']}", end="")
  print()
  pprint(response['Document'])


  
def main():
  build_attached_policies_list(attachedPolicyList)
  print_list(attachedPolicyList, msg="List of Attached Policies")

  build_list_of_users(users)
  print_list(users, msg="List of Users")

  rich = locate_user('rgoldstein')
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


if __name__ == "__main__":
  main()

