"""
Document Template Manager Module
文档模板管理器模块，提供各种预设的文档模板
"""

import json
import os
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional
from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QPushButton, QTextEdit,
    QComboBox, QLabel, QListWidget, QListWidgetItem, QGroupBox,
    QTabWidget, QWidget, QMessageBox, QLineEdit, QCheckBox,
    QPlainTextEdit, QFrame, QSplitter
)
from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtGui import QFont

class DocumentTemplate:
    """文档模板类"""
    
    def __init__(self, name: str, category: str, description: str, content: str, 
                 variables: Optional[Dict] = None, metadata: Optional[Dict] = None):
        self.name = name
        self.category = category
        self.description = description
        self.content = content
        self.variables = variables or {}
        self.metadata = metadata or {}
        self.created_date = datetime.now()
        
    def to_dict(self) -> Dict:
        """转换为字典"""
        return {
            'name': self.name,
            'category': self.category,
            'description': self.description,
            'content': self.content,
            'variables': self.variables,
            'metadata': self.metadata,
            'created_date': self.created_date.isoformat()
        }
        
    @classmethod
    def from_dict(cls, data: Dict) -> 'DocumentTemplate':
        """从字典创建模板"""
        template = cls(
            name=data['name'],
            category=data['category'],
            description=data['description'],
            content=data['content'],
            variables=data.get('variables', {}),
            metadata=data.get('metadata', {})
        )
        if 'created_date' in data:
            template.created_date = datetime.fromisoformat(data['created_date'])
        return template

