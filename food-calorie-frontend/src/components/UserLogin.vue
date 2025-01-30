<template>
  <div class="login-container">
    <h1 class="system-title">基于yolov7的食物识别与热量估算系统</h1>
    <div class="login-box"> 
      <h2 class="title">登录</h2>
      <form @submit.prevent="handleLogin">
        <div class="input-group">
          <label for="username">用户名:</label>
          <input type="text" v-model="username" id="username" required placeholder="请输入用户名" />
        </div>
        <div class="input-group">
          <label for="password">密码:</label>
          <input type="password" v-model="password" id="password" required placeholder="请输入密码" />
        </div>
        <button type="submit" class="login-button">登录</button>
      </form>
      <p class="register-link">还没有账号？ <router-link to="/register">注册</router-link></p>
    </div>
  </div>
</template>

<script>
import axios from 'axios'
import { ElNotification } from 'element-plus';
const api = axios.create({
    baseURL: 'http://localhost:8000/',
    withCredentials: true, // 重要
});

export default {
  name: 'UserLogin',
  data() {
    return {
      username: '',
      password: '',
      error: ''
    }
  },
  methods: {
    async handleLogin() {
      const currentTime = new Date().toLocaleString();
      try {
        const response = await api.post('/api/login/', {
          username: this.username,
          password: this.password
        }, {
          headers: {
            'Content-Type': 'application/json'
          },
          withCredentials: true
        })
        this.success = response.data.message
        
        ElNotification({title: `${this.success}`,message:  `${currentTime}`,type: 'success',position: 'top-right',});
        this.$router.push('/index')
        
      } catch (err) {
        if (err.response?.data?.error) {
          this.error = err.response.data.error
          ElNotification({
          title: `${this.error}`,
          message:  `${currentTime}`,
          type: 'error',
          position: 'top-right',
        });
        } else {
          this.error = err;
          ElNotification({title: `${this.error}`,message:  `${currentTime}`,type: 'error',position: 'top-right',});
        }
      }
    }
  }
}
</script>

<style scoped>
@import url('https://fonts.googleapis.com/css2?family=Roboto:wght@400;500;700&display=swap');

html, body {
  margin: 0;
  padding: 0;
  height: 100%;
  background: #121212;
  background: linear-gradient(135deg, #1f1f1f, #2c2c2c);
  font-family: 'Roboto', sans-serif;
  color: #ffffff;
}

.login-container {
  min-height: 100vh;
  display: flex;
  flex-direction: column;
  justify-content: center;
  align-items: center;
}

.system-title {
  color: #00c6ff;
  font-size: 32px;
  font-weight: 700;
  margin-bottom: 100px;
  text-align: center;
  letter-spacing: 1px;
}

.login-box {
  background: rgba(255, 255, 255, 0.05);
  padding: 40px 30px;
  border-radius: 12px;
  box-shadow: 0 8px 32px 0 rgba(31, 38, 135, 0.37);
  backdrop-filter: blur(8.5px);
  -webkit-backdrop-filter: blur(8.5px);
  border: 1px solid rgba(255, 255, 255, 0.18);
  width: 100%;
  max-width: 400px;
}

.title {
  text-align: center;
  color: #ffffff;
  margin-bottom: 30px;
  font-size: 24px;
  font-weight: 700;
  letter-spacing: 1.5px;
}

.input-group {
  margin-bottom: 20px;
  display: flex;
  flex-direction: column;
}

.input-group label {
  color: #ffffff;
  margin-bottom: 8px;
  font-size: 14px;
}

.input-group input {
  padding: 12px 15px;
  border: none;
  border-radius: 8px;
  background: rgba(255, 255, 255, 0.1);
  color: #ffffff;
  font-size: 16px;
  transition: background 0.3s ease;
}

.input-group input::placeholder {
  color: #b3b3b3;
}

.input-group input:focus {
  outline: none;
  background: rgba(255, 255, 255, 0.2);
}

.login-button {
  width: 100%;
  padding: 12px;
  border: none;
  border-radius: 8px;
  background: #00c6ff;
  background: linear-gradient(45deg, #00c6ff, #0072ff);
  color: #ffffff;
  font-size: 16px;
  font-weight: 500;
  cursor: pointer;
  transition: transform 0.2s ease, box-shadow 0.2s ease;
}

.login-button:hover {
  transform: translateY(-2px);
  box-shadow: 0 4px 15px rgba(0, 198, 255, 0.4);
}

.error {
  color: #ff6b6b;
  text-align: center;
  margin-top: 10px;
}

.register-link {
  text-align: center;
  margin-top: 20px;
  color: #b3b3b3;
}

.register-link a {
  color: #00c6ff;
  text-decoration: none;
  transition: color 0.3s ease;
}

.register-link a:hover {
  color: #0072ff;
}
</style>