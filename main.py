#!/usr/bin/env python3

from time import sleep
from git import Repo
from git.exc import NoSuchPathError
import subprocess
import os

class TaskProvider:
    def has_new_task(self):
        pass

    def get_new_task(self):
        pass

empty_task = []

class GitRepo(TaskProvider):
    def __init__(self, repo_url, local_path):
        self.repo_url = repo_url
        self.local_path = local_path
        try:
            self.repo = Repo(local_path)
        except NoSuchPathError:
            self.repo = Repo.clone_from(repo_url, local_path)
        self.task_file = os.path.join(local_path, "task.sh")
        self.pull()

    def get_local_commit(self):
        return self.repo.head.commit.hexsha

    def get_remote_commit(self):
        self.repo.remote().fetch()
        return self.repo.remote().refs[0].commit.hexsha

    def get_diff_file_list(self, local_commit, remote_commit):
        return self.repo.git.diff("--name-only", local_commit, remote_commit)

    def pull(self):
        self.repo.remotes.origin.pull(rebase=True)

    def push(self):
        self.repo.remotes.origin.push()


    def do_task(self):
        subprocess.run(f"cat {self.task_file} >> {os.path.join(self.local_path, "history")}", shell=True)
        subprocess.run(f"cat {self.task_file} > {os.path.join(self.local_path, "running")}", shell=True)
        self.repo.index.remove(["task.sh"], working_tree=True)
        self.repo.index.add(["history", "running"])
        self.repo.index.commit(f"New task completed: {time.now()}")
        self.pull()
        self.push()
        output_file = f"output_{time.now()}"
        subprocess.run(f"bash {self.task_file} > {os.path.join(self.local_path, output_file)}", shell=True)
        self.repo.index.add(output_file)
        self.repo.index.remove(["running"], working_tree=True)
        self.repo.index.commit(f"Removed task file: {time.now()}")
        self.push()

    def run_task(self):
        while True:
            sleep(1)
            self.pull()
            if os.path.exists(self.task_file):
                self.do_task()





if __name__ == "__main__":
    g = GitRepo("git@github.com:skyfireitdiy/gitask-task.git", ".gitask-task")
    g.run_task()

    # m = TaskManager(g)
    # m.run()

