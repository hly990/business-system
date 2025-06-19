"""
KPI仪表板组件
"""
import logging
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QGridLayout,
    QLabel, QFrame, QScrollArea, QToolBar, QComboBox
)
from PyQt6.QtCore import Qt, pyqtSignal, QTimer
from PyQt6.QtGui import QPainter, QColor, QFont, QPen, QBrush
from PyQt6.QtCharts import QChart, QChartView, QLineSeries, QPieSeries, QBarSeries, QBarSet

from ..ui.components.custom_widgets import CustomButton
from ..services.data_manager import DataManager


class KPICard(QFrame):
    """KPI卡片组件"""
    
    def __init__(self, kpi_data, parent=None):
        super().__init__(parent)
        self.kpi_data = kpi_data
        self.init_ui()
        
    def init_ui(self):
        """初始化UI"""
        self.setFrameStyle(QFrame.Shape.Box)
        self.setStyleSheet("""
            QFrame {
                background-color: white;
                border: 1px solid #e0e0e0;
                border-radius: 8px;
                padding: 10px;
            }
            QFrame:hover {
                border-color: #1976d2;
                box-shadow: 0 2px 8px rgba(0,0,0,0.1);
            }
        """)
        
        layout = QVBoxLayout(self)
        layout.setSpacing(8)
        
        # 标题
        title_label = QLabel(self.kpi_data.get('name', '未命名指标'))
        title_label.setFont(QFont("Arial", 12, QFont.Weight.Bold))
        title_label.setStyleSheet("color: #333; margin-bottom: 5px;")
        layout.addWidget(title_label)
        
        # 当前值
        current_value = self.kpi_data.get('current_value', 0)
        target_value = self.kpi_data.get('target_value', 100)
        
        value_label = QLabel(f"{current_value}")
        value_label.setFont(QFont("Arial", 24, QFont.Weight.Bold))
        value_label.setStyleSheet("color: #1976d2;")
        value_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(value_label)
        
        # 目标值
        target_label = QLabel(f"目标: {target_value}")
        target_label.setStyleSheet("color: #666; font-size: 12px;")
        target_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(target_label)
        
        # 进度条
        progress_widget = self.create_progress_bar(current_value, target_value)
        layout.addWidget(progress_widget)
        
        # 趋势指示器
        trend = self.kpi_data.get('trend', 'stable')
        trend_label = self.create_trend_indicator(trend)
        layout.addWidget(trend_label)
        
    def create_progress_bar(self, current, target):
        """创建进度条"""
        progress_widget = QWidget()
        progress_widget.setFixedHeight(20)
        
        def paint_progress(event):
            painter = QPainter(progress_widget)
            painter.setRenderHint(QPainter.RenderHint.Antialiasing)
            
            rect = progress_widget.rect()
            
            # 背景
            painter.setPen(Qt.PenStyle.NoPen)
            painter.setBrush(QBrush(QColor("#f0f0f0")))
            painter.drawRoundedRect(rect, 10, 10)
            
            # 进度
            if target > 0:
                progress_ratio = min(current / target, 1.0)
                progress_width = rect.width() * progress_ratio
                
                color = QColor("#4caf50") if progress_ratio >= 1.0 else QColor("#1976d2")
                painter.setBrush(QBrush(color))
                painter.drawRoundedRect(0, 0, progress_width, rect.height(), 10, 10)
                
        progress_widget.paintEvent = paint_progress
        return progress_widget
        
    def create_trend_indicator(self, trend):
        """创建趋势指示器"""
        trend_label = QLabel()
        trend_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        if trend == 'up':
            trend_label.setText("↗ 上升")
            trend_label.setStyleSheet("color: #4caf50; font-size: 12px;")
        elif trend == 'down':
            trend_label.setText("↘ 下降")
            trend_label.setStyleSheet("color: #f44336; font-size: 12px;")
        else:
            trend_label.setText("→ 稳定")
            trend_label.setStyleSheet("color: #ff9800; font-size: 12px;")
            
        return trend_label


