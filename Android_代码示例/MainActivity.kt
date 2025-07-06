package com.automate.mobile

import android.content.Intent
import android.os.Bundle
import android.provider.Settings
import androidx.activity.ComponentActivity
import androidx.activity.compose.setContent
import androidx.compose.foundation.layout.*
import androidx.compose.foundation.lazy.LazyColumn
import androidx.compose.foundation.lazy.items
import androidx.compose.material.icons.Icons
import androidx.compose.material.icons.filled.*
import androidx.compose.material3.*
import androidx.compose.runtime.*
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.platform.LocalContext
import androidx.compose.ui.text.font.FontWeight
import androidx.compose.ui.unit.dp
import androidx.compose.ui.unit.sp
import androidx.hilt.navigation.compose.hiltViewModel
import androidx.lifecycle.compose.collectAsStateWithLifecycle
import androidx.navigation.NavController
import androidx.navigation.compose.NavHost
import androidx.navigation.compose.composable
import androidx.navigation.compose.rememberNavController
import com.automate.mobile.ui.theme.AutoMateMobileTheme
import com.automate.mobile.ui.components.*
import com.automate.mobile.viewmodel.MainViewModel
import com.automate.mobile.data.model.TaskStatus
import dagger.hilt.android.AndroidEntryPoint

@AndroidEntryPoint
class MainActivity : ComponentActivity() {
    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        setContent {
            AutoMateMobileTheme {
                AutoMateApp()
            }
        }
    }
}

@OptIn(ExperimentalMaterial3Api::class)
@Composable
fun AutoMateApp() {
    val navController = rememberNavController()
    
    Scaffold(
        bottomBar = {
            BottomNavigationBar(navController)
        }
    ) { innerPadding ->
        NavHost(
            navController = navController,
            startDestination = "home",
            modifier = Modifier.padding(innerPadding)
        ) {
            composable("home") {
                HomeScreen()
            }
            composable("tasks") {
                TasksScreen()
            }
            composable("chat") {
                ChatScreen()
            }
            composable("settings") {
                SettingsScreen()
            }
        }
    }
}

@Composable
fun BottomNavigationBar(navController: NavController) {
    val items = listOf(
        BottomNavItem("home", "首页", Icons.Default.Home),
        BottomNavItem("tasks", "任务", Icons.Default.List),
        BottomNavItem("chat", "对话", Icons.Default.Chat),
        BottomNavItem("settings", "设置", Icons.Default.Settings)
    )
    
    NavigationBar {
        val currentRoute = navController.currentDestination?.route
        items.forEach { item ->
            NavigationBarItem(
                selected = currentRoute == item.route,
                onClick = {
                    navController.navigate(item.route) {
                        popUpTo(navController.graph.startDestinationId)
                        launchSingleTop = true
                    }
                },
                icon = {
                    Icon(
                        imageVector = item.icon,
                        contentDescription = item.title
                    )
                },
                label = {
                    Text(text = item.title)
                }
            )
        }
    }
}

@OptIn(ExperimentalMaterial3Api::class)
@Composable
fun HomeScreen(
    viewModel: MainViewModel = hiltViewModel()
) {
    val uiState by viewModel.uiState.collectAsStateWithLifecycle()
    val context = LocalContext.current
    
    Column(
        modifier = Modifier
            .fillMaxSize()
            .padding(16.dp)
    ) {
        // 头部信息
        Card(
            modifier = Modifier
                .fillMaxWidth()
                .padding(vertical = 8.dp)
        ) {
            Column(
                modifier = Modifier.padding(16.dp)
            ) {
                Row(
                    modifier = Modifier.fillMaxWidth(),
                    horizontalArrangement = Arrangement.SpaceBetween,
                    verticalAlignment = Alignment.CenterVertically
                ) {
                    Text(
                        text = "🤖 AutoMate Mobile",
                        fontSize = 20.sp,
                        fontWeight = FontWeight.Bold
                    )
                    Row {
                        IconButton(onClick = { /* 通知 */ }) {
                            Icon(Icons.Default.Notifications, contentDescription = "通知")
                        }
                        IconButton(onClick = { /* 设置 */ }) {
                            Icon(Icons.Default.Settings, contentDescription = "设置")
                        }
                    }
                }
            }
        }
        
        // 快速操作区域
        Card(
            modifier = Modifier
                .fillMaxWidth()
                .padding(vertical = 8.dp)
        ) {
            Column(
                modifier = Modifier.padding(16.dp)
            ) {
                Text(
                    text = "🎯 快速操作",
                    fontSize = 18.sp,
                    fontWeight = FontWeight.SemiBold,
                    modifier = Modifier.padding(bottom = 12.dp)
                )
                
                LazyColumn(
                    verticalArrangement = Arrangement.spacedBy(8.dp)
                ) {
                    items(uiState.quickActions) { action ->
                        QuickActionCard(
                            title = action.title,
                            description = action.description,
                            icon = action.icon,
                            onClick = {
                                viewModel.executeQuickAction(action)
                            }
                        )
                    }
                }
            }
        }
        
        // 今日统计
        Card(
            modifier = Modifier
                .fillMaxWidth()
                .padding(vertical = 8.dp)
        ) {
            Column(
                modifier = Modifier.padding(16.dp)
            ) {
                Text(
                    text = "📊 今日统计",
                    fontSize = 18.sp,
                    fontWeight = FontWeight.SemiBold,
                    modifier = Modifier.padding(bottom = 12.dp)
                )
                
                Row(
                    modifier = Modifier.fillMaxWidth(),
                    horizontalArrangement = Arrangement.SpaceBetween
                ) {
                    StatItem("执行任务", "${uiState.todayStats.tasksExecuted} 次")
                    StatItem("节省时间", "${uiState.todayStats.timeSaved} 分钟")
                }
                
                Row(
                    modifier = Modifier.fillMaxWidth(),
                    horizontalArrangement = Arrangement.SpaceBetween
                ) {
                    StatItem("成功率", "${uiState.todayStats.successRate}%")
                    StatItem("活跃应用", uiState.todayStats.activeApps)
                }
            }
        }
        
        // 语音输入区域
        Card(
            modifier = Modifier
                .fillMaxWidth()
                .padding(vertical = 8.dp)
        ) {
            Column(
                modifier = Modifier.padding(16.dp)
            ) {
                Text(
                    text = "🎤 对我说话...",
                    fontSize = 18.sp,
                    fontWeight = FontWeight.SemiBold,
                    modifier = Modifier.padding(bottom = 12.dp)
                )
                
                VoiceInputField(
                    value = uiState.voiceInput,
                    onValueChange = { viewModel.updateVoiceInput(it) },
                    onSendClick = { viewModel.processVoiceInput() },
                    onVoiceClick = { viewModel.startVoiceRecognition() }
                )
            }
        }
        
        // 检查无障碍服务
        if (!uiState.isAccessibilityEnabled) {
            AccessibilityPermissionCard(
                onEnableClick = {
                    val intent = Intent(Settings.ACTION_ACCESSIBILITY_SETTINGS)
                    context.startActivity(intent)
                }
            )
        }
    }
}

