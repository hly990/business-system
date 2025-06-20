#!/usr/bin/env python3
"""
SelfMastery B2B业务系统 - 窗口标题修改脚本
使用 Sentry 监控修改过程
"""
import os
import sys
import logging
import json
from datetime import datetime

# 添加项目根目录到 Python 路径
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

try:
    from selfmastery.frontend.services.monitoring import (
        init_frontend_sentry_monitoring,
        capture_frontend_message,
        add_frontend_breadcrumb
    )
    SENTRY_AVAILABLE = True
except ImportError:
    SENTRY_AVAILABLE = False

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class WindowTitleChanger:
    """窗口标题修改器"""
    
    def __init__(self, new_title: str):
        self.new_title = new_title
        self.changes_made = []
        self.backup_files = []
        
        # 初始化 Sentry 监控
        if SENTRY_AVAILABLE:
            try:
                init_frontend_sentry_monitoring()
                capture_frontend_message(
                    f"开始修改窗口标题为: {new_title}",
                    level="info"
                )
                add_frontend_breadcrumb(
                    message="窗口标题修改任务开始",
                    category="title_change",
                    data={"new_title": new_title}
                )
            except Exception as e:
                logger.warning(f"Sentry 初始化失败: {e}")
    
    def find_title_locations(self):
        """查找所有需要修改标题的位置"""
        locations = [
            {
                "file": "selfmastery/frontend/ui/main_window.py",
                "line": 62,
                "pattern": 'self.setWindowTitle("SelfMastery 自动化业务系统")',
                "replacement": f'self.setWindowTitle("{self.new_title}")'
            },
            {
                "file": "scripts/start_ui_simple.py", 
                "line": 110,
                "pattern": 'self.setWindowTitle("SelfMastery B2B业务系统")',
                "replacement": f'self.setWindowTitle("{self.new_title}")'
            },
            {
                "file": "scripts/start_ui_simple.py",
                "line": 122, 
                "pattern": 'title_label = QLabel("SelfMastery B2B业务系统")',
                "replacement": f'title_label = QLabel("{self.new_title}")'
            },
            {
                "file": "scripts/start_ui_simple.py",
                "line": 282,
                "pattern": 'app.setApplicationName("SelfMastery B2B业务系统")',
                "replacement": f'app.setApplicationName("{self.new_title}")'
            }
        ]
        return locations
    
    def backup_file(self, file_path: str):
        """备份文件"""
        try:
            backup_path = f"{file_path}.backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
            
            with open(file_path, 'r', encoding='utf-8') as original:
                content = original.read()
            
            with open(backup_path, 'w', encoding='utf-8') as backup:
                backup.write(content)
            
            self.backup_files.append(backup_path)
            logger.info(f"文件已备份: {backup_path}")
            
            if SENTRY_AVAILABLE:
                add_frontend_breadcrumb(
                    message=f"文件备份完成: {file_path}",
                    category="backup",
                    data={"backup_path": backup_path}
                )
            
            return True
        except Exception as e:
            logger.error(f"备份文件失败 {file_path}: {e}")
            if SENTRY_AVAILABLE:
                capture_frontend_message(
                    f"文件备份失败: {file_path} - {e}",
                    level="error"
                )
            return False
    
    def modify_file(self, location: dict):
        """修改单个文件"""
        file_path = location["file"]
        
        try:
            # 备份文件
            if not self.backup_file(file_path):
                return False
            
            # 读取文件内容
            with open(file_path, 'r', encoding='utf-8') as file:
                lines = file.readlines()
            
            # 查找并修改指定行
            modified = False
            for i, line in enumerate(lines):
                if location["pattern"] in line:
                    lines[i] = line.replace(location["pattern"], location["replacement"])
                    modified = True
                    logger.info(f"已修改 {file_path}:{i+1}")
                    
                    if SENTRY_AVAILABLE:
                        add_frontend_breadcrumb(
                            message=f"代码行修改成功: {file_path}:{i+1}",
                            category="code_change",
                            data={
                                "file": file_path,
                                "line": i+1,
                                "old": location["pattern"],
                                "new": location["replacement"]
                            }
                        )
                    break
            
            if not modified:
                logger.warning(f"在 {file_path} 中未找到匹配的模式: {location['pattern']}")
                return False
            
            # 写回文件
            with open(file_path, 'w', encoding='utf-8') as file:
                file.writelines(lines)
            
            self.changes_made.append({
                "file": file_path,
                "line": location["line"],
                "old": location["pattern"],
                "new": location["replacement"],
                "timestamp": datetime.now().isoformat()
            })
            
            return True
            
        except Exception as e:
            logger.error(f"修改文件失败 {file_path}: {e}")
            if SENTRY_AVAILABLE:
                capture_frontend_message(
                    f"文件修改失败: {file_path} - {e}",
                    level="error"
                )
            return False
    
    def change_all_titles(self):
        """修改所有标题位置"""
        locations = self.find_title_locations()
        success_count = 0
        
        logger.info(f"找到 {len(locations)} 个需要修改的位置")
        
        for location in locations:
            if self.modify_file(location):
                success_count += 1
            else:
                logger.error(f"修改失败: {location['file']}")
        
        # 生成修改报告  
        report = {
            "task": "窗口标题修改",
            "new_title": self.new_title,
            "total_locations": len(locations),
            "successful_changes": success_count,
            "failed_changes": len(locations) - success_count,
            "changes_made": self.changes_made,
            "backup_files": self.backup_files,
            "timestamp": datetime.now().isoformat()
        }
        
        # 保存报告
        report_file = "title_change_report.json"
        with open(report_file, 'w', encoding='utf-8') as f:
            json.dump(report, f, ensure_ascii=False, indent=2)
        
        logger.info(f"修改报告已保存: {report_file}")
        
        if SENTRY_AVAILABLE:
            capture_frontend_message(
                f"窗口标题修改完成: {success_count}/{len(locations)} 个位置修改成功",
                level="info" if success_count == len(locations) else "warning"
            )
        
        return success_count == len(locations)
    
    def rollback_changes(self):
        """回滚所有更改"""
        logger.info("开始回滚更改...")
        
        rollback_success = 0
        for backup_file in self.backup_files:
            try:
                original_file = backup_file.split('.backup_')[0]
                
                # 恢复原文件
                with open(backup_file, 'r', encoding='utf-8') as backup:
                    content = backup.read()
                
                with open(original_file, 'w', encoding='utf-8') as original:
                    original.write(content)
                
                logger.info(f"已回滚: {original_file}")
                rollback_success += 1
                
            except Exception as e:
                logger.error(f"回滚失败 {backup_file}: {e}")
        
        if SENTRY_AVAILABLE:
            capture_frontend_message(
                f"回滚操作完成: {rollback_success}/{len(self.backup_files)} 个文件回滚成功",
                level="info"
            )
        
        return rollback_success == len(self.backup_files)


