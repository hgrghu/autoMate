package com.automate.mobile.service

import android.accessibilityservice.AccessibilityService
import android.accessibilityservice.GestureDescription
import android.content.Intent
import android.graphics.Path
import android.os.Bundle
import android.util.Log
import android.view.accessibility.AccessibilityEvent
import android.view.accessibility.AccessibilityNodeInfo
import androidx.localbroadcastmanager.content.LocalBroadcastManager
import com.automate.mobile.data.model.ScreenAnalysis
import com.automate.mobile.data.model.UIElement
import com.automate.mobile.core.vision.VisionEngine
import dagger.hilt.android.AndroidEntryPoint
import kotlinx.coroutines.*
import javax.inject.Inject

@AndroidEntryPoint
class AutoMateAccessibilityService : AccessibilityService() {
    
    @Inject
    lateinit var visionEngine: VisionEngine
    
    private val serviceScope = CoroutineScope(Dispatchers.Main + SupervisorJob())
    private var currentScreenAnalysis: ScreenAnalysis? = null
    private var isTaskRunning = false
    
    companion object {
        private const val TAG = "AutoMateAccessibility"
        const val ACTION_SCREEN_CHANGED = "com.automate.mobile.SCREEN_CHANGED"
        const val ACTION_TASK_RESULT = "com.automate.mobile.TASK_RESULT"
        
        var instance: AutoMateAccessibilityService? = null
            private set
    }
    
    override fun onCreate() {
        super.onCreate()
        instance = this
        Log.d(TAG, "AutoMate 无障碍服务已启动")
    }
    
    override fun onDestroy() {
        super.onDestroy()
        instance = null
        serviceScope.cancel()
        Log.d(TAG, "AutoMate 无障碍服务已停止")
    }
    
    override fun onAccessibilityEvent(event: AccessibilityEvent?) {
        event?.let { handleAccessibilityEvent(it) }
    }
    
    override fun onInterrupt() {
        Log.d(TAG, "无障碍服务中断")
        stopCurrentTask()
    }
    
    private fun handleAccessibilityEvent(event: AccessibilityEvent) {
        when (event.eventType) {
            AccessibilityEvent.TYPE_WINDOW_STATE_CHANGED -> {
                updateCurrentApp(event)
                analyzeCurrentScreen()
            }
            AccessibilityEvent.TYPE_WINDOW_CONTENT_CHANGED -> {
                if (!isTaskRunning) {
                    analyzeCurrentScreen()
                }
            }
            AccessibilityEvent.TYPE_VIEW_CLICKED -> {
                logUserAction("点击", event)
            }
            AccessibilityEvent.TYPE_VIEW_LONG_CLICKED -> {
                logUserAction("长按", event)
            }
        }
    }
    
    private fun updateCurrentApp(event: AccessibilityEvent) {
        event.packageName?.let { packageName ->
            Log.d(TAG, "当前应用: $packageName")
            broadcastScreenChange(packageName.toString())
        }
    }
    
    private fun analyzeCurrentScreen() {
        serviceScope.launch {
            try {
                val rootNode = rootInActiveWindow
                if (rootNode != null) {
                    val uiElements = extractUIElements(rootNode)
                    currentScreenAnalysis = ScreenAnalysis(
                        timestamp = System.currentTimeMillis(),
                        uiElements = uiElements,
                        screenSize = getScreenSize(),
                        currentApp = rootNode.packageName?.toString() ?: "未知应用"
                    )
                    
                    // 可选：使用 ML 模型进一步分析
                    // val analysisResult = visionEngine.analyzeScreen(takeScreenshot())
                    // currentScreenAnalysis = currentScreenAnalysis?.copy(mlAnalysis = analysisResult)
                }
            } catch (e: Exception) {
                Log.e(TAG, "屏幕分析失败", e)
            }
        }
    }
    
    private fun extractUIElements(rootNode: AccessibilityNodeInfo): List<UIElement> {
        val elements = mutableListOf<UIElement>()
        extractUIElementsRecursive(rootNode, elements)
        return elements.filter { it.isInteractable }
    }
    
