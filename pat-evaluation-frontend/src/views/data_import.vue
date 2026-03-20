<template>
  <div class="import-page">
    <div class="page-container">
      <!-- 面包屑 -->
      <div class="breadcrumb">
        <router-link to="/search">检索</router-link>
        <span class="breadcrumb__sep">/</span>
        <span>数据导入</span>
      </div>

      <!-- 说明卡片 -->
      <div class="card intro-card">
        <div class="card-header">
          <span class="card-header__indicator"></span>
          <span class="card-header__title">导入专利数据</span>
        </div>
        <p class="intro-text">
          上传 Excel 文件（.xlsx），系统将自动解析并导入到数据库。
          文件格式需与<strong>生物医药.xlsx</strong>模板一致，包含以下字段：
        </p>
        <div class="field-tags">
          <span class="field-tag" v-for="f in fieldList" :key="f">{{ f }}</span>
        </div>
      </div>

      <!-- 当前数据量 -->
      <div class="card stat-card">
        <div class="stat-row">
          <span class="stat-label">当前数据库专利总量</span>
          <span class="stat-value text-mono">{{ esCount === null ? '加载中...' : esCount.toLocaleString() }}</span>
          <button class="refresh-btn" @click="fetchStatus" title="刷新">
            <svg viewBox="0 0 20 20" fill="currentColor" width="16" height="16">
              <path fill-rule="evenodd" d="M4 2a1 1 0 011 1v2.101a7.002 7.002 0 0111.601 2.566 1 1 0 11-1.885.666A5.002 5.002 0 005.999 7H9a1 1 0 010 2H4a1 1 0 01-1-1V3a1 1 0 011-1zm.008 9.057a1 1 0 011.276.61A5.002 5.002 0 0014.001 13H11a1 1 0 110-2h5a1 1 0 011 1v5a1 1 0 11-2 0v-2.101a7.002 7.002 0 01-11.601-2.566 1 1 0 01.61-1.276z" clip-rule="evenodd"/>
            </svg>
          </button>
        </div>
      </div>

      <!-- 上传区域 -->
      <div class="card upload-card">
        <div class="card-header">
          <span class="card-header__indicator"></span>
          <span class="card-header__title">选择文件</span>
        </div>

        <div class="upload-zone"
             :class="{ 'upload-zone--drag': isDragging, 'upload-zone--has-file': selectedFile }"
             @dragover.prevent="isDragging = true"
             @dragleave.prevent="isDragging = false"
             @drop.prevent="onDrop">
          <input type="file" ref="fileInput" accept=".xlsx,.xls" @change="onFileChange" style="display:none" />
          <div v-if="!selectedFile" class="upload-zone__empty" @click="$refs.fileInput.click()">
            <svg viewBox="0 0 48 48" fill="none" stroke="currentColor" stroke-width="1.5" width="48" height="48">
              <path d="M28 8H12a4 4 0 00-4 4v24a4 4 0 004 4h24a4 4 0 004-4V20L28 8z"/>
              <polyline points="28,8 28,20 40,20"/>
              <line x1="24" y1="26" x2="24" y2="36"/>
              <line x1="19" y1="31" x2="29" y2="31"/>
            </svg>
            <p>点击选择或拖拽 Excel 文件到此处</p>
            <p class="upload-zone__hint">支持 .xlsx / .xls 格式</p>
          </div>
          <div v-else class="upload-zone__file">
            <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5" width="24" height="24">
              <path d="M14 2H6a2 2 0 00-2 2v16a2 2 0 002 2h12a2 2 0 002-2V8z"/>
              <polyline points="14,2 14,8 20,8"/>
            </svg>
            <div class="file-info">
              <span class="file-info__name">{{ selectedFile.name }}</span>
              <span class="file-info__size">{{ formatSize(selectedFile.size) }}</span>
            </div>
            <button class="remove-btn" @click.stop="selectedFile = null" title="移除">✕</button>
          </div>
        </div>

        <!-- 操作按钮 -->
        <div class="upload-actions">
          <el-button type="primary" :loading="uploading" :disabled="!selectedFile" @click="doUpload">
            {{ uploading ? '导入中...' : '开始导入' }}
          </el-button>
          <el-button @click="selectedFile = null; result = null" :disabled="uploading">重置</el-button>
        </div>

        <!-- 进度 -->
        <div v-if="uploading" class="progress-wrap">
          <el-progress :percentage="100" status="warning" :stroke-width="6" :show-text="false" />
          <p class="progress-text">正在解析并导入数据，请稍候...</p>
        </div>

        <!-- 结果 -->
        <div v-if="result" class="result-card" :class="result.error_code === 'success' ? 'result-card--ok' : 'result-card--fail'">
          <div v-if="result.error_code === 'success'" class="result-body">
            <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" width="28" height="28" class="result-icon result-icon--ok">
              <path d="M22 11.08V12a10 10 0 11-5.93-9.14"/>
              <polyline points="22 4 12 14.01 9 11.01"/>
            </svg>
            <div>
              <p class="result-title">导入完成</p>
              <p>共 {{ result.total }} 条，成功 <strong>{{ result.success_count }}</strong> 条，失败 {{ result.fail_count }} 条</p>
              <ul v-if="result.errors && result.errors.length" class="result-errors">
                <li v-for="(e, i) in result.errors" :key="i">{{ e }}</li>
              </ul>
            </div>
          </div>
          <div v-else class="result-body">
            <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" width="28" height="28" class="result-icon result-icon--fail">
              <circle cx="12" cy="12" r="10"/>
              <line x1="15" y1="9" x2="9" y2="15"/>
              <line x1="9" y1="9" x2="15" y2="15"/>
            </svg>
            <div>
              <p class="result-title">导入失败</p>
              <p>{{ result.error || '未知错误' }}</p>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>


