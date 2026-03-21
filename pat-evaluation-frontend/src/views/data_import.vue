<template>
  <div class="import-page">
    <div class="page-container">
      <div class="breadcrumb">
        <router-link to="/search">检索</router-link>
        <span class="breadcrumb__sep">›</span>
        <span>数据导入</span>
      </div>

      <div class="card">
        <div class="card-header">
          <span class="card-header__indicator"></span>
          <span class="card-header__title">导入专利数据</span>
        </div>
        <p class="intro-text">上传 Excel 文件（.xlsx），系统将自动解析并导入。格式需与 <strong>生物医药.xlsx</strong> 模板一致。</p>
        <div class="field-tags">
          <span class="field-tag" v-for="f in fieldList" :key="f">{{ f }}</span>
        </div>
      </div>

      <div class="card stat-card">
        <div class="stat-row">
          <span class="stat-label">当前专利总量</span>
          <span class="stat-value text-mono">{{ esCount === null ? '...' : esCount.toLocaleString() }}</span>
          <button class="icon-btn-sm" @click="fetchStatus" title="刷新">
            <svg viewBox="0 0 20 20" fill="currentColor" width="16" height="16"><path fill-rule="evenodd" d="M4 2a1 1 0 011 1v2.101a7.002 7.002 0 0111.601 2.566 1 1 0 11-1.885.666A5.002 5.002 0 005.999 7H9a1 1 0 010 2H4a1 1 0 01-1-1V3a1 1 0 011-1zm.008 9.057a1 1 0 011.276.61A5.002 5.002 0 0014.001 13H11a1 1 0 110-2h5a1 1 0 011 1v5a1 1 0 11-2 0v-2.101a7.002 7.002 0 01-11.601-2.566 1 1 0 01.61-1.276z" clip-rule="evenodd"/></svg>
          </button>
        </div>
      </div>

      <div class="card">
        <div class="card-header">
          <span class="card-header__indicator"></span>
          <span class="card-header__title">选择文件</span>
        </div>
        <div class="upload-zone" :class="{ 'upload-zone--drag': isDragging, 'upload-zone--has': selectedFile }" @dragover.prevent="isDragging=true" @dragleave.prevent="isDragging=false" @drop.prevent="onDrop">
          <input type="file" ref="fileInput" accept=".xlsx,.xls" @change="onFileChange" style="display:none" />
          <div v-if="!selectedFile" class="upload-empty" @click="$refs.fileInput.click()">
            <svg viewBox="0 0 48 48" fill="none" stroke="currentColor" stroke-width="1.5" width="48" height="48"><path d="M28 8H12a4 4 0 00-4 4v24a4 4 0 004 4h24a4 4 0 004-4V20L28 8z"/><polyline points="28,8 28,20 40,20"/><line x1="24" y1="26" x2="24" y2="36"/><line x1="19" y1="31" x2="29" y2="31"/></svg>
            <p>点击选择或拖拽 Excel 文件</p>
            <p class="upload-hint">支持 .xlsx / .xls</p>
          </div>
          <div v-else class="upload-file">
            <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5" width="24" height="24"><path d="M14 2H6a2 2 0 00-2 2v16a2 2 0 002 2h12a2 2 0 002-2V8z"/><polyline points="14,2 14,8 20,8"/></svg>
            <div><span class="file-name">{{ selectedFile.name }}</span><br/><span class="file-size">{{ formatSize(selectedFile.size) }}</span></div>
            <button class="remove-btn" @click.stop="selectedFile=null">✕</button>
          </div>
        </div>
        <div class="upload-actions">
          <el-button type="primary" :loading="uploading" :disabled="!selectedFile" @click="doUpload">{{ uploading ? '导入中...' : '开始导入' }}</el-button>
          <el-button @click="selectedFile=null;result=null" :disabled="uploading">重置</el-button>
        </div>
        <div v-if="uploading" class="progress-wrap">
          <el-progress :percentage="100" status="warning" :stroke-width="6" :show-text="false" />
          <p class="progress-text">正在解析并导入数据...</p>
        </div>
        <div v-if="result" class="result-card" :class="result.error_code==='success'?'result--ok':'result--fail'">
          <div v-if="result.error_code==='success'" class="result-body">
            <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" width="28" height="28" style="color:var(--md-success);flex-shrink:0"><path d="M22 11.08V12a10 10 0 11-5.93-9.14"/><polyline points="22 4 12 14.01 9 11.01"/></svg>
            <div><p class="result-title" style="color:var(--md-success)">导入完成</p><p>共 {{ result.total }} 条，成功 <strong>{{ result.success_count }}</strong> 条，失败 {{ result.fail_count }} 条</p></div>
          </div>
          <div v-else class="result-body">
            <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" width="28" height="28" style="color:var(--md-error);flex-shrink:0"><circle cx="12" cy="12" r="10"/><line x1="15" y1="9" x2="9" y2="15"/><line x1="9" y1="9" x2="15" y2="15"/></svg>
            <div><p class="result-title" style="color:var(--md-error)">导入失败</p><p>{{ result.error || '未知错误' }}</p></div>
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
      fieldList: ['专利号','专利名','主分类号','IPC分类号','申请人','当前权利人','发明人','公开日','公开号','代理机构','代理人','申请日','申请人地址','优先权','国省代码','摘要','主权项','引用专利','引用文献','法律状态','专利类型','转化收益(万元)'],
      selectedFile: null, uploading: false, isDragging: false, result: null, esCount: null
    };
  },
  mounted() { this.fetchStatus(); },
  methods: {
    fetchStatus() { axios.get("/api/import/status").then(r => { this.esCount = r.data.count || 0; }).catch(() => { this.esCount = 0; }); },
    onFileChange(e) { var files = e.target.files; if (files && files.length) this.selectedFile = files[0]; this.result = null; },
    onDrop(e) { this.isDragging = false; var files = e.dataTransfer.files; if (files && files.length) { var f = files[0]; var ext = f.name.split('.').pop().toLowerCase(); if (ext === 'xlsx' || ext === 'xls') { this.selectedFile = f; this.result = null; } } },
    formatSize(bytes) { if (bytes < 1024) return bytes + ' B'; if (bytes < 1048576) return (bytes / 1024).toFixed(1) + ' KB'; return (bytes / 1048576).toFixed(1) + ' MB'; },
    doUpload() {
      if (!this.selectedFile) return;
      this.uploading = true; this.result = null;
      var fd = new FormData(); fd.append('file', this.selectedFile);
      axios.post('/api/import/upload', fd, { headers: { 'Content-Type': 'multipart/form-data' }, timeout: 300000 })
        .then(r => { this.result = r.data; this.fetchStatus(); })
        .catch(err => { this.result = err.response && err.response.data ? err.response.data : { error_code: 'network_error', error: '网络错误' }; })
        .finally(() => { this.uploading = false; });
    }
  }
};
</script>

