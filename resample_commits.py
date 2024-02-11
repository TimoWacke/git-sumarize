import os
import subprocess
import datetime

# import temp directory
from tempfile import mkdtemp
import shutil


def parse_commits(repo_path, interval_units):
    commits_info = {}

    # Run git log command to get commit information
    git_log_output = subprocess.check_output(['git', 'log', '--pretty=format:%H|%ct|%an|%ae|%s'], cwd=repo_path, universal_newlines=True)

    
    # Iterate over each line of git log output
    for line in git_log_output.strip().split('\n'):
        commit_id, commit_time, author_name, author_email, commit_message = line.split('|')

        # Convert commit time to integer
        commit_time = int(commit_time)

        # Add commit information to the dictionary
        commit_info = {
            'commit_id': commit_id,
            'commit_time': commit_time,
            'author_info': {
                'name': author_name,
                'email': author_email
            },
            'message': commit_message
        }
       
        # Convert the commit time to hours only
        commit_interval = commit_time // (interval_units * 60)

        # Add the commit to the list of commits for the hour
        if commit_interval not in commits_info:
            commits_info[commit_interval] = []
        commits_info[commit_interval].append(commit_info)

    # Create a list to store the last commit of each hour
    desired_commits = []

    # Iterate over the commits grouped by hour
    for interval, commits in sorted(commits_info.items()):
        # Append the last commit of the hour to the desired_commits list
        # print messages of commits summarised
        desired_commits.append({ "lead_commit": commits[-1], "summarizing_commit_ids": [commit["commit_id"] for commit in commits] })

    return desired_commits


if __name__ == "__main__":
    # input repository url
    repo_url = input("Enter repository url: ")
    # input new branch name
    new_branch_name = input("Enter new branch name: ")
    # input source branch
    source_branch = input("Enter branch to summarize: ")
    # commiter name
    commiter_name = input("Enter commiter name: ")
    # commiter email
    commiter_email = input("Enter commiter email: ")
    # time interval of commits to be summarized
    interval = int(input("How many minutes between commits to summarize? "))
    
    # make a temporary directory and clone the repository
    temp_source_dir = mkdtemp()    
    temp_dir = mkdtemp()

    # get the list of desired commits from the source branch
    subprocess.run(["git", "clone", repo_url, temp_source_dir])
    subprocess.run(["git", "checkout", source_branch], cwd=temp_source_dir)
    desired_commits = parse_commits(temp_source_dir, interval)
   
    # connect in the destination directory to the origin and create a new clean empty branch
    # git init with origin
    subprocess.run(["git", "init"], cwd=temp_dir)
    subprocess.run(["git", "config", "user.email",  commiter_email], cwd=temp_dir)
    subprocess.run(["git", "config", "user.name",  commiter_name], cwd=temp_dir)
    subprocess.run(["git", "remote", "add", "origin", repo_url], cwd=temp_dir)
    subprocess.run(["git", "checkout", "-b", new_branch_name], cwd=temp_dir)
    
    # for each commit in the list of desired commits checkout the source branch and copy it to the destination directory
    for commit_group in desired_commits:
        subprocess.run(["git", "checkout", commit_group["lead_commit"]["commit_id"]], cwd=temp_source_dir)
        # copy the files from the source directory to the destination directory
        # ignore the .git directory
        subprocess.run(["rsync", "-a", "--exclude", ".git", "--delete", temp_source_dir + "/", temp_dir], cwd=temp_dir)
        subprocess.run(["git", "add", "."], cwd=temp_dir)
        # commit the changes
        # time format Wed Feb 16 14:00 2011 +0100
        args = ["git", "commit", "-m", commit_group["lead_commit"]["message"], f'--date={datetime.datetime.fromtimestamp(commit_group["lead_commit"]["commit_time"]).strftime("%a %b %d %H:%M %Y %z")}']
        subprocess.run(args, cwd=temp_dir)
        print(args)
        
    # git filter-branch --env-filter 'export GIT_COMMITTER_DATE="$GIT_AUTHOR_DATE"'
    subprocess.run(["git", "filter-branch", "--env-filter", 'export GIT_COMMITTER_DATE="$GIT_AUTHOR_DATE"'], cwd=temp_dir)
        
    subprocess.run(["git", "push", "--force", "origin", new_branch_name], cwd=temp_dir)
    
    shutil.rmtree(temp_source_dir)
    shutil.rmtree(temp_dir)