import os
from PyQt5.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QPushButton, QLabel, QLineEdit, QTextEdit,
    QFileDialog, QMessageBox, QGroupBox, QSplitter,
    QTabWidget, QCheckBox, QSpinBox, QProgressDialog,
    QDialog, QFormLayout, QDialogButtonBox
)
from PyQt5.QtCore import Qt, QThread, pyqtSignal
from PyQt5.QtGui import QFont
from .directory_scanner import DirectoryScanner
from .git_history import GitHistoryExtractor
from .ai_analyzer import AIAnalyzer
from .readme_generator import READMEGenerator

class ScanThread(QThread):
    scan_finished = pyqtSignal(dict)
    scan_error = pyqtSignal(str)
    scan_progress = pyqtSignal(str)
    
    def __init__(self, directory, scanner, git_extractor):
        super().__init__()
        self.directory = directory
        self.scanner = scanner
        self.git_extractor = git_extractor
    
    def run(self):
        try:
            self.scan_progress.emit("正在扫描目录结构...")
            scan_result = self.scanner.scan(self.directory)
            
            self.scan_progress.emit("正在提取Git历史...")
            git_history = self.git_extractor.extract(self.directory)
            
            result = {
                'scan_result': scan_result,
                'git_history': git_history
            }
            
            self.scan_finished.emit(result)
        except Exception as e:
            self.scan_error.emit(str(e))

class TestApiKeyThread(QThread):
    test_finished = pyqtSignal(bool, str)
    
    def __init__(self, api_key, ai_analyzer):
        super().__init__()
        self.api_key = api_key
        self.ai_analyzer = ai_analyzer
    
    def run(self):
        try:
            test_prompt = "Hello, this is a test message. Please respond with 'API_KEY_VALID' if you receive this message."
            
            system_prompt = "You are a helpful assistant. When the user sends a test message, respond exactly with 'API_KEY_VALID'."
            
            result = self.ai_analyzer._call_api(system_prompt, test_prompt, max_tokens=100)
            
            if "API_KEY_VALID" in result or result.strip():
                self.test_finished.emit(True, "API Key 验证成功！您的 DeepSeek API Key 配置正确，可以正常使用。")
            else:
                self.test_finished.emit(False, "API Key 验证失败：返回结果不符合预期。")
                
        except Exception as e:
            error_msg = str(e)
            if "401" in error_msg or "Unauthorized" in error_msg or "invalid" in error_msg.lower():
                self.test_finished.emit(False, f"API Key 无效：{error_msg}\n\n请检查您的 API Key 是否正确，或访问 https://platform.deepseek.com/ 获取新的 API Key。")
            elif "402" in error_msg or "Insufficient Balance" in error_msg:
                self.test_finished.emit(False, f"API Key 余额不足：{error_msg}\n\n请访问 https://platform.deepseek.com/ 为您的账户充值。")
            elif "429" in error_msg or "Too Many Requests" in error_msg:
                self.test_finished.emit(False, f"请求过于频繁：{error_msg}\n\n请稍后再试，或检查您的 API 调用频率限制。")
            else:
                self.test_finished.emit(False, f"API Key 验证失败：{error_msg}\n\n请检查网络连接或稍后重试。")

class GenerateProgressDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("正在生成 README")
        self.setMinimumSize(400, 150)
        self.setModal(True)
        self._init_ui()
    
    def _init_ui(self):
        layout = QVBoxLayout(self)
        
        title_label = QLabel("🔄 正在调用 DeepSeek API 生成专业 README...")
        title_label.setFont(QFont("Arial", 12, QFont.Bold))
        title_label.setAlignment(Qt.AlignCenter)
        layout.addWidget(title_label)
        
        layout.addSpacing(20)
        
        self.progress_label = QLabel("准备中...")
        self.progress_label.setAlignment(Qt.AlignCenter)
        self.progress_label.setStyleSheet("color: #666; font-size: 14px;")
        layout.addWidget(self.progress_label)
        
        layout.addSpacing(20)
        
        info_label = QLabel("💡 正在进行以下操作：\n• 分析核心代码片段\n• 生成项目概述\n• 总结 Git 历史\n• 整合生成 README\n\n请稍候，这可能需要几秒钟...")
        info_label.setStyleSheet("color: #888; font-size: 11px;")
        info_label.setAlignment(Qt.AlignLeft)
        layout.addWidget(info_label)
        
        layout.addStretch()
    
    def update_progress(self, message):
        self.progress_label.setText(f"📌 {message}")

