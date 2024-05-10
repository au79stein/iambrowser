# iam browser

Browse iam info from the CLI - a work in progress

##  GUI... Too much clicking

Working on a way to connect all useful information within IAM into something that flows and is seemingly connected from an admin perspective.
The idea is to not only browse most of what can be seen from the GUI but also, to build out team relationships, permissions, etc and to
be able to query against it.

## thinking aloud...

not sure if it makes sense to 'cache' this data for longer periods of time, or make sure you go back to the ultimate source of truth
each time.  If the local cache is ephemeral, then perhaps use in memory db to retain that information?  Perhaps to build out a local
in-memory db that is forced to refresh when new elements or relationships are added in order to stay in-sync?

I obviously don't want to just recreate a CLI version of the IAM service... but who decides what is useful... um, me for now :) 
Also, when building out the local cache, I would like to set this up such that the relationships exist in a way that is fairly 
easy to generate reports.  But what reports do I need, how useful or how frequently used are they?

## first pass

going to skip the cache for now and use just live calls to IAM until I can figure out what I need to retain.

I will be working mostly on security reporting from a company audit perspective - so, users, groups, roles, attached and inline policies.
it would be nice to be able to 'see' who has access and permissions to modify.


