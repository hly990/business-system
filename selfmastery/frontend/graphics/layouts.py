"""
自动布局算法
"""
import math
from typing import List, Dict, Tuple
from PyQt6.QtCore import QPointF, QRectF
from PyQt6.QtWidgets import QGraphicsItem


class AutoLayoutManager:
    """自动布局管理器"""
    
    def __init__(self, scene):
        self.scene = scene
        
    def apply_hierarchical_layout(self, system_items, process_items, connection_items):
        """应用层次布局"""
        if not system_items and not process_items:
            return
            
        # 构建层次结构
        hierarchy = self.build_hierarchy(system_items, process_items, connection_items)
        
        # 计算布局
        self.calculate_hierarchical_positions(hierarchy)
        
        # 应用位置
        self.apply_positions(hierarchy)
        
    def build_hierarchy(self, system_items, process_items, connection_items):
        """构建层次结构"""
        hierarchy = {
            'systems': {},
            'processes': {},
            'connections': connection_items,
            'levels': []
        }
        
        # 处理系统项目
        for item in system_items:
            system_id = item.data.get('id')
            parent_id = item.data.get('parent_id')
            
            hierarchy['systems'][system_id] = {
                'item': item,
                'parent_id': parent_id,
                'children': [],
                'level': 0,
                'position': QPointF(0, 0)
            }
            
        # 建立父子关系
        for system_id, system_info in hierarchy['systems'].items():
            parent_id = system_info['parent_id']
            if parent_id and parent_id in hierarchy['systems']:
                hierarchy['systems'][parent_id]['children'].append(system_id)
                
        # 计算层级
        self.calculate_levels(hierarchy['systems'])
        
        # 处理流程项目
        for item in process_items:
            process_id = item.data.get('id')
            system_id = item.data.get('system_id')
            
            hierarchy['processes'][process_id] = {
                'item': item,
                'system_id': system_id,
                'level': 0,
                'position': QPointF(0, 0),
                'connections_in': [],
                'connections_out': []
            }
            
        # 建立连接关系
        for connection in connection_items:
            from_id = connection.data.get('from_process_id')
            to_id = connection.data.get('to_process_id')
            
            if from_id in hierarchy['processes']:
                hierarchy['processes'][from_id]['connections_out'].append(to_id)
            if to_id in hierarchy['processes']:
                hierarchy['processes'][to_id]['connections_in'].append(from_id)
                
        return hierarchy
        
    def calculate_levels(self, systems):
        """计算系统层级"""
        # 找到根系统
        roots = [sid for sid, sinfo in systems.items() if not sinfo['parent_id']]
        
        # 递归计算层级
        def set_level(system_id, level):
            if system_id in systems:
                systems[system_id]['level'] = level
                for child_id in systems[system_id]['children']:
                    set_level(child_id, level + 1)
                    
        for root_id in roots:
            set_level(root_id, 0)
            
    def calculate_hierarchical_positions(self, hierarchy):
        """计算层次布局位置"""
        # 系统布局参数
        system_spacing_x = 200
        system_spacing_y = 150
        process_spacing_x = 150
        process_spacing_y = 100
        
        # 按层级组织系统
        levels = {}
        for system_id, system_info in hierarchy['systems'].items():
            level = system_info['level']
            if level not in levels:
                levels[level] = []
            levels[level].append(system_id)
            
        # 布局系统
        for level, system_ids in levels.items():
            y = level * system_spacing_y
            total_width = len(system_ids) * system_spacing_x
            start_x = -total_width / 2
            
            for i, system_id in enumerate(system_ids):
                x = start_x + i * system_spacing_x
                hierarchy['systems'][system_id]['position'] = QPointF(x, y)
                
        # 布局流程（在对应系统附近）
        for process_id, process_info in hierarchy['processes'].items():
            system_id = process_info['system_id']
            if system_id in hierarchy['systems']:
                system_pos = hierarchy['systems'][system_id]['position']
                
                # 在系统右侧布局流程
                process_x = system_pos.x() + 250
                process_y = system_pos.y()
                
                process_info['position'] = QPointF(process_x, process_y)
                
    def apply_positions(self, hierarchy):
        """应用计算出的位置"""
        # 应用系统位置
        for system_info in hierarchy['systems'].values():
            item = system_info['item']
            position = system_info['position']
            item.setPos(position)
            
        # 应用流程位置
        for process_info in hierarchy['processes'].values():
            item = process_info['item']
            position = process_info['position']
            item.setPos(position)
            
        # 更新连接线
        for connection in hierarchy['connections']:
            if hasattr(connection, 'update_path'):
                connection.update_path()
                
    def apply_force_directed_layout(self, items, iterations=100):
        """应用力导向布局"""
        if len(items) < 2:
            return
            
        # 布局参数
        area = 1000 * 1000
        k = math.sqrt(area / len(items))
        
        # 初始化位置（如果没有位置）
        for i, item in enumerate(items):
            if item.pos().isNull():
                angle = 2 * math.pi * i / len(items)
                radius = 200
                x = radius * math.cos(angle)
                y = radius * math.sin(angle)
                item.setPos(x, y)
                
        # 迭代计算
        for iteration in range(iterations):
            # 计算斥力
            for i, item1 in enumerate(items):
                force_x = 0
                force_y = 0
                
                for j, item2 in enumerate(items):
                    if i != j:
                        dx = item1.pos().x() - item2.pos().x()
                        dy = item1.pos().y() - item2.pos().y()
                        distance = math.sqrt(dx * dx + dy * dy)
                        
                        if distance > 0:
                            # 斥力
                            repulsion = k * k / distance
                            force_x += (dx / distance) * repulsion
                            force_y += (dy / distance) * repulsion
                            
                # 应用力
                new_x = item1.pos().x() + force_x * 0.1
                new_y = item1.pos().y() + force_y * 0.1
                item1.setPos(new_x, new_y)
                
    def apply_circular_layout(self, items, center=QPointF(0, 0), radius=300):
        """应用圆形布局"""
        if not items:
            return
            
        angle_step = 2 * math.pi / len(items)
        
        for i, item in enumerate(items):
            angle = i * angle_step
            x = center.x() + radius * math.cos(angle)
            y = center.y() + radius * math.sin(angle)
            item.setPos(x, y)
            
    def apply_grid_layout(self, items, cols=None, spacing=150):
        """应用网格布局"""
        if not items:
            return
            
        if cols is None:
            cols = math.ceil(math.sqrt(len(items)))
            
        for i, item in enumerate(items):
            row = i // cols
            col = i % cols
            x = col * spacing
            y = row * spacing
            item.setPos(x, y)
            
    def apply_tree_layout(self, root_items, child_items, connections):
        """应用树形布局"""
        if not root_items:
            return
            
        # 构建树结构
        tree = self.build_tree_structure(root_items, child_items, connections)
        
        # 计算树布局
        self.calculate_tree_positions(tree)
        
    def build_tree_structure(self, root_items, child_items, connections):
        """构建树结构"""
        # TODO: 实现树结构构建
        pass
        
    def calculate_tree_positions(self, tree):
        """计算树形布局位置"""
        # TODO: 实现树形位置计算
        pass
        
    def optimize_layout(self, items, connections):
        """优化布局（减少连线交叉）"""
        if len(items) < 3:
            return
            
        # 计算当前交叉数
        initial_crossings = self.count_crossings(connections)
        
        # 尝试交换位置来减少交叉
        improved = True
        max_iterations = 50
        iteration = 0
        
        while improved and iteration < max_iterations:
            improved = False
            iteration += 1
            
            for i in range(len(items)):
                for j in range(i + 1, len(items)):
                    # 交换位置
                    pos1 = items[i].pos()
                    pos2 = items[j].pos()
                    
                    items[i].setPos(pos2)
                    items[j].setPos(pos1)
                    
                    # 更新连接线
                    for connection in connections:
                        if hasattr(connection, 'update_path'):
                            connection.update_path()
                            
                    # 检查是否改善
                    new_crossings = self.count_crossings(connections)
                    
                    if new_crossings < initial_crossings:
                        initial_crossings = new_crossings
                        improved = True
                    else:
                        # 恢复位置
                        items[i].setPos(pos1)
                        items[j].setPos(pos2)
                        
                        # 恢复连接线
                        for connection in connections:
                            if hasattr(connection, 'update_path'):
                                connection.update_path()
                                
    def count_crossings(self, connections):
        """计算连线交叉数"""
        crossings = 0
        
        for i in range(len(connections)):
            for j in range(i + 1, len(connections)):
                if self.lines_intersect(connections[i], connections[j]):
                    crossings += 1
                    
        return crossings
        
    def lines_intersect(self, line1, line2):
        """检查两条线是否相交"""
        # TODO: 实现线段相交检测
        return False
        
    def align_items(self, items, alignment='left'):
        """对齐项目"""
        if not items:
            return
            
        if alignment == 'left':
            min_x = min(item.pos().x() for item in items)
            for item in items:
                item.setPos(min_x, item.pos().y())
        elif alignment == 'right':
            max_x = max(item.pos().x() + item.boundingRect().width() for item in items)
            for item in items:
                item.setPos(max_x - item.boundingRect().width(), item.pos().y())
        elif alignment == 'top':
            min_y = min(item.pos().y() for item in items)
            for item in items:
                item.setPos(item.pos().x(), min_y)
        elif alignment == 'bottom':
            max_y = max(item.pos().y() + item.boundingRect().height() for item in items)
            for item in items:
                item.setPos(item.pos().x(), max_y - item.boundingRect().height())
        elif alignment == 'center_horizontal':
            center_x = sum(item.pos().x() + item.boundingRect().width() / 2 for item in items) / len(items)
            for item in items:
                item.setPos(center_x - item.boundingRect().width() / 2, item.pos().y())
        elif alignment == 'center_vertical':
            center_y = sum(item.pos().y() + item.boundingRect().height() / 2 for item in items) / len(items)
            for item in items:
                item.setPos(item.pos().x(), center_y - item.boundingRect().height() / 2)
                
    def distribute_items(self, items, direction='horizontal'):
        """分布项目"""
        if len(items) < 3:
            return
            
        if direction == 'horizontal':
            # 按X坐标排序
            items.sort(key=lambda item: item.pos().x())
            
            # 计算总宽度
            left = items[0].pos().x()
            right = items[-1].pos().x() + items[-1].boundingRect().width()
            total_width = right - left
            
            # 计算间距
            item_widths = sum(item.boundingRect().width() for item in items)
            spacing = (total_width - item_widths) / (len(items) - 1)
            
            # 重新分布
            current_x = left
            for item in items:
                item.setPos(current_x, item.pos().y())
                current_x += item.boundingRect().width() + spacing
                
        elif direction == 'vertical':
            # 按Y坐标排序
            items.sort(key=lambda item: item.pos().y())
            
            # 计算总高度
            top = items[0].pos().y()
            bottom = items[-1].pos().y() + items[-1].boundingRect().height()
            total_height = bottom - top
            
            # 计算间距
            item_heights = sum(item.boundingRect().height() for item in items)
            spacing = (total_height - item_heights) / (len(items) - 1)
            
            # 重新分布
            current_y = top
            for item in items:
                item.setPos(item.pos().x(), current_y)
                current_y += item.boundingRect().height() + spacing