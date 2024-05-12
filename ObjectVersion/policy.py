#!/usr/bin/env python3
# user.py
from pprint import pprint


class User:
  # Username: rgoldstein, Arn: arn:aws:iam::079704269206:user/rgoldstein, Created: 04/25/2024 PasswordLastUsed: 05/09/2024

  username    = ""
  userid      = ""
  arn         = ""
  create_date = ""
  pw_date     = ""
  groups = []
  attached_policies = []
  inline_policies = []

  def __init__(self, username, userid, arn, create_date, pw_date):
    self.username          = username
    self.userid            = userid
    self.arn               = arn
    self.create_date       = create_date
    self.pw_date           = pw_date
    self.groups            = []
    self.inline_policies   = []
    self.attached_policies = []

  def show(self):
    print(f"UserName: {self.username}, UserId: {self.userid}, Arn: {self.arn}, Created: {self.create_date}, PWDate: {self.pw_date}")

  def add_group(self, group):
    self.groups.append(group)

  def show_groups(self):
    for g in self.groups:
      g.show()

  def add_attached_policy(self, policy):
    self.attached_policies.append(policy)

  def add_inline_policy(self, policy):
    self.inline_policies.append(policy)

  def show_attached_policies(self):
    for a in self.attached_policies:
      a.show()

  def show_inline_policies(self):
    for a in self.inline_policies:
      a.show()


class Group:

  # 20: GroupName: devops-beginner,  GroupId: AGPARFDV6UGLOMCC4MNWD
  groupname = ""
  groupid   = ""
  arn       = ""
  users     = []

  def __init__(self, groupname, groupid, arn):
    self.groupname = groupname
    self.groupid   = groupid
    self.arn       = arn

  def show(self):
    print(f"GroupName: {self.groupname}, GroupId: {self.groupid}, Arn: {self.arn}")

  def show_users(self):
    for u in self.users:
      print(f"user: {u.username}")
    

class Policy:
  policyname         = ""
  policyid           = ""
  arn                = ""
  attachmentcount    = ""
  defaultversionid   = ""
  # not sure, do I want to save the policy document
  document           = ""

  def __init__(self, policyname, policyid, arn):
    self.policyname = policyname
    self.policyid   = policyid
    self.arn        = arn

  def show(self, nl=False):
    print(f"PolicyId: {self.policyid}, PolicyName: {self.policyname},  Arn: {self.arn},  AttachCount: {self.attachmentcount}, DefaultVerId: {self.defaultversionid}")

  def show_document(self):
    pprint(self.document)
      

    
