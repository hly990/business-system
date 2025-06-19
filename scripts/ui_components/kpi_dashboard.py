"""
KPI指标监控仪表板窗口
按照技术架构文档设计的KPI监控界面
"""
from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QGridLayout, QTableWidget, QTableWidgetItem,
    QPushButton, QLabel, QMessageBox, QWidget, QTextBrowser, QGroupBox,
    QFormLayout, QLineEdit, QTextEdit, QComboBox, QSpinBox, QHeaderView,
    QTabWidget, QListWidget, QListWidgetItem, QCheckBox, QDateEdit,
    QProgressBar, QFrame, QScrollArea, QSlider
)
from PyQt6.QtCore import Qt, QThread, pyqtSignal, QDate, QTimer
from PyQt6.QtGui import QFont, QIcon, QPalette, QColor, QPainter, QPen, QBrush
import random

class KPICard(QFrame):
    """KPI指标卡片组件"""
    
    def __init__(self, kpi_data, parent=None):
        super().__init__(parent)
        self.kpi_data = kpi_data
        self.setup_ui()
        
    def setup_ui(self):
        self.setFrameStyle(QFrame.Shape.Box)
        self.setStyleSheet("""
            QFrame {
                background-color: white;
                border: 1px solid #E5E7EB;
                border-radius: 8px;
                padding: 16px;
                margin: 4px;
            }
            QFrame:hover {
                border-color: #1976d2;
                box-shadow: 0 2px 8px rgba(0,0,0,0.1);
            }
        """)
        
        layout = QVBoxLayout()
        
        # KPI名称
        name_label = QLabel(self.kpi_data.get('name', 'KPI指标'))
        name_label.setStyleSheet("""
            QLabel {
                font-weight: bold;
                font-size: 14px;
                color: #374151;
                margin-bottom: 8px;
            }
        """)
        layout.addWidget(name_label)
        
        # 当前值
        current_value = self.kpi_data.get('value', 0)
        target_value = self.kpi_data.get('target', 100)
        unit = self.kpi_data.get('unit', '')
        
        value_label = QLabel(f"{current_value:.1f}{unit}")
        value_label.setStyleSheet("""
            QLabel {
                font-size: 28px;
                font-weight: bold;
                color: #1976d2;
                margin: 8px 0;
            }
        """)
        layout.addWidget(value_label)
        
        # 目标值
        target_label = QLabel(f"目标: {target_value:.1f}{unit}")
        target_label.setStyleSheet("""
            QLabel {
                font-size: 12px;
                color: #6B7280;
                margin-bottom: 8px;
            }
        """)
        layout.addWidget(target_label)
        
        # 进度条
        progress = QProgressBar()
        completion_rate = min(100, (current_value / target_value * 100) if target_value > 0 else 0)
        progress.setValue(int(completion_rate))
        
        # 根据完成率设置颜色
        if completion_rate >= 100:
            color = "#10B981"  # 绿色
        elif completion_rate >= 80:
            color = "#F59E0B"  # 黄色
        else:
            color = "#EF4444"  # 红色
            
        progress.setStyleSheet(f"""
            QProgressBar {{
                border: 1px solid #E5E7EB;
                border-radius: 4px;
                text-align: center;
                height: 20px;
            }}
            QProgressBar::chunk {{
                background-color: {color};
                border-radius: 3px;
            }}
        """)
        layout.addWidget(progress)
        
        # 完成率标签
        rate_label = QLabel(f"{completion_rate:.1f}%")
        rate_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        rate_label.setStyleSheet(f"""
            QLabel {{
                font-size: 12px;
                font-weight: bold;
                color: {color};
                margin-top: 4px;
            }}
        """)
        layout.addWidget(rate_label)
        
        self.setLayout(layout)

