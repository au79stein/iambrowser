#!/usr/bin/env python3

import sys
import pyperclip
import boto3
from botocore.exceptions import ClientError
import json
import yaml
import pprint
from pick import pick
import policy as P

RESET  = "\033[0m"
RED    = "\033[0;31m"
GREEN  = "\033[0;32m"
YELLOW = "\033[0;33m"
CYAN   = "\033[0;36m"

GLOBAL_DEBUG = 0

profile = "mfa"
region  = "us-east-2"
service = "iam"

inlineUserPolicyList  = []
inlineGroupPolicyList = []
inlinePolicyList      = []
attachedPolicyList    = []
users = []
groups = []


# read config file
def read_config(cfile="config.yml"):
  with open(cfile) as cf:
    try:
      config = yaml.safe_load(cf)
      admin_policies = config['admin_policies']
      #print(f"admin_policies: {admin_policies}")
    except yaml.YAMLError as exc:
      print(exc)
    return admin_policies


# temp to display test show 
def look_at_policies(pollist):
  plen = len(pollist)
  print(f"length of pollist: {plen}")
  for p in pollist:
    print(f"{p.policyname}")

def look_at_mbrlist(somelist):
  slen = len(somelist)
  print(f"length of somelist: {slen}")
  for s in somelist:
    print(f"{s.username}")

def look_at_groups():
  glen = len(groups)
  print(f"length of group list is: {glen}")
  for g in groups:
    print(f"{g.groupname}")


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
  for p in inlinePolicyList:
    if p.policyname == policyname:
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


#######################
# build list of users #
#######################
def build_list_of_users(userList):
  '''creates a list of user objects'''
  debug = 0
  if debug > 0:
    print(f"build list of users...")
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
  if debug > 0:
    print_list(userList, msg="USER LIST")
    #ans = input("enter to continue")
    print()


########################
# build list of groups #
########################
def build_list_of_groups(groupList):
  '''create a list of group objects'''
  debug = 0
  if debug > 0:
    print(f"build list of groups...")
  iam = boto3.client('iam', region_name=region)
  paginator = iam.get_paginator('list_groups')
  for response in paginator.paginate():
    for group in response['Groups']:
      groupList.append(P.Group(group['GroupName'], group['GroupId'], group['Arn']))
  if debug > 0:
    print_list(groupList, msg="GROUP LIST")
    #ans = input("enter to continue")
    print()



################################
# build attached policies list #
################################
def build_attached_policies_list(policyList):
  '''creates a list of attached policies
     attached policies are a subset of all policies
     but are actually attached to something'''
  debug = 0
  if debug > 0:
    print(f"build attached policies list - all policies attached to account...")
  iam = boto3.client('iam', region_name=region)
  paginator = iam.get_paginator('list_policies')
  policy_params = {'OnlyAttached': True}
  for response in paginator.paginate(**policy_params):
    for policy in response["Policies"]:
      policyList.append(P.Policy(policy['PolicyName'], policy['PolicyId'], policy['Arn']))
  if debug > 0:
    print_list(policyList, msg="ATTACHED POLICIES LIST")
    #ans = input("enter to continue")
    print()


################################
# build inline policies lists  #
################################
# build inlineUserPolicyList
# build inlineGroupPolicyList
# build inlinePolicyList
# thinking that I could manage lists separately and merge into one also?
#
# add_user_inline_policies(username):
#
#def build_inline_policies_lists(inlinePolicyList, inlineUserPolicyList, inlineGroupPolicyList):
def build_inline_policies_lists():
  for u in users:
    add_user_inline_policies(u.username)

  for g in groups:
    add_group_inline_policies(g.groupname)


def update_policy_data(policyarn):
  '''update a policy object with attachment count and version id'''
  debug = 0
  iam = boto3.client('iam', region_name=region)
  response = iam.get_policy(PolicyArn=policyarn)['Policy']
  p = locate_policy_by_name(response['PolicyName'])
  if p:
    p.attachmentcount  =  response['AttachmentCount']
    p.defaultversionid =  response['DefaultVersionId']
    # try to save policy doc
    get_policy_document(policyarn, p.defaultversionid)
    if debug > 0:
      p.show()


def update_all_policies_data():
  '''loop through attached policies list
     for each policy, update policy data'''
  for p in attachedPolicyList:
    update_policy_data(p.arn)


