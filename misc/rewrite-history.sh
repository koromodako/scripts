#!/usr/bin/env bash
git filter-branch -f --env-filter '
    if test "$GIT_AUTHOR_EMAIL" = "<email-to-be-removed-here>"
    then
        GIT_AUTHOR_NAME="koromodako"
        GIT_AUTHOR_EMAIL="koromodako@gmail.com"
        GIT_COMMITTER_NAME="koromodako"
        GIT_COMMITTER_EMAIL="koromodako@gmail.com"
    fi
' HEAD
