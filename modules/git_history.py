import os
from pathlib import Path
from datetime import datetime

try:
    from git import Repo, InvalidGitRepositoryError, GitCommandError
    GIT_AVAILABLE = True
except ImportError:
    GIT_AVAILABLE = False

class GitHistoryExtractor:
    def __init__(self):
        self.git_available = GIT_AVAILABLE
    
    def extract(self, directory, max_commits=10):
        if not self.git_available:
            return {
                'error': 'GitPython 库未安装，请安装: pip install GitPython',
                'commits': [],
                'current_branch': None,
                'remotes': {}
            }
        
        try:
            repo_path = self._find_git_repo(directory)
            if not repo_path:
                return {
                    'error': '不是有效的 Git 仓库',
                    'commits': [],
                    'current_branch': None,
                    'remotes': {}
                }
            
            repo = Repo(repo_path)
            
            current_branch = self._get_current_branch(repo)
            remotes = self._get_remotes(repo)
            commits = self._get_commits(repo, max_commits)
            
            return {
                'commits': commits,
                'current_branch': current_branch,
                'remotes': remotes,
                'repo_path': str(repo_path)
            }
            
        except InvalidGitRepositoryError:
            return {
                'error': '无效的 Git 仓库',
                'commits': [],
                'current_branch': None,
                'remotes': {}
            }
        except Exception as e:
            return {
                'error': f'提取 Git 历史时出错: {str(e)}',
                'commits': [],
                'current_branch': None,
                'remotes': {}
            }
    
    def _find_git_repo(self, directory):
        path = Path(directory)
        if (path / '.git').exists():
            return path
        
        for parent in path.parents:
            if (parent / '.git').exists():
                return parent
        
        return None
    
    def _get_current_branch(self, repo):
        try:
            if repo.head.is_detached:
                return f"HEAD (detached) at {repo.head.commit.hexsha[:7]}"
            return repo.active_branch.name
        except Exception:
            return None
    
    def _get_remotes(self, repo):
        remotes = {}
        try:
            for remote in repo.remotes:
                try:
                    url = remote.url
                    remotes[remote.name] = url
                except Exception:
                    pass
        except Exception:
            pass
        return remotes
    
    def _get_commits(self, repo, max_commits):
        commits = []
        try:
            for commit in repo.iter_commits(max_count=max_commits):
                commit_info = {
                    'hash': commit.hexsha,
                    'message': commit.message.strip(),
                    'author': commit.author.name,
                    'email': commit.author.email,
                    'date': self._format_date(commit.committed_datetime),
                    'timestamp': commit.committed_date,
                    'parents': [p.hexsha for p in commit.parents]
                }
                
                try:
                    commit_info['stats'] = {
                        'files_changed': commit.stats.total.get('files', 0),
                        'insertions': commit.stats.total.get('insertions', 0),
                        'deletions': commit.stats.total.get('deletions', 0)
                    }
                except Exception:
                    commit_info['stats'] = {
                        'files_changed': 0,
                        'insertions': 0,
                        'deletions': 0
                    }
                
                commits.append(commit_info)
        except Exception:
            pass
        
        return commits
    
    def _format_date(self, dt):
        if hasattr(dt, 'strftime'):
            return dt.strftime('%Y-%m-%d %H:%M:%S')
        return str(dt)
    
    def get_commit_details(self, repo_path, commit_hash):
        if not self.git_available:
            return None
        
        try:
            repo = Repo(repo_path)
            commit = repo.commit(commit_hash)
            
            details = {
                'hash': commit.hexsha,
                'message': commit.message.strip(),
                'author': commit.author.name,
                'email': commit.author.email,
                'date': self._format_date(commit.committed_datetime),
                'files_changed': [],
                'diff': []
            }
            
            try:
                for file in commit.stats.files:
                    details['files_changed'].append(file)
            except Exception:
                pass
            
            try:
                if commit.parents:
                    parent = commit.parents[0]
                    diff = parent.diff(commit, create_patch=True)
                    for diff_item in diff:
                        details['diff'].append({
                            'file': diff_item.a_path or diff_item.b_path,
                            'change_type': diff_item.change_type,
                            'patch': diff_item.diff.decode('utf-8', errors='ignore') if diff_item.diff else ''
                        })
            except Exception:
                pass
            
            return details
            
        except Exception:
            return None
    
    def get_file_history(self, repo_path, file_path, max_commits=20):
        if not self.git_available:
            return []
        
        try:
            repo = Repo(repo_path)
            commits = []
            
            rel_path = os.path.relpath(file_path, repo_path)
            
            for commit in repo.iter_commits(paths=rel_path, max_count=max_commits):
                commits.append({
                    'hash': commit.hexsha,
                    'message': commit.message.strip(),
                    'author': commit.author.name,
                    'date': self._format_date(commit.committed_datetime)
                })
            
            return commits
            
        except Exception:
            return []
