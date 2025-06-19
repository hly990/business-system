#!/usr/bin/env python3
"""
SelfMastery B2B业务系统 - 简化UI启动脚本
修复模块导入问题
"""
import sys
import os
from pathlib import Path

# 设置项目根目录
PROJECT_ROOT = Path(__file__).parent.parent
SELFMASTERY_ROOT = PROJECT_ROOT / "selfmastery"

# 将项目路径添加到sys.path
sys.path.insert(0, str(PROJECT_ROOT))
sys.path.insert(0, str(SELFMASTERY_ROOT))

print("🎯 SelfMastery B2B UI启动工具")
print("=" * 50)

try:
    print("📦 检查环境...")
    
    # 检查PyQt6
    import PyQt6.QtWidgets
    print("   ✅ PyQt6已安装")
    
    # 设置环境变量
    os.environ['PYTHONPATH'] = f"{PROJECT_ROOT}:{SELFMASTERY_ROOT}"
    
    print("🎨 启动UI界面...")
    
    # 使用PyQt6直接创建一个简单的应用
    app = PyQt6.QtWidgets.QApplication(sys.argv)
    
    # 创建主窗口
    from PyQt6.QtWidgets import QMainWindow, QLabel, QVBoxLayout, QWidget, QPushButton
    from PyQt6.QtCore import Qt
    
    class SimpleMainWindow(QMainWindow):
        def __init__(self):
            super().__init__()
            self.setWindowTitle("SelfMastery B2B业务系统")
            self.setGeometry(100, 100, 800, 600)
            
            # 创建中央部件
            central_widget = QWidget()
            self.setCentralWidget(central_widget)
            
            # 创建布局
            layout = QVBoxLayout()
            central_widget.setLayout(layout)
            
            # 添加标题
            title_label = QLabel("SelfMastery B2B业务系统")
            title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
            title_label.setStyleSheet("""
                QLabel {
                    font-size: 24px;
                    font-weight: bold;
                    color: #1976d2;
                    margin: 20px;
                }
            """)
            layout.addWidget(title_label)
            
            # 添加状态信息
            status_label = QLabel("系统启动成功！前端UI界面正在运行...")
            status_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
            status_label.setStyleSheet("""
                QLabel {
                    font-size: 14px;
                    color: #666;
                    margin: 10px;
                }
            """)
            layout.addWidget(status_label)
            
            # 添加功能按钮
            buttons_info = [
                ("🏢 业务系统管理", "管理业务系统架构"),
                ("🔄 业务流程设计", "设计和优化业务流程"),
                ("📋 SOP文档管理", "标准作业程序文档"),
                ("📊 KPI指标监控", "关键绩效指标dashboard"),
                ("✅ 任务管理", "项目任务跟踪管理")
            ]
            
            for button_text, description in buttons_info:
                btn = QPushButton(button_text)
                btn.setToolTip(description)
                btn.setStyleSheet("""
                    QPushButton {
                        background-color: #1976d2;
                        color: white;
                        border: none;
                        padding: 12px;
                        margin: 5px;
                        border-radius: 6px;
                        font-size: 14px;
                    }
                    QPushButton:hover {
                        background-color: #1565c0;
                    }
                    QPushButton:pressed {
                        background-color: #0d47a1;
                    }
                """)
                layout.addWidget(btn)
            
            # 添加底部信息
            info_label = QLabel("""
💡 提示：
• 确保后端API服务正在运行 (端口8000)
• 使用 'python scripts/final_startup_fix.py' 启动后端
• API文档: http://localhost:8000/docs
• 健康检查: http://localhost:8000/health
            """)
            info_label.setStyleSheet("""
                QLabel {
                    background-color: #f5f5f5;
                    border: 1px solid #ddd;
                    border-radius: 8px;
                    padding: 15px;
                    margin: 10px;
                    font-size: 12px;
                    color: #555;
                }
            """)
            layout.addWidget(info_label)
            
    # 创建并显示主窗口
    window = SimpleMainWindow()
    window.show()
    
    print("   ✅ UI界面已启动")
    print("\n🎉 成功！UI界面正在运行...")
    print("📊 系统状态:")
    print("   ✅ UI界面: 正在运行")
    print("   ℹ️  这是简化版本UI")
    print("   💡 请确保后端服务运行在 http://localhost:8000")
    
    # 运行应用
    sys.exit(app.exec())
    
except ImportError as e:
    print(f"❌ 导入错误: {e}")
    print("\n💡 解决方案:")
    print("   1. 安装PyQt6: pip install PyQt6")
    print("   2. 检查Python环境")
    sys.exit(1)
    
except Exception as e:
    print(f"❌ 启动失败: {e}")
    import traceback
    traceback.print_exc()
    print("\n💡 故障排除:")
    print("   1. 检查PyQt6安装")
    print("   2. 检查系统环境")
    print("   3. 尝试重新安装依赖")
    sys.exit(1) 