<script>
import axios from "axios";

export default {
  data() {
    return {
      fieldList: [
        '专利号', '专利名', '主分类号', 'IPC分类号', '申请人', '当前权利人',
        '发明人', '公开日', '公开号', '代理机构', '代理人', '申请日',
        '申请人地址', '优先权', '国省代码', '摘要', '主权项',
        '引用专利', '引用文献', '法律状态', '专利类型', '转化收益(万元)'
      ],
      selectedFile: null,
      uploading: false,
      isDragging: false,
      result: null,
      esCount: null
    };
  },
  mounted() {
    this.fetchStatus();
  },
  methods: {
    fetchStatus() {
      axios.get("/api/import/status").then(r => {
        this.esCount = r.data.count || 0;
      }).catch(() => { this.esCount = 0; });
    },
    onFileChange(e) {
      var files = e.target.files;
      if (files && files.length) this.selectedFile = files[0];
      this.result = null;
    },
    onDrop(e) {
      this.isDragging = false;
      var files = e.dataTransfer.files;
      if (files && files.length) {
        var f = files[0];
        var ext = f.name.split('.').pop().toLowerCase();
        if (ext === 'xlsx' || ext === 'xls') {
          this.selectedFile = f;
          this.result = null;
        }
      }
    },
    formatSize(bytes) {
      if (bytes < 1024) return bytes + ' B';
      if (bytes < 1048576) return (bytes / 1024).toFixed(1) + ' KB';
      return (bytes / 1048576).toFixed(1) + ' MB';
    },
    doUpload() {
      if (!this.selectedFile) return;
      this.uploading = true;
      this.result = null;
      var fd = new FormData();
      fd.append('file', this.selectedFile);
      axios.post('/api/import/upload', fd, {
        headers: { 'Content-Type': 'multipart/form-data' },
        timeout: 300000
      }).then(r => {
        this.result = r.data;
        this.fetchStatus();
      }).catch(err => {
        if (err.response && err.response.data) {
          this.result = err.response.data;
        } else {
          this.result = { error_code: 'network_error', error: '网络错误，请重试' };
        }
      }).finally(() => {
        this.uploading = false;
      });
    }
  }
};
</script>

