import os
from collections import defaultdict
from pathlib import Path

LANGUAGE_EXTENSIONS = {
    'Python': ['.py', '.pyw', '.pyx', '.pyi'],
    'JavaScript': ['.js', '.jsx', '.mjs', '.cjs'],
    'TypeScript': ['.ts', '.tsx'],
    'Java': ['.java', '.jar', '.war'],
    'C++': ['.cpp', '.hpp', '.h', '.cc', '.cxx'],
    'C': ['.c', '.h'],
    'C#': ['.cs'],
    'Go': ['.go'],
    'Rust': ['.rs', '.toml'],
    'PHP': ['.php'],
    'Ruby': ['.rb', '.gemfile'],
    'Swift': ['.swift'],
    'Kotlin': ['.kt', '.kts'],
    'Dart': ['.dart'],
    'Scala': ['.scala'],
    'R': ['.r', '.R'],
    'Shell': ['.sh', '.bash', '.zsh', '.fish'],
    'PowerShell': ['.ps1', '.psm1', '.psd1'],
    'HTML': ['.html', '.htm', '.xhtml'],
    'CSS': ['.css', '.scss', '.sass', '.less', '.styl'],
    'Markdown': ['.md', '.markdown'],
    'JSON': ['.json'],
    'YAML': ['.yml', '.yaml'],
    'XML': ['.xml'],
    'SQL': ['.sql'],
    'Docker': ['.dockerfile', 'Dockerfile'],
    'Makefile': ['Makefile', '.mk'],
    'CMake': ['CMakeLists.txt'],
}

FRAMEWORK_INDICATORS = {
    'React': ['package.json', 'react', 'react-dom'],
    'Vue': ['package.json', 'vue', 'vue-router'],
    'Angular': ['package.json', '@angular'],
    'Next.js': ['package.json', 'next', 'pages/', 'app/'],
    'Nuxt.js': ['package.json', 'nuxt'],
    'Express': ['package.json', 'express'],
    'Django': ['manage.py', 'settings.py', 'urls.py'],
    'Flask': ['app.py', 'flask'],
    'FastAPI': ['main.py', 'fastapi'],
    'Spring Boot': ['pom.xml', 'build.gradle', 'application.properties'],
    'Laravel': ['artisan', 'composer.json', 'laravel'],
    'Ruby on Rails': ['Gemfile', 'rails', 'app/controllers/'],
    'ASP.NET Core': ['Program.cs', 'Startup.cs', 'appsettings.json'],
    'Gin': ['go.mod', 'gin-gonic'],
    'Actix': ['Cargo.toml', 'actix'],
}

BUILD_TOOL_INDICATORS = {
    'Webpack': ['webpack.config.js', 'webpack'],
    'Vite': ['vite.config.js', 'vite.config.ts', 'vite'],
    'Rollup': ['rollup.config.js'],
    'Parcel': ['.parcelrc'],
    'npm': ['package.json'],
    'yarn': ['yarn.lock'],
    'pnpm': ['pnpm-lock.yaml'],
    'Maven': ['pom.xml'],
    'Gradle': ['build.gradle', 'build.gradle.kts'],
    'Make': ['Makefile'],
    'CMake': ['CMakeLists.txt'],
    'Meson': ['meson.build'],
    'Cargo': ['Cargo.toml'],
    'Go Modules': ['go.mod'],
    'pip': ['requirements.txt', 'setup.py', 'pyproject.toml'],
    'Poetry': ['pyproject.toml', 'poetry.lock'],
    'Composer': ['composer.json'],
    'Bundler': ['Gemfile', 'Gemfile.lock'],
}

DATABASE_INDICATORS = {
    'MySQL': ['mysql', 'mysqli', 'pdo_mysql'],
    'PostgreSQL': ['pg', 'psycopg', 'postgresql'],
    'MongoDB': ['mongoose', 'mongodb', 'pymongo'],
    'Redis': ['redis', 'ioredis'],
    'SQLite': ['sqlite', 'sqlite3'],
    'Oracle': ['oracle', 'cx_Oracle'],
    'SQL Server': ['mssql', 'pyodbc', 'System.Data.SqlClient'],
}

