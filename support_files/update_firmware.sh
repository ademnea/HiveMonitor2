#!/bin/bash

REPO_DIR="/home/pi/Desktop/HiveMonitor2"
LOG_FILE="/home/pi/Desktop/HiveMonitor2/support_files/update.log"

cd $REPO_DIR

# Fetch the latest changes from the remote repository
git fetch origin

# Check if there are any new commits
LOCAL=$(git rev-parse @)
REMOTE=$(git rev-parse @{u})

if [ $LOCAL != $REMOTE ]; then
    echo "$(date) Updates found. Pulling the latest changes..." >> $LOG_FILE
    
    # Attempt to merge the latest changes from the master branch
    # Use 'git merge' with the '--no-commit' flag to prevent automatic commit if merge succeeds without conflict
    git merge origin/master --no-commit
    
    # Check if there was a merge conflict
    if [ $? -ne 0 ]; then
        echo "$(date) Merge conflict detected. Aborting merge." >> $LOG_FILE
        git merge --abort
    else
        echo "$(date) Merge successful. Committing changes." >> $LOG_FILE
        git commit -m "Merged latest changes from master automatically."
    fi

    # Add any additional steps here, like restarting services or deploying
    # For example, to restart a service:
    # systemctl restart your_service_name

    echo "$(date) Update process completed." >> $LOG_FILE
else
    echo "$(date) No updates found." >> $LOG_FILE
fi