#######################
# get policy document #
#######################
def get_policy_document(policyarn, versionid):
  '''get the policy document using policyarn and versionid'''
  pa = locate_policy_by_arn(policyarn)
  if pa:
    iam = boto3.client('iam', region_name=region)
    response = iam.get_policy_version(PolicyArn=policyarn, VersionId=versionid)['PolicyVersion']
    pa.document = response['Document']
    # open policy doc file
    policy_file_name = f"./Output/{pa.policyname}"
    pa.fdoc = open(policy_file_name, 'w')
    #pprint_json_str = pprint.pformat(json.dumps(pa.document), indent=4, width=1, depth=1)
    #pa.fdoc.write(json.dumps(pa.document))
    #pa.fdoc.write(json.dumps(pprint_json_str))
    #pa.fdoc.write(pprint_json_str)
    pa.fdoc.write(json.dumps(pa.document))
    pa.fdoc.close()
    
  else:
    print(f"policy arn {policyarn} not found")
  

##################################
# add inline policies to group   #
##################################
def add_inline_policies_to_group(groupname):
  '''list group inline policies'''
  debug = 0
  if debug > 0:
    print(f"{CYAN}---adding inline group policies to group {groupname}{RESET}")
  gn = locate_group_by_name(groupname)
  iam = boto3.client('iam', region_name=region)
  paginator = iam.get_paginator('list_group_policies')
  group_params = {'GroupName': groupname}
  try:
    for response in paginator.paginate(**group_params):
      for policy in response['PolicyNames']:
        if debug > 0:
          print(f"!>!>in add inline policies... policy = {policy}")
        pn = locate_policy_by_name(policy)
        if pn:
          if pn not in gn.inline_policies:
            gn.inline_policies.append(pn)
  except ClientError:
    print("couldn't list attached policies for {}".format(groupname))
  if debug > 0:
    print(f"   {YELLOW}---showing inline policies for group {groupname}---{RESET}")
    gn.show_inline_policies()


##################################
# add attached policies to group #
##################################
def add_attached_policies_to_group(groupname):
  '''get list of group attached policies
     add the policies to the group attached policy list'''
  debug = 0
  if debug > 0:
    print(f"{CYAN}---adding attached group policies to group {groupname}{RESET}")
  gn = locate_group_by_name(groupname)
  iam = boto3.client('iam', region_name=region)
  paginator = iam.get_paginator('list_attached_group_policies')
  group_params = {'GroupName': groupname}
  try:
    for response in paginator.paginate(**group_params):
      for policy in response['AttachedPolicies']:
        pn = locate_policy_by_name(policy['PolicyName'])
        if pn:
          gn.attached_policies.append(pn)
          #gn.show_attached_policies()
  except ClientError:
    print("couldn't list attached policies for {}".format(groupname))
  if debug > 0:
    print(f"   {YELLOW}---showing attached policies for group {groupname}---{RESET}")
    gn.show_attached_policies()


######################
# add groups to user #
######################
def add_groups_to_user(username):
  '''list groups to which a user belongs
     and add those groups to users list'''
  debug = 0
  if debug > 0:
    print(f"{CYAN}Adding groups to {username}{RESET}")
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
  except ClientError:
    print("couldn't list groups for {}".format(username))
  if debug > 0:
    print(f"---showing groups for {username}")
    un.show_groups()


########################
# add users into group #
########################
def add_users_into_group(groupname):
  '''get users in a group and add them to the group membership list'''
  debug = 0
  if debug > 0:
    print(f"---{CYAN}adding group users into group {groupname}{RESET}")
  gn = locate_group_by_name(groupname)
  iam = boto3.client('iam', region_name=region)
  paginator = iam.get_paginator('get_group')
  group_params = {'GroupName': groupname}
  try:
    for response in paginator.paginate(**group_params):
      for user in response['Users']:
        un = locate_user_by_name(user['UserName'])
        if un:
          if un not in gn.users:
            gn.users.append(un)
  except ClientError:
    print("couldn't get users for {}".format(groupname))
  if debug > 0:
    print(f"{YELLOW}display users added to group {groupname}")
    gn.show_users()

  
