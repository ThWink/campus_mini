<template>
  <div class="app-wrapper">
    <!-- 登录页面 -->
    <div v-if="!user" class="login-container">
      <el-card class="login-card" shadow="hover">
        <div class="login-header">
          <h2>🎓 校园跑腿系统</h2>
          <p>{{ isRegister ? '新用户注册' : '欢迎回来' }}</p>
        </div>

        <el-form :model="loginForm" label-position="top">
          <el-form-item label="用户名">
            <el-input v-model="loginForm.username" placeholder="请输入用户名" />
          </el-form-item>
          <el-form-item label="密码">
            <el-input v-model="loginForm.password" type="password" placeholder="请输入密码" show-password />
          </el-form-item>

          <div style="margin-top: 20px;">
            <el-button type="primary" class="login-btn" @click="handleAuth">
              {{ isRegister ? '立 即 注 册' : '立 即 登 录' }}
            </el-button>
            <el-button link class="switch-btn" @click="isRegister = !isRegister">
              {{ isRegister ? '已有账号？去登录' : '没有账号？去注册' }}
            </el-button>
          </div>
        </el-form>
      </el-card>
    </div>

    <!-- 管理员后台 -->
    <div v-else-if="user.username === 'admin'" class="admin-container">
      <el-container style="height: 100vh; border: 1px solid #eee;">
        <el-aside width="200px" style="background-color: #303133;">
          <div class="admin-logo">
            <h3 style="color: white; text-align: center; padding: 20px 0;">校园跑腿系统</h3>
          </div>
          <el-menu
            :default-active="activeMenu"
            class="el-menu-vertical-demo"
            background-color="#303133"
            text-color="#fff"
            active-text-color="#409EFF"
            @select="handleMenuSelect"
          >
            <el-menu-item index="dashboard">
              <el-icon><House /></el-icon>
              <span>仪表盘</span>
            </el-menu-item>
            <el-menu-item index="users">
              <el-icon><UserFilled /></el-icon>
              <span>用户管理</span>
            </el-menu-item>
            <el-menu-item index="orders">
              <el-icon><Document /></el-icon>
              <span>订单管理</span>
            </el-menu-item>
            <el-menu-item index="logout" @click="logout">
              <el-icon><SwitchButton /></el-icon>
              <span>退出登录</span>
            </el-menu-item>
          </el-menu>
        </el-aside>

        <el-container>
          <el-header style="text-align: right; font-size: 12px; background-color: white; padding: 0 20px;">
            <div style="line-height: 60px;">
              <span>欢迎，{{ user.username }}</span>
              <el-button type="text" @click="logout" style="margin-left: 20px;">退出</el-button>
            </div>
          </el-header>
          <el-main>
            <!-- 仪表盘 -->
            <div v-if="activeMenu === 'dashboard'" class="dashboard">
              <el-card shadow="hover" class="stats-card">
                <template #header>
                  <div class="card-header">
                    <span>系统概览</span>
                  </div>
                </template>
                <div class="stats-grid">
                  <el-card class="stat-item">
                    <div class="stat-icon users-icon"><el-icon><UserFilled /></el-icon></div>
                    <div class="stat-info">
                      <div class="stat-number">{{ userCount }}</div>
                      <div class="stat-label">总用户数</div>
                    </div>
                  </el-card>
                  <el-card class="stat-item">
                    <div class="stat-icon orders-icon"><el-icon><Document /></el-icon></div>
                    <div class="stat-info">
                      <div class="stat-number">{{ orderCount }}</div>
                      <div class="stat-label">总订单数</div>
                    </div>
                  </el-card>
                </div>
              </el-card>
            </div>

            <!-- 用户管理 -->
            <div v-if="activeMenu === 'users'" class="users-management">
              <el-card shadow="hover">
                <template #header>
                  <div class="card-header">
                    <span>用户管理</span>
                  </div>
                </template>
                <el-table :data="users" style="width: 100%">
                  <el-table-column prop="id" label="ID" width="80" />
                  <el-table-column prop="username" label="用户名" />
                  <el-table-column prop="phone" label="手机号" />
                  <el-table-column prop="role" label="角色" />
                  <el-table-column prop="createTime" label="创建时间" />
                  <el-table-column label="状态" width="100">
                    <template #default="scope">
                      <el-tag :type="scope.row.role === 'BANNED' ? 'danger' : 'success'">
                        {{ scope.row.role === 'BANNED' ? '封禁' : '正常' }}
                      </el-tag>
                    </template>
                  </el-table-column>
                  <el-table-column label="操作" width="200">
                    <template #default="scope">
                      <el-button type="primary" size="small" @click="editUser(scope.row)">
                        编辑
                      </el-button>
                      <el-button 
                        :type="scope.row.role === 'BANNED' ? 'success' : 'danger'" 
                        size="small" 
                        @click="toggleUserStatus(scope.row)"
                      >
                        {{ scope.row.role === 'BANNED' ? '解封' : '封禁' }}
                      </el-button>
                    </template>
                  </el-table-column>
                </el-table>
              </el-card>
            </div>

            <!-- 订单管理 -->
            <div v-if="activeMenu === 'orders'" class="orders-management">
              <el-card shadow="hover">
                <template #header>
                  <div class="card-header">
                    <span>订单管理</span>
                  </div>
                </template>
                <el-table :data="orders" style="width: 100%">
                  <el-table-column prop="id" label="订单ID" width="80" />
                  <el-table-column prop="taskId" label="任务ID" width="80" />
                  <el-table-column prop="title" label="标题" />
                  <el-table-column prop="reward" label="赏金" width="80" />
                  <el-table-column prop="status" label="状态" width="100">
                    <template #default="scope">
                      <el-tag :type="orderStatusMap[scope.row.status]?.type">
                        {{ orderStatusMap[scope.row.status]?.label }}
                      </el-tag>
                    </template>
                  </el-table-column>
                  <el-table-column prop="createTime" label="创建时间" />
                  <el-table-column label="操作" width="200">
                    <template #default="scope">
                      <el-button type="primary" size="small" @click="editOrder(scope.row)">
                        编辑
                      </el-button>
                      <el-button 
                        v-if="scope.row.status !== 3" 
                        type="danger" 
                        size="small" 
                        @click="banOrder(scope.row)"
                      >
                        封禁
                      </el-button>
                    </template>
                  </el-table-column>
                </el-table>
              </el-card>
            </div>


          </el-main>
        </el-container>
      </el-container>
    </div>

    <!-- 用户端 -->
    <div v-else class="mobile-container">
      <div class="mobile-header">
        <span>你好，{{ user.username }}</span>
        <el-button link type="danger" @click="logout">退出</el-button>
      </div>

      <div class="task-list">
        <el-card v-for="order in pendingOrders" :key="order.id" class="task-card">
          <div class="task-info">
            <h3>任务 #{{ order.taskId }}</h3>
            <p>{{ order.title }}</p>
            <p class="task-reward">赏金: ¥{{ order.reward }}</p>
          </div>
          <el-button type="primary" round @click="acceptOrder(order.id)">抢单</el-button>
        </el-card>
      </div>

      <div class="mobile-tabbar">
        <div class="plus-circle" @click="showPostDialog = true">+</div>
      </div>
    </div>

    <!-- 编辑用户对话框 -->
    <el-dialog v-model="showEditUserDialog" title="编辑用户" width="500px">
      <el-form :model="editUserForm">
        <el-form-item label="用户名">
          <el-input v-model="editUserForm.username" disabled />
        </el-form-item>
        <el-form-item label="手机号">
          <el-input v-model="editUserForm.phone" />
        </el-form-item>
        <el-form-item label="角色">
          <el-select v-model="editUserForm.role">
            <el-option label="普通用户" value="USER" />
            <el-option label="管理员" value="ADMIN" />
          </el-select>
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="showEditUserDialog = false">取消</el-button>
        <el-button type="primary" @click="updateUser">保存</el-button>
      </template>
    </el-dialog>

    <!-- 发布任务对话框 -->
    <el-dialog v-model="showPostDialog" title="发布任务" width="90%">
      <el-form :model="postForm">
        <el-form-item label="标题"><el-input v-model="postForm.title" /></el-form-item>
        <el-form-item label="描述"><el-input v-model="postForm.description" type="textarea" /></el-form-item>
        <el-form-item label="赏金"><el-input-number v-model="postForm.reward" /></el-form-item>
      </el-form>
      <template #footer>
        <el-button type="primary" @click="submitTask" style="width: 100%">发布</el-button>
      </template>
    </el-dialog>

    <!-- 编辑订单对话框 -->
    <el-dialog v-model="showEditOrderDialog" title="编辑订单" width="500px">
      <el-form :model="editOrderForm">
        <el-form-item label="订单ID">
          <el-input v-model="editOrderForm.id" disabled />
        </el-form-item>
        <el-form-item label="任务ID">
          <el-input v-model="editOrderForm.taskId" disabled />
        </el-form-item>
        <el-form-item label="标题">
          <el-input v-model="editOrderForm.title" disabled />
        </el-form-item>
        <el-form-item label="状态">
          <el-select v-model="editOrderForm.status">
            <el-option label="待接单" value="0" />
            <el-option label="已接单" value="1" />
            <el-option label="已完成" value="2" />
            <el-option label="已取消" value="3" />
          </el-select>
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="showEditOrderDialog = false">取消</el-button>
        <el-button type="primary" @click="updateOrder">保存</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import request from './utils/request'
