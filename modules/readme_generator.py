import os
from datetime import datetime
from pathlib import Path

class READMEGenerator:
    def __init__(self):
        self.project_name = ""
        self.generation_date = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
    def generate(self, scan_result, code_analysis, project_overview, git_summary):
        self.project_name = scan_result.get('structure', {}).get('name', 'Unknown Project')
        
        sections = []
        
        sections.append(self._generate_header())
        sections.append(self._generate_project_overview(project_overview))
        sections.append(self._generate_tech_stack(scan_result.get('tech_stack', {})))
        sections.append(self._generate_directory_structure(scan_result.get('structure', {})))
        sections.append(self._generate_core_files(scan_result.get('entry_files', [])))
        sections.append(self._generate_code_analysis(code_analysis))
        sections.append(self._generate_git_evolution(git_summary))
        sections.append(self._generate_quick_start(scan_result.get('tech_stack', {})))
        sections.append(self._generate_footer())
        
        return "\n\n".join(sections)
    
    def _generate_header(self):
        return f"""# {self.project_name}

> 由 Auto README Generator 自动生成
> 
> 生成时间: {self.generation_date}

---
"""
    
    def _generate_project_overview(self, project_overview):
        sections = ["## 项目概述\n"]
        
        if project_overview and project_overview.get('overview'):
            sections.append(project_overview['overview'])
        else:
            tech_stack = project_overview.get('tech_stack_summary', {}) if project_overview else {}
            languages = tech_stack.get('languages', [])
            frameworks = tech_stack.get('frameworks', [])
            
            sections.append("### 项目简介")
            sections.append("该项目是一个正在开发中的软件项目。")
            
            if languages:
                sections.append(f"\n### 主要技术")
                sections.append(f"- **编程语言**: {', '.join(languages)}")
            
            if frameworks:
                sections.append(f"- **框架**: {', '.join(frameworks)}")
        
        return "\n".join(sections)
    
    def _generate_tech_stack(self, tech_stack):
        sections = ["## 技术栈\n"]
        
        if not tech_stack:
            sections.append("暂无技术栈信息。")
            return "\n".join(sections)
        
        languages = tech_stack.get('languages', {})
        if languages:
            sections.append("### 编程语言")
            for lang, details in languages.items():
                file_count = details.get('files', 0)
                sections.append(f"- **{lang}**: {file_count} 个文件")
            sections.append("")
        
        frameworks = tech_stack.get('frameworks', [])
        if frameworks:
            sections.append("### 框架和库")
            for framework in frameworks:
                sections.append(f"- {framework}")
            sections.append("")
        
        build_tools = tech_stack.get('build_tools', [])
        if build_tools:
            sections.append("### 构建工具")
            for tool in build_tools:
                sections.append(f"- {tool}")
            sections.append("")
        
        package_managers = tech_stack.get('package_managers', [])
        if package_managers:
            sections.append("### 包管理器")
            for pm in package_managers:
                sections.append(f"- {pm}")
            sections.append("")
        
        databases = tech_stack.get('databases', [])
        if databases:
            sections.append("### 数据库")
            for db in databases:
                sections.append(f"- {db}")
        
        return "\n".join(sections)
    
    def _generate_directory_structure(self, structure):
        sections = ["## 目录结构\n"]
        
        if not structure:
            sections.append("暂无目录结构信息。")
            return "\n".join(sections)
        
        def format_tree(node, prefix="", is_last=True):
            lines = []
            connector = "└── " if is_last else "├── "
            lines.append(f"{prefix}{connector}{node['name']}")
            
            if node.get('children'):
                children = node['children']
                new_prefix = prefix + ("    " if is_last else "│   ")
                for i, child in enumerate(children):
                    child_lines = format_tree(child, new_prefix, i == len(children) - 1)
                    lines.extend(child_lines)
            
            return lines
        
        tree_lines = format_tree(structure)
        sections.append("```")
        sections.extend(tree_lines)
        sections.append("```")
        
        return "\n".join(sections)
    
    def _generate_core_files(self, entry_files):
        sections = ["## 核心入口文件\n"]
        
        if not entry_files:
            sections.append("暂无核心入口文件信息。")
            return "\n".join(sections)
        
        for entry_file in entry_files:
            name = entry_file.get('name', 'Unknown')
            path = entry_file.get('path', 'Unknown')
            language = entry_file.get('language', 'Unknown')
            description = entry_file.get('description', '')
            purpose = entry_file.get('purpose', '')
            
            sections.append(f"### {name}")
            sections.append(f"- **路径**: `{path}`")
            sections.append(f"- **语言**: {language}")
            
            if description:
                sections.append(f"- **描述**: {description}")
            
            if purpose:
                sections.append(f"- **用途**: {purpose}")
            
            sections.append("")
        
        return "\n".join(sections)
    
    def _generate_code_analysis(self, code_analysis):
        sections = ["## 代码分析\n"]
        
        if not code_analysis:
            sections.append("暂无代码分析信息。")
            return "\n".join(sections)
        
        if code_analysis.get('error'):
            sections.append(f"⚠️ 代码分析过程中出现错误: {code_analysis['error']}")
            sections.append("\n以下是可用的基本信息:")
        
        if code_analysis.get('analysis'):
            sections.append(code_analysis['analysis'])
        
        core_files = code_analysis.get('core_files', [])
        if core_files:
            sections.append("\n### 分析的核心文件")
            for i, file_path in enumerate(core_files, 1):
                sections.append(f"{i}. `{file_path}`")
        
        return "\n".join(sections)
    
    def _generate_git_evolution(self, git_summary):
        sections = ["## 项目演进\n"]
        
        if not git_summary:
            sections.append("暂无 Git 历史信息。")
            return "\n".join(sections)
        
        if git_summary.get('error'):
            sections.append(f"⚠️ Git 历史分析过程中出现错误: {git_summary['error']}")
        
        commit_count = git_summary.get('commit_count', 0)
        current_branch = git_summary.get('current_branch', 'unknown')
        evolution_status = git_summary.get('evolution_status', '未知')
        
        sections.append("### 当前状态")
        sections.append(f"- **当前分支**: {current_branch}")
        sections.append(f"- **提交总数**: {commit_count}")
        sections.append(f"- **演进状态**: {evolution_status}")
        sections.append("")
        
        if git_summary.get('summary'):
            sections.append("### 演进分析")
            sections.append(git_summary['summary'])
        
        return "\n".join(sections)
    
    def _generate_quick_start(self, tech_stack):
        sections = ["## 快速开始\n"]
        
        frameworks = tech_stack.get('frameworks', [])
        build_tools = tech_stack.get('build_tools', [])
        package_managers = tech_stack.get('package_managers', [])
        languages = list(tech_stack.get('languages', {}).keys())
        
        if 'React' in frameworks or 'Vue' in frameworks or 'Angular' in frameworks:
            sections.append(self._generate_frontend_quick_start(frameworks, package_managers))
        elif 'Django' in frameworks or 'Flask' in frameworks or 'FastAPI' in frameworks:
            sections.append(self._generate_python_backend_quick_start(frameworks))
        elif 'Spring Boot' in frameworks:
            sections.append(self._generate_java_spring_quick_start())
        elif 'Express' in frameworks:
            sections.append(self._generate_node_backend_quick_start(package_managers))
        elif 'Python' in languages:
            sections.append(self._generate_python_quick_start(package_managers))
        elif 'JavaScript' in languages or 'TypeScript' in languages:
            sections.append(self._generate_javascript_quick_start(package_managers))
        else:
            sections.append(self._generate_generic_quick_start())
        
        return "\n".join(sections)
    
    def _generate_frontend_quick_start(self, frameworks, package_managers):
        sections = []
        
        if 'npm' in package_managers:
            sections.append("### 安装依赖")
            sections.append("```bash")
            sections.append("npm install")
            sections.append("```")
        elif 'yarn' in package_managers:
            sections.append("### 安装依赖")
            sections.append("```bash")
            sections.append("yarn install")
            sections.append("```")
        elif 'pnpm' in package_managers:
            sections.append("### 安装依赖")
            sections.append("```bash")
            sections.append("pnpm install")
            sections.append("```")
        
        if 'React' in frameworks or 'Vue' in frameworks or 'Angular' in frameworks:
            sections.append("\n### 开发模式")
            sections.append("```bash")
            sections.append("npm run dev")
            sections.append("```")
            
            sections.append("\n### 构建生产版本")
            sections.append("```bash")
            sections.append("npm run build")
            sections.append("```")
        
        return "\n".join(sections)
    
    def _generate_python_backend_quick_start(self, frameworks):
        sections = []
        
        sections.append("### 创建虚拟环境")
        sections.append("```bash")
        sections.append("python -m venv venv")
        sections.append("source venv/bin/activate  # Linux/Mac")
        sections.append("venv\\Scripts\\activate  # Windows")
        sections.append("```")
        
        sections.append("\n### 安装依赖")
        sections.append("```bash")
        sections.append("pip install -r requirements.txt")
        sections.append("```")
        
        if 'Django' in frameworks:
            sections.append("\n### 数据库迁移")
            sections.append("```bash")
            sections.append("python manage.py migrate")
            sections.append("```")
            
            sections.append("\n### 启动开发服务器")
            sections.append("```bash")
            sections.append("python manage.py runserver")
            sections.append("```")
        elif 'Flask' in frameworks:
            sections.append("\n### 启动开发服务器")
            sections.append("```bash")
            sections.append("flask run")
            sections.append("```")
        elif 'FastAPI' in frameworks:
            sections.append("\n### 启动开发服务器")
            sections.append("```bash")
            sections.append("uvicorn main:app --reload")
            sections.append("```")
        
        return "\n".join(sections)
    
    def _generate_java_spring_quick_start(self):
        sections = []
        
        sections.append("### 构建项目")
        sections.append("```bash")
        sections.append("./mvnw clean install  # Maven")
        sections.append("# 或")
        sections.append("./gradlew build  # Gradle")
        sections.append("```")
        
        sections.append("\n### 运行应用")
        sections.append("```bash")
        sections.append("./mvnw spring-boot:run  # Maven")
        sections.append("# 或")
        sections.append("./gradlew bootRun  # Gradle")
        sections.append("```")
        
        return "\n".join(sections)
    
    def _generate_node_backend_quick_start(self, package_managers):
        sections = []
        
        sections.append("### 安装依赖")
        if 'npm' in package_managers:
            sections.append("```bash")
            sections.append("npm install")
            sections.append("```")
        elif 'yarn' in package_managers:
            sections.append("```bash")
            sections.append("yarn install")
            sections.append("```")
        
        sections.append("\n### 启动应用")
        sections.append("```bash")
        sections.append("npm start")
        sections.append("```")
        
        sections.append("\n### 开发模式")
        sections.append("```bash")
        sections.append("npm run dev")
        sections.append("```")
        
        return "\n".join(sections)
    
    def _generate_python_quick_start(self, package_managers):
        sections = []
        
        sections.append("### 创建虚拟环境")
        sections.append("```bash")
        sections.append("python -m venv venv")
        sections.append("source venv/bin/activate  # Linux/Mac")
        sections.append("venv\\Scripts\\activate  # Windows")
        sections.append("```")
        
        sections.append("\n### 安装依赖")
        if 'Poetry' in package_managers:
            sections.append("```bash")
            sections.append("poetry install")
            sections.append("```")
        else:
            sections.append("```bash")
            sections.append("pip install -r requirements.txt")
            sections.append("```")
        
        sections.append("\n### 运行应用")
        sections.append("```bash")
        sections.append("python main.py")
        sections.append("```")
        
        return "\n".join(sections)
    
    def _generate_javascript_quick_start(self, package_managers):
        sections = []
        
        sections.append("### 安装依赖")
        if 'npm' in package_managers:
            sections.append("```bash")
            sections.append("npm install")
            sections.append("```")
        elif 'yarn' in package_managers:
            sections.append("```bash")
            sections.append("yarn install")
            sections.append("```")
        elif 'pnpm' in package_managers:
            sections.append("```bash")
            sections.append("pnpm install")
            sections.append("```")
        
        sections.append("\n### 运行应用")
        sections.append("```bash")
        sections.append("npm start")
        sections.append("```")
        
        return "\n".join(sections)
    
    def _generate_generic_quick_start(self):
        sections = []
        
        sections.append("### 安装依赖")
        sections.append("请根据项目使用的技术栈安装相应的依赖。")
        
        sections.append("\n### 运行应用")
        sections.append("请查看项目的配置文件（如 package.json、Makefile 等）了解如何运行该项目。")
        
        return "\n".join(sections)
    
    def _generate_footer(self):
        return f"""---

*本文档由 **Auto README Generator** 自动生成*  
*生成时间: {self.generation_date}*

> 💡 提示: 建议根据实际项目情况对本文档进行审查和补充
"""
    
    def save_to_file(self, content, file_path):
        try:
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(content)
            return True, f"成功保存到: {file_path}"
        except Exception as e:
            return False, f"保存失败: {str(e)}"
