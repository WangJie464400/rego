<template>
  <div class="food-detector-container dark-theme">
    <header class="user-header" v-if="isAuthenticated">
      <div class="avatar-container" @click="toggleDropdown">
        <img src="../assets/head_img.jpg" alt="User Avatar" class="avatar">
        <div v-if="dropdownVisible" class="dropdown-menu">
          <button @click="changeAccount" class="dropdown-item">更换账号</button>
          <button @click="logout" class="dropdown-item">注销</button>
        </div>
      </div>
      <span class="welcome-text">{{ username }}</span>
    </header>
    
    <h1 class="main-title">食物识别与热量估算系统</h1>
    
    <div class="content-wrapper">
      <section class="upload-section glass-effect">
        <h3 class="section-title">上传文件</h3>
        <!-- 摄像头上传 -->
        <div class="file-upload">
          <label :class="['upload-label', { active: cameraActive }]" @click="toggleCamera">
            <span class="label-text">
              {{ cameraActive ? '关闭摄像头' : '开启摄像头' }}
            </span>
            <span class="upload-icon">📹</span>
          </label>
        </div>
        <div class="file-upload">
          <label class="upload-label">
            <span class="label-text">上传图片</span>
            <input type="file" accept="image/*" @change="onFileChange($event, 'image')" class="file-input" multiple>
            <span class="upload-icon">📸</span>
          </label>
        </div>
        <!-- 如果只处理图片上传，可以移除视频上传部分 -->
        <div class="file-upload">
          <label class="upload-label">
            <span class="label-text">上传视频</span>
            <input type="file" accept="video/*" @change="onFileChange($event, 'video')" class="file-input">
            <span class="upload-icon">🎥</span>
          </label>
        </div>

        <button @click="detectFood" class="detect-button" :disabled="!selectedFiles.length && !cameraActive">
          <span class="button-text">开始识别</span>
          <span class="button-icon">🔍</span>
        </button>
      </section>

      <section class="preview-section glass-effect">
        <h3 class="section-title">预览</h3>
        <div v-if="previewUrls.length || cameraActive" class="preview-container">
          <button v-if="isImage && previewUrls.length > 1" @click="prevImage" class="nav-button prev-button">上一张</button>
          <template v-if="selectedFileType === 'image'">
            <img :src="currentPreviewUrl" alt="Uploaded Preview" class="image-preview">
          </template>
          <template v-else-if="selectedFileType === 'video'">
            <video :src="previewUrls[0]" controls class="video-preview"></video>
          </template>
          <template v-else-if="cameraActive">
            <div class="camera-wrapper">
              <video ref="cameraVideo" autoplay class="video-preview"></video>
              <canvas ref="videoCanvas" class="video-canvas"></canvas>
            </div>
          </template>
          <button v-if="isImage && previewUrls.length > 1" @click="nextImage" class="nav-button next-button">下一张</button>
        </div>
        <div v-else class="empty-preview">
          <span class="empty-icon">🖼️</span>
          <p>上传一个文件或开启摄像头以查看预览</p>
        </div>
      </section>

      <section class="results-section glass-effect">
        <h3 class="section-title">检测结果</h3>
        <div class="results-container">
          <div v-if="loading && !cameraActive" class="loader"></div>
          <!-- 进度条添加在loader正下方 -->
          <div v-if="loading && !cameraActive" class="progress-bar-container">
            <div class="progress-bar" :style="{ width: progress + '%' }"></div>
          </div>
          <template v-else>
            <div class="results-header">
              <span>识别到 {{ currentDetectedItems.length }} 个结果</span>
              <button @click="saveResults" class="save-button" :disabled="!results.length">保存结果</button>
            </div>
            <article v-for="item in currentDetectedItems" :key="item.id" class="detected-item">
              <div class="food-icon">🍽️</div>
              <div class="food-info">
                <p>
                  <span class="id-label">标记框: {{ item.id }}</span> <br>
                  类别: {{ item.class_name }} <br>
                  置信度: {{ (item.confidence * 100).toFixed(2) }}%
                </p>
              </div>
            </article>
            <div v-if="!currentDetectedItems.length && !loading" class="empty-results">
              <span class="empty-icon">📊</span>
              <p>暂无结果</p>
            </div>
          </template>
        </div>
        <div v-if="results.length > 1 && selectedFileType === 'image'" class="navigation-info">
          <p>{{ currentIndex + 1 }} / {{ results.length }}</p>
        </div>
      </section>
    </div>
  </div>