import { ElMessage } from 'element-plus'
import { House, UserFilled, Document, CollectionTag, SwitchButton, ChatDotRound, Search, Plus, Delete, Edit, Refresh } from '@element-plus/icons-vue'

const user = ref(JSON.parse(localStorage.getItem('user')))
const isRegister = ref(false) // 切换登录/注册
const loginForm = ref({ username: '', password: '' })
const pendingOrders = ref([])
const showPostDialog = ref(false)
const postForm = ref({ title: '', description: '', reward: 5 })

// 管理员相关状态
const activeMenu = ref('dashboard')
const users = ref([])
const orders = ref([])
const userCount = ref(0)
const orderCount = ref(0)
const showEditUserDialog = ref(false)
const editUserForm = ref({})
const showEditOrderDialog = ref(false)
const editOrderForm = ref({})
// 搜索和筛选
const searchKeyword = ref('')
const statusFilter = ref('')

// 订单状态映射
const orderStatusMap = {
  0: { label: '待接单', type: 'warning' },
  1: { label: '已接单', type: 'primary' },
  2: { label: '已完成', type: 'success' },
  3: { label: '已取消', type: 'danger' }
}

// 核心方法：处理登录或注册
const handleAuth = async () => {
  const url = isRegister.value ? '/user/register' : '/user/login'
  try {
    const res = await request.post(url, loginForm.value)
    if (isRegister.value) {
      ElMessage.success('注册成功，请登录！')
      isRegister.value = false // 切换回登录页
    } else {
      user.value = res
      localStorage.setItem('user', JSON.stringify(res))
      ElMessage.success('登录成功')
      // admin用户名或role为ADMIN进入管理端
      if (res.username === 'admin' || res.role === 'ADMIN') {
        fetchAdminData()
      } else {
        fetchPendingOrders()
      }
    }
  } catch (error) {
    ElMessage.error('操作失败，请重试')
  }
}

