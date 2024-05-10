#!/usr/bin/env python3

import botocore.exceptions

for key, value in sorted(botocore.exceptions.__dict__.items()):
  if isinstance(value, type):
    print(key)