</template>

<script>
import axios from 'axios';
import { ElNotification } from 'element-plus';
const api = axios.create({
    baseURL: 'http://localhost:8000/',
    withCredentials: true, // 重要
});



export default {
  data() {
    return {
      selectedFiles: [], // 存储多个文件
      selectedFileType: null,
      results: [], // 存储多个文件的检测结果
      loading: false,
      previewUrls: [], // 存储多个预览 URL
      currentIndex: 0, // 当前预览索引
      cameraActive: false, // 摄像头状态
      videoStream: null, // 摄像头流
      detectionInterval: null, // 检测定时器
      progress: 0, // 进度条百分比
      progressInterval: null, // 进度条更新定时器
      total_frames: 0, // 总帧数
      previousDetections: [], // 用于存储上一帧的检测结果

      // 新增的用户相关数据
      username: '',
      isAuthenticated: false,

      // 新增的下拉菜单状态
      dropdownVisible: false,
    };
  },
  computed: {
    isImage() {
      return this.selectedFileType === 'image';
    },
    currentPreviewUrl() {
      return this.previewUrls[this.currentIndex];
    },
    currentDetectedItems() {
      if (this.results.length > 0 && this.isImage) {
        return this.results[this.currentIndex].results;
      } else if (this.results.length > 0 && !this.isImage) {
        return this.results[0].results;
      }
      return [];
    }
  },
  methods: {
    onFileChange(event, fileType) {
      const files = Array.from(event.target.files);
      this.selectedFileType = fileType;

      if (fileType === 'image') {
        this.selectedFiles = files;
        this.previewUrls = files.map(file => URL.createObjectURL(file));
        this.total_frames = files.length; // 每张图片视为一帧
      } else if (fileType === 'video') {
        this.selectedFiles = files.slice(0, 1); // 只处理一个视频
        this.previewUrls = files.slice(0,1).map(file => URL.createObjectURL(file));
        this.total_frames = 0; // 初始化总帧数

        // 加载视频以获取总帧数
        const video = document.createElement('video');
        video.src = this.previewUrls[0];
        video.preload = 'metadata';
        video.onloadedmetadata = () => {
          const duration = video.duration; // 视频时长（秒）
          const frameRate = 30; // 假设帧率为30fps
          this.total_frames = Math.floor(duration * frameRate);
        };
      }

      // 重置检测结果和导航
      this.results = [];
      this.currentIndex = 0;
    },
    toggleCamera() {
      if (this.cameraActive) {
        this.stopCamera();
      } else {
        this.startCamera();
      }
    },
    async startCamera() {
      try {
        this.videoStream = await navigator.mediaDevices.getUserMedia({ video: true });
        this.cameraActive = true;
        this.selectedFileType = 'camera';
        this.results = [];
        this.loading = false; // 确保加载动画不显示

        // 清空预览 URL，因为摄像头正在使用
        this.previewUrls = [];

        // 等待 DOM 更新完成
        this.$nextTick(() => {
          if (this.$refs.cameraVideo) {
            this.$refs.cameraVideo.srcObject = this.videoStream;

            // 确保视频元素播放
            this.$refs.cameraVideo.onloadedmetadata = () => {
              this.$refs.cameraVideo.play();
            };

            // 开始定期检测
            this.detectionInterval = setInterval(this.captureAndDetectFrame, 600); // 每0.6秒检测一次
          } else {
            console.error('摄像头视频元素未找到。');
          }
        });

      } catch (error) {
        console.error('无法访问摄像头:', error);
        alert('无法访问摄像头。请检查权限设置。');
      }
    },
    stopCamera() {
      if (this.videoStream) {
        this.videoStream.getTracks().forEach(track => track.stop());
      }
      this.cameraActive = false;
      this.selectedFileType = null;
      this.results = [];
      this.previewUrls = [];
      clearInterval(this.detectionInterval);
      this.detectionInterval = null;
    },
    captureAndDetectFrame() {
      if (!this.cameraActive) return;

      const video = this.$refs.cameraVideo;
      if (!video) return;

      const canvas = document.createElement('canvas');
      canvas.width = video.videoWidth;
      canvas.height = video.videoHeight;
      const ctx = canvas.getContext('2d');
      if (!ctx) return;

      ctx.drawImage(video, 0, 0, canvas.width, canvas.height);
      canvas.toBlob(blob => {
        if (blob) {
          this.sendFrameForDetection(blob);
        }
      }, 'image/jpeg');
    },
    sendFrameForDetection(blob) {
      const formData = new FormData();
      formData.append('files', blob, 'frame.jpg');

      this.loading = true;

      api.post(`/api/detect/`, formData, {
        headers: {
          'Content-Type': 'multipart/form-data',
        },
      }).then(response => {
        // 处理响应数据
        const results = response.data.results;
        this.results = results;

        if (results.length > 0) {
          const frameResult = results[0];
          if (frameResult.results && frameResult.results.length > 0) {
            this.drawDetections(frameResult.results);
          }
        }

        this.loading = false;
      }).catch(error => {
        console.error('Error:', error);
        alert('处理摄像头帧时发生错误。');
        this.loading = false;
      });
    },
    detectFood() {
      if (!this.selectedFiles.length && !this.cameraActive) {
        alert('请先上传一个文件或开启摄像头进行检测。');
        return;
      }

      if (!this.cameraActive) {
        this.loading = true;
        this.progress = 0;

        let total_time_seconds = 0;

        if (this.isImage) {
          this.total_frames = this.selectedFiles.length;
          total_time_seconds = this.total_frames / 8;
        } else if (this.selectedFileType === 'video') {
          // 如果还未获得总帧数，假设为默认值
          if (this.total_frames === 0) {
            this.total_frames = 300; // 假设10秒视频，30fps
          }
          total_time_seconds = this.total_frames / 8;
        }

        const total_time_ms = total_time_seconds * 1000;
        const progress_increment_interval = 100; // 毫秒
        const progress_step = 100 / (total_time_ms / progress_increment_interval);

        this.progressInterval = setInterval(() => {
          if (this.progress < 100) {
            this.progress += progress_step;
            if (this.progress > 100) {
              this.progress = 100;
            }
          }
        }, progress_increment_interval);

        const formData = new FormData();

        if (this.isImage) {
          this.selectedFiles.forEach(file => {
            formData.append('files', file); // 发送多个文件
          });
        } else {
          // 处理视频上传
          formData.append('files', this.selectedFiles[0]); // 仅发送一个视频文件
        }

        api.post(`/api/detect/`, formData, {  // 请确保 URL 以斜杠结尾
          headers: {
            'Content-Type': 'multipart/form-data',
          },
        }).then(response => {
          this.results = response.data.results; // 包含每个文件的检测结果
          if (this.isImage) {
            this.previewUrls = this.results.map(result => result.result_image);
          } else if (this.selectedFileType === 'video') {
            this.previewUrls = [response.data.results[0].result_video];
          }

          this.loading = false;
          this.progress = 100;

          if (this.progressInterval) {
            clearInterval(this.progressInterval);
            this.progressInterval = null;
          }
        }).catch(error => {
          console.error('Error:', error);
          alert('处理文件时发生错误。');
          this.loading = false;
          this.progress = 0;
          if (this.progressInterval) {
            clearInterval(this.progressInterval);
            this.progressInterval = null;
          }
        });
      }
      // 摄像头模式下无需额外操作，因为检测已通过定时器开始
    },
    prevImage() {
      if (this.currentIndex > 0) {
        this.currentIndex--;
      }
    },
    nextImage() {
      if (this.currentIndex < this.previewUrls.length - 1) {
        this.currentIndex++;
      }
    },
    /**
     * 绘制检测结果到画布上
     * @param {Array} detectedItems - 检测结果数组
     */
    drawDetections(detectedItems) {
      const canvas = this.$refs.videoCanvas;
      const video = this.$refs.cameraVideo;
      const ctx = canvas.getContext('2d');

      // 设置画布大小与视频相同
      canvas.width = video.videoWidth;
      canvas.height = video.videoHeight;

      // 清除之前的绘制
      ctx.clearRect(0, 0, canvas.width, canvas.height);

      detectedItems.forEach(item => {
        const [x1, y1, x2, y2] = item.bbox;
        const className = item.class_name;
        const confidence = (item.confidence * 100).toFixed(2);

        // 绘制边界框
        ctx.strokeStyle = '#4CAF50'; // 边框颜色
        ctx.lineWidth = 2;
        ctx.strokeRect(x1, y1, x2 - x1, y2 - y1);

        // 绘制标签背景
        ctx.fillStyle = '#4CAF50'; // 标签背景颜色
        ctx.font = '16px Arial';
        const text = `${className} ${confidence}%`;
        const textWidth = ctx.measureText(text).width;
        ctx.fillRect(x1, y1 - 20, textWidth + 10, 20);

        // 绘制标签文本
        ctx.fillStyle = '#FFFFFF'; // 标签文本颜色
        ctx.fillText(text, x1 + 5, y1 - 5);
      });
    },
    /**
     * 保存检测结果为TXT文件
     */
    saveResults() {
      if (!this.results.length) {
        alert('暂无结果可保存。');
        return;
      }

      let content = '';

      this.results.forEach((fileResult) => {
        content += `文件: ${fileResult.original_file}\n`;
        fileResult.results.forEach(item => {
          const url = this.isImage
            ? fileResult.result_image 
            : (fileResult.result_video || 'N/A');
          content += `ID: ${item.id}, 类别: ${item.class_name}, 置信度: ${(item.confidence * 100).toFixed(2)}%, 边界框: [${item.bbox.join(', ')}], URL: ${url}\n`;
        });
        content += '\n';
      });

      const blob = new Blob([content], { type: 'text/plain;charset=utf-8' });
      const url = URL.createObjectURL(blob);
      const link = document.createElement('a');
      link.href = url;
      const timestamp = new Date().toISOString().replace(/[:\-T.]/g, '');
      link.download = `detection_results_${timestamp}.txt`;
      document.body.appendChild(link);
      link.click();
      document.body.removeChild(link);
      URL.revokeObjectURL(url);
    },
    /**
     * 检查用户认证状态
     */
    checkAuth() {
      const currentTime = new Date().toLocaleString();
      api.get('/api/check-auth/', { withCredentials: true })
      .then(response => {
        if (response.data.authenticated) {
          this.isAuthenticated = true;
          this.username = response.data.username;
        } else {
          this.isAuthenticated = false;
          this.username = '';

          // 重定向到登录页面
          this.$router.push('/'); // 确保 Vue Router 已配置
          ElNotification({title: "请登录！",message:  `${currentTime}`,type: 'error',position: 'top-right',});
          // 或者，如果未使用 Vue Router，可以使用 window.location
          // window.location.href = '/';
        }
      })
      .catch(error => {
        console.error('请登录:', error);
        this.isAuthenticated = false;
        this.username = '';
        // 在请求失败时也进行重定向
        this.$router.push('/'); // 确保 Vue Router 已配置
        // 或者使用 window.location
        // window.location.href = '/';
      });
  },
    /**
     * 新增方法：退出登录
     */
    logout() {
      api.post('/api/logout/', { withCredentials: true })
        .then(() => {
          // alert('已成功退出登录。');
          this.isAuthenticated = false;
          this.username = '';
          this.dropdownVisible = false;
          this.$router.push('/');
          // 可根据需要重定向到登录页面
        })
        .catch(error => {
          console.error('退出登录失败:', error);
          alert('退出登录时发生错误。');
        });
    },
    /**
     * 新增方法：更换账号
     */
    changeAccount() {
      this.dropdownVisible = false;
      // 实现更换账号的逻辑，这里简单重定向到登录页面
      this.$router.push('/'); // 确保 Vue Router 已配置并有登录路由
      // 或者使用 window.location
      // window.location.href = '/login';
    },
    /**
     * 切换下拉菜单的显示状态
     */
    toggleDropdown() {
      this.dropdownVisible = !this.dropdownVisible;
    },
    /**
     * 新增方法：处理外部点击以关闭下拉菜单
     */
    handleClickOutside(event) {
      const avatarContainer = this.$el.querySelector('.avatar-container');
      if (avatarContainer && !avatarContainer.contains(event.target)) {
        this.dropdownVisible = false;
      }
    },
  },
  mounted() {
    this.checkAuth();

    // 点击外部区域时关闭下拉菜单
    document.addEventListener('click', this.handleClickOutside);
  },
  beforeUnmount() {
    // 释放预览 URL
    this.previewUrls.forEach(url => URL.revokeObjectURL(url));
    // 停止摄像头
    if (this.cameraActive) {
      this.stopCamera();
    }
    // 清除进度条定时器
    if (this.progressInterval) {
      clearInterval(this.progressInterval);
    }
    // 清除之前的检测结果
    this.previousDetections = [];
    // 新增：清理用户相关数据
    this.username = '';
    this.isAuthenticated = false;

    // 移除点击外部区域的事件监听
    document.removeEventListener('click', this.handleClickOutside);
  }
};
</script>