    private fun extractUIElementsRecursive(
        node: AccessibilityNodeInfo,
        elements: MutableList<UIElement>
    ) {
        // 获取节点边界
        val bounds = android.graphics.Rect()
        node.getBoundsInScreen(bounds)
        
        if (bounds.width() > 0 && bounds.height() > 0) {
            val element = UIElement(
                id = node.hashCode().toString(),
                className = node.className?.toString() ?: "",
                text = node.text?.toString() ?: "",
                contentDescription = node.contentDescription?.toString() ?: "",
                bounds = bounds,
                isClickable = node.isClickable,
                isScrollable = node.isScrollable,
                isEditable = node.isEditable,
                isCheckable = node.isCheckable,
                isChecked = node.isChecked,
                isEnabled = node.isEnabled,
                isPassword = node.isPassword,
                viewIdResourceName = node.viewIdResourceName ?: "",
                packageName = node.packageName?.toString() ?: "",
                isInteractable = node.isClickable || node.isScrollable || node.isEditable || node.isCheckable
            )
            elements.add(element)
        }
        
        // 递归处理子节点
        for (i in 0 until node.childCount) {
            node.getChild(i)?.let { child ->
                extractUIElementsRecursive(child, elements)
            }
        }
    }
    
    /**
     * 执行点击操作
     */
    fun performClick(x: Int, y: Int, callback: (Boolean) -> Unit = {}) {
        val path = Path().apply {
            moveTo(x.toFloat(), y.toFloat())
        }
        
        val gestureBuilder = GestureDescription.Builder()
        gestureBuilder.addStroke(GestureDescription.StrokeDescription(path, 0, 100))
        
        dispatchGesture(gestureBuilder.build(), object : GestureResultCallback() {
            override fun onCompleted(gestureDescription: GestureDescription?) {
                super.onCompleted(gestureDescription)
                Log.d(TAG, "点击操作完成: ($x, $y)")
                callback(true)
            }
            
            override fun onCancelled(gestureDescription: GestureDescription?) {
                super.onCancelled(gestureDescription)
                Log.e(TAG, "点击操作取消: ($x, $y)")
                callback(false)
            }
        }, null)
    }
    
    /**
     * 执行滑动操作
     */
    fun performSwipe(
        startX: Int, startY: Int,
        endX: Int, endY: Int,
        duration: Long = 300,
        callback: (Boolean) -> Unit = {}
    ) {
        val path = Path().apply {
            moveTo(startX.toFloat(), startY.toFloat())
            lineTo(endX.toFloat(), endY.toFloat())
        }
        
        val gestureBuilder = GestureDescription.Builder()
        gestureBuilder.addStroke(GestureDescription.StrokeDescription(path, 0, duration))
        
        dispatchGesture(gestureBuilder.build(), object : GestureResultCallback() {
            override fun onCompleted(gestureDescription: GestureDescription?) {
                super.onCompleted(gestureDescription)
                Log.d(TAG, "滑动操作完成: ($startX, $startY) -> ($endX, $endY)")
                callback(true)
            }
            
            override fun onCancelled(gestureDescription: GestureDescription?) {
                super.onCancelled(gestureDescription)
                Log.e(TAG, "滑动操作取消: ($startX, $startY) -> ($endX, $endY)")
                callback(false)
            }
        }, null)
    }
    
    /**
     * 执行文本输入
     */
    fun performTextInput(text: String, callback: (Boolean) -> Unit = {}) {
        val focusedNode = rootInActiveWindow?.findFocus(AccessibilityNodeInfo.FOCUS_INPUT)
        
        if (focusedNode != null) {
            val arguments = Bundle().apply {
                putCharSequence(AccessibilityNodeInfo.ACTION_ARGUMENT_SET_TEXT_CHARSEQUENCE, text)
            }
            
            val success = focusedNode.performAction(AccessibilityNodeInfo.ACTION_SET_TEXT, arguments)
            Log.d(TAG, "文本输入${if (success) "成功" else "失败"}: $text")
            callback(success)
        } else {
            Log.e(TAG, "未找到可输入的焦点节点")
            callback(false)
        }
    }
    