const logout = () => {
  localStorage.removeItem('user')
  user.value = null
  activeMenu.value = 'dashboard'
}

// 管理员相关方法
const handleMenuSelect = (key) => {
  activeMenu.value = key
  if (key === 'users') {
    fetchUsers()
  } else if (key === 'orders') {
    fetchOrders()
  }
}

const fetchAdminData = async () => {
  await Promise.all([
    fetchUsers(),
    fetchOrders()
  ])
}

const fetchComments = async () => {
  try {
    const res = await request.get('/admin/comments')
    comments.value = res.data || []
    commentCount.value = comments.value.length
  } catch (error) {
    ElMessage.error('获取评论列表失败')
  }
}

const deleteComment = async (id) => {
  try {
    await request.delete(`/admin/comments?commentId=${id}`)
    ElMessage.success('删除成功')
    fetchComments()
  } catch (error) {
    ElMessage.error('删除失败，请重试')
  }
}

const fetchUsers = async () => {
  try {
    const res = await request.get('/admin/users')
    users.value = res || []
    userCount.value = users.value.length
  } catch (error) {
    ElMessage.error('获取用户列表失败')
  }
}

const fetchOrders = async () => {
  try {
    const res = await request.get('/admin/orders')
    orders.value = res || []
    orderCount.value = orders.value.length
  } catch (error) {
    ElMessage.error('获取订单列表失败')
  }
}

const editUser = (user) => {
  editUserForm.value = { ...user }
  showEditUserDialog.value = true
}

const updateUser = async () => {
  try {
    await request.post('/admin/updateUserRole', {
      userId: editUserForm.value.id,
      role: editUserForm.value.role
    })
    ElMessage.success('更新成功')
    showEditUserDialog.value = false
    fetchUsers()
  } catch (error) {
    ElMessage.error('更新失败，请重试')
  }
}

