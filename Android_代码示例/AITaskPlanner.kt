package com.automate.mobile.core.ai

import android.content.Context
import android.util.Log
import com.automate.mobile.data.model.*
import com.automate.mobile.data.repository.SettingsRepository
import com.automate.mobile.network.OpenAIClient
import com.automate.mobile.network.model.ChatCompletionRequest
import com.automate.mobile.network.model.ChatMessage
import com.automate.mobile.network.model.ChatCompletionResponse
import com.google.gson.Gson
import com.google.gson.reflect.TypeToken
import dagger.hilt.android.qualifiers.ApplicationContext
import kotlinx.coroutines.flow.first
import java.util.UUID
import javax.inject.Inject
import javax.inject.Singleton

@Singleton
class AITaskPlanner @Inject constructor(
    @ApplicationContext private val context: Context,
    private val openAIClient: OpenAIClient,
    private val settingsRepository: SettingsRepository,
    private val gson: Gson
) {
    
    companion object {
        private const val TAG = "AITaskPlanner"
        private const val SYSTEM_PROMPT = """
你是一个专业的移动端自动化任务规划专家。你的职责是根据用户的自然语言指令和当前屏幕信息，规划出精确可执行的移动端操作步骤序列。

## 核心能力
1. 理解用户的自然语言指令
2. 分析当前屏幕的UI元素和结构
3. 规划合理的操作步骤序列
4. 处理异常情况和错误恢复

## 支持的操作类型
- CLICK: 点击操作（需要指定目标元素或坐标）
- INPUT: 文本输入（需要指定输入内容）
- SWIPE: 滑动操作（需要指定方向和距离）
- WAIT: 等待操作（需要指定等待时间）
- SCROLL: 滚动操作（需要指定方向）
- BACK: 返回操作
- HOME: 主页操作
- APP_SWITCH: 切换应用（需要指定目标应用）
- SCREENSHOT: 截图操作

## 移动端特殊考虑
1. 屏幕尺寸限制：考虑不同设备的屏幕尺寸差异
2. 手势操作：优化点击和滑动的精确度
3. 应用切换：处理多任务和应用间跳转
4. 权限管理：考虑安卓权限限制
5. 网络状态：处理网络相关的延迟和错误

## 输出格式要求
请以JSON格式返回任务计划，包含以下字段：
- reasoning: 详细的推理过程
- taskPlan: 任务计划对象
- confidence: 置信度 (0.0-1.0)
- alternatives: 可选的替代方案

任务计划对象包含：
- id: 唯一标识符
- title: 任务标题
- description: 任务描述
- steps: 步骤列表
- estimatedDuration: 预计执行时间（毫秒）
- targetApp: 目标应用包名
- category: 任务分类
- priority: 任务优先级

## 示例响应
```json
{
  "reasoning": "用户想要在微信朋友圈给好友点赞。我需要：1. 打开微信 2. 进入朋友圈 3. 识别好友动态 4. 点击点赞按钮。考虑到需要避免过于频繁的点赞以免被限制。",
  "taskPlan": {
    "id": "task_123",
    "title": "微信朋友圈点赞",
    "description": "自动在微信朋友圈给好友点赞",
    "steps": [
      {
        "id": "step_1",
        "type": "APP_SWITCH",
        "description": "打开微信应用",
        "target": "com.tencent.mm",
        "delayAfter": 2000
      },
      {
        "id": "step_2",
        "type": "CLICK",
        "description": "点击发现标签",
        "target": "发现",
        "delayAfter": 1000
      }
    ],
    "estimatedDuration": 30000,
    "targetApp": "com.tencent.mm",
    "category": "SOCIAL",
    "priority": "NORMAL"
  },
  "confidence": 0.9,
  "alternatives": []
}
```

## 安全考虑
1. 不要执行可能造成数据丢失的操作
2. 避免在银行、支付等敏感应用中执行自动化
3. 对于涉及金钱交易的操作，应该要求用户确认
4. 保护用户隐私，不要记录敏感信息

请根据用户指令和屏幕信息，规划最合适的任务执行方案。
"""
    }
    
    /**
     * 根据用户指令和屏幕信息规划任务
     */
    suspend fun planTask(
        userInput: String,
        screenAnalysis: ScreenAnalysis?,
        context: String? = null
    ): Result<AITaskPlanResponse> {
        return try {
            Log.d(TAG, "开始规划任务: $userInput")
            
            val settings = settingsRepository.getSettings().first()
            val prompt = buildPrompt(userInput, screenAnalysis, context)
            
            val response = openAIClient.chatCompletion(
                request = ChatCompletionRequest(
                    model = settings.aiModel,
                    messages = listOf(
                        ChatMessage(role = "system", content = SYSTEM_PROMPT),
                        ChatMessage(role = "user", content = prompt)
                    ),
                    temperature = 0.7,
                    maxTokens = 2000
                )
            )
            
            val taskPlanResponse = parseResponse(response)
            Log.d(TAG, "任务规划成功: ${taskPlanResponse.taskPlan.title}")
            
            Result.success(taskPlanResponse)
            
        } catch (e: Exception) {
            Log.e(TAG, "任务规划失败", e)
            Result.failure(e)
        }
    }
    
    /**
     * 构建提示词
     */
    private fun buildPrompt(
        userInput: String,
        screenAnalysis: ScreenAnalysis?,
        context: String?
    ): String {
        val promptBuilder = StringBuilder()
        
        // 用户指令
        promptBuilder.append("## 用户指令\n")
        promptBuilder.append("$userInput\n\n")
        
        // 屏幕信息
        if (screenAnalysis != null) {
            promptBuilder.append("## 当前屏幕信息\n")
            promptBuilder.append("应用: ${screenAnalysis.currentApp}\n")
            promptBuilder.append("屏幕尺寸: ${screenAnalysis.screenSize.first}x${screenAnalysis.screenSize.second}\n")
            promptBuilder.append("分析时间: ${screenAnalysis.timestamp}\n\n")
            
            // 可交互元素
            val interactableElements = screenAnalysis.uiElements.filter { it.isInteractable }
            if (interactableElements.isNotEmpty()) {
                promptBuilder.append("### 可交互元素\n")
                interactableElements.take(20).forEach { element ->
                    promptBuilder.append("- ${element.className}")
                    if (element.text.isNotBlank()) {
                        promptBuilder.append(" 文本: '${element.text}'")
                    }
                    if (element.contentDescription.isNotBlank()) {
                        promptBuilder.append(" 描述: '${element.contentDescription}'")
                    }
                    promptBuilder.append(" 位置: (${element.bounds.left},${element.bounds.top})")
                    promptBuilder.append(" 大小: ${element.bounds.width()}x${element.bounds.height()}")
                    
                    val capabilities = mutableListOf<String>()
                    if (element.isClickable) capabilities.add("可点击")
                    if (element.isScrollable) capabilities.add("可滚动")
                    if (element.isEditable) capabilities.add("可编辑")
                    if (element.isCheckable) capabilities.add("可选择")
                    if (capabilities.isNotEmpty()) {
                        promptBuilder.append(" 能力: ${capabilities.joinToString(", ")}")
                    }
                    promptBuilder.append("\n")
                }
                promptBuilder.append("\n")
            }
            
            // ML分析结果
            screenAnalysis.mlAnalysis?.let { mlAnalysis ->
                promptBuilder.append("### ML分析结果\n")
                
                // 检测到的对象
                if (mlAnalysis.detectedObjects.isNotEmpty()) {
                    promptBuilder.append("检测到的对象:\n")
                    mlAnalysis.detectedObjects.forEach { obj ->
                        promptBuilder.append("- ${obj.className} (置信度: ${obj.confidence})")
                        promptBuilder.append(" 位置: (${obj.bounds.left},${obj.bounds.top})")
                        promptBuilder.append(" 大小: ${obj.bounds.width()}x${obj.bounds.height()}\n")
                    }
                }
                
                // 提取的文本
                if (mlAnalysis.extractedText.isNotEmpty()) {
                    promptBuilder.append("提取的文本:\n")
                    mlAnalysis.extractedText.forEach { textElement ->
                        promptBuilder.append("- '${textElement.text}' (置信度: ${textElement.confidence})")
                        promptBuilder.append(" 位置: (${textElement.bounds.left},${textElement.bounds.top})\n")
                    }
                }
                promptBuilder.append("\n")
            }
        }
        
        // 上下文信息
        if (context != null) {
            promptBuilder.append("## 上下文信息\n")
            promptBuilder.append("$context\n\n")
        }
        
        // 设备信息
        promptBuilder.append("## 设备信息\n")
        promptBuilder.append("系统: Android\n")
        promptBuilder.append("语言: 中文\n\n")
        
        promptBuilder.append("请根据以上信息，规划详细的任务执行步骤。")
        
        return promptBuilder.toString()
    }
    
    /**
     * 解析AI响应
     */
    private fun parseResponse(response: ChatCompletionResponse): AITaskPlanResponse {
        val content = response.choices.firstOrNull()?.message?.content
            ?: throw IllegalStateException("AI响应为空")
        
        Log.d(TAG, "AI响应内容: $content")
        
        // 尝试解析JSON响应
        return try {
            val jsonResponse = gson.fromJson(content, AITaskPlanResponse::class.java)
            validateTaskPlan(jsonResponse.taskPlan)
            jsonResponse
        } catch (e: Exception) {
            Log.w(TAG, "JSON解析失败，尝试提取任务信息", e)
            // 如果JSON解析失败，尝试从文本中提取任务信息
            extractTaskFromText(content)
        }
    }
    
    /**
     * 验证任务计划
     */
    private fun validateTaskPlan(taskPlan: TaskPlan) {
        require(taskPlan.steps.isNotEmpty()) { "任务步骤不能为空" }
        require(taskPlan.title.isNotBlank()) { "任务标题不能为空" }
        require(taskPlan.estimatedDuration > 0) { "预计执行时间必须大于0" }
        
        // 验证步骤
        taskPlan.steps.forEach { step ->
            require(step.type in TaskStepType.values()) { "无效的步骤类型: ${step.type}" }
            require(step.description.isNotBlank()) { "步骤描述不能为空" }
            
            // 根据步骤类型验证必要参数
            when (step.type) {
                TaskStepType.CLICK -> {
                    require(step.target.isNotBlank() || step.coordinates != null) {
                        "点击操作必须指定目标或坐标"
                    }
                }
                TaskStepType.INPUT -> {
                    require(step.text.isNotBlank()) { "输入操作必须指定文本内容" }
                }
                TaskStepType.SWIPE -> {
                    require(step.direction != null) { "滑动操作必须指定方向" }
                }
                TaskStepType.WAIT -> {
                    require(step.duration > 0) { "等待操作必须指定持续时间" }
                }
                TaskStepType.APP_SWITCH -> {
                    require(step.target.isNotBlank()) { "切换应用操作必须指定目标应用" }
                }
                else -> { /* 其他类型暂不验证 */ }
            }
        }
    }
    
    /**
     * 从文本中提取任务信息（备用方案）
     */
    private fun extractTaskFromText(content: String): AITaskPlanResponse {
        // 创建一个基本的任务计划
        val taskId = UUID.randomUUID().toString()
        val basicTaskPlan = TaskPlan(
            id = taskId,
            title = "基于文本的任务",
            description = "根据AI回复创建的基本任务",
            steps = listOf(
                TaskStep(
                    id = UUID.randomUUID().toString(),
                    type = TaskStepType.WAIT,
                    description = "等待用户进一步指令",
                    duration = 1000,
                    delayAfter = 0
                )
            ),
            estimatedDuration = 5000,
            targetApp = "",
            category = TaskCategory.GENERAL,
            priority = TaskPriority.NORMAL
        )
        
        return AITaskPlanResponse(
            reasoning = "无法解析结构化响应，创建基本任务计划。原始回复：$content",
            taskPlan = basicTaskPlan,
            confidence = 0.3f,
            alternatives = emptyList()
        )
    }
    
    /**
     * 优化任务计划
     */
    suspend fun optimizeTaskPlan(
        originalPlan: TaskPlan,
        executionHistory: List<TaskExecutionResult>
    ): Result<TaskPlan> {
        return try {
            Log.d(TAG, "开始优化任务计划: ${originalPlan.title}")
            
            // 分析历史执行结果
            val failedSteps = executionHistory.flatMap { result ->
                result.stepResults.filter { !it.success }
            }
            
            if (failedSteps.isEmpty()) {
                Log.d(TAG, "无需优化，任务计划执行良好")
                return Result.success(originalPlan)
            }
            
            // 构建优化提示
            val optimizationPrompt = buildOptimizationPrompt(originalPlan, failedSteps)
            val settings = settingsRepository.getSettings().first()
            
            val response = openAIClient.chatCompletion(
                request = ChatCompletionRequest(
                    model = settings.aiModel,
                    messages = listOf(
                        ChatMessage(role = "system", content = SYSTEM_PROMPT),
                        ChatMessage(role = "user", content = optimizationPrompt)
                    ),
                    temperature = 0.5,
                    maxTokens = 1500
                )
            )
            
            val optimizedResponse = parseResponse(response)
            Log.d(TAG, "任务计划优化成功")
            
            Result.success(optimizedResponse.taskPlan)
            
        } catch (e: Exception) {
            Log.e(TAG, "任务计划优化失败", e)
            Result.failure(e)
        }
    }
    
    /**
     * 构建优化提示
     */
    private fun buildOptimizationPrompt(
        originalPlan: TaskPlan,
        failedSteps: List<StepResult>
    ): String {
        val promptBuilder = StringBuilder()
        
        promptBuilder.append("## 任务优化请求\n")
        promptBuilder.append("请优化以下任务计划，重点解决执行过程中遇到的问题。\n\n")
        
        promptBuilder.append("### 原始任务计划\n")
        promptBuilder.append("标题: ${originalPlan.title}\n")
        promptBuilder.append("描述: ${originalPlan.description}\n")
        promptBuilder.append("步骤数量: ${originalPlan.steps.size}\n\n")
        
        promptBuilder.append("### 执行问题\n")
        failedSteps.forEach { step ->
            promptBuilder.append("- 步骤ID: ${step.stepId}\n")
            promptBuilder.append("  失败原因: ${step.message}\n")
            promptBuilder.append("  时间: ${step.timestamp}\n")
        }
        
        promptBuilder.append("\n### 优化要求\n")
        promptBuilder.append("1. 提高步骤的成功率\n")
        promptBuilder.append("2. 增加必要的等待时间\n")
        promptBuilder.append("3. 添加错误处理机制\n")
        promptBuilder.append("4. 优化元素定位方式\n")
        promptBuilder.append("5. 考虑网络延迟和界面加载时间\n\n")
        
        promptBuilder.append("请返回优化后的任务计划。")
        
        return promptBuilder.toString()
    }
    
    /**
     * 生成任务模板
     */
    suspend fun generateTaskTemplate(
        category: TaskCategory,
        targetApp: String? = null
    ): Result<List<TaskPlan>> {
        return try {
            Log.d(TAG, "生成任务模板，分类: $category, 目标应用: $targetApp")
            
            val templatePrompt = buildTemplatePrompt(category, targetApp)
            val settings = settingsRepository.getSettings().first()
            
            val response = openAIClient.chatCompletion(
                request = ChatCompletionRequest(
                    model = settings.aiModel,
                    messages = listOf(
                        ChatMessage(role = "system", content = SYSTEM_PROMPT),
                        ChatMessage(role = "user", content = templatePrompt)
                    ),
                    temperature = 0.8,
                    maxTokens = 3000
                )
            )
            
            val templates = parseTemplateResponse(response)
            Log.d(TAG, "任务模板生成成功，数量: ${templates.size}")
            
            Result.success(templates)
            
        } catch (e: Exception) {
            Log.e(TAG, "任务模板生成失败", e)
            Result.failure(e)
        }
    }
    
    /**
     * 构建模板生成提示
     */
    private fun buildTemplatePrompt(category: TaskCategory, targetApp: String?): String {
        val promptBuilder = StringBuilder()
        
        promptBuilder.append("## 任务模板生成请求\n")
        promptBuilder.append("请为以下分类生成常用的任务模板。\n\n")
        
        promptBuilder.append("### 任务分类\n")
        promptBuilder.append("分类: ${category.name}\n")
        
        if (targetApp != null) {
            promptBuilder.append("目标应用: $targetApp\n")
        }
        
        promptBuilder.append("\n### 生成要求\n")
        promptBuilder.append("1. 生成3-5个常用任务模板\n")
        promptBuilder.append("2. 每个模板包含详细的步骤\n")
        promptBuilder.append("3. 考虑中国用户的使用习惯\n")
        promptBuilder.append("4. 步骤要具体可执行\n")
        promptBuilder.append("5. 包含适当的等待和错误处理\n\n")
        
        // 根据分类提供具体建议
        when (category) {
            TaskCategory.SOCIAL -> {
                promptBuilder.append("### 社交应用常见任务\n")
                promptBuilder.append("- 朋友圈点赞\n")
                promptBuilder.append("- 群消息回复\n")
                promptBuilder.append("- 好友申请处理\n")
                promptBuilder.append("- 动态发布\n")
            }
            TaskCategory.SHOPPING -> {
                promptBuilder.append("### 购物应用常见任务\n")
                promptBuilder.append("- 商品价格监控\n")
                promptBuilder.append("- 优惠券领取\n")
                promptBuilder.append("- 购物车管理\n")
                promptBuilder.append("- 订单查询\n")
            }
            TaskCategory.PRODUCTIVITY -> {
                promptBuilder.append("### 效率应用常见任务\n")
                promptBuilder.append("- 邮件处理\n")
                promptBuilder.append("- 日程管理\n")
                promptBuilder.append("- 文档整理\n")
                promptBuilder.append("- 数据备份\n")
            }
            else -> {
                promptBuilder.append("### 通用任务\n")
                promptBuilder.append("- 应用启动\n")
                promptBuilder.append("- 设置调整\n")
                promptBuilder.append("- 数据同步\n")
            }
        }
        
        promptBuilder.append("\n请返回JSON格式的任务模板列表。")
        
        return promptBuilder.toString()
    }
    
    /**
     * 解析模板响应
     */
    private fun parseTemplateResponse(response: ChatCompletionResponse): List<TaskPlan> {
        val content = response.choices.firstOrNull()?.message?.content
            ?: throw IllegalStateException("AI响应为空")
        
        return try {
            val type = object : TypeToken<List<TaskPlan>>() {}.type
            val templates: List<TaskPlan> = gson.fromJson(content, type)
            templates.forEach { validateTaskPlan(it) }
            templates
        } catch (e: Exception) {
            Log.w(TAG, "模板解析失败", e)
            // 返回默认模板
            listOf(createDefaultTemplate())
        }
    }
    
    /**
     * 创建默认模板
     */
    private fun createDefaultTemplate(): TaskPlan {
        return TaskPlan(
            id = UUID.randomUUID().toString(),
            title = "基础任务模板",
            description = "一个基础的任务模板",
            steps = listOf(
                TaskStep(
                    id = UUID.randomUUID().toString(),
                    type = TaskStepType.WAIT,
                    description = "等待用户操作",
                    duration = 1000,
                    delayAfter = 0
                )
            ),
            estimatedDuration = 5000,
            targetApp = "",
            category = TaskCategory.GENERAL,
            priority = TaskPriority.NORMAL
        )
    }
}