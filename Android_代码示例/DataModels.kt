package com.automate.mobile.data.model

import android.graphics.Rect
import android.os.Parcelable
import androidx.room.Entity
import androidx.room.PrimaryKey
import androidx.room.TypeConverters
import com.automate.mobile.data.converter.DateConverter
import com.automate.mobile.data.converter.RectConverter
import kotlinx.parcelize.Parcelize
import java.util.Date

/**
 * UI元素数据模型
 */
@Parcelize
data class UIElement(
    val id: String,
    val className: String,
    val text: String,
    val contentDescription: String,
    val bounds: Rect,
    val isClickable: Boolean = false,
    val isScrollable: Boolean = false,
    val isEditable: Boolean = false,
    val isCheckable: Boolean = false,
    val isChecked: Boolean = false,
    val isEnabled: Boolean = true,
    val isPassword: Boolean = false,
    val viewIdResourceName: String = "",
    val packageName: String = "",
    val isInteractable: Boolean = false
) : Parcelable

/**
 * 屏幕分析结果
 */
@Parcelize
data class ScreenAnalysis(
    val timestamp: Long,
    val uiElements: List<UIElement>,
    val screenSize: Pair<Int, Int>,
    val currentApp: String,
    val mlAnalysis: MLAnalysisResult? = null
) : Parcelable

/**
 * ML分析结果
 */
@Parcelize
data class MLAnalysisResult(
    val detectedObjects: List<DetectedObject>,
    val extractedText: List<TextElement>,
    val screenStructure: ScreenStructure
) : Parcelable

/**
 * 检测到的对象
 */
@Parcelize
data class DetectedObject(
    val id: String,
    val className: String,
    val confidence: Float,
    val bounds: Rect
) : Parcelable

/**
 * 文本元素
 */
@Parcelize
data class TextElement(
    val text: String,
    val bounds: Rect,
    val confidence: Float = 1.0f
) : Parcelable

/**
 * 屏幕结构
 */
@Parcelize
data class ScreenStructure(
    val layout: String,
    val navigationElements: List<UIElement>,
    val contentElements: List<UIElement>,
    val inputElements: List<UIElement>
) : Parcelable

/**
 * 任务状态枚举
 */
enum class TaskStatus {
    PENDING,     // 等待执行
    RUNNING,     // 执行中
    COMPLETED,   // 已完成
    FAILED,      // 失败
    CANCELLED    // 已取消
}

/**
 * 任务步骤类型
 */
enum class TaskStepType {
    CLICK,       // 点击
    INPUT,       // 输入
    SWIPE,       // 滑动
    WAIT,        // 等待
    SCROLL,      // 滚动
    BACK,        // 返回
    HOME,        // 主页
    APP_SWITCH,  // 切换应用
    SCREENSHOT   // 截图
}

/**
 * 任务步骤
 */
@Parcelize
data class TaskStep(
    val id: String,
    val type: TaskStepType,
    val description: String,
    val target: String = "",           // 目标元素描述
    val coordinates: Pair<Int, Int>? = null,  // 坐标
    val text: String = "",             // 输入文本
    val direction: SwipeDirection? = null,    // 滑动方向
    val distance: Int = 0,             // 滑动距离
    val duration: Long = 0,            // 持续时间
    val delayAfter: Long = 1000,       // 执行后延迟
    val retryCount: Int = 3,           // 重试次数
    val isOptional: Boolean = false     // 是否可选
) : Parcelable

/**
 * 滑动方向
 */
enum class SwipeDirection {
    UP, DOWN, LEFT, RIGHT
}

/**
 * 任务计划
 */
@Parcelize
data class TaskPlan(
    val id: String,
    val title: String,
    val description: String,
    val steps: List<TaskStep>,
    val estimatedDuration: Long,
    val targetApp: String = "",
    val category: TaskCategory = TaskCategory.GENERAL,
    val priority: TaskPriority = TaskPriority.NORMAL,
    val createdAt: Long = System.currentTimeMillis()
) : Parcelable

/**
 * 任务分类
 */
enum class TaskCategory {
    GENERAL,     // 通用
    SOCIAL,      // 社交
    SHOPPING,    // 购物
    PRODUCTIVITY, // 效率
    ENTERTAINMENT // 娱乐
}

/**
 * 任务优先级
 */
enum class TaskPriority {
    LOW, NORMAL, HIGH, URGENT
}

/**
 * 任务执行结果
 */
@Parcelize
data class TaskExecutionResult(
    val taskId: String,
    val status: TaskStatus,
    val startTime: Long,
    val endTime: Long,
    val stepResults: List<StepResult>,
    val errorMessage: String? = null,
    val screenshots: List<String> = emptyList()
) : Parcelable

/**
 * 步骤执行结果
 */