class KPIEditDialog(QDialog):
    """KPI编辑对话框"""
    
    def __init__(self, kpi_data=None, parent=None):
        super().__init__(parent)
        self.kpi_data = kpi_data
        self.setWindowTitle("编辑KPI指标" if kpi_data else "新建KPI指标")
        self.setModal(True)
        self.resize(500, 400)
        self.setup_ui()
        
        if kpi_data:
            self.load_kpi_data()
            
    def setup_ui(self):
        layout = QVBoxLayout()
        
        # 基本信息区域
        info_group = QGroupBox("基本信息")
        info_layout = QFormLayout()
        
        self.name_edit = QLineEdit()
        self.name_edit.setPlaceholderText("请输入KPI指标名称")
        info_layout.addRow("指标名称*:", self.name_edit)
        
        self.description_edit = QTextEdit()
        self.description_edit.setPlaceholderText("请输入指标描述")
        self.description_edit.setMaximumHeight(80)
        info_layout.addRow("指标描述:", self.description_edit)
        
        self.process_combo = QComboBox()
        self.process_combo.addItems(["客户开发流程", "订单处理流程", "生产计划流程", "质量控制流程"])
        info_layout.addRow("关联流程:", self.process_combo)
        
        self.type_combo = QComboBox()
        self.type_combo.addItems(["数量", "百分比", "金额", "时长"])
        info_layout.addRow("指标类型:", self.type_combo)
        
        self.unit_edit = QLineEdit()
        self.unit_edit.setPlaceholderText("如：%、元、分钟等")
        info_layout.addRow("单位:", self.unit_edit)
        
        info_group.setLayout(info_layout)
        layout.addWidget(info_group)
        
        # 目标设置区域
        target_group = QGroupBox("目标设置")
        target_layout = QFormLayout()
        
        self.target_spin = QSpinBox()
        self.target_spin.setRange(0, 999999)
        self.target_spin.setValue(100)
        target_layout.addRow("目标值*:", self.target_spin)
        
        self.current_spin = QSpinBox()
        self.current_spin.setRange(0, 999999)
        self.current_spin.setValue(0)
        target_layout.addRow("当前值:", self.current_spin)
        
        self.frequency_combo = QComboBox()
        self.frequency_combo.addItems(["实时", "每小时", "每日", "每周", "每月"])
        target_layout.addRow("更新频率:", self.frequency_combo)
        
        target_group.setLayout(target_layout)
        layout.addWidget(target_group)
        
        # 数据源设置区域
        source_group = QGroupBox("数据源设置")
        source_layout = QFormLayout()
        
        self.source_combo = QComboBox()
        self.source_combo.addItems(["手动输入", "API接口", "数据库查询", "文件导入"])
        source_layout.addRow("数据源:", self.source_combo)
        
        self.source_config_edit = QTextEdit()
        self.source_config_edit.setPlaceholderText("数据源配置信息（JSON格式）")
        self.source_config_edit.setMaximumHeight(80)
        source_layout.addRow("配置信息:", self.source_config_edit)
        
        source_group.setLayout(source_layout)
        layout.addWidget(source_group)
        
        # 按钮区域
        button_layout = QHBoxLayout()
        
        self.save_btn = QPushButton("保存")
        self.save_btn.clicked.connect(self.save_kpi)
        self.save_btn.setStyleSheet("""
            QPushButton {
                background-color: #10B981;
                color: white;
                border: none;
                padding: 8px 16px;
                border-radius: 4px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #059669;
            }
        """)
        
        self.cancel_btn = QPushButton("取消")
        self.cancel_btn.clicked.connect(self.reject)
        self.cancel_btn.setStyleSheet("""
            QPushButton {
                background-color: #6B7280;
                color: white;
                border: none;
                padding: 8px 16px;
                border-radius: 4px;
            }
            QPushButton:hover {
                background-color: #4B5563;
            }
        """)
        
        button_layout.addStretch()
        button_layout.addWidget(self.save_btn)
        button_layout.addWidget(self.cancel_btn)
        
        layout.addLayout(button_layout)
        self.setLayout(layout)
        
    def load_kpi_data(self):
        """加载KPI数据"""
        if self.kpi_data:
            self.name_edit.setText(self.kpi_data.get('name', ''))
            self.description_edit.setText(self.kpi_data.get('description', ''))
            self.target_spin.setValue(int(self.kpi_data.get('target', 100)))
            self.current_spin.setValue(int(self.kpi_data.get('value', 0)))
            self.unit_edit.setText(self.kpi_data.get('unit', ''))
            
    def save_kpi(self):
        """保存KPI"""
        name = self.name_edit.text().strip()
        if not name:
            QMessageBox.warning(self, "验证错误", "KPI指标名称不能为空")
            return
            
        target = self.target_spin.value()
        if target <= 0:
            QMessageBox.warning(self, "验证错误", "目标值必须大于0")
            return
            
        QMessageBox.information(self, "保存成功", f"KPI指标 '{name}' 已保存")
        self.accept()