class KPIDashboard(QWidget):
    """KPI仪表板组件"""
    
    # 信号定义
    kpi_selected = pyqtSignal(dict)
    refresh_requested = pyqtSignal()
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.logger = logging.getLogger(__name__)
        self.data_manager = DataManager()
        
        # 数据缓存
        self.kpis_data = []
        self.charts_data = {}
        
        # 刷新定时器
        self.refresh_timer = QTimer()
        self.refresh_timer.timeout.connect(self.refresh_data)
        
        self.init_ui()
        self.setup_connections()
        self.load_data()
        
        # 启动自动刷新（每5分钟）
        self.refresh_timer.start(300000)
        
    def init_ui(self):
        """初始化用户界面"""
        layout = QVBoxLayout(self)
        
        # 工具栏
        self.create_toolbar()
        layout.addWidget(self.toolbar)
        
        # 滚动区域
        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_area.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAsNeeded)
        scroll_area.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        
        # 主内容区域
        self.content_widget = QWidget()
        self.content_layout = QVBoxLayout(self.content_widget)
        
        # KPI卡片区域
        self.create_kpi_cards_section()
        
        # 图表区域
        self.create_charts_section()
        
        scroll_area.setWidget(self.content_widget)
        layout.addWidget(scroll_area)
        
    def create_toolbar(self):
        """创建工具栏"""
        self.toolbar = QToolBar()
        
        # 刷新按钮
        refresh_btn = CustomButton("刷新", ":/icons/refresh.png", "primary")
        refresh_btn.clicked.connect(self.refresh_data)
        self.toolbar.addWidget(refresh_btn)
        
        self.toolbar.addSeparator()
        
        # 时间范围选择
        self.toolbar.addWidget(QLabel("时间范围:"))
        self.time_range_combo = QComboBox()
        self.time_range_combo.addItems(["今天", "本周", "本月", "本季度", "本年"])
        self.time_range_combo.setCurrentText("本月")
        self.time_range_combo.currentTextChanged.connect(self.on_time_range_changed)
        self.toolbar.addWidget(self.time_range_combo)
        
        self.toolbar.addSeparator()
        
        # 导出按钮
        export_btn = CustomButton("导出报告", ":/icons/export.png", "secondary")
        export_btn.clicked.connect(self.export_report)
        self.toolbar.addWidget(export_btn)
        
    def create_kpi_cards_section(self):
        """创建KPI卡片区域"""
        # 标题
        title_label = QLabel("关键绩效指标")
        title_label.setFont(QFont("Arial", 16, QFont.Weight.Bold))
        title_label.setStyleSheet("color: #333; margin: 10px 0;")
        self.content_layout.addWidget(title_label)
        
        # 卡片网格
        self.cards_widget = QWidget()
        self.cards_layout = QGridLayout(self.cards_widget)
        self.cards_layout.setSpacing(15)
        
        self.content_layout.addWidget(self.cards_widget)
        
    def create_charts_section(self):
        """创建图表区域"""
        # 标题
        charts_title = QLabel("趋势分析")
        charts_title.setFont(QFont("Arial", 16, QFont.Weight.Bold))
        charts_title.setStyleSheet("color: #333; margin: 20px 0 10px 0;")
        self.content_layout.addWidget(charts_title)
        
        # 图表容器
        self.charts_widget = QWidget()
        self.charts_layout = QGridLayout(self.charts_widget)
        self.charts_layout.setSpacing(15)
        
        self.content_layout.addWidget(self.charts_widget)
        
    def setup_connections(self):
        """设置信号连接"""
        # 数据管理器信号
        self.data_manager.data_loaded.connect(self.on_data_loaded)
        self.data_manager.error_occurred.connect(self.on_error_occurred)
        
    def load_data(self):
        """加载数据"""
        try:
            self.data_manager.load_kpis()
        except Exception as e:
            self.logger.error(f"加载KPI数据失败: {e}")
            
    def refresh_data(self):
        """刷新数据"""
        self.load_data()
        self.refresh_requested.emit()
        
    def on_data_loaded(self, data_type):
        """数据加载完成处理"""
        if data_type == 'kpis':
            self.kpis_data = self.data_manager.get_kpis()
            self.update_kpi_cards()
            self.update_charts()
            
    def on_error_occurred(self, error_msg):
        """错误处理"""
        self.logger.error(f"KPI仪表板错误: {error_msg}")
        
    def update_kpi_cards(self):
        """更新KPI卡片"""
        # 清除现有卡片
        for i in reversed(range(self.cards_layout.count())):
            child = self.cards_layout.itemAt(i).widget()
            if child:
                child.setParent(None)
                
        # 创建新卡片
        row, col = 0, 0
        max_cols = 4
        
        for kpi_data in self.kpis_data:
            card = KPICard(kpi_data)
            card.mousePressEvent = lambda event, data=kpi_data: self.on_kpi_card_clicked(data)
            
            self.cards_layout.addWidget(card, row, col)
            
            col += 1
            if col >= max_cols:
                col = 0
                row += 1
                
    def update_charts(self):
        """更新图表"""
        # 清除现有图表
        for i in reversed(range(self.charts_layout.count())):
            child = self.charts_layout.itemAt(i).widget()
            if child:
                child.setParent(None)
                
        # 创建趋势图表
        self.create_trend_chart()
        
        # 创建分布图表
        self.create_distribution_chart()
        
    def create_trend_chart(self):
        """创建趋势图表"""
        try:
            # 创建线性图表
            chart = QChart()
            chart.setTitle("KPI趋势分析")
            chart.setAnimationOptions(QChart.AnimationOption.SeriesAnimations)
            
            # 模拟数据（实际应用中从数据库获取）
            series = QLineSeries()
            series.setName("平均完成率")
            
            # 添加数据点
            for i in range(30):
                import random
                value = 70 + random.randint(-10, 20)
                series.append(i, value)
                
            chart.addSeries(series)
            chart.createDefaultAxes()
            
            # 创建图表视图
            chart_view = QChartView(chart)
            chart_view.setRenderHint(QPainter.RenderHint.Antialiasing)
            chart_view.setMinimumHeight(300)
            
            self.charts_layout.addWidget(chart_view, 0, 0)
            
        except Exception as e:
            self.logger.error(f"创建趋势图表失败: {e}")
            
    def create_distribution_chart(self):
        """创建分布图表"""
        try:
            # 创建饼图
            chart = QChart()
            chart.setTitle("KPI分布情况")
            chart.setAnimationOptions(QChart.AnimationOption.SeriesAnimations)
            
            series = QPieSeries()
            
            # 统计KPI状态分布
            status_count = {'优秀': 0, '良好': 0, '一般': 0, '需改进': 0}
            
            for kpi in self.kpis_data:
                current = kpi.get('current_value', 0)
                target = kpi.get('target_value', 100)
                
                if target > 0:
                    ratio = current / target
                    if ratio >= 1.0:
                        status_count['优秀'] += 1
                    elif ratio >= 0.8:
                        status_count['良好'] += 1
                    elif ratio >= 0.6:
                        status_count['一般'] += 1
                    else:
                        status_count['需改进'] += 1
                        
            # 添加数据到饼图
            colors = ['#4caf50', '#2196f3', '#ff9800', '#f44336']
            for i, (status, count) in enumerate(status_count.items()):
                if count > 0:
                    slice = series.append(status, count)
                    slice.setColor(QColor(colors[i % len(colors)]))
                    
            chart.addSeries(series)
            
            # 创建图表视图
            chart_view = QChartView(chart)
            chart_view.setRenderHint(QPainter.RenderHint.Antialiasing)
            chart_view.setMinimumHeight(300)
            
            self.charts_layout.addWidget(chart_view, 0, 1)
            
        except Exception as e:
            self.logger.error(f"创建分布图表失败: {e}")
            
    def on_kpi_card_clicked(self, kpi_data):
        """KPI卡片点击处理"""
        self.kpi_selected.emit(kpi_data)
        
    def on_time_range_changed(self, time_range):
        """时间范围变化处理"""
        self.logger.info(f"时间范围切换到: {time_range}")
        # 重新加载对应时间范围的数据
        self.refresh_data()
        
    def export_report(self):
        """导出报告"""
        try:
            # TODO: 实现报告导出功能
            self.logger.info("导出KPI报告")
        except Exception as e:
            self.logger.error(f"导出报告失败: {e}")
            
    def get_summary_stats(self):
        """获取汇总统计"""
        if not self.kpis_data:
            return {}
            
        total_kpis = len(self.kpis_data)
        completed_kpis = 0
        total_progress = 0
        
        for kpi in self.kpis_data:
            current = kpi.get('current_value', 0)
            target = kpi.get('target_value', 100)
            
            if target > 0:
                progress = min(current / target, 1.0)
                total_progress += progress
                
                if progress >= 1.0:
                    completed_kpis += 1
                    
        avg_progress = total_progress / total_kpis if total_kpis > 0 else 0
        completion_rate = completed_kpis / total_kpis if total_kpis > 0 else 0
        
        return {
            'total_kpis': total_kpis,
            'completed_kpis': completed_kpis,
            'avg_progress': avg_progress,
            'completion_rate': completion_rate
        }
        
    def has_unsaved_changes(self):
        """检查是否有未保存的更改"""
        return False
        
    def save(self):
        """保存"""
        pass
        
    def zoom_in(self):
        """放大"""
        pass
        
    def zoom_out(self):
        """缩小"""
        pass
        
    def zoom_fit(self):
        """适应窗口"""
        pass