##############################
# add user attached policies #
##############################
def add_user_attached_policies(username):
  '''get user attached policies
     add them to user attached policies list'''
  debug = 0
  if debug > 0:
    print(f"---{YELLOW}Adding user attached policies for {username}{RESET}")
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
  if debug > 0:
    print(f"   ---{CYAN}showing attached policies for {username}{RESET}")
    u.show_attached_policies()


#############################
# add_group_inline_policies #
#############################
def add_group_inline_policies(groupname):
  '''get group inline policies
     add to group inline policies list'''
  debug = 0
  if debug > 0:
    print(f"---{YELLOW}Adding group inline policies for {groupname}{RESET}")
  gn = locate_group_by_name(groupname)
  iam = boto3.client('iam', region_name=region)
  paginator = iam.get_paginator('list_group_policies')
  policy_params = {'GroupName': groupname}
  try:
    for response in paginator.paginate(**policy_params):
      for policy in response['PolicyNames']:
        p = locate_policy_by_name(policy)
        if not p:
          p = P.Policy(policy, "", "")
        inlinePolicyList.append(p)
        inlineGroupPolicyList.append(p)
        gn.inline_policies.append(p)
  except ClientError:
    print("couldn't list group inline policies for {}".format(username))
  if debug > 0:
    print(f"   ---{CYAN}showing inline policies for {groupname}{RESET}")
    gn.show_inline_policies()


############################
# add user_inline_policies #
############################
def add_user_inline_policies(username):
  '''get user inline policies
     add to user inline policies list'''
  debug = 0
  if debug > 0:
    print(f"---{YELLOW}Adding user inline policies for {username}{RESET}")
  u = locate_user_by_name(username)
  iam = boto3.client('iam', region_name=region)
  paginator = iam.get_paginator('list_user_policies')
  policy_params = {'UserName': username}
  try:
    for response in paginator.paginate(**policy_params):
      for policy in response['PolicyNames']:
        p = locate_policy_by_name(policy)
        if not p:
          #p = P.Policy(policy['PolicyName'], policy['PolicyId'], policy['Arn'])
          p = P.Policy(policy, "", "")
        if p not in inlinePolicyList:
          inlinePolicyList.append(p)
        if p not in inlineUserPolicyList:
          inlineUserPolicyList.append(p)
  except ClientError:
    print("couldn't list inline policies for {}".format(username))
  if debug > 0:
    print(f"   ---{CYAN}showing inline policies for {username}{RESET}")
    u.show_inline_policies()


######################################
# add group policies to member users #
######################################
def add_group_policies_to_users():
  def populate_mbrlist(g, mbrlist):
    debug = 0
    for mbr in g.users:
      mbrlist.append(mbr)

    mlen = len(mbrlist)
    if debug > 0:
      print(f"mbrlist length: {mlen}")
      for m in mbrlist:
        print(f"mbrlist: mbr: {m.username}") 
    return mbrlist

  def populate_attached_policy_list(g, plist):
    debug = 0
    for p in g.attached_policies:
      plist.append(p)

    plen = len(plist)
    if debug > 0:
      print(f"plist length: {plen}")
      for x in plist:
        print(f"plist: policy name: {x.policyname}")
    return plist

  def populate_inline_policy_list(g, plist):
    for p in g.inline_policies:
      plist.append(p)

    plen = len(plist)
    if debug > 0:
      print(f"plist length: {plen}")
      for x in plist:
        print(f"plist: policy name: {x.policyname}")
    return plist

  def assign_group_policies_to_members_by_group(g, inlinepollist, attachpollist, mbrlist):
    debug = 0
    if debug > 0:
      print(f"   ---assigning group policies for groupname: {g.groupname} to members...")
    for m in mbrlist:
      for i in inlinepollist:
        if i not in m.group_inline_policies:
          m.group_inline_policies.append(i)
      for a in attachpollist:
        if a not in attachpollist:
          m.group_attached_policies.append(a)
      if debug > 0:
        print(f"{RED}attached group {g.groupname} policies to user {m.username}{RESET}")
        print(f"   ---{m.username}: {m.show_group_policies()}")
        print()

  ncnt = 0
  debug = 0
  if debug > 0:
    print(f"---{CYAN}adding group policies to users...{RESET}")
  mbrlist = []
  inlinepollist = []
  attachpollist = []

  for g in groups:
    if debug > 0:
      print(f"group name: {g.groupname}")
    mbrlist = []
    populate_mbrlist(g, mbrlist)

    inlinepollist = []
    attachpollist = []
    populate_inline_policy_list(g, inlinepollist)
    populate_attached_policy_list(g, attachpollist)

    assign_group_policies_to_members_by_group(g, inlinepollist, attachpollist, mbrlist)

    '''
    look_at_mbrlist(mbrlist)
    ncnt = ncnt + 1
    print()
    look_at_policies(inlinepollist)
    print()
    look_at_policies(attachpollist)
    print()
    if ncnt > 5:
      exit()
    '''

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