@Parcelize
data class StepResult(
    val stepId: String,
    val success: Boolean,
    val message: String,
    val timestamp: Long = System.currentTimeMillis(),
    val screenshotPath: String? = null
) : Parcelable

/**
 * 快速操作
 */
@Parcelize
data class QuickAction(
    val id: String,
    val title: String,
    val description: String,
    val icon: String,
    val taskPlan: TaskPlan,
    val isEnabled: Boolean = true,
    val usageCount: Int = 0,
    val category: TaskCategory = TaskCategory.GENERAL
) : Parcelable

/**
 * 今日统计
 */
@Parcelize
data class TodayStats(
    val tasksExecuted: Int,
    val timeSaved: Int,        // 分钟
    val successRate: Float,    // 百分比
    val activeApps: String
) : Parcelable

/**
 * 聊天消息
 */
@Entity(tableName = "chat_messages")
@TypeConverters(DateConverter::class)
data class ChatMessage(
    @PrimaryKey val id: String,
    val role: MessageRole,
    val content: String,
    val timestamp: Date = Date(),
    val sessionId: String = "",
    val isFromUser: Boolean = role == MessageRole.USER
)

/**
 * 消息角色
 */
enum class MessageRole {
    USER, ASSISTANT, SYSTEM
}

/**
 * 自动化任务实体
 */
@Entity(tableName = "automation_tasks")
@TypeConverters(DateConverter::class, RectConverter::class)
data class AutomationTask(
    @PrimaryKey val id: String,
    val title: String,
    val description: String,
    val category: TaskCategory,
    val priority: TaskPriority,
    val status: TaskStatus,
    val targetApp: String,
    val isScheduled: Boolean = false,
    val scheduleTime: Date? = null,
    val isRecurring: Boolean = false,
    val recurringPattern: String? = null,
    val createdAt: Date = Date(),
    val updatedAt: Date = Date(),
    val executionCount: Int = 0,
    val lastExecutionTime: Date? = null,
    val estimatedDuration: Long = 0,
    val isEnabled: Boolean = true
)

/**
 * 应用信息
 */
@Parcelize
data class AppInfo(
    val packageName: String,
    val appName: String,
    val versionName: String,
    val versionCode: Int,
    val isSystemApp: Boolean = false,
    val isEnabled: Boolean = true,
    val supportLevel: AppSupportLevel = AppSupportLevel.UNKNOWN
) : Parcelable

/**
 * 应用支持级别
 */
enum class AppSupportLevel {
    FULL,        // 完全支持
    PARTIAL,     // 部分支持
    LIMITED,     // 有限支持
    UNKNOWN      // 未知
}

/**
 * 用户设置
 */
@Parcelize
data class UserSettings(
    val aiModel: String = "gpt-4o-mini",
    val apiKey: String = "",
    val baseUrl: String = "https://api.openai.com/v1",
    val executionSpeed: ExecutionSpeed = ExecutionSpeed.MEDIUM,
    val retryCount: Int = 3,
    val operationDelay: Long = 2000,
    val isDarkMode: Boolean = false,
    val isVibrationEnabled: Boolean = true,
    val isSoundEnabled: Boolean = true,
    val language: String = "zh-CN",
    val isDataCollectionEnabled: Boolean = true,
    val isSecurityModeEnabled: Boolean = true,
    val blacklistedApps: List<String> = emptyList()
) : Parcelable

/**
 * 执行速度
 */
enum class ExecutionSpeed {
    SLOW, MEDIUM, FAST
}

/**
 * API响应
 */
@Parcelize
data class ApiResponse<T>(
    val success: Boolean,
    val data: T? = null,
    val error: String? = null,
    val timestamp: Long = System.currentTimeMillis()
) : Parcelable

/**
 * AI任务规划响应
 */
@Parcelize
data class AITaskPlanResponse(
    val reasoning: String,
    val taskPlan: TaskPlan,
    val confidence: Float,
    val alternatives: List<TaskPlan> = emptyList()
) : Parcelable

/**
 * 语音识别结果
 */
@Parcelize
data class VoiceRecognitionResult(
    val text: String,
    val confidence: Float,
    val language: String,
    val isComplete: Boolean = true
) : Parcelable

/**
 * 应用使用统计
 */
@Parcelize
data class AppUsageStats(
    val packageName: String,
    val appName: String,
    val totalTime: Long,      // 总使用时间(毫秒)
    val launchCount: Int,     // 启动次数
    val automationCount: Int, // 自动化次数
    val lastUsed: Long        // 最后使用时间
) : Parcelable

/**
 * 错误信息
 */
@Parcelize
data class ErrorInfo(
    val code: String,
    val message: String,
    val details: String? = null,
    val timestamp: Long = System.currentTimeMillis(),
    val isRecoverable: Boolean = false
) : Parcelable