const toggleUserStatus = async (user) => {
  try {
    const url = user.role === 'BANNED' ? '/admin/unbanUser' : '/admin/banUser'
    await request.post(url, {
      userId: user.id
    })
    ElMessage.success(user.role === 'BANNED' ? '用户已解封' : '用户已封禁')
    fetchUsers()
  } catch (error) {
    ElMessage.error('操作失败，请重试')
  }
}

const editOrder = (order) => {
  editOrderForm.value = { ...order }
  showEditOrderDialog.value = true
}

const updateOrder = async () => {
  try {
    await request.post('/admin/updateOrderStatus', {
      orderId: editOrderForm.value.id,
      status: editOrderForm.value.status
    })
    ElMessage.success('更新成功')
    showEditOrderDialog.value = false
    fetchOrders()
  } catch (error) {
    ElMessage.error('更新失败，请重试')
  }
}

const banOrder = async (order) => {
  try {
    await request.post('/admin/banOrder', {
      orderId: order.id
    })
    ElMessage.success('订单已封禁')
    fetchOrders()
  } catch (error) {
    ElMessage.error('操作失败，请重试')
  }
}

// 用户端相关方法
const fetchPendingOrders = async () => {
  try {
    const res = await request.get('/order/listPending')
    pendingOrders.value = res || []
  } catch (error) {
    ElMessage.error('获取任务列表失败')
  }
}

const submitTask = async () => {
  try {
    await request.post('/task/save', { ...postForm.value, publisherId: user.value.id })
    ElMessage.success('发布成功')
    showPostDialog.value = false
    fetchPendingOrders()
  } catch (error) {
    ElMessage.error('发布失败，请重试')
  }
}

const acceptOrder = async (id) => {
  try {
    await request.post('/order/accept', { orderId: id, runnerId: user.value.id })
    ElMessage.success('抢单成功')
    fetchPendingOrders()
  } catch (error) {
    ElMessage.error('抢单失败，请重试')
  }
}

onMounted(() => {
  if (user.value) {
    if (user.value.username === 'admin') {
      fetchAdminData()
    } else {
      fetchPendingOrders()
    }
  }
})
</script>

<style scoped>
/* 登录页面样式 */
.switch-btn { margin-top: 10px; width: 100%; text-align: center; color: #409eff; }
.login-container { display: flex; justify-content: center; align-items: center; height: 100vh; background: #f5f7fa; }
.login-card { width: 350px; padding: 20px; }

/* 管理员后台样式 */
.admin-container {
  height: 100vh;
  overflow: hidden;
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

/* 仪表盘样式 */
.stats-grid {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: 20px;
  margin-top: 20px;
}

.stat-item {
  display: flex;
  align-items: center;
  padding: 20px;
}

.stat-icon {
  width: 60px;
  height: 60px;
  border-radius: 50%;
  display: flex;
  justify-content: center;
  align-items: center;
  margin-right: 20px;
  font-size: 24px;
}

.users-icon {
  background-color: #ecf5ff;
  color: #409eff;
}

.orders-icon {
  background-color: #f0f9eb;
  color: #67c23a;
}

.tasks-icon {
  background-color: #fdf6ec;
  color: #e6a23c;
}

.stat-number {
  font-size: 24px;
  font-weight: bold;
  margin-bottom: 5px;
}

.stat-label {
  font-size: 14px;
  color: #909399;
}

/* 移动端样式 */
.mobile-container { max-width: 450px; margin: 0 auto; background: #fff; min-height: 100vh; position: relative; }
.mobile-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 15px;
  border-bottom: 1px solid #f0f0f0;
}

.task-list {
  padding: 15px;
}

.task-card {
  margin-bottom: 15px;
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.task-reward {
  color: #e6a23c;
  font-weight: bold;
  margin-top: 5px;
}

.plus-circle {
  position: fixed;
  bottom: 20px;
  left: 50%;
  transform: translateX(-50%);
  width: 60px;
  height: 60px;
  background: #409eff;
  color: #fff;
  border-radius: 50%;
  display: flex;
  justify-content: center;
  align-items: center;
  font-size: 30px;
  box-shadow: 0 4px 12px rgba(0,0,0,0.2);
  cursor: pointer;
}
</style>