<style scoped>
.import-page { min-height: calc(100vh - 160px); padding-top: var(--spacing-lg); }
.breadcrumb { font-size: 13px; color: var(--color-text-tertiary); margin-bottom: var(--spacing-lg); }
.breadcrumb a { color: var(--color-accent); }
.breadcrumb__sep { margin: 0 8px; color: var(--color-border); }

.intro-text { font-size: 14px; color: var(--color-text-secondary); line-height: 1.7; margin-bottom: var(--spacing-md); }
.field-tags { display: flex; flex-wrap: wrap; gap: 6px; }
.field-tag {
  display: inline-block; font-size: 12px; padding: 3px 10px;
  background: var(--color-bg); border: 1px solid var(--color-border-light);
  border-radius: 20px; color: var(--color-text-secondary);
}

.stat-card { padding: var(--spacing-md) var(--spacing-lg); }
.stat-row { display: flex; align-items: center; gap: var(--spacing-md); }
.stat-label { font-size: 14px; color: var(--color-text-secondary); }
.stat-value { font-size: 22px; font-weight: 700; color: var(--color-primary); }
.refresh-btn {
  background: none; border: none; cursor: pointer; color: var(--color-text-tertiary);
  padding: 4px; border-radius: var(--radius-sm); transition: color 0.2s;
}
.refresh-btn:hover { color: var(--color-accent); }

/* 上传区域 */
.upload-zone {
  border: 2px dashed var(--color-border); border-radius: var(--radius-lg);
  padding: var(--spacing-xl); text-align: center; cursor: pointer;
  transition: all 0.2s; background: var(--color-bg);
}
.upload-zone--drag { border-color: var(--color-accent); background: var(--color-accent-light); }
.upload-zone:hover { border-color: var(--color-primary-light); }
.upload-zone__empty svg { color: var(--color-text-tertiary); margin-bottom: var(--spacing-sm); }
.upload-zone__empty p { font-size: 14px; color: var(--color-text-secondary); margin: 4px 0; }
.upload-zone__hint { font-size: 12px; color: var(--color-text-tertiary); }
.upload-zone__file {
  display: flex; align-items: center; gap: var(--spacing-md); justify-content: center;
}
.upload-zone__file svg { color: var(--color-primary); flex-shrink: 0; }
.file-info { text-align: left; }
.file-info__name { display: block; font-size: 14px; font-weight: 600; color: var(--color-text-primary); }
.file-info__size { font-size: 12px; color: var(--color-text-tertiary); }
.remove-btn {
  background: none; border: none; cursor: pointer; font-size: 16px;
  color: var(--color-text-tertiary); padding: 4px 8px; border-radius: var(--radius-sm);
}
.remove-btn:hover { color: var(--color-danger); background: #fef2f2; }

.upload-actions { display: flex; gap: var(--spacing-sm); margin-top: var(--spacing-lg); }

.progress-wrap { margin-top: var(--spacing-lg); }
.progress-text { font-size: 13px; color: var(--color-text-tertiary); margin-top: var(--spacing-sm); }

/* 结果 */
.result-card {
  margin-top: var(--spacing-lg); padding: var(--spacing-md) var(--spacing-lg);
  border-radius: var(--radius-md); border: 1px solid;
}
.result-card--ok { background: #f0fdf4; border-color: #bbf7d0; }
.result-card--fail { background: #fef2f2; border-color: #fecaca; }
.result-body { display: flex; align-items: flex-start; gap: var(--spacing-md); }
.result-icon--ok { color: var(--color-success); flex-shrink: 0; }
.result-icon--fail { color: var(--color-danger); flex-shrink: 0; }
.result-title { font-size: 15px; font-weight: 600; margin-bottom: 4px; }
.result-card--ok .result-title { color: var(--color-success); }
.result-card--fail .result-title { color: var(--color-danger); }
.result-errors { margin-top: var(--spacing-sm); padding-left: 18px; font-size: 12px; color: var(--color-text-tertiary); }
</style>