class GenerateThread(QThread):
    generate_finished = pyqtSignal(str)
    generate_error = pyqtSignal(str)
    generate_progress = pyqtSignal(str)
    
    def __init__(self, scan_result, git_history, ai_analyzer, readme_generator, api_key, max_commits):
        super().__init__()
        self.scan_result = scan_result
        self.git_history = git_history
        self.ai_analyzer = ai_analyzer
        self.readme_generator = readme_generator
        self.api_key = api_key
        self.max_commits = max_commits
    
    def run(self):
        try:
            self.generate_progress.emit("正在分析核心代码...")
            code_analysis = self.ai_analyzer.analyze_code(
                self.scan_result,
                self.api_key
            )
            
            self.generate_progress.emit("正在生成项目概述...")
            project_overview = self.ai_analyzer.generate_project_overview(
                self.scan_result,
                self.api_key
            )
            
            self.generate_progress.emit("正在总结Git历史...")
            git_summary = self.ai_analyzer.summarize_git_history(
                self.git_history,
                self.api_key,
                self.max_commits
            )
            
            self.generate_progress.emit("正在生成README文件...")
            readme_content = self.readme_generator.generate(
                self.scan_result,
                code_analysis,
                project_overview,
                git_summary
            )
            
            self.generate_finished.emit(readme_content)
        except Exception as e:
            self.generate_error.emit(str(e))

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("专业 README 生成工具")
        self.setMinimumSize(1200, 800)
        
        self.directory_scanner = DirectoryScanner()
        self.git_extractor = GitHistoryExtractor()
        self.ai_analyzer = AIAnalyzer()
        self.readme_generator = READMEGenerator()
        
        self.scan_result = None
        self.git_history = None
        self.generated_readme = ""
        
        self._init_ui()
        self._connect_signals()
    
    def _init_ui(self):
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        main_layout = QVBoxLayout(central_widget)
        main_layout.setSpacing(10)
        main_layout.setContentsMargins(15, 15, 15, 15)
        
        dir_group = QGroupBox("项目目录选择")
        dir_layout = QHBoxLayout(dir_group)
        
        self.dir_label = QLabel("目录:")
        self.dir_edit = QLineEdit()
        self.dir_edit.setPlaceholderText("选择要分析的项目目录...")
        self.dir_edit.setReadOnly(True)
        
        self.browse_btn = QPushButton("浏览...")
        self.scan_btn = QPushButton("开始扫描")
        
        dir_layout.addWidget(self.dir_label)
        dir_layout.addWidget(self.dir_edit)
        dir_layout.addWidget(self.browse_btn)
        dir_layout.addWidget(self.scan_btn)
        
        main_layout.addWidget(dir_group)
        
        settings_group = QGroupBox("AI 分析设置")
        settings_layout = QHBoxLayout(settings_group)
        
        self.api_key_label = QLabel("DeepSeek API Key:")
        self.api_key_edit = QLineEdit()
        self.api_key_edit.setEchoMode(QLineEdit.Password)
        self.api_key_edit.setPlaceholderText("输入您的 DeepSeek API Key")
        
        self.test_api_btn = QPushButton("测试 API Key")
        self.test_api_btn.setToolTip("点击测试 API Key 是否有效")
        
        self.max_commits_label = QLabel("最近提交数:")
        self.max_commits_spin = QSpinBox()
        self.max_commits_spin.setRange(1, 100)
        self.max_commits_spin.setValue(10)
        
        self.include_git_check = QCheckBox("包含 Git 历史分析")
        self.include_git_check.setChecked(True)
        
        settings_layout.addWidget(self.api_key_label)
        settings_layout.addWidget(self.api_key_edit)
        settings_layout.addWidget(self.test_api_btn)
        settings_layout.addWidget(self.max_commits_label)
        settings_layout.addWidget(self.max_commits_spin)
        settings_layout.addWidget(self.include_git_check)
        settings_layout.addStretch()
        
        main_layout.addWidget(settings_group)
        
        splitter = QSplitter(Qt.Horizontal)
        
        left_widget = QWidget()
        left_layout = QVBoxLayout(left_widget)
        left_layout.setContentsMargins(0, 0, 0, 0)
        
        self.left_tabs = QTabWidget()
        
        self.dir_structure_text = QTextEdit()
        self.dir_structure_text.setReadOnly(True)
        self.dir_structure_text.setPlaceholderText("扫描后显示目录结构...")
        self.left_tabs.addTab(self.dir_structure_text, "目录结构")
        
        self.tech_stack_text = QTextEdit()
        self.tech_stack_text.setReadOnly(True)
        self.tech_stack_text.setPlaceholderText("扫描后显示技术栈信息...")
        self.left_tabs.addTab(self.tech_stack_text, "技术栈")
        
        self.entry_files_text = QTextEdit()
        self.entry_files_text.setReadOnly(True)
        self.entry_files_text.setPlaceholderText("扫描后显示核心入口文件...")
        self.left_tabs.addTab(self.entry_files_text, "入口文件")
        
        left_layout.addWidget(self.left_tabs)
        splitter.addWidget(left_widget)
        
        right_widget = QWidget()
        right_layout = QVBoxLayout(right_widget)
        right_layout.setContentsMargins(0, 0, 0, 0)
        
        self.right_tabs = QTabWidget()
        
        self.git_history_text = QTextEdit()
        self.git_history_text.setReadOnly(True)
        self.git_history_text.setPlaceholderText("扫描后显示 Git 历史...")
        self.right_tabs.addTab(self.git_history_text, "Git 历史")
        
        self.ai_analysis_text = QTextEdit()
        self.ai_analysis_text.setReadOnly(True)
        self.ai_analysis_text.setPlaceholderText("生成后显示 AI 分析结果...")
        self.right_tabs.addTab(self.ai_analysis_text, "AI 分析")
        
        self.readme_preview_text = QTextEdit()
        self.readme_preview_text.setReadOnly(True)
        self.readme_preview_text.setPlaceholderText("生成后显示 README 预览...")
        self.right_tabs.addTab(self.readme_preview_text, "README 预览")
        
        right_layout.addWidget(self.right_tabs)
        splitter.addWidget(right_widget)
        
        splitter.setSizes([600, 600])
        main_layout.addWidget(splitter)
        
        bottom_layout = QHBoxLayout()
        
        self.status_label = QLabel("就绪")
        self.generate_btn = QPushButton("生成 README")
        self.generate_btn.setEnabled(False)
        self.save_btn = QPushButton("保存 README")
        self.save_btn.setEnabled(False)
        
        bottom_layout.addWidget(self.status_label)
        bottom_layout.addStretch()
        bottom_layout.addWidget(self.generate_btn)
        bottom_layout.addWidget(self.save_btn)
        
        main_layout.addLayout(bottom_layout)
    
    def _connect_signals(self):
        self.browse_btn.clicked.connect(self._browse_directory)
        self.scan_btn.clicked.connect(self._start_scan)
        self.generate_btn.clicked.connect(self._generate_readme)
        self.save_btn.clicked.connect(self._save_readme)
        self.test_api_btn.clicked.connect(self._test_api_key)
    
    def _browse_directory(self):
        directory = QFileDialog.getExistingDirectory(self, "选择项目目录")
        if directory:
            self.dir_edit.setText(directory)
    
    def _start_scan(self):
        directory = self.dir_edit.text().strip()
        if not directory:
            QMessageBox.warning(self, "警告", "请先选择项目目录")
            return
        
        if not os.path.isdir(directory):
            QMessageBox.warning(self, "警告", "目录不存在")
            return
        
        self.scan_btn.setEnabled(False)
        self.generate_btn.setEnabled(False)
        self.save_btn.setEnabled(False)
        self.status_label.setText("正在扫描...")
        
        self.scan_thread = ScanThread(
            directory,
            self.directory_scanner,
            self.git_extractor
        )
        self.scan_thread.scan_finished.connect(self._on_scan_finished)
        self.scan_thread.scan_error.connect(self._on_scan_error)
        self.scan_thread.scan_progress.connect(self._on_scan_progress)
        self.scan_thread.start()
    
    def _on_scan_progress(self, message):
        self.status_label.setText(message)
    
    def _on_scan_finished(self, result):
        self.scan_result = result['scan_result']
        self.git_history = result['git_history']
        
        self.dir_structure_text.setText(self._format_directory_structure(self.scan_result['structure']))
        self.tech_stack_text.setText(self._format_tech_stack(self.scan_result['tech_stack']))
        self.entry_files_text.setText(self._format_entry_files(self.scan_result['entry_files']))
        self.git_history_text.setText(self._format_git_history(self.git_history))
        
        self.scan_btn.setEnabled(True)
        self.generate_btn.setEnabled(True)
        self.status_label.setText("扫描完成")
        
        QMessageBox.information(self, "完成", f"扫描完成！\n\n文件总数: {self.scan_result['file_count']}\n识别语言: {', '.join(self.scan_result['languages'])}")
    
    def _on_scan_error(self, error_message):
        self.scan_btn.setEnabled(True)
        self.status_label.setText("扫描失败")
        QMessageBox.critical(self, "错误", f"扫描失败: {error_message}")
    
    def _test_api_key(self):
        api_key = self.api_key_edit.text().strip()
        if not api_key:
            QMessageBox.warning(self, "警告", "请先输入 DeepSeek API Key")
            return
        
        self.test_api_btn.setEnabled(False)
        self.status_label.setText("正在测试 API Key...")
        
        self.test_api_thread = TestApiKeyThread(api_key, self.ai_analyzer)
        self.test_api_thread.test_finished.connect(self._on_test_api_finished)
        self.test_api_thread.start()
    
    def _on_test_api_finished(self, success, message):
        self.test_api_btn.setEnabled(True)
        
        if success:
            self.status_label.setText("API Key 验证成功")
            QMessageBox.information(
                self,
                "API Key 验证成功",
                f"✅ {message}\n\n您的 DeepSeek API Key 配置正确，可以正常使用。"
            )
        else:
            self.status_label.setText("API Key 验证失败")
            QMessageBox.warning(
                self,
                "API Key 验证失败",
                f"❌ {message}"
            )
    
    def _generate_readme(self):
        if not self.scan_result:
            QMessageBox.warning(self, "警告", "请先扫描项目目录")
            return
        
        api_key = self.api_key_edit.text().strip()
        if not api_key:
            QMessageBox.warning(self, "警告", "请输入 DeepSeek API Key")
            return
        
        max_commits = self.max_commits_spin.value()
        
        self.scan_btn.setEnabled(False)
        self.generate_btn.setEnabled(False)
        self.save_btn.setEnabled(False)
        self.status_label.setText("正在生成 README...")
        
        self.progress_dialog = GenerateProgressDialog(self)
        self.progress_dialog.show()
        
        self.generate_thread = GenerateThread(
            self.scan_result,
            self.git_history,
            self.ai_analyzer,
            self.readme_generator,
            api_key,
            max_commits
        )
        self.generate_thread.generate_finished.connect(self._on_generate_finished)
        self.generate_thread.generate_error.connect(self._on_generate_error)
        self.generate_thread.generate_progress.connect(self._on_generate_progress)
        self.generate_thread.start()
    
    def _on_generate_progress(self, message):
        self.status_label.setText(message)
        if hasattr(self, 'progress_dialog') and self.progress_dialog:
            self.progress_dialog.update_progress(message)
    
    def _on_generate_finished(self, readme_content):
        if hasattr(self, 'progress_dialog') and self.progress_dialog:
            self.progress_dialog.close()
            self.progress_dialog = None
        
        self.generated_readme = readme_content
        self.readme_preview_text.setText(readme_content)
        self.ai_analysis_text.setText("AI 分析已完成，请查看 README 预览")
        
        self.scan_btn.setEnabled(True)
        self.generate_btn.setEnabled(True)
        self.save_btn.setEnabled(True)
        self.status_label.setText("README 生成完成")
        
        QMessageBox.information(
            self, 
            "完成", 
            "✅ README 生成完成！\n\n文档已生成并预览，您可以点击「保存 README」按钮将其保存到项目目录。"
        )
    
    def _on_generate_error(self, error_message):
        if hasattr(self, 'progress_dialog') and self.progress_dialog:
            self.progress_dialog.close()
            self.progress_dialog = None
        
        self.scan_btn.setEnabled(True)
        self.generate_btn.setEnabled(True)
        self.status_label.setText("生成失败")
        
        error_details = f"❌ 生成失败: {error_message}\n\n"
        error_details += "💡 可能的解决方案：\n"
        error_details += "1. 检查 API Key 是否正确\n"
        error_details += "2. 检查网络连接\n"
        error_details += "3. 检查 API Key 余额是否充足\n"
        error_details += "4. 稍后重试（可能是服务器繁忙）"
        
        QMessageBox.critical(self, "错误", error_details)
    
    def _save_readme(self):
        if not self.generated_readme:
            QMessageBox.warning(self, "警告", "没有可保存的 README 内容")
            return
        
        directory = self.dir_edit.text().strip()
        if not directory:
            file_path, _ = QFileDialog.getSaveFileName(
                self,
                "保存 README 文件",
                "README.md",
                "Markdown 文件 (*.md)"
            )
        else:
            default_path = os.path.join(directory, "README.md")
            file_path, _ = QFileDialog.getSaveFileName(
                self,
                "保存 README 文件",
                default_path,
                "Markdown 文件 (*.md)"
            )
        
        if file_path:
            try:
                with open(file_path, 'w', encoding='utf-8') as f:
                    f.write(self.generated_readme)
                QMessageBox.information(self, "成功", f"README 已保存到: {file_path}")
            except Exception as e:
                QMessageBox.critical(self, "错误", f"保存失败: {str(e)}")
    
    def _format_directory_structure(self, structure):
        if not structure:
            return "无目录结构信息"
        
        lines = ["# 目录结构\n"]
        
        def format_node(node, prefix="", is_last=True):
            node_lines = []
            connector = "└── " if is_last else "├── "
            node_lines.append(f"{prefix}{connector}{node['name']}")
            
            if node.get('children'):
                new_prefix = prefix + ("    " if is_last else "│   ")
                children = node['children']
                for i, child in enumerate(children):
                    child_lines = format_node(child, new_prefix, i == len(children) - 1)
                    node_lines.extend(child_lines)
            
            return node_lines
        
        lines.extend(format_node(structure))
        return "\n".join(lines)
    
    def _format_tech_stack(self, tech_stack):
        if not tech_stack:
            return "无技术栈信息"
        
        lines = ["# 技术栈\n"]
        
        if tech_stack.get('languages'):
            lines.append("## 编程语言")
            for lang, details in tech_stack['languages'].items():
                lines.append(f"- **{lang}**")
                if details.get('files'):
                    lines.append(f"  - 文件数: {details['files']}")
                if details.get('extensions'):
                    lines.append(f"  - 扩展名: {', '.join(details['extensions'])}")
            lines.append("")
        
        if tech_stack.get('frameworks'):
            lines.append("## 框架和库")
            for framework in tech_stack['frameworks']:
                lines.append(f"- {framework}")
            lines.append("")
        
        if tech_stack.get('build_tools'):
            lines.append("## 构建工具")
            for tool in tech_stack['build_tools']:
                lines.append(f"- {tool}")
            lines.append("")
        
        if tech_stack.get('package_managers'):
            lines.append("## 包管理器")
            for pm in tech_stack['package_managers']:
                lines.append(f"- {pm}")
            lines.append("")
        
        if tech_stack.get('databases'):
            lines.append("## 数据库")
            for db in tech_stack['databases']:
                lines.append(f"- {db}")
            lines.append("")
        
        return "\n".join(lines)
    
    def _format_entry_files(self, entry_files):
        if not entry_files:
            return "无入口文件信息"
        
        lines = ["# 核心入口文件\n"]
        
        for entry_file in entry_files:
            lines.append(f"## {entry_file['name']}")
            lines.append(f"**路径**: {entry_file['path']}")
            
            if entry_file.get('description'):
                lines.append(f"\n**描述**: {entry_file['description']}")
            
            if entry_file.get('purpose'):
                lines.append(f"\n**用途**: {entry_file['purpose']}")
            
            if entry_file.get('size'):
                lines.append(f"\n**大小**: {entry_file['size']} 字节")
            
            lines.append("")
        
        return "\n".join(lines)
    
    def _format_git_history(self, git_history):
        if not git_history or not git_history.get('commits'):
            return "无 Git 历史信息（可能不是 Git 仓库）"
        
        lines = ["# Git 历史\n"]
        
        if git_history.get('current_branch'):
            lines.append(f"**当前分支**: {git_history['current_branch']}\n")
        
        if git_history.get('remotes'):
            lines.append("**远程仓库**:")
            for name, url in git_history['remotes'].items():
                lines.append(f"- {name}: {url}")
            lines.append("")
        
        lines.append("## 最近提交\n")
        
        for commit in git_history['commits']:
            lines.append(f"### {commit['message']}")
            lines.append(f"- **提交者**: {commit['author']} <{commit['email']}>")
            lines.append(f"- **日期**: {commit['date']}")
            lines.append(f"- **Hash**: {commit['hash'][:7]}")
            lines.append("")
        
        return "\n".join(lines)