@Composable
fun QuickActionCard(
    title: String,
    description: String,
    icon: String,
    onClick: () -> Unit
) {
    Card(
        modifier = Modifier
            .fillMaxWidth()
            .padding(vertical = 4.dp),
        onClick = onClick
    ) {
        Row(
            modifier = Modifier
                .fillMaxWidth()
                .padding(16.dp),
            verticalAlignment = Alignment.CenterVertically
        ) {
            Text(
                text = icon,
                fontSize = 24.sp,
                modifier = Modifier.padding(end = 12.dp)
            )
            Column(
                modifier = Modifier.weight(1f)
            ) {
                Text(
                    text = title,
                    fontSize = 16.sp,
                    fontWeight = FontWeight.Medium
                )
                Text(
                    text = description,
                    fontSize = 14.sp,
                    color = MaterialTheme.colorScheme.onSurfaceVariant
                )
            }
            Icon(
                Icons.Default.ChevronRight,
                contentDescription = "执行",
                tint = MaterialTheme.colorScheme.primary
            )
        }
    }
}

@Composable
fun StatItem(label: String, value: String) {
    Column(
        horizontalAlignment = Alignment.CenterHorizontally
    ) {
        Text(
            text = value,
            fontSize = 16.sp,
            fontWeight = FontWeight.Bold,
            color = MaterialTheme.colorScheme.primary
        )
        Text(
            text = label,
            fontSize = 12.sp,
            color = MaterialTheme.colorScheme.onSurfaceVariant
        )
    }
}

@OptIn(ExperimentalMaterial3Api::class)
@Composable
fun VoiceInputField(
    value: String,
    onValueChange: (String) -> Unit,
    onSendClick: () -> Unit,
    onVoiceClick: () -> Unit
) {
    Row(
        modifier = Modifier.fillMaxWidth(),
        verticalAlignment = Alignment.CenterVertically
    ) {
        OutlinedTextField(
            value = value,
            onValueChange = onValueChange,
            placeholder = { Text("请告诉我你想要自动化的操作") },
            modifier = Modifier.weight(1f),
            singleLine = true
        )
        
        IconButton(
            onClick = onSendClick,
            modifier = Modifier.padding(start = 8.dp)
        ) {
            Icon(Icons.Default.Send, contentDescription = "发送")
        }
        
        IconButton(
            onClick = onVoiceClick
        ) {
            Icon(Icons.Default.Mic, contentDescription = "语音输入")
        }
    }
}

@Composable
fun AccessibilityPermissionCard(
    onEnableClick: () -> Unit
) {
    Card(
        modifier = Modifier
            .fillMaxWidth()
            .padding(vertical = 8.dp),
        colors = CardDefaults.cardColors(
            containerColor = MaterialTheme.colorScheme.errorContainer
        )
    ) {
        Column(
            modifier = Modifier.padding(16.dp)
        ) {
            Row(
                verticalAlignment = Alignment.CenterVertically,
                modifier = Modifier.padding(bottom = 8.dp)
            ) {
                Icon(
                    Icons.Default.Warning,
                    contentDescription = "警告",
                    tint = MaterialTheme.colorScheme.error,
                    modifier = Modifier.padding(end = 8.dp)
                )
                Text(
                    text = "需要开启无障碍服务",
                    fontSize = 16.sp,
                    fontWeight = FontWeight.Medium,
                    color = MaterialTheme.colorScheme.onErrorContainer
                )
            }
            
            Text(
                text = "为了实现自动化操作，请在设置中开启 AutoMate 的无障碍服务权限。",
                fontSize = 14.sp,
                color = MaterialTheme.colorScheme.onErrorContainer,
                modifier = Modifier.padding(bottom = 12.dp)
            )
            
            Button(
                onClick = onEnableClick,
                modifier = Modifier.fillMaxWidth()
            ) {
                Text("去设置")
            }
        }
    }
}

data class BottomNavItem(
    val route: String,
    val title: String,
    val icon: androidx.compose.ui.graphics.vector.ImageVector
)