ENTRY_FILE_PATTERNS = {
    'Python': ['main.py', '__main__.py', 'app.py', 'run.py', 'manage.py', 'setup.py'],
    'JavaScript': ['index.js', 'main.js', 'app.js', 'server.js', 'start.js'],
    'TypeScript': ['index.ts', 'main.ts', 'app.ts', 'server.ts'],
    'React': ['src/index.js', 'src/index.jsx', 'src/index.ts', 'src/index.tsx', 'src/main.jsx'],
    'Vue': ['src/main.js', 'src/main.ts', 'src/App.vue'],
    'Angular': ['src/main.ts'],
    'Next.js': ['pages/index.js', 'pages/index.tsx', 'app/page.js', 'app/page.tsx'],
    'Java': ['src/main/java/**/Main.java', 'src/main/java/**/Application.java'],
    'C++': ['main.cpp', 'main.cxx', 'main.cc'],
    'C': ['main.c'],
    'Go': ['main.go'],
    'Rust': ['src/main.rs'],
    'PHP': ['index.php', 'public/index.php'],
    'Ruby': ['config.ru', 'app.rb'],
    'Swift': ['main.swift', 'AppDelegate.swift'],
    'Kotlin': ['src/main/kotlin/**/Main.kt'],
    'Dart': ['lib/main.dart'],
    'HTML': ['index.html', 'home.html', 'default.html'],
}

IGNORED_DIRECTORIES = [
    '__pycache__', '.git', '.svn', '.hg', 'node_modules',
    'venv', 'env', '.venv', '.env', 'virtualenv',
    'dist', 'build', 'target', 'out',
    '.idea', '.vscode', '.vs',
    'logs', 'tmp', 'temp', 'cache',
    '.next', '.nuxt', '.parcel-cache',
    'bower_components', 'jspm_packages',
    '__pycache__', '.pytest_cache', '.mypy_cache',
    'coverage', '.coverage', 'htmlcov',
    '.tox', '.nox',
]

IGNORED_EXTENSIONS = [
    '.pyc', '.pyo', '.pyd',
    '.class', '.jar', '.war', '.ear',
    '.dll', '.so', '.dylib', '.exe',
    '.obj', '.o', '.a', '.lib',
    '.jpg', '.jpeg', '.png', '.gif', '.bmp', '.ico', '.svg',
    '.pdf', '.doc', '.docx', '.xls', '.xlsx', '.ppt', '.pptx',
    '.zip', '.tar', '.gz', '.rar', '.7z',
    '.mp3', '.mp4', '.avi', '.mov', '.wmv',
    '.log', '.tmp', '.temp', '.cache',
    '.min.js', '.min.css',
]