class KPIDashboardWindow(QDialog):
    """KPI指标监控仪表板窗口"""
    
    def __init__(self, api_client, parent=None):
        super().__init__(parent)
        self.api_client = api_client
        self.setWindowTitle("KPI指标监控")
        self.setGeometry(200, 200, 1200, 800)
        self.kpi_cards = []
        self.setup_ui()
        self.load_data()
        
        # 设置定时器自动刷新数据
        self.refresh_timer = QTimer()
        self.refresh_timer.timeout.connect(self.auto_refresh_data)
        self.refresh_timer.start(30000)  # 30秒刷新一次
        
    def setup_ui(self):
        layout = QVBoxLayout()
        
        # 标题区域
        title_layout = QHBoxLayout()
        title_label = QLabel("KPI指标监控面板")
        title_label.setStyleSheet("""
            QLabel {
                font-size: 20px;
                font-weight: bold;
                color: #1976d2;
                margin: 10px 0;
            }
        """)
        
        self.refresh_btn = QPushButton("🔄 刷新数据")
        self.refresh_btn.clicked.connect(self.load_data)
        self.refresh_btn.setStyleSheet("""
            QPushButton {
                background-color: #1976d2;
                color: white;
                border: none;
                padding: 8px 16px;
                border-radius: 4px;
            }
            QPushButton:hover {
                background-color: #1565c0;
            }
        """)
        
        self.auto_refresh_label = QLabel("🔄 自动刷新: 开启")
        self.auto_refresh_label.setStyleSheet("color: #10B981; font-size: 12px;")
        
        title_layout.addWidget(title_label)
        title_layout.addStretch()
        title_layout.addWidget(self.auto_refresh_label)
        title_layout.addWidget(self.refresh_btn)
        layout.addLayout(title_layout)
        
        # 工具栏
        toolbar_layout = QHBoxLayout()
        
        self.add_kpi_btn = QPushButton("➕ 新建KPI")
        self.add_kpi_btn.clicked.connect(self.add_kpi)
        
        self.edit_kpi_btn = QPushButton("✏️ 编辑KPI")
        self.edit_kpi_btn.clicked.connect(self.edit_kpi)
        
        self.delete_kpi_btn = QPushButton("🗑️ 删除KPI")
        self.delete_kpi_btn.clicked.connect(self.delete_kpi)
        
        self.export_btn = QPushButton("📊 导出报表")
        self.export_btn.clicked.connect(self.export_report)
        
        # 设置按钮样式
        button_style = """
            QPushButton {
                background-color: #1976d2;
                color: white;
                border: none;
                padding: 8px 16px;
                border-radius: 4px;
                margin: 2px;
            }
            QPushButton:hover {
                background-color: #1565c0;
            }
        """
        
        for btn in [self.add_kpi_btn, self.edit_kpi_btn, self.delete_kpi_btn, self.export_btn]:
            btn.setStyleSheet(button_style)
            toolbar_layout.addWidget(btn)
            
        toolbar_layout.addStretch()
        layout.addLayout(toolbar_layout)
        
        # 主内容区域
        main_tab_widget = QTabWidget()
        
        # KPI概览标签页
        overview_tab = QWidget()
        overview_layout = QVBoxLayout()
        
        # KPI卡片区域
        cards_scroll = QScrollArea()
        cards_widget = QWidget()
        self.cards_layout = QGridLayout()
        cards_widget.setLayout(self.cards_layout)
        cards_scroll.setWidget(cards_widget)
        cards_scroll.setWidgetResizable(True)
        cards_scroll.setMaximumHeight(300)
        
        overview_layout.addWidget(QLabel("KPI指标概览"))
        overview_layout.addWidget(cards_scroll)
        
        # KPI详细表格
        overview_layout.addWidget(QLabel("KPI详细数据"))
        
        self.kpi_table = QTableWidget()
        self.kpi_table.setColumnCount(6)
        self.kpi_table.setHorizontalHeaderLabels(["指标名称", "当前值", "目标值", "完成率", "状态", "更新时间"])
        
        # 设置表格属性
        header = self.kpi_table.horizontalHeader()
        header.setStretchLastSection(True)
        header.setSectionResizeMode(0, QHeaderView.ResizeMode.Stretch)
        
        self.kpi_table.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        self.kpi_table.setAlternatingRowColors(True)
        
        overview_layout.addWidget(self.kpi_table)
        
        overview_tab.setLayout(overview_layout)
        main_tab_widget.addTab(overview_tab, "KPI概览")
        
        # 趋势分析标签页
        trend_tab = QWidget()
        trend_layout = QVBoxLayout()
        
        # 图表占位符
        chart_placeholder = QLabel("📈 趋势图表区域")
        chart_placeholder.setAlignment(Qt.AlignmentFlag.AlignCenter)
        chart_placeholder.setStyleSheet("""
            QLabel {
                background-color: #f5f5f5;
                border: 2px dashed #ccc;
                border-radius: 8px;
                padding: 60px;
                font-size: 18px;
                color: #666;
                margin: 20px;
            }
        """)
        chart_placeholder.setMinimumHeight(300)
        
        trend_layout.addWidget(chart_placeholder)
        
        # 趋势分析控制面板
        trend_control_group = QGroupBox("分析设置")
        trend_control_layout = QHBoxLayout()
        
        trend_control_layout.addWidget(QLabel("时间范围:"))
        time_range_combo = QComboBox()
        time_range_combo.addItems(["最近7天", "最近30天", "最近3个月", "最近1年"])
        trend_control_layout.addWidget(time_range_combo)
        
        trend_control_layout.addWidget(QLabel("KPI选择:"))
        kpi_select_combo = QComboBox()
        kpi_select_combo.addItems(["全部KPI", "客户满意度", "生产效率", "成本控制率", "订单及时率"])
        trend_control_layout.addWidget(kpi_select_combo)
        
        analyze_btn = QPushButton("📊 生成分析")
        analyze_btn.setStyleSheet(button_style)
        trend_control_layout.addWidget(analyze_btn)
        
        trend_control_layout.addStretch()
        trend_control_group.setLayout(trend_control_layout)
        trend_layout.addWidget(trend_control_group)
        
        # 分析结果
        analysis_result = QTextBrowser()
        analysis_result.setMaximumHeight(200)
        analysis_result.setHtml("""
        <h3>KPI趋势分析报告</h3>
        <h4>总体表现：</h4>
        <ul>
            <li>📈 <strong>客户满意度</strong>: 呈上升趋势，较上月提升2.3%</li>
            <li>📊 <strong>生产效率</strong>: 保持稳定，略有波动</li>
            <li>📉 <strong>成本控制率</strong>: 需要关注，较目标偏高3.7%</li>
            <li>✅ <strong>订单及时率</strong>: 表现优秀，超出目标4.2%</li>
        </ul>
        <h4>改进建议：</h4>
        <ol>
            <li>继续保持客户满意度的提升势头</li>
            <li>重点关注成本控制，寻找优化空间</li>
            <li>分析生产效率波动原因</li>
            <li>总结订单及时率的成功经验</li>
        </ol>
        """)
        trend_layout.addWidget(analysis_result)
        
        trend_tab.setLayout(trend_layout)
        main_tab_widget.addTab(trend_tab, "趋势分析")
        
        # 预警设置标签页
        alert_tab = QWidget()
        alert_layout = QVBoxLayout()
        
        # 预警规则表格
        alert_layout.addWidget(QLabel("预警规则设置"))
        
        alert_table = QTableWidget()
        alert_table.setColumnCount(5)
        alert_table.setHorizontalHeaderLabels(["KPI指标", "预警条件", "阈值", "通知方式", "状态"])
        
        # 添加示例预警规则
        alert_table.setRowCount(4)
        alert_rules = [
            ("客户满意度", "低于目标", "85%", "邮件+短信", "启用"),
            ("生产效率", "连续下降", "3天", "邮件", "启用"),
            ("成本控制率", "超出目标", "10%", "邮件+钉钉", "启用"),
            ("订单及时率", "低于目标", "95%", "短信", "禁用")
        ]
        
        for row, (kpi, condition, threshold, notify, status) in enumerate(alert_rules):
            alert_table.setItem(row, 0, QTableWidgetItem(kpi))
            alert_table.setItem(row, 1, QTableWidgetItem(condition))
            alert_table.setItem(row, 2, QTableWidgetItem(threshold))
            alert_table.setItem(row, 3, QTableWidgetItem(notify))
            alert_table.setItem(row, 4, QTableWidgetItem(status))
            
        alert_table.horizontalHeader().setStretchLastSection(True)
        alert_layout.addWidget(alert_table)
        
        # 预警操作按钮
        alert_btn_layout = QHBoxLayout()
        
        add_alert_btn = QPushButton("➕ 添加预警")
        edit_alert_btn = QPushButton("✏️ 编辑预警")
        delete_alert_btn = QPushButton("🗑️ 删除预警")
        test_alert_btn = QPushButton("🔔 测试预警")
        
        for btn in [add_alert_btn, edit_alert_btn, delete_alert_btn, test_alert_btn]:
            btn.setStyleSheet(button_style)
            alert_btn_layout.addWidget(btn)
            
        alert_btn_layout.addStretch()
        alert_layout.addLayout(alert_btn_layout)
        
        # 预警历史
        alert_layout.addWidget(QLabel("预警历史"))
        
        alert_history = QListWidget()
        history_items = [
            "⚠️ 2024-01-15 14:30 - 客户满意度低于目标值 (84.2%)",
            "🔔 2024-01-14 09:15 - 生产效率连续下降3天",
            "⚠️ 2024-01-13 16:45 - 成本控制率超出目标10.5%",
            "✅ 2024-01-12 11:20 - 订单及时率恢复正常水平"
        ]
        
        for item_text in history_items:
            alert_history.addItem(item_text)
            
        alert_history.setMaximumHeight(150)
        alert_layout.addWidget(alert_history)
        
        alert_tab.setLayout(alert_layout)
        main_tab_widget.addTab(alert_tab, "预警设置")
        
        layout.addWidget(main_tab_widget)
        self.setLayout(layout)
        
    def load_data(self):
        """加载KPI数据"""
        try:
            kpis = self.api_client.get_kpis()
            
            # 清除现有卡片
            for card in self.kpi_cards:
                card.setParent(None)
            self.kpi_cards.clear()
            
            # 创建KPI卡片
            for i, kpi in enumerate(kpis):
                card = KPICard(kpi)
                self.kpi_cards.append(card)
                row = i // 4
                col = i % 4
                self.cards_layout.addWidget(card, row, col)
                
            # 更新表格
            self.kpi_table.setRowCount(len(kpis))
            for row, kpi in enumerate(kpis):
                current_value = kpi.get('value', 0)
                target_value = kpi.get('target', 1)
                completion_rate = (current_value / target_value * 100) if target_value > 0 else 0
                
                # 状态判断
                if completion_rate >= 100:
                    status = "✅ 达标"
                elif completion_rate >= 80:
                    status = "⚠️ 接近"
                else:
                    status = "❌ 偏低"
                
                self.kpi_table.setItem(row, 0, QTableWidgetItem(kpi.get('name', '')))
                self.kpi_table.setItem(row, 1, QTableWidgetItem(f"{current_value:.1f}{kpi.get('unit', '')}"))
                self.kpi_table.setItem(row, 2, QTableWidgetItem(f"{target_value:.1f}{kpi.get('unit', '')}"))
                self.kpi_table.setItem(row, 3, QTableWidgetItem(f"{completion_rate:.1f}%"))
                self.kpi_table.setItem(row, 4, QTableWidgetItem(status))
                self.kpi_table.setItem(row, 5, QTableWidgetItem("2024-01-15 14:30"))
                
        except Exception as e:
            QMessageBox.warning(self, "错误", f"加载KPI数据失败:\n{str(e)}")
            
    def auto_refresh_data(self):
        """自动刷新数据"""
        # 模拟数据变化
        for card in self.kpi_cards:
            if hasattr(card, 'kpi_data'):
                # 随机微调数值
                current_value = card.kpi_data.get('value', 0)
                variation = random.uniform(-2, 2)
                new_value = max(0, current_value + variation)
                card.kpi_data['value'] = new_value
                
        # 重新加载数据
        self.load_data()
        
    def add_kpi(self):
        """新建KPI"""
        dialog = KPIEditDialog(parent=self)
        if dialog.exec() == QDialog.DialogCode.Accepted:
            self.load_data()
            
    def edit_kpi(self):
        """编辑KPI"""
        selected_rows = self.kpi_table.selectionModel().selectedRows()
        if not selected_rows:
            QMessageBox.information(self, "提示", "请先选择要编辑的KPI指标")
            return
            
        row = selected_rows[0].row()
        kpi_data = {
            'name': self.kpi_table.item(row, 0).text(),
            'value': float(self.kpi_table.item(row, 1).text().rstrip('%元分钟')),
            'target': float(self.kpi_table.item(row, 2).text().rstrip('%元分钟')),
        }
        
        dialog = KPIEditDialog(kpi_data, parent=self)
        if dialog.exec() == QDialog.DialogCode.Accepted:
            self.load_data()
            
    def delete_kpi(self):
        """删除KPI"""
        selected_rows = self.kpi_table.selectionModel().selectedRows()
        if not selected_rows:
            QMessageBox.information(self, "提示", "请先选择要删除的KPI指标")
            return
            
        row = selected_rows[0].row()
        kpi_name = self.kpi_table.item(row, 0).text()
        
        reply = QMessageBox.question(
            self, 
            "确认删除", 
            f"确定要删除KPI指标 '{kpi_name}' 吗？\n\n此操作不可撤销。",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )
        
        if reply == QMessageBox.StandardButton.Yes:
            QMessageBox.information(self, "删除成功", f"KPI指标 '{kpi_name}' 已删除")
            self.load_data()
            
    def export_report(self):
        """导出报表"""
        QMessageBox.information(
            self, 
            "导出报表", 
            "KPI报表导出功能\n\n支持格式:\n• Excel表格 (.xlsx)\n• PDF报告 (.pdf)\n• CSV数据 (.csv)\n\n功能开发中..."
        )