######################################
# add attached polices to all groups #
######################################
def add_attached_policies_to_all_groups():
  debug = 0
  for g in groups:
    if debug > 0:
      print(f"{CYAN}Adding Inline Policies To Group")
    add_inline_policies_to_group(g.groupname)
    if debug > 0:
      print(f"{CYAN}Adding Attached Policies To Group")
    add_attached_policies_to_group(g.groupname)
    #g.show_attached_policies()


#######################
# add users to groups #
#######################
def add_users_to_groups():
  ''' go thru the list of groups
      get the users in each group
      update the group with the names of each user
      that is a member'''
  debug = 0
  if debug > 0:
    print(f"{CYAN}Adding group users into groups{RESET}")
  for g in groups:
    gn = locate_group_by_name(g.groupname)
    add_users_into_group(g.groupname)
    #gn.show_users()


#######################
# add groups to users #
#######################
def add_groups_to_users():
  ''' loop through list of users
      get list of groups to which they belong
      add these groups to the users list
      already have func to do this for one user'''
  debug = 0
  if debug > 0:
    print(f"{CYAN}Adding Groups To Users...{RESET}")
  for u in users:
    if debug > 0:
      print(f"{u.username} ", end="")
    add_groups_to_user(u.username)
    #u.show_groups()
    if debug > 0:
      print(f"done!")


#####################
# add user policies #
#####################
def add_user_policies():
  debug = 0
  if debug > 0:
    print(f"{CYAN}Adding User Policies...{RESET}")
  for u in users:
    #print(f">> {u.username}")
    add_user_inline_policies(u.username)
    #u.show_inline_policies()

    if debug > 0:
      print(f"!! {u.username}")
    add_user_attached_policies(u.username)
    #u.show_attached_policies()


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
  build_inline_policies_lists()

  ##########################
  # print users and groups #
  ##########################
  #print_list(users, msg="List of Users")
  #print_list(groups, msg="List of Groups")
  #print_list(attachedPolicyList, msg="List of Attached Policies")

  ####################################################
  # add group inline and attached policies to groups #
  ####################################################
  add_attached_policies_to_all_groups()

  ####################################################
  # tell users about the groups to which they belong #
  ####################################################
  add_groups_to_users()

  ############################
  # update groups with users #
  ############################
  add_users_to_groups()

  ##########################################################
  # add group policies to the users that belong to a group #
  ##########################################################
  add_group_policies_to_users()

  ###############################################################
  # add user policies, inline and attached to user policy lists #
  ###############################################################
  add_user_policies()

  update_all_policies_data()


def main():

  ## get config parameters ##
  admin_policies = read_config()
  for ap in admin_policies:
    P.Policy.admin_policies.append(ap)
  #print(f"Policy.admin_policies = {P.Policy.admin_policies}")
  

  ########################
  # initialize and setup #
  ########################
  init_build_lists()

  ##!!!!  temp force copy of group policies to user policies

  for g in groups:
    ul = []
    ul = g.userlist()
    for u in ul:
      g.copy_inline_policies_to_user(u)
      g.copy_attached_policies_to_user(u)

  '''
  rich = locate_user_by_name('rgoldstein')
  if rich:
    rich.db_row()
    print()
    #rich.show_attached_policies()
    #rich.show_inline_policies()
    #rich.show_group_attached_policies()
    #rich.show_group_inline_policies()

  dsilva = locate_user_by_name('dsilva')
  if dsilva:
    dsilva.db_row()
    print()

  ibassi = locate_user_by_name('ibassi')
  if ibassi:
    ibassi.db_row()
    print()

  mlimachi = locate_user_by_name('mlimachi')
  if mlimachi:
    mlimachi.db_row()
    print()

  '''

  for u in users:
    u.db_row()





if __name__ == "__main__":
  main()