<style scoped>
.import-page { min-height: calc(100vh - 160px); }
.breadcrumb { font-size: 13px; color: var(--md-outline); margin-bottom: var(--space-lg); }
.breadcrumb a { color: var(--md-primary); }
.breadcrumb__sep { margin: 0 8px; color: var(--md-outline-variant); }
.intro-text { font-size: 14px; color: var(--md-on-surface-variant); line-height: 1.7; margin-bottom: var(--space-md); }
.field-tags { display: flex; flex-wrap: wrap; gap: 6px; }
.field-tag { font-size: 12px; padding: 4px 12px; background: var(--md-surface-container); border-radius: var(--radius-full); color: var(--md-on-surface-variant); }
.stat-card { padding: var(--space-md) var(--space-lg); }
.stat-row { display: flex; align-items: center; gap: var(--space-md); }
.stat-label { font-size: 14px; color: var(--md-on-surface-variant); }
.stat-value { font-size: 24px; font-weight: 700; color: var(--md-primary); }
.icon-btn-sm { background: var(--md-surface-container); border: none; cursor: pointer; color: var(--md-outline); padding: 6px; border-radius: var(--radius-full); transition: all 0.2s; }
.icon-btn-sm:hover { color: var(--md-primary); background: var(--sci-accent-light); }
.upload-zone { border: 2px dashed var(--md-outline-variant); border-radius: var(--radius-sm); padding: var(--space-xl); text-align: center; cursor: pointer; transition: all 0.2s; background: var(--md-surface-container-low); }
.upload-zone--drag { border-color: var(--md-primary); background: var(--sci-accent-light); }
.upload-zone:hover { border-color: var(--md-primary); }
.upload-empty svg { color: var(--md-outline); margin-bottom: var(--space-sm); }
.upload-empty p { font-size: 14px; color: var(--md-on-surface-variant); margin: 4px 0; }
.upload-hint { font-size: 12px; color: var(--md-outline); }
.upload-file { display: flex; align-items: center; gap: var(--space-md); justify-content: center; }
.upload-file svg { color: var(--md-primary); flex-shrink: 0; }
.file-name { font-size: 14px; font-weight: 600; color: var(--md-on-surface); }
.file-size { font-size: 12px; color: var(--md-outline); }
.remove-btn { background: none; border: none; cursor: pointer; font-size: 16px; color: var(--md-outline); padding: 4px 8px; border-radius: var(--radius-full); }
.remove-btn:hover { color: var(--md-error); background: var(--md-error-container); }
.upload-actions { display: flex; gap: var(--space-sm); margin-top: var(--space-lg); }
.progress-wrap { margin-top: var(--space-lg); }
.progress-text { font-size: 13px; color: var(--md-outline); margin-top: var(--space-sm); }
.result-card { margin-top: var(--space-lg); padding: var(--space-md) var(--space-lg); border-radius: var(--radius-sm); }
.result--ok { background: var(--md-success-container); }
.result--fail { background: var(--md-error-container); }
.result-body { display: flex; align-items: flex-start; gap: var(--space-md); }
.result-title { font-size: 15px; font-weight: 600; margin-bottom: 4px; }
</style>
