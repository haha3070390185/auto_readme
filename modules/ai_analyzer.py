import os
import json
from pathlib import Path

try:
    import requests
    REQUESTS_AVAILABLE = True
except ImportError:
    REQUESTS_AVAILABLE = False

try:
    from openai import OpenAI
    OPENAI_AVAILABLE = True
except ImportError:
    OPENAI_AVAILABLE = False

class AIAnalyzer:
    def __init__(self, api_key=None, base_url="https://api.deepseek.com/v1", model="deepseek-v4-pro"):
        self.api_key = api_key
        self.base_url = base_url
        self.model = model
        self.use_openai_sdk = OPENAI_AVAILABLE
        
        if self.use_openai_sdk and api_key:
            self.client = OpenAI(
                api_key=api_key,
                base_url=base_url
            )
        else:
            self.client = None
    
    def _call_api(self, system_prompt, user_prompt, max_tokens=4096, temperature=1.0, top_p=1.0):
        if not self.api_key:
            raise ValueError("API key not provided")
        
        if not REQUESTS_AVAILABLE and not self.use_openai_sdk:
            raise ImportError("Neither requests nor openai library is available")
        
        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt}
        ]
        
        if self.use_openai_sdk and self.client:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=messages,
                max_tokens=max_tokens,
                temperature=temperature,
                top_p=top_p
            )
            return response.choices[0].message.content
        else:
            if not REQUESTS_AVAILABLE:
                raise ImportError("requests library is required")
            
            headers = {
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json"
            }
            
            payload = {
                "model": self.model,
                "messages": messages,
                "max_tokens": max_tokens,
                "temperature": temperature,
                "top_p": top_p
            }
            
            response = requests.post(
                f"{self.base_url}/chat/completions",
                headers=headers,
                json=payload
            )
            
            if response.status_code != 200:
                raise Exception(f"API call failed: {response.status_code} - {response.text}")
            
            data = response.json()
            return data["choices"][0]["message"]["content"]
    
    def analyze_code(self, scan_result, api_key=None):
        if api_key:
            self.api_key = api_key
            if self.use_openai_sdk:
                self.client = OpenAI(
                    api_key=api_key,
                    base_url=self.base_url
                )
        
        core_files = self._get_core_files(scan_result)
        code_snippets = self._extract_code_snippets(core_files)
        
        system_prompt = """你是一位专业的软件工程师和技术文档专家。你的任务是分析代码片段并生成专业的技术分析。

请根据提供的代码片段，分析以下内容：
1. 核心逻辑说明：解释代码的主要功能和实现原理
2. API 列表：识别并列出所有公开的函数、类、方法及其参数和返回值
3. 关键依赖：识别代码使用的主要库和框架
4. 技术亮点：指出代码中值得关注的设计模式或技术实现

请以清晰、专业的格式输出分析结果，使用 Markdown 格式。"""
        
        user_prompt = f"""请分析以下项目的代码片段：

项目信息：
- 编程语言：{', '.join(scan_result.get('languages', []))}
- 技术栈：{json.dumps(scan_result.get('tech_stack', {}), indent=2, ensure_ascii=False)}
- 核心入口文件：{[f['name'] for f in scan_result.get('entry_files', [])]}

代码片段：
{code_snippets}

请生成详细的代码分析，包括核心逻辑说明、API 列表、关键依赖和技术亮点。"""
        
        try:
            analysis = self._call_api(system_prompt, user_prompt)
            return {
                'analysis': analysis,
                'core_files': core_files,
                'snippets_count': len(code_snippets)
            }
        except Exception as e:
            return {
                'error': str(e),
                'core_files': core_files,
                'snippets_count': len(code_snippets)
            }
    
    def generate_project_overview(self, scan_result, api_key=None):
        if api_key:
            self.api_key = api_key
            if self.use_openai_sdk:
                self.client = OpenAI(
                    api_key=api_key,
                    base_url=self.base_url
                )
        
        tech_stack = scan_result.get('tech_stack', {})
        languages = scan_result.get('languages', [])
        entry_files = scan_result.get('entry_files', [])
        file_count = scan_result.get('file_count', 0)
        
        system_prompt = """你是一位专业的技术文档作家和项目分析师。你的任务是根据项目信息生成专业的项目概述。

请根据提供的信息，生成以下内容：
1. 项目简介：用简洁的语言描述项目的整体定位和用途
2. 技术栈说明：详细说明项目使用的编程语言、框架、构建工具等
3. 项目结构：描述项目的目录结构和主要模块
4. 快速开始：提供基本的安装和运行说明（基于检测到的技术栈）

请以清晰、专业的格式输出，使用 Markdown 格式，语言使用中文。"""
        
        user_prompt = f"""请根据以下信息生成项目概述：

项目基本信息：
- 文件总数：{file_count}
- 编程语言：{', '.join(languages) if languages else '未检测到'}

技术栈信息：
- 框架：{', '.join(tech_stack.get('frameworks', [])) or '未检测到'}
- 构建工具：{', '.join(tech_stack.get('build_tools', [])) or '未检测到'}
- 包管理器：{', '.join(tech_stack.get('package_managers', [])) or '未检测到'}
- 数据库：{', '.join(tech_stack.get('databases', [])) or '未检测到'}

核心入口文件：
{self._format_entry_files(entry_files)}

请生成专业的项目概述，包括项目简介、技术栈说明、项目结构和快速开始指南。"""
        
        try:
            overview = self._call_api(system_prompt, user_prompt)
            return {
                'overview': overview,
                'tech_stack_summary': {
                    'languages': languages,
                    'frameworks': tech_stack.get('frameworks', []),
                    'build_tools': tech_stack.get('build_tools', []),
                    'package_managers': tech_stack.get('package_managers', []),
                    'databases': tech_stack.get('databases', [])
                }
            }
        except Exception as e:
            return {
                'error': str(e),
                'tech_stack_summary': {
                    'languages': languages,
                    'frameworks': tech_stack.get('frameworks', []),
                    'build_tools': tech_stack.get('build_tools', []),
                    'package_managers': tech_stack.get('package_managers', []),
                    'databases': tech_stack.get('databases', [])
                }
            }
    
    def summarize_git_history(self, git_history, api_key=None, max_commits=10):
        if api_key:
            self.api_key = api_key
            if self.use_openai_sdk:
                self.client = OpenAI(
                    api_key=api_key,
                    base_url=self.base_url
                )
        
        commits = git_history.get('commits', [])[:max_commits]
        current_branch = git_history.get('current_branch', 'unknown')
        remotes = git_history.get('remotes', {})
        
        if not commits:
            return {
                'summary': '无 Git 提交历史可供分析',
                'evolution_status': '项目可能刚初始化或不是 Git 仓库'
            }
        
        system_prompt = """你是一位专业的项目分析师和版本控制专家。你的任务是分析 Git 提交历史并生成项目演进总结。

请根据提供的提交历史，分析以下内容：
1. 项目演进状态：描述项目的开发进度和当前状态
2. 主要功能变化：总结最近提交中添加、修改或删除的主要功能
3. 开发趋势：分析项目的开发模式和方向
4. 关键提交：指出最重要的几次提交及其影响

请以清晰、专业的格式输出，使用 Markdown 格式，语言使用中文。"""
        
        formatted_commits = self._format_commits(commits)
        
        user_prompt = f"""请分析以下 Git 提交历史：

仓库信息：
- 当前分支：{current_branch}
- 远程仓库：{json.dumps(remotes, indent=2, ensure_ascii=False) if remotes else '无'}

最近 {len(commits)} 次提交：
{formatted_commits}

请生成项目演进总结，包括项目状态、主要功能变化、开发趋势和关键提交分析。"""
        
        try:
            summary = self._call_api(system_prompt, user_prompt)
            return {
                'summary': summary,
                'commit_count': len(commits),
                'current_branch': current_branch,
                'evolution_status': self._infer_evolution_status(commits)
            }
        except Exception as e:
            return {
                'error': str(e),
                'commit_count': len(commits),
                'current_branch': current_branch,
                'evolution_status': self._infer_evolution_status(commits)
            }
    
    def _get_core_files(self, scan_result):
        core_files = []
        
        entry_files = scan_result.get('entry_files', [])
        for entry_file in entry_files:
            core_files.append(entry_file.get('path', ''))
        
        language_files = scan_result.get('language_files', {})
        for lang, files in language_files.items():
            for file_path in files[:5]:
                if file_path not in core_files:
                    core_files.append(file_path)
        
        return core_files
    
    def _extract_code_snippets(self, core_files, max_snippets=10, max_lines_per_file=100):
        snippets = []
        
        for file_path in core_files:
            if len(snippets) >= max_snippets:
                break
            
            try:
                path = Path(file_path)
                if not path.exists():
                    continue
                
                with open(path, 'r', encoding='utf-8', errors='ignore') as f:
                    lines = f.readlines()
                    snippet_lines = lines[:max_lines_per_file]
                    snippet = ''.join(snippet_lines)
                    
                    if len(lines) > max_lines_per_file:
                        snippet += f"\n... (共 {len(lines)} 行，省略了 {len(lines) - max_lines_per_file} 行)"
                    
                    snippets.append(f"\n--- 文件: {path.name} ---\n{snippet}\n")
            except Exception:
                continue
        
        return '\n'.join(snippets)
    
    def _format_entry_files(self, entry_files):
        if not entry_files:
            return "未检测到核心入口文件"
        
        lines = []
        for i, entry_file in enumerate(entry_files, 1):
            lines.append(f"{i}. {entry_file.get('name', 'Unknown')}")
            lines.append(f"   路径: {entry_file.get('path', 'Unknown')}")
            lines.append(f"   语言: {entry_file.get('language', 'Unknown')}")
            if entry_file.get('description'):
                lines.append(f"   描述: {entry_file['description'][:100]}...")
            lines.append("")
        
        return '\n'.join(lines)
    
    def _format_commits(self, commits):
        lines = []
        for i, commit in enumerate(commits, 1):
            lines.append(f"提交 #{i}:")
            lines.append(f"  Hash: {commit.get('hash', '')[:7]}")
            lines.append(f"  作者: {commit.get('author', 'Unknown')}")
            lines.append(f"  日期: {commit.get('date', 'Unknown')}")
            lines.append(f"  消息: {commit.get('message', '')}")
            
            stats = commit.get('stats', {})
            if stats:
                lines.append(f"  统计: {stats.get('files_changed', 0)} 个文件变更, "
                           f"+{stats.get('insertions', 0)} 插入, "
                           f"-{stats.get('deletions', 0)} 删除")
            lines.append("")
        
        return '\n'.join(lines)
    
    def _infer_evolution_status(self, commits):
        if not commits:
            return "项目刚初始化或无提交历史"
        
        if len(commits) < 3:
            return "项目处于早期开发阶段"
        
        recent_commits = commits[:5]
        has_feature_commits = any(
            'feature' in commit.get('message', '').lower() or
            'add' in commit.get('message', '').lower() or
            'new' in commit.get('message', '').lower()
            for commit in recent_commits
        )
        
        has_bugfix_commits = any(
            'fix' in commit.get('message', '').lower() or
            'bug' in commit.get('message', '').lower() or
            'resolve' in commit.get('message', '').lower()
            for commit in recent_commits
        )
        
        if has_feature_commits and has_bugfix_commits:
            return "项目处于活跃开发阶段，既有新功能开发也有 Bug 修复"
        elif has_feature_commits:
            return "项目处于功能开发阶段，主要在添加新功能"
        elif has_bugfix_commits:
            return "项目处于稳定阶段，主要在进行 Bug 修复和维护"
        else:
            return "项目处于维护阶段"
    
    def test_api_key(self, api_key, base_url="https://api.deepseek.com/v1", model="deepseek-v4-flash"):
        """
        测试 API Key 是否有效
        
        Args:
            api_key: DeepSeek API Key
            base_url: API 基础 URL
            model: 用于测试的模型（默认使用较便宜的 flash 模型）
        
        Returns:
            tuple: (success: bool, message: str)
                - success: True 表示验证成功，False 表示失败
                - message: 详细的结果或错误信息
        """
        if not api_key or not api_key.strip():
            return False, "API Key 不能为空"
        
        api_key = api_key.strip()
        
        try:
            messages = [
                {"role": "user", "content": "Hello, please respond with 'OK' if you receive this message."}
            ]
            
            if OPENAI_AVAILABLE:
                try:
                    client = OpenAI(
                        api_key=api_key,
                        base_url=base_url
                    )
                    
                    response = client.chat.completions.create(
                        model=model,
                        messages=messages,
                        max_tokens=10,
                        temperature=0.0
                    )
                    
                    content = response.choices[0].message.content
                    if content and content.strip():
                        return True, f"API Key 验证成功！模型响应: {content.strip()}"
                    else:
                        return True, "API Key 验证成功！"
                        
                except Exception as e:
                    error_msg = str(e)
                    
                    if "401" in error_msg or "Unauthorized" in error_msg or "invalid_api_key" in error_msg.lower():
                        return False, f"API Key 无效（401 Unauthorized）。\n\n错误详情: {error_msg}\n\n💡 请检查您的 API Key 是否正确，或访问 https://platform.deepseek.com/ 获取新的 API Key。"
                    
                    elif "402" in error_msg or "Insufficient" in error_msg or "balance" in error_msg.lower():
                        return False, f"API Key 余额不足（402 Payment Required）。\n\n错误详情: {error_msg}\n\n💡 请访问 https://platform.deepseek.com/ 为您的账户充值。"
                    
                    elif "403" in error_msg or "Forbidden" in error_msg:
                        return False, f"API Key 权限不足（403 Forbidden）。\n\n错误详情: {error_msg}\n\n💡 请检查您的 API Key 权限设置。"
                    
                    elif "429" in error_msg or "Too Many" in error_msg or "rate_limit" in error_msg.lower():
                        return False, f"请求过于频繁（429 Too Many Requests）。\n\n错误详情: {error_msg}\n\n💡 请稍后再试，或检查您的 API 调用频率限制。"
                    
                    elif "model_not_found" in error_msg.lower() or "model" in error_msg.lower() and "not" in error_msg.lower():
                        return self.test_api_key(api_key, base_url, "deepseek-chat")
                    
                    else:
                        return False, f"OpenAI SDK 调用失败: {error_msg}"
            
            elif REQUESTS_AVAILABLE:
                headers = {
                    "Authorization": f"Bearer {api_key}",
                    "Content-Type": "application/json"
                }
                
                payload = {
                    "model": model,
                    "messages": messages,
                    "max_tokens": 10,
                    "temperature": 0.0
                }
                
                try:
                    response = requests.post(
                        f"{base_url}/chat/completions",
                        headers=headers,
                        json=payload,
                        timeout=30
                    )
                    
                    if response.status_code == 200:
                        data = response.json()
                        if "choices" in data and len(data["choices"]) > 0:
                            content = data["choices"][0].get("message", {}).get("content", "")
                            if content and content.strip():
                                return True, f"API Key 验证成功！模型响应: {content.strip()}"
                            else:
                                return True, "API Key 验证成功！"
                        else:
                            return True, "API Key 验证成功！"
                    
                    else:
                        try:
                            error_data = response.json()
                            error_msg = error_data.get("error", {}).get("message", response.text)
                        except:
                            error_msg = response.text
                        
                        status_code = response.status_code
                        
                        if status_code == 401:
                            return False, f"API Key 无效（401 Unauthorized）。\n\n错误详情: {error_msg}\n\n💡 请检查您的 API Key 是否正确，或访问 https://platform.deepseek.com/ 获取新的 API Key。"
                        
                        elif status_code == 402:
                            return False, f"API Key 余额不足（402 Payment Required）。\n\n错误详情: {error_msg}\n\n💡 请访问 https://platform.deepseek.com/ 为您的账户充值。"
                        
                        elif status_code == 403:
                            return False, f"API Key 权限不足（403 Forbidden）。\n\n错误详情: {error_msg}\n\n💡 请检查您的 API Key 权限设置。"
                        
                        elif status_code == 429:
                            return False, f"请求过于频繁（429 Too Many Requests）。\n\n错误详情: {error_msg}\n\n💡 请稍后再试，或检查您的 API 调用频率限制。"
                        
                        elif status_code == 404 and ("model" in error_msg.lower() or "not found" in error_msg.lower()):
                            return self.test_api_key(api_key, base_url, "deepseek-chat")
                        
                        else:
                            return False, f"API 调用失败（HTTP {status_code}）。\n\n错误详情: {error_msg}"
                            
                except requests.exceptions.Timeout:
                    return False, "请求超时。\n\n💡 请检查您的网络连接，或稍后重试。"
                    
                except requests.exceptions.ConnectionError:
                    return False, "网络连接错误。\n\n💡 请检查您的网络连接，确保能够访问 https://api.deepseek.com。"
                    
                except Exception as e:
                    return False, f"HTTP 请求失败: {str(e)}"
            else:
                return False, "缺少必要的依赖库。\n\n💡 请安装 openai 或 requests 库：\n   pip install openai\n   或\n   pip install requests"
                
        except Exception as e:
            return False, f"验证过程中发生意外错误: {str(e)}"