class DirectoryScanner:
    def __init__(self):
        self.language_files = defaultdict(list)
        self.framework_indicators = []
        self.build_tool_indicators = []
        self.database_indicators = []
        self.entry_files = []
    
    def scan(self, directory):
        root_path = Path(directory)
        if not root_path.exists() or not root_path.is_dir():
            raise ValueError(f"Invalid directory: {directory}")
        
        self._reset()
        
        structure = self._build_structure(root_path)
        file_count = self._count_files(root_path)
        languages = self._detect_languages()
        tech_stack = self._detect_tech_stack(root_path)
        entry_files = self._find_entry_files(root_path)
        
        return {
            'structure': structure,
            'file_count': file_count,
            'languages': list(languages),
            'tech_stack': tech_stack,
            'entry_files': entry_files,
            'language_files': dict(self.language_files)
        }
    
    def _reset(self):
        self.language_files = defaultdict(list)
        self.framework_indicators = []
        self.build_tool_indicators = []
        self.database_indicators = []
        self.entry_files = []
    
    def _build_structure(self, root_path):
        def build_node(path, name):
            node = {
                'name': name,
                'type': 'directory' if path.is_dir() else 'file',
                'children': []
            }
            
            if path.is_dir():
                for child in sorted(path.iterdir(), key=lambda x: (not x.is_dir(), x.name.lower())):
                    if self._should_ignore(child):
                        continue
                    
                    child_node = build_node(child, child.name)
                    node['children'].append(child_node)
            
            return node
        
        return build_node(root_path, root_path.name)
    
    def _should_ignore(self, path):
        name = path.name.lower()
        if path.is_dir() and (name in IGNORED_DIRECTORIES or name.startswith('.')):
            return True
        
        if path.is_file():
            ext = path.suffix.lower()
            if ext in IGNORED_EXTENSIONS:
                return True
            name_lower = path.name.lower()
            for pattern in IGNORED_EXTENSIONS:
                if name_lower.endswith(pattern):
                    return True
        
        return False
    
    def _count_files(self, root_path):
        count = 0
        for root, dirs, files in os.walk(root_path):
            dirs[:] = [d for d in dirs if d not in IGNORED_DIRECTORIES and not d.startswith('.')]
            for file in files:
                file_path = Path(root) / file
                if not self._should_ignore(file_path):
                    count += 1
                    self._classify_file(file_path)
        return count
    
    def _classify_file(self, file_path):
        name = file_path.name.lower()
        ext = file_path.suffix.lower()
        
        for language, extensions in LANGUAGE_EXTENSIONS.items():
            for lang_ext in extensions:
                if ext == lang_ext.lower() or name == lang_ext.lower():
                    self.language_files[language].append(str(file_path))
                    break
    
    def _detect_languages(self):
        return set(self.language_files.keys())
    
    def _detect_tech_stack(self, root_path):
        tech_stack = {
            'languages': {},
            'frameworks': [],
            'build_tools': [],
            'package_managers': [],
            'databases': []
        }
        
        for lang, files in self.language_files.items():
            tech_stack['languages'][lang] = {
                'files': len(files),
                'extensions': []
            }
        
        for framework, indicators in FRAMEWORK_INDICATORS.items():
            if self._check_indicators(root_path, indicators):
                tech_stack['frameworks'].append(framework)
        
        for build_tool, indicators in BUILD_TOOL_INDICATORS.items():
            if self._check_indicators(root_path, indicators):
                tech_stack['build_tools'].append(build_tool)
        
        package_managers = ['npm', 'yarn', 'pnpm', 'pip', 'Poetry', 'Composer', 'Bundler', 'Cargo', 'Go Modules']
        for pm in package_managers:
            if pm in tech_stack['build_tools']:
                tech_stack['package_managers'].append(pm)
        
        for database, indicators in DATABASE_INDICATORS.items():
            if self._check_code_indicators(indicators):
                tech_stack['databases'].append(database)
        
        return tech_stack
    
    def _check_indicators(self, root_path, indicators):
        for indicator in indicators:
            indicator_path = root_path / indicator
            if indicator_path.exists():
                return True
            
            for root, dirs, files in os.walk(root_path):
                dirs[:] = [d for d in dirs if d not in IGNORED_DIRECTORIES]
                for file in files:
                    if indicator in file.lower() or indicator in file:
                        return True
                    
                    file_path = Path(root) / file
                    if file_path.suffix in ['.json', '.yaml', '.yml', '.toml', '.py', '.js', '.ts']:
                        try:
                            with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                                content = f.read().lower()
                                if indicator.lower() in content:
                                    return True
                        except:
                            pass
        
        return False
    
    def _check_code_indicators(self, indicators):
        for files in self.language_files.values():
            for file_path in files:
                try:
                    with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                        content = f.read().lower()
                        for indicator in indicators:
                            if indicator.lower() in content:
                                return True
                except:
                    pass
        
        return False
    
    def _find_entry_files(self, root_path):
        entry_files = []
        found_files = set()
        
        for language, patterns in ENTRY_FILE_PATTERNS.items():
            for pattern in patterns:
                if '**' in pattern:
                    parts = pattern.split('**')
                    base_dir = root_path
                    for part in parts:
                        if part:
                            if part.startswith('/'):
                                part = part[1:]
                            if part.endswith('/'):
                                base_dir = base_dir / part[:-1]
                            else:
                                for root, dirs, files in os.walk(base_dir):
                                    dirs[:] = [d for d in dirs if d not in IGNORED_DIRECTORIES]
                                    for file in files:
                                        if file == part or file.endswith(part):
                                            file_path = Path(root) / file
                                            if str(file_path) not in found_files:
                                                entry_files.append(self._create_entry_file_info(file_path, language))
                                                found_files.add(str(file_path))
                else:
                    file_path = root_path / pattern
                    if file_path.exists() and str(file_path) not in found_files:
                        entry_files.append(self._create_entry_file_info(file_path, language))
                        found_files.add(str(file_path))
        
        return sorted(entry_files, key=lambda x: x['size'] if x.get('size') else 0, reverse=True)
    
    def _create_entry_file_info(self, file_path, language):
        info = {
            'name': file_path.name,
            'path': str(file_path),
            'language': language,
            'size': file_path.stat().st_size if file_path.exists() else 0,
            'description': '',
            'purpose': ''
        }
        
        if file_path.exists():
            try:
                with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                    content = f.read(2000)
                    info['description'] = self._extract_description(content, language)
                    info['purpose'] = self._extract_purpose(content, language)
            except:
                pass
        
        return info
    
    def _extract_description(self, content, language):
        lines = content.split('\n')[:50]
        comments = []
        
        if language in ['Python']:
            for line in lines:
                stripped = line.strip()
                if stripped.startswith('#'):
                    comments.append(stripped[1:].strip())
                elif stripped.startswith('"""') or stripped.startswith("'''"):
                    comments.append(stripped.strip('"\''))
                    break
        
        elif language in ['JavaScript', 'TypeScript', 'React', 'Vue', 'Angular', 'Next.js']:
            in_block_comment = False
            for line in lines:
                stripped = line.strip()
                if stripped.startswith('/*'):
                    in_block_comment = True
                    comments.append(stripped[2:].strip())
                elif stripped.endswith('*/'):
                    in_block_comment = False
                    comments.append(stripped[:-2].strip())
                elif in_block_comment:
                    comments.append(stripped)
                elif stripped.startswith('//'):
                    comments.append(stripped[2:].strip())
        
        elif language in ['Java', 'C++', 'C', 'C#', 'Go', 'Rust']:
            in_block_comment = False
            for line in lines:
                stripped = line.strip()
                if stripped.startswith('/*') or stripped.startswith('/**'):
                    in_block_comment = True
                    comments.append(stripped.lstrip('/*').strip())
                elif stripped.endswith('*/'):
                    in_block_comment = False
                    comments.append(stripped[:-2].strip())
                elif in_block_comment:
                    comments.append(stripped.lstrip('*').strip())
                elif stripped.startswith('//'):
                    comments.append(stripped[2:].strip())
        
        return ' '.join(comments[:5]) if comments else ''
    
    def _extract_purpose(self, content, language):
        purpose_indicators = [
            'main', 'entry', 'start', 'run', 'app', 'server',
            '入口', '主函数', '启动', '运行', '应用', '服务器'
        ]
        
        lines = content.split('\n')
        purpose_lines = []
        
        for line in lines[:100]:
            lower_line = line.lower()
            for indicator in purpose_indicators:
                if indicator in lower_line:
                    purpose_lines.append(line.strip())
                    break
        
        return ' '.join(purpose_lines[:3]) if purpose_lines else ''