def main():
    """主函数"""
    if len(sys.argv) < 2:
        print("用法: python change_window_title.py <新标题> [--rollback]")
        print("示例: python change_window_title.py '我的业务系统'")
        print("回滚: python change_window_title.py --rollback")
        return
    
    if sys.argv[1] == "--rollback":
        # 回滚功能（需要从报告文件中读取备份信息）
        try:
            with open("title_change_report.json", 'r', encoding='utf-8') as f:
                report = json.load(f)
            
            changer = WindowTitleChanger("")  # 空标题，仅用于回滚
            changer.backup_files = report.get("backup_files", [])
            
            if changer.rollback_changes():
                print("✅ 回滚成功！")
            else:
                print("❌ 回滚过程中出现错误")
                
        except FileNotFoundError:
            print("❌ 未找到修改报告文件，无法回滚")
        except Exception as e:
            print(f"❌ 回滚失败: {e}")
        return
    
    new_title = sys.argv[1]
    
    print(f"🎯 准备将窗口标题修改为: {new_title}")
    print("📋 将要修改的文件位置:")
    print("   1. selfmastery/frontend/ui/main_window.py (第62行)")
    print("   2. scripts/start_ui_simple.py (第110、122、282行)")
    
    if SENTRY_AVAILABLE:
        print("📊 Sentry 监控已启用")
    else:
        print("⚠️  Sentry 监控不可用")
    
    confirm = input("\n确认继续修改？(y/N): ")
    if confirm.lower() not in ['y', 'yes']:
        print("操作已取消")
        return
    
    # 执行修改
    changer = WindowTitleChanger(new_title)
    
    if changer.change_all_titles():
        print("✅ 窗口标题修改成功！")
        print(f"📄 修改报告: title_change_report.json")
        print("\n📌 要使修改生效，请重新启动应用程序")
        print("🔄 如需回滚，请运行: python change_window_title.py --rollback")
    else:
        print("❌ 修改过程中出现错误，请查看日志")


if __name__ == "__main__":
    main() 