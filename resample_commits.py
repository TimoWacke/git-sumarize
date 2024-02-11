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
    # repo_url = input("Enter repository url: ")
    repo_url = "https://github.com/TimoWacke/Second-Brain.git"
    # input new branch name
    # new_branch_name = input("Enter new branch name: ")
    new_branch_name = "squash"
    # input source branch
    # source_branch = input("Enter branch to summarize: ")
    source_branch = "main"
    # commiter name
    # commiter_name = input("Enter commiter name: ")
    commiter_name = "Timo Wacke"
    # commiter email
    # commiter_email = input("Enter commiter email: ")
    commiter_email = "wacketimo@gmail.com"
    # time interval of commits to be summarized
    interval = int(input("How many minutes between commits to summarize? "))
    
    # make a temporary directory and clone the repository
    temp_dir = mkdtemp()
    

    # get the list of desired commits from the source branch
    subprocess.run(["git", "clone", repo_url, temp_dir])
    subprocess.run(["git", "checkout", source_branch], cwd=temp_dir)
    desired_commits = parse_commits(temp_dir, interval)
   
    # connect in the destination directory to the origin and create a new clean empty branch
    # git init with origin
    subprocess.run(["git", "init"], cwd=temp_dir)
    subprocess.run(["git", "config", "user.email",  commiter_email], cwd=temp_dir)
    subprocess.run(["git", "config", "user.name",  commiter_name], cwd=temp_dir)
    subprocess.run(["git", "remote", "add", "origin", repo_url], cwd=temp_dir)
    subprocess.run(["git", "switch", "--orphan", new_branch_name], cwd=temp_dir)
    
    
    # for each commit in the list of desired commits, cherry-pick the commit from the source branch
    for commit_group in desired_commits:
        commit = commit_group.get("lead_commit")
        # cherry-pick the commits from the source branch
        subprocess.run(["git", "cherry-pick"] + [commit_id for commit_id in commit_group.get("summarizing_commit_ids")], cwd=temp_dir)
        subprocess.run(["git", "add", "."], cwd=temp_dir)
        # commit the changes to the destination directory
        commit_time = datetime.datetime.utcfromtimestamp(commit["commit_time"])
        author_email = commit["author_info"]["email"]
        author_name = commit["author_info"]["name"]
        message = commit["message"]
        subprocess.run(["git", "commit", "--date", commit_time.strftime('%Y-%m-%d %H:%M:%S'), "--author", f"{author_name} <{author_email}>", "-m", message], cwd=temp_dir)
        
    subprocess.run(["git", "push", "origin", new_branch_name], cwd=temp_dir)