<style scoped>
.food-detector-container {  
  position: relative; /* 添加定位以支持伪元素 */
  padding: 24px;
  width: 97%;
  min-height: 9vh;
  max-height: 120vh;
  background: linear-gradient(135deg, #2c3e50 0%, #34495e 100%);
  margin: 0 auto;
  overflow: hidden; /* 隐藏溢出内容，防止滚动条 */
  padding-top: 20px; /* 根据头部高度调整 */
  padding-bottom: 20px;
}

/* 新增暗黑主题类 */
.dark-theme {
  background: linear-gradient(135deg, #2c3e50 0%, #34495e 100%);
  color: #ecf0f1;
}

/* 添加背景图和设置透明度 */
.food-detector-container::before {
  content: '';
  position: absolute;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  background-image: url('../assets/bg.jpg'); /* 更换为暗黑主题背景图 */
  background-size: cover;
  background-position: center;
  opacity: 0.7;
  z-index: -1;
}

.main-title {
  text-align: center;
  color: #ecf0f1;
  font-size: 2.2em;
  margin-bottom: 30px;
  margin: 1px 0; 
  text-shadow: 2px 2px 4px rgba(0,0,0,0.5);
}

.content-wrapper {
  display: flex;
  gap: 20px;
  margin-top: 15px;
  width: 100%;
  height: 100%; /* 确保内容区域占满容器的高度 */
  overflow: auto; /* 如有需要，可以在内部子容器上设置滚动 */
}

.glass-effect {
  background: rgba(44, 62, 80, 0.8); /* 调整为深色玻璃效果 */
  backdrop-filter: blur(10px);
  border-radius: 16px;
  box-shadow: 0 4px 30px rgba(0, 0, 0, 0.5);
  border: 1px solid rgba(44, 62, 80, 0.3);
  transition: transform 0.3s ease;
}

.glass-effect:hover {
  transform: translateY(-5px);
}

.section-title {
  color: #ecf0f1;
  font-size: 1.5em;
  margin-bottom: 20px;
  text-align: center;
}

/* Upload Section */
.upload-section {
  flex: 2;
  min-width: 250px;
  padding: 25px;
}

.upload-label {
  display: flex;
  flex-direction: column;
  align-items: center;
  padding: 20px;
  background: rgba(236, 240, 241, 0.7);
  border-radius: 12px;
  cursor: pointer;
  transition: all 0.3s ease;
  margin: 15px 0;
}

.upload-label:hover {
  background: rgba(231, 76, 60, 0.7);
  transform: scale(1.02);
}

.upload-icon {
  font-size: 2em;
  margin: 10px 0;
}

.file-input {
  display: none;
}

.label-text {
  color: #2c3e50;
  font-weight: 500;
}

/* 当摄像头按钮处于激活状态时的样式 */
.upload-label.active {
  background: rgba(46, 204, 113, 0.7);
  transform: scale(1.02);
}

/* Preview Section */
.preview-section {
  flex: 5;
  padding: 25px;
  position: relative;
}

.preview-container {
  width: 100%;
  height: 500px;
  display: flex;
  justify-content: center;
  align-items: center;
  background: rgba(236, 240, 241, 0.7);
  border-radius: 12px;
  overflow: hidden;
  position: relative;
}

.image-preview {
  max-width: 100%;
  max-height: 100%;
  object-fit: contain;
  transition: transform 0.3s ease;
}

.image-preview:hover {
  transform: scale(1.02);
}

.video-preview {
  width: 100%;
  height: 100%;
  object-fit: contain;
  border-radius: 12px;
}

.video-preview:hover {
  transform: scale(1.02);
}

.empty-preview {
  height: 500px;
  display: flex;
  flex-direction: column;
  justify-content: center;
  align-items: center;
  color: #7f8c8d;
}

.empty-icon {
  font-size: 4em;
  margin-bottom: 20px;
}

/* Results Section */
.results-section {
  flex: 3;
  padding: 25px;
}

.results-container {
  max-height: 500px;
  overflow-y: auto;
}

.loader {
  border: 4px solid rgba(236, 240, 241, 0.3);
  border-radius: 50%;
  border-top: 4px solid #27ae60;
  width: 40px;
  height: 40px;
  animation: spin 1s linear infinite;
  margin: 50px auto;
}

/* 新增的进度条样式 */
.progress-bar-container {
  width: 80%;
  height: 10px;
  background-color: #bdc3c7;
  border-radius: 5px;
  margin: 10px auto;
}

.progress-bar {
  height: 100%;
  background-color: #27ae60;
  width: 0%;
  border-radius: 5px;
  transition: width 0.1s linear;
}

@keyframes spin {
  0% { transform: rotate(0deg); }
  100% { transform: rotate(360deg); }
}

/* Scrollbar Styling */
::-webkit-scrollbar {
  width: 8px;
}

::-webkit-scrollbar-track {
  background: #34495e;
  border-radius: 4px;
}

::-webkit-scrollbar-thumb {
  background: #7f8c8d;
  border-radius: 4px;
}

::-webkit-scrollbar-thumb:hover {
  background: #95a5a6;
}

/* Navigation Buttons */
.nav-button {
  position: absolute;
  top: 50%;
  transform: translateY(-50%);
  background: rgba(46, 204, 113, 0.7);
  border: none;
  color: white;
  padding: 10px;
  border-radius: 50%;
  cursor: pointer;
  font-size: 1em;
  /* Ensure buttons are always visible */
  opacity: 1;
  transition: background 0.3s;
}

.nav-button:hover {
  background: rgba(46, 204, 113, 1);
}

.prev-button {
  left: 10px;
}

.next-button {
  right: 10px;
}

/* 新增ID标签的样式 */
.id-label {
  background-color: rgba(39, 174, 96, 0.7); /* 绿色半透明背景 */
  color: white;
  padding: 2px 6px;
  border-radius: 4px;
  font-weight: bold;
}

/* 如果需要，调整.food-info 中 <p> 标签的样式以适应新标签 */
.food-info p {
  margin: 0;
  color: #ecf0f1;
  font-size: 1.1em;
}

.food-info p:after {
  content: '';
  display: block;
  margin-top: 5px;
  width: 100%;
  height: 1px;
  background: #7f8c8d;
}

/* Camera Wrapper */
.camera-wrapper {
  position: relative;
  width: 100%;
  height: 500px;
}

.video-preview {
  width: 100%;
  height: 100%;
  object-fit: contain;
  border-radius: 12px;
}

.video-canvas {
  position: absolute;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  pointer-events: none; /* 确保点击事件传递给视频元素 */
}

/* Results Header */
.results-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 10px;
  color: #ecf0f1;
}

/* Save Button 在 Results Header */
.save-button {
  background: linear-gradient(135deg, #2980b9 0%, #3498db 100%);
  color: white;
  border: none;
  border-radius: 8px;
  padding: 8px 16px;
  cursor: pointer;
  font-size: 0.9em;
  transition: background 0.3s ease;
}

.save-button:hover:not(:disabled) {
  background: linear-gradient(135deg, #1abc9c 0%, #16a085 100%);
}

.save-button:disabled {
  background: linear-gradient(135deg, #7f8c8d 0%, #95a5a6 100%);
  cursor: not-allowed;
}

/* 新增用户头部样式 */
.user-header {
  display: flex;
  flex-direction: column;   
  justify-content: center;
  align-items: center;
  padding: 25px 30px;
  /* background-color: rgba(44, 62, 80, 0.9);
  border-bottom: 1px solid #2c3e50; */
  position: absolute;
  top: 0;
  right: 0;
  left: 400; 
  box-sizing: border-box;
  z-index: 10;
}

.welcome-text {
  color: #ecf0f1;
  margin-top: 0px; /* 添加上边距，使文本位于头像下方 */
  font-size: 1em;
  text-align: center;
}

/* Avatar Container */
.avatar-container {
  position: relative;
  cursor: pointer;
}

.avatar {
  width: 35px; /* 增大头像尺寸以更好展示 */
  height: 35px;
  border-radius: 50%;
  object-fit: cover;
  border: 2px solid #ecf0f1;
}

.dropdown-menu {
  position: absolute;
  top: 70px; /* 调整下拉菜单位置，使其位于头像下方 */
  right: 0;
  background: rgba(44, 62, 80, 0.95);
  border: 1px solid #2c3e50;
  border-radius: 8px;
  box-shadow: 0 4px 8px rgba(0, 0, 0, 0.2);
  width: 150px;
  z-index: 20;
}

.dropdown-item {
  width: 100%;
  padding: 10px 15px;
  background: none;
  border: none;
  color: #ecf0f1;
  text-align: left;
  cursor: pointer;
  font-size: 0.95em;
  transition: background 0.3s;
}

.dropdown-item:hover {
  background: rgba(39, 174, 96, 0.2);
}

/* Results Section Continued */
.results-container {
  max-height: 500px;
  overflow-y: auto;
}

.detected-item {
  display: flex;
  align-items: center;
  padding: 15px;
  margin: 10px 0;
  background: rgba(52, 73, 94, 0.8);
  border-radius: 12px;
  box-shadow: 0 2px 10px rgba(0,0,0,0.5);
  transition: transform 0.2s ease;
}

.detected-item:hover {
  transform: translateX(5px);
}

.food-icon {
  font-size: 1.5em;
  margin-right: 15px;
}

.food-info p {
  margin: 0;
  color: #ecf0f1;
  font-size: 1.1em;
}

.empty-results {
  display: flex;
  flex-direction: column;
  align-items: center;
  color: #7f8c8d;
}

.empty-results .empty-icon {
  font-size: 2em;
  margin-bottom: 10px;
}

/* Navigation Info */
.navigation-info {
  text-align: center;
  margin-top: 10px;
  color: #ecf0f1;
  font-size: 1em;
}

/* Button Styles */
.detect-button {
  width: 100%;
  background: linear-gradient(135deg, #27ae60 0%, #2ecc71 100%);
  color: white;
  border: none;
  border-radius: 12px;
  padding: 15px 25px;
  cursor: pointer;
  font-size: 1.1em;
  display: flex;
  justify-content: center;
  align-items: center;
  gap: 10px;
  transition: all 0.3s ease;
}

.detect-button:hover:not(:disabled) {
  transform: translateY(-2px);
  box-shadow: 0 5px 15px rgba(39, 174, 96, 0.5);
}

.detect-button:disabled {
  background: linear-gradient(135deg, #7f8c8d 0%, #95a5a6 100%);
  cursor: not-allowed;
}

/* Save Button */
.save-button {
  background: linear-gradient(135deg, #2980b9 0%, #3498db 100%);
  color: white;
  border: none;
  border-radius: 8px;
  padding: 8px 16px;
  cursor: pointer;
  font-size: 0.9em;
  transition: background 0.3s ease;
}

.save-button:hover:not(:disabled) {
  background: linear-gradient(135deg, #1abc9c 0%, #16a085 100%);
}

.save-button:disabled {
  background: linear-gradient(135deg, #7f8c8d 0%, #95a5a6 100%);
  cursor: not-allowed;
}

/* Loader */
.loader {
  border: 4px solid rgba(236, 240, 241, 0.3);
  border-radius: 50%;
  border-top: 4px solid #27ae60;
  width: 40px;
  height: 40px;
  animation: spin 1s linear infinite;
  margin: 50px auto;
}

/* 新增的进度条样式 */
.progress-bar-container {
  width: 80%;
  height: 10px;
  background-color: #bdc3c7;
  border-radius: 5px;
  margin: 10px auto;
}

.progress-bar {
  height: 100%;
  background-color: #27ae60;
  width: 0%;
  border-radius: 5px;
  transition: width 0.1s linear;
}

@keyframes spin {
  0% { transform: rotate(0deg); }
  100% { transform: rotate(360deg); }
}

/* Scrollbar Styling */
::-webkit-scrollbar {
  width: 8px;
}

::-webkit-scrollbar-track {
  background: #34495e;
  border-radius: 4px;
}

::-webkit-scrollbar-thumb {
  background: #7f8c8d;
  border-radius: 4px;
}

::-webkit-scrollbar-thumb:hover {
  background: #95a5a6;
}

/* Navigation Buttons */
.nav-button {
  position: absolute;
  top: 50%;
  transform: translateY(-50%);
  background: rgba(46, 204, 113, 0.7);
  border: none;
  color: white;
  padding: 10px;
  border-radius: 50%;
  cursor: pointer;
  font-size: 1em;
  /* Ensure buttons are always visible */
  opacity: 1;
  transition: background 0.3s;
}

.nav-button:hover {
  background: rgba(46, 204, 113, 1);
}

.prev-button {
  left: 10px;
}

.next-button {
  right: 10px;
}

/* 新增ID标签的样式 */
.id-label {
  background-color: rgba(39, 174, 96, 0.7); /* 绿色半透明背景 */
  color: white;
  padding: 2px 6px;
  border-radius: 4px;
  font-weight: bold;
}

/* 如果需要，调整.food-info 中 <p> 标签的样式以适应新标签 */
.food-info p {
  margin: 0;
  color: #ecf0f1;
  font-size: 1.1em;
}

.food-info p:after {
  content: '';
  display: block;
  margin-top: 5px;
  width: 100%;
  height: 1px;
  background: #7f8c8d;
}

/* Camera Wrapper */
.camera-wrapper {
  position: relative;
  width: 100%;
  height: 500px;
}

.video-preview {
  width: 100%;
  height: 100%;
  object-fit: contain;
  border-radius: 12px;
}

.video-canvas {
  position: absolute;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  pointer-events: none; /* 确保点击事件传递给视频元素 */
}

/* Results Header */
.results-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 10px;
  color: #ecf0f1;
}

/* Save Button 在 Results Header */
.save-button {
  background: linear-gradient(135deg, #2980b9 0%, #3498db 100%);
  color: white;
  border: none;
  border-radius: 8px;
  padding: 8px 16px;
  cursor: pointer;
  font-size: 0.9em;
  transition: background 0.3s ease;
}

.save-button:hover:not(:disabled) {
  background: linear-gradient(135deg, #1abc9c 0%, #16a085 100%);
}

.save-button:disabled {
  background: linear-gradient(135deg, #7f8c8d 0%, #95a5a6 100%);
  cursor: not-allowed;
}
</style>