    /**
     * 执行返回操作
     */
    fun performBack(callback: (Boolean) -> Unit = {}) {
        val success = performGlobalAction(GLOBAL_ACTION_BACK)
        Log.d(TAG, "返回操作${if (success) "成功" else "失败"}")
        callback(success)
    }
    
    /**
     * 执行Home键操作
     */
    fun performHome(callback: (Boolean) -> Unit = {}) {
        val success = performGlobalAction(GLOBAL_ACTION_HOME)
        Log.d(TAG, "Home键操作${if (success) "成功" else "失败"}")
        callback(success)
    }
    
    /**
     * 执行最近任务操作
     */
    fun performRecents(callback: (Boolean) -> Unit = {}) {
        val success = performGlobalAction(GLOBAL_ACTION_RECENTS)
        Log.d(TAG, "最近任务操作${if (success) "成功" else "失败"}")
        callback(success)
    }
    
    /**
     * 根据文本查找并点击元素
     */
    fun clickByText(text: String, callback: (Boolean) -> Unit = {}) {
        val rootNode = rootInActiveWindow
        if (rootNode != null) {
            val targetNode = findNodeByText(rootNode, text)
            if (targetNode != null) {
                val bounds = android.graphics.Rect()
                targetNode.getBoundsInScreen(bounds)
                val centerX = bounds.centerX()
                val centerY = bounds.centerY()
                performClick(centerX, centerY, callback)
            } else {
                Log.e(TAG, "未找到文本为 '$text' 的元素")
                callback(false)
            }
        } else {
            Log.e(TAG, "无法获取根节点")
            callback(false)
        }
    }
    
    /**
     * 根据ID查找并点击元素
     */
    fun clickById(resourceId: String, callback: (Boolean) -> Unit = {}) {
        val rootNode = rootInActiveWindow
        if (rootNode != null) {
            val targetNode = findNodeById(rootNode, resourceId)
            if (targetNode != null) {
                val bounds = android.graphics.Rect()
                targetNode.getBoundsInScreen(bounds)
                val centerX = bounds.centerX()
                val centerY = bounds.centerY()
                performClick(centerX, centerY, callback)
            } else {
                Log.e(TAG, "未找到ID为 '$resourceId' 的元素")
                callback(false)
            }
        } else {
            Log.e(TAG, "无法获取根节点")
            callback(false)
        }
    }
    
    private fun findNodeByText(rootNode: AccessibilityNodeInfo, text: String): AccessibilityNodeInfo? {
        if (rootNode.text?.toString()?.contains(text, ignoreCase = true) == true ||
            rootNode.contentDescription?.toString()?.contains(text, ignoreCase = true) == true
        ) {
            return rootNode
        }
        
        for (i in 0 until rootNode.childCount) {
            rootNode.getChild(i)?.let { child ->
                val result = findNodeByText(child, text)
                if (result != null) return result
            }
        }
        return null
    }
    
    private fun findNodeById(rootNode: AccessibilityNodeInfo, resourceId: String): AccessibilityNodeInfo? {
        if (rootNode.viewIdResourceName == resourceId) {
            return rootNode
        }
        
        for (i in 0 until rootNode.childCount) {
            rootNode.getChild(i)?.let { child ->
                val result = findNodeById(child, resourceId)
                if (result != null) return result
            }
        }
        return null
    }
    
    private fun getScreenSize(): Pair<Int, Int> {
        val displayMetrics = resources.displayMetrics
        return Pair(displayMetrics.widthPixels, displayMetrics.heightPixels)
    }
    
    private fun logUserAction(action: String, event: AccessibilityEvent) {
        Log.d(TAG, "用户操作: $action - ${event.className}")
    }
    
    private fun broadcastScreenChange(packageName: String) {
        val intent = Intent(ACTION_SCREEN_CHANGED).apply {
            putExtra("packageName", packageName)
            putExtra("timestamp", System.currentTimeMillis())
        }
        LocalBroadcastManager.getInstance(this).sendBroadcast(intent)
    }
    
    private fun stopCurrentTask() {
        isTaskRunning = false
    }
    
    fun getCurrentScreenAnalysis(): ScreenAnalysis? {
        return currentScreenAnalysis
    }
    
    fun setTaskRunning(running: Boolean) {
        isTaskRunning = running
    }
}