class TemplateManager:
    """模板管理器"""
    
    def __init__(self):
        self.templates = {}
        self.templates_dir = Path(__file__).parent / "templates"
        self.templates_dir.mkdir(exist_ok=True)
        self.load_builtin_templates()
        self.load_custom_templates()
        
    def load_builtin_templates(self):
        """加载内置模板"""
        builtin_templates = [
            DocumentTemplate(
                name="学术论文",
                category="学术",
                description="标准学术论文格式，包含摘要、引言、方法、结果、讨论、结论等部分",
                content="""# {title}

**作者**: {author}  
**单位**: {institution}  
**日期**: {date}

## 摘要

{abstract}

**关键词**: {keywords}

## 1. 引言

{introduction}

## 2. 文献综述

{literature_review}

## 3. 研究方法

{methodology}

## 4. 研究结果

{results}

## 5. 讨论与分析

{discussion}

## 6. 结论

{conclusion}

## 参考文献

{references}
""",
                variables={
                    "title": "论文标题",
                    "author": "作者姓名",
                    "institution": "作者单位",
                    "date": str(datetime.now().strftime("%Y年%m月%d日")),
                    "abstract": "[在此处填写摘要内容]",
                    "keywords": "[关键词1; 关键词2; 关键词3]",
                    "introduction": "[在此处填写引言内容]",
                    "literature_review": "[在此处填写文献综述]",
                    "methodology": "[在此处填写研究方法]",
                    "results": "[在此处填写研究结果]",
                    "discussion": "[在此处填写讨论内容]",
                    "conclusion": "[在此处填写结论]",
                    "references": "[1] 参考文献示例..."
                }
            ),
            
            DocumentTemplate(
                name="商业计划书",
                category="商业",
                description="完整的商业计划书模板，适用于创业项目和投资申请",
                content="""# {company_name} 商业计划书

**编制日期**: {date}  
**版本**: {version}  
**保密等级**: {confidentiality}

---

## 执行摘要

{executive_summary}

## 1. 公司概述

### 1.1 公司简介
{company_intro}

### 1.2 愿景与使命
**愿景**: {vision}  
**使命**: {mission}

### 1.3 核心价值观
{core_values}

## 2. 市场分析

### 2.1 行业概况
{industry_overview}

### 2.2 目标市场
{target_market}

### 2.3 竞争分析
{competition_analysis}

## 3. 产品与服务

### 3.1 产品描述
{product_description}

### 3.2 核心优势
{core_advantages}

### 3.3 研发计划
{rd_plan}

## 4. 营销策略

### 4.1 营销目标
{marketing_goals}

### 4.2 定价策略
{pricing_strategy}

### 4.3 推广渠道
{promotion_channels}

## 5. 运营计划

### 5.1 组织架构
{organizational_structure}

### 5.2 运营流程
{operational_process}

### 5.3 质量控制
{quality_control}

## 6. 财务预测

### 6.1 收入预测
{revenue_forecast}

### 6.2 成本分析
{cost_analysis}

### 6.3 盈利预测
{profit_forecast}

## 7. 风险评估

### 7.1 市场风险
{market_risks}

### 7.2 技术风险
{technical_risks}

### 7.3 风险应对措施
{risk_mitigation}

## 8. 融资需求

### 8.1 资金需求
{funding_requirements}

### 8.2 资金用途
{fund_usage}

### 8.3 退出策略
{exit_strategy}

## 附录

{appendix}
""",
                variables={
                    "company_name": "公司名称",
                    "date": str(datetime.now().strftime("%Y年%m月%d日")),
                    "version": "1.0",
                    "confidentiality": "商业机密",
                    "executive_summary": "[在此处填写执行摘要]",
                    "company_intro": "[在此处填写公司简介]",
                    "vision": "[公司愿景]",
                    "mission": "[公司使命]",
                    "core_values": "[核心价值观]",
                    "industry_overview": "[行业概况分析]",
                    "target_market": "[目标市场描述]",
                    "competition_analysis": "[竞争对手分析]",
                    "product_description": "[产品/服务描述]",
                    "core_advantages": "[核心竞争优势]",
                    "rd_plan": "[研发计划]",
                    "marketing_goals": "[营销目标]",
                    "pricing_strategy": "[定价策略]",
                    "promotion_channels": "[推广渠道]",
                    "organizational_structure": "[组织架构]",
                    "operational_process": "[运营流程]",
                    "quality_control": "[质量控制措施]",
                    "revenue_forecast": "[收入预测]",
                    "cost_analysis": "[成本分析]",
                    "profit_forecast": "[盈利预测]",
                    "market_risks": "[市场风险分析]",
                    "technical_risks": "[技术风险分析]",
                    "risk_mitigation": "[风险应对措施]",
                    "funding_requirements": "[资金需求]",
                    "fund_usage": "[资金用途]",
                    "exit_strategy": "[退出策略]",
                    "appendix": "[附录内容]"
                }
            ),
            
            DocumentTemplate(
                name="技术文档",
                category="技术",
                description="软件或技术项目的标准文档模板",
                content="""# {project_name} 技术文档

**版本**: {version}  
**日期**: {date}  
**作者**: {author}  
**状态**: {status}

---

## 1. 概述

### 1.1 项目简介
{project_intro}

### 1.2 文档目的
{document_purpose}

### 1.3 目标读者
{target_audience}

## 2. 系统架构

### 2.1 整体架构
{system_architecture}

### 2.2 技术栈
{tech_stack}

### 2.3 系统依赖
{dependencies}

## 3. 功能说明

### 3.1 核心功能
{core_features}

### 3.2 功能模块
{feature_modules}

### 3.3 用户界面
{user_interface}

## 4. 技术实现

### 4.1 核心算法
{core_algorithms}

### 4.2 数据结构
{data_structures}

### 4.3 接口设计
{api_design}

## 5. 部署指南

### 5.1 环境要求
{environment_requirements}

### 5.2 安装步骤
{installation_steps}

### 5.3 配置说明
{configuration}

## 6. 使用说明

### 6.1 快速开始
{quick_start}

### 6.2 详细教程
{detailed_tutorial}

### 6.3 最佳实践
{best_practices}

## 7. API 文档

### 7.1 接口列表
{api_list}

### 7.2 请求格式
{request_format}

### 7.3 响应格式
{response_format}

## 8. 故障排除

### 8.1 常见问题
{common_issues}

### 8.2 错误代码
{error_codes}

### 8.3 调试指南
{debugging_guide}

## 9. 版本历史

### 9.1 更新日志
{changelog}

### 9.2 已知问题
{known_issues}

### 9.3 计划功能
{planned_features}

## 10. 联系信息

{contact_info}
""",
                variables={
                    "project_name": "项目名称",
                    "version": "1.0.0",
                    "date": str(datetime.now().strftime("%Y-%m-%d")),
                    "author": "开发团队",
                    "status": "草稿",
                    "project_intro": "[项目简介]",
                    "document_purpose": "[文档目的]",
                    "target_audience": "[目标读者]",
                    "system_architecture": "[系统架构描述]",
                    "tech_stack": "[技术栈列表]",
                    "dependencies": "[系统依赖]",
                    "core_features": "[核心功能描述]",
                    "feature_modules": "[功能模块说明]",
                    "user_interface": "[用户界面描述]",
                    "core_algorithms": "[核心算法]",
                    "data_structures": "[数据结构]",
                    "api_design": "[接口设计]",
                    "environment_requirements": "[环境要求]",
                    "installation_steps": "[安装步骤]",
                    "configuration": "[配置说明]",
                    "quick_start": "[快速开始指南]",
                    "detailed_tutorial": "[详细教程]",
                    "best_practices": "[最佳实践]",
                    "api_list": "[API接口列表]",
                    "request_format": "[请求格式]",
                    "response_format": "[响应格式]",
                    "common_issues": "[常见问题]",
                    "error_codes": "[错误代码说明]",
                    "debugging_guide": "[调试指南]",
                    "changelog": "[更新日志]",
                    "known_issues": "[已知问题]",
                    "planned_features": "[计划功能]",
                    "contact_info": "[联系信息]"
                }
            ),
            
            DocumentTemplate(
                name="项目报告",
                category="管理",
                description="项目进展和总结报告模板",
                content="""# {project_name} 项目报告

**报告类型**: {report_type}  
**报告期间**: {period}  
**提交日期**: {date}  
**项目经理**: {project_manager}

---

## 执行摘要

{executive_summary}

## 1. 项目概述

### 1.1 项目背景
{project_background}

### 1.2 项目目标
{project_objectives}

### 1.3 项目范围
{project_scope}

## 2. 项目进展

### 2.1 已完成工作
{completed_work}

### 2.2 正在进行的工作
{ongoing_work}

### 2.3 计划工作
{planned_work}

## 3. 里程碑状态

### 3.1 已达成里程碑
{achieved_milestones}

### 3.2 即将到来的里程碑
{upcoming_milestones}

### 3.3 延期里程碑
{delayed_milestones}

## 4. 资源使用情况

### 4.1 人力资源
{human_resources}

### 4.2 财务状况
{financial_status}

### 4.3 设备资源
{equipment_resources}

## 5. 风险管理

### 5.1 已识别风险
{identified_risks}

### 5.2 风险缓解措施
{risk_mitigation}

### 5.3 新风险
{new_risks}

## 6. 问题与挑战

### 6.1 当前问题
{current_issues}

### 6.2 解决方案
{solutions}

### 6.3 需要支持
{support_needed}

## 7. 质量管理

### 7.1 质量指标
{quality_metrics}

### 7.2 质量问题
{quality_issues}

### 7.3 改进措施
{improvement_measures}

## 8. 下阶段计划

### 8.1 短期目标
{short_term_goals}

### 8.2 关键活动
{key_activities}

### 8.3 预期成果
{expected_outcomes}

## 9. 建议与结论

### 9.1 主要建议
{recommendations}

### 9.2 结论
{conclusions}

### 9.3 下次报告计划
{next_report_plan}

## 附录

### A. 详细数据
{detailed_data}

### B. 相关文档
{related_documents}
""",
                variables={
                    "project_name": "项目名称",
                    "report_type": "进展报告",
                    "period": f"{datetime.now().strftime('%Y年%m月')}",
                    "date": str(datetime.now().strftime("%Y年%m月%d日")),
                    "project_manager": "项目经理姓名",
                    "executive_summary": "[执行摘要]",
                    "project_background": "[项目背景]",
                    "project_objectives": "[项目目标]",
                    "project_scope": "[项目范围]",
                    "completed_work": "[已完成工作]",
                    "ongoing_work": "[正在进行的工作]",
                    "planned_work": "[计划工作]",
                    "achieved_milestones": "[已达成里程碑]",
                    "upcoming_milestones": "[即将到来的里程碑]",
                    "delayed_milestones": "[延期里程碑]",
                    "human_resources": "[人力资源使用情况]",
                    "financial_status": "[财务状况]",
                    "equipment_resources": "[设备资源]",
                    "identified_risks": "[已识别风险]",
                    "risk_mitigation": "[风险缓解措施]",
                    "new_risks": "[新风险]",
                    "current_issues": "[当前问题]",
                    "solutions": "[解决方案]",
                    "support_needed": "[需要支持]",
                    "quality_metrics": "[质量指标]",
                    "quality_issues": "[质量问题]",
                    "improvement_measures": "[改进措施]",
                    "short_term_goals": "[短期目标]",
                    "key_activities": "[关键活动]",
                    "expected_outcomes": "[预期成果]",
                    "recommendations": "[主要建议]",
                    "conclusions": "[结论]",
                    "next_report_plan": "[下次报告计划]",
                    "detailed_data": "[详细数据]",
                    "related_documents": "[相关文档]"
                }
            ),
            
            DocumentTemplate(
                name="会议记录",
                category="管理",
                description="标准会议记录模板",
                content="""# {meeting_title} 会议记录

**会议时间**: {meeting_date}  
**会议地点**: {meeting_location}  
**会议主持**: {meeting_host}  
**记录人员**: {recorder}

## 参会人员

{attendees}

## 会议议程

{agenda}

## 会议内容

### 1. 开场
{opening}

### 2. 主要议题

#### 议题一: {topic_1_title}
**讨论内容**: {topic_1_content}  
**决议**: {topic_1_decision}  
**责任人**: {topic_1_owner}  
**截止时间**: {topic_1_deadline}

#### 议题二: {topic_2_title}
**讨论内容**: {topic_2_content}  
**决议**: {topic_2_decision}  
**责任人**: {topic_2_owner}  
**截止时间**: {topic_2_deadline}

#### 议题三: {topic_3_title}
**讨论内容**: {topic_3_content}  
**决议**: {topic_3_decision}  
**责任人**: {topic_3_owner}  
**截止时间**: {topic_3_deadline}

### 3. 其他事项
{other_matters}

## 行动计划

| 序号 | 行动项 | 责任人 | 截止时间 | 状态 |
|------|--------|--------|----------|------|
| 1    | {action_1} | {owner_1} | {deadline_1} | 待开始 |
| 2    | {action_2} | {owner_2} | {deadline_2} | 待开始 |
| 3    | {action_3} | {owner_3} | {deadline_3} | 待开始 |

## 下次会议

**时间**: {next_meeting_date}  
**地点**: {next_meeting_location}  
**主要议题**: {next_meeting_agenda}

## 附件

{attachments}

---

**记录确认**:  
主持人签字: ___________  日期: ___________  
记录人签字: ___________  日期: ___________
""",
                variables={
                    "meeting_title": "会议标题",
                    "meeting_date": str(datetime.now().strftime("%Y年%m月%d日 %H:%M")),
                    "meeting_location": "会议地点",
                    "meeting_host": "会议主持人",
                    "recorder": "记录人",
                    "attendees": "[参会人员列表]",
                    "agenda": "[会议议程]",
                    "opening": "[开场内容]",
                    "topic_1_title": "议题一标题",
                    "topic_1_content": "[议题一讨论内容]",
                    "topic_1_decision": "[议题一决议]",
                    "topic_1_owner": "[责任人]",
                    "topic_1_deadline": "[截止时间]",
                    "topic_2_title": "议题二标题",
                    "topic_2_content": "[议题二讨论内容]",
                    "topic_2_decision": "[议题二决议]",
                    "topic_2_owner": "[责任人]",
                    "topic_2_deadline": "[截止时间]",
                    "topic_3_title": "议题三标题",
                    "topic_3_content": "[议题三讨论内容]",
                    "topic_3_decision": "[议题三决议]",
                    "topic_3_owner": "[责任人]",
                    "topic_3_deadline": "[截止时间]",
                    "other_matters": "[其他事项]",
                    "action_1": "行动项1",
                    "owner_1": "责任人1",
                    "deadline_1": "截止时间1",
                    "action_2": "行动项2",
                    "owner_2": "责任人2",
                    "deadline_2": "截止时间2",
                    "action_3": "行动项3",
                    "owner_3": "责任人3",
                    "deadline_3": "截止时间3",
                    "next_meeting_date": "[下次会议时间]",
                    "next_meeting_location": "[下次会议地点]",
                    "next_meeting_agenda": "[下次会议议题]",
                    "attachments": "[附件列表]"
                }
            )
        ]
        
        for template in builtin_templates:
            self.templates[template.name] = template
            
    def load_custom_templates(self):
        """加载自定义模板"""
        custom_file = self.templates_dir / "custom_templates.json"
        if custom_file.exists():
            try:
                with open(custom_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    for template_data in data:
                        template = DocumentTemplate.from_dict(template_data)
                        self.templates[template.name] = template
            except Exception as e:
                print(f"加载自定义模板失败: {e}")
                
    def save_custom_templates(self):
        """保存自定义模板"""
        custom_templates = [
            template.to_dict() for template in self.templates.values()
            if template.category == "自定义"
        ]
        
        custom_file = self.templates_dir / "custom_templates.json"
        try:
            with open(custom_file, 'w', encoding='utf-8') as f:
                json.dump(custom_templates, f, ensure_ascii=False, indent=2)
        except Exception as e:
            print(f"保存自定义模板失败: {e}")
            
    def get_templates_by_category(self, category: str) -> List[DocumentTemplate]:
        """按类别获取模板"""
        return [template for template in self.templates.values() 
                if template.category == category]
        
    def get_all_categories(self) -> List[str]:
        """获取所有类别"""
        categories = set(template.category for template in self.templates.values())
        return sorted(list(categories))
        
    def add_template(self, template: DocumentTemplate):
        """添加模板"""
        self.templates[template.name] = template
        if template.category == "自定义":
            self.save_custom_templates()
            
    def remove_template(self, name: str):
        """删除模板"""
        if name in self.templates:
            template = self.templates[name]
            del self.templates[name]
            if template.category == "自定义":
                self.save_custom_templates()
                
    def get_template(self, name: str) -> Optional[DocumentTemplate]:
        """获取指定模板"""
        return self.templates.get(name)

class TemplateDialog(QDialog):
    """模板选择对话框"""
    
    template_selected = pyqtSignal(str)  # 生成的文档内容
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.template_manager = TemplateManager()
        self.setup_ui()
        self.load_templates()
        
    def setup_ui(self):
        """设置界面"""
        self.setWindowTitle("文档模板库")
        self.setModal(True)
        self.resize(1000, 700)
        
        layout = QVBoxLayout(self)
        
        # 创建分割器
        splitter = QSplitter(Qt.Orientation.Horizontal)
        
        # 左侧：模板列表
        left_widget = QWidget()
        left_layout = QVBoxLayout(left_widget)
        
        # 类别选择
        category_layout = QHBoxLayout()
        category_layout.addWidget(QLabel("类别:"))
        self.category_combo = QComboBox()
        self.category_combo.currentTextChanged.connect(self.filter_templates)
        category_layout.addWidget(self.category_combo)
        left_layout.addLayout(category_layout)
        
        # 模板列表
        self.template_list = QListWidget()
        self.template_list.currentItemChanged.connect(self.on_template_selected)
        left_layout.addWidget(self.template_list)
        
        # 按钮
        button_layout = QHBoxLayout()
        
        new_template_btn = QPushButton("新建模板")
        new_template_btn.clicked.connect(self.create_new_template)
        button_layout.addWidget(new_template_btn)
        
        edit_template_btn = QPushButton("编辑模板")
        edit_template_btn.clicked.connect(self.edit_template)
        button_layout.addWidget(edit_template_btn)
        
        delete_template_btn = QPushButton("删除模板")
        delete_template_btn.clicked.connect(self.delete_template)
        button_layout.addWidget(delete_template_btn)
        
        left_layout.addLayout(button_layout)
        
        splitter.addWidget(left_widget)
        
        # 右侧：模板预览和参数设置
        right_widget = QWidget()
        right_layout = QVBoxLayout(right_widget)
        
        # 标签页
        self.tab_widget = QTabWidget()
        
        # 预览标签页
        preview_widget = QWidget()
        preview_layout = QVBoxLayout(preview_widget)
        
        preview_layout.addWidget(QLabel("模板预览:"))
        self.preview_text = QTextEdit()
        self.preview_text.setReadOnly(True)
        preview_layout.addWidget(self.preview_text)
        
        self.tab_widget.addTab(preview_widget, "预览")
        
        # 参数设置标签页
        params_widget = QWidget()
        params_layout = QVBoxLayout(params_widget)
        
        params_layout.addWidget(QLabel("模板参数:"))
        self.params_area = QWidget()
        self.params_layout = QVBoxLayout(self.params_area)
        params_layout.addWidget(self.params_area)
        
        params_layout.addStretch()
        self.tab_widget.addTab(params_widget, "参数设置")
        
        right_layout.addWidget(self.tab_widget)
        
        # 使用模板按钮
        use_template_btn = QPushButton("使用此模板")
        use_template_btn.clicked.connect(self.use_template)
        right_layout.addWidget(use_template_btn)
        
        splitter.addWidget(right_widget)
        splitter.setSizes([300, 700])
        
        layout.addWidget(splitter)
        
        # 底部按钮
        bottom_layout = QHBoxLayout()
        
        close_btn = QPushButton("关闭")
        close_btn.clicked.connect(self.reject)
        bottom_layout.addStretch()
        bottom_layout.addWidget(close_btn)
        
        layout.addLayout(bottom_layout)
        
        # 存储参数控件
        self.param_widgets = {}
        
    def load_templates(self):
        """加载模板列表"""
        # 加载类别
        categories = ["所有"] + self.template_manager.get_all_categories()
        self.category_combo.clear()
        self.category_combo.addItems(categories)
        
        # 加载模板列表
        self.filter_templates("所有")
        
    def filter_templates(self, category):
        """按类别过滤模板"""
        self.template_list.clear()
        
        if category == "所有":
            templates = list(self.template_manager.templates.values())
        else:
            templates = self.template_manager.get_templates_by_category(category)
            
        for template in templates:
            item = QListWidgetItem(f"{template.name}\n{template.description}")
            item.setData(Qt.ItemDataRole.UserRole, template.name)
            self.template_list.addItem(item)
            
    def on_template_selected(self, current, previous):
        """模板选择改变"""
        if not current:
            return
            
        template_name = current.data(Qt.ItemDataRole.UserRole)
        template = self.template_manager.get_template(template_name)
        
        if template:
            # 更新预览
            self.preview_text.setPlainText(template.content)
            
            # 更新参数设置
            self.setup_parameters(template)
            
    def setup_parameters(self, template):
        """设置模板参数"""
        # 清除现有参数控件
        for widget in self.param_widgets.values():
            widget.deleteLater()
        self.param_widgets.clear()
        
        # 清除布局
        while self.params_layout.count():
            child = self.params_layout.takeAt(0)
            if child.widget():
                child.widget().deleteLater()
                
        # 添加参数控件
        for param_name, default_value in template.variables.items():
            param_layout = QHBoxLayout()
            
            label = QLabel(f"{param_name}:")
            param_layout.addWidget(label)
            
            if len(str(default_value)) > 50:  # 长文本使用文本编辑器
                param_widget = QTextEdit()
                param_widget.setMaximumHeight(80)
                param_widget.setPlainText(str(default_value))
            else:  # 短文本使用单行编辑器
                param_widget = QLineEdit()
                param_widget.setText(str(default_value))
                
            param_layout.addWidget(param_widget)
            self.params_layout.addLayout(param_layout)
            
            self.param_widgets[param_name] = param_widget
            
    def use_template(self):
        """使用选择的模板"""
        current_item = self.template_list.currentItem()
        if not current_item:
            QMessageBox.warning(self, "提示", "请先选择一个模板")
            return
            
        template_name = current_item.data(Qt.ItemDataRole.UserRole)
        template = self.template_manager.get_template(template_name)
        
        if not template:
            QMessageBox.warning(self, "错误", "模板不存在")
            return
            
        # 获取用户输入的参数值
        param_values = {}
        for param_name, widget in self.param_widgets.items():
            if isinstance(widget, QTextEdit):
                param_values[param_name] = widget.toPlainText()
            else:
                param_values[param_name] = widget.text()
                
        # 替换模板中的变量
        content = template.content
        for param_name, param_value in param_values.items():
            content = content.replace(f"{{{param_name}}}", param_value)
            
        # 发送生成的内容
        self.template_selected.emit(content)
        self.accept()
        
    def create_new_template(self):
        """创建新模板"""
        dialog = TemplateEditorDialog(self)
        if dialog.exec() == QDialog.DialogCode.Accepted:
            template = dialog.get_template()
            if template:
                self.template_manager.add_template(template)
                self.load_templates()
                
    def edit_template(self):
        """编辑模板"""
        current_item = self.template_list.currentItem()
        if not current_item:
            QMessageBox.warning(self, "提示", "请先选择一个模板")
            return
            
        template_name = current_item.data(Qt.ItemDataRole.UserRole)
        template = self.template_manager.get_template(template_name)
        
        if template.category != "自定义":
            QMessageBox.warning(self, "提示", "只能编辑自定义模板")
            return
            
        dialog = TemplateEditorDialog(self, template)
        if dialog.exec() == QDialog.DialogCode.Accepted:
            updated_template = dialog.get_template()
            if updated_template:
                self.template_manager.add_template(updated_template)
                self.load_templates()
                
    def delete_template(self):
        """删除模板"""
        current_item = self.template_list.currentItem()
        if not current_item:
            QMessageBox.warning(self, "提示", "请先选择一个模板")
            return
            
        template_name = current_item.data(Qt.ItemDataRole.UserRole)
        template = self.template_manager.get_template(template_name)
        
        if template.category != "自定义":
            QMessageBox.warning(self, "提示", "只能删除自定义模板")
            return
            
        reply = QMessageBox.question(
            self, "确认删除",
            f"确定要删除模板 '{template_name}' 吗？",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )
        
        if reply == QMessageBox.StandardButton.Yes:
            self.template_manager.remove_template(template_name)
            self.load_templates()

class TemplateEditorDialog(QDialog):
    """模板编辑对话框"""
    
    def __init__(self, parent=None, template=None):
        super().__init__(parent)
        self.template = template
        self.setup_ui()
        if template:
            self.load_template()
            
    def setup_ui(self):
        """设置界面"""
        self.setWindowTitle("模板编辑器")
        self.setModal(True)
        self.resize(800, 600)
        
        layout = QVBoxLayout(self)
        
        # 基本信息
        info_group = QGroupBox("基本信息")
        info_layout = QVBoxLayout(info_group)
        
        name_layout = QHBoxLayout()
        name_layout.addWidget(QLabel("模板名称:"))
        self.name_edit = QLineEdit()
        name_layout.addWidget(self.name_edit)
        info_layout.addLayout(name_layout)
        
        desc_layout = QHBoxLayout()
        desc_layout.addWidget(QLabel("描述:"))
        self.desc_edit = QLineEdit()
        desc_layout.addWidget(self.desc_edit)
        info_layout.addLayout(desc_layout)
        
        layout.addWidget(info_group)
        
        # 模板内容
        content_group = QGroupBox("模板内容")
        content_layout = QVBoxLayout(content_group)
        
        self.content_edit = QPlainTextEdit()
        self.content_edit.setPlaceholderText(
            "在此输入模板内容，使用 {变量名} 来定义可替换的变量。\n\n"
            "例如：\n"
            "# {标题}\n\n"
            "作者：{作者}\n"
            "日期：{日期}\n\n"
            "{正文内容}"
        )
        content_layout.addWidget(self.content_edit)
        
        layout.addWidget(content_group)
        
        # 按钮
        button_layout = QHBoxLayout()
        
        save_btn = QPushButton("保存")
        save_btn.clicked.connect(self.accept)
        
        cancel_btn = QPushButton("取消")
        cancel_btn.clicked.connect(self.reject)
        
        button_layout.addStretch()
        button_layout.addWidget(save_btn)
        button_layout.addWidget(cancel_btn)
        
        layout.addLayout(button_layout)
        
    def load_template(self):
        """加载模板数据"""
        self.name_edit.setText(self.template.name)
        self.desc_edit.setText(self.template.description)
        self.content_edit.setPlainText(self.template.content)
        
    def get_template(self):
        """获取编辑后的模板"""
        name = self.name_edit.text().strip()
        description = self.desc_edit.text().strip()
        content = self.content_edit.toPlainText().strip()
        
        if not name or not content:
            QMessageBox.warning(self, "错误", "模板名称和内容不能为空")
            return None
            
        # 自动提取变量
        import re
        variables = {}
        for match in re.finditer(r'\{([^}]+)\}', content):
            var_name = match.group(1)
            if var_name not in variables:
                variables[var_name] = f"[{var_name}]"
                
        return DocumentTemplate(
            name=name,
            category="自定义",
            description=description,
            content=content,
            variables=variables
        )