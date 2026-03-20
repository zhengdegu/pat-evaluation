<template>
  <div class="search-page">
    <div class="page-container">
      <!-- 搜索区域 -->
      <section class="search-hero">
        <div class="search-hero__badge">Patent Search</div>
        <h1 class="search-hero__title">生物医药领域专利价值评价</h1>
        <p class="search-hero__desc">输入专利号、专利名称或关键词，快速定位目标专利</p>
        <div class="search-box">
          <el-input
            placeholder="请输入专利号或关键词，如 CN200310119410"
            v-model="keywords"
            size="large"
            @keyup.enter.native="doSearch()"
            clearable
          >
            <el-button
              slot="append"
              icon="el-icon-search"
              @click="doSearch()"
            >检索</el-button>
          </el-input>
        </div>
        <div class="search-hero__tips">
          <span class="search-tip" @click="quickSearch('CN200310119410')">CN200310119410</span>
          <span class="search-tip" @click="quickSearch('神经网络')">神经网络</span>
          <span class="search-tip" @click="quickSearch('生物医药')">生物医药</span>
        </div>
      </section>

      <!-- 搜索结果 -->
      <section v-if="showResult" class="search-results">
        <div class="results-header">
          <h3 class="results-header__title">检索结果</h3>
          <span class="results-header__count">共 {{ searchResult.length }} 条</span>
        </div>
        <div class="results-table">
          <el-table :data="searchResult" style="width: 100%" :header-cell-style="tableHeaderStyle">
            <el-table-column type="index" label="#" width="56" align="center" />
            <el-table-column prop="title" label="专利名称" min-width="300">
              <template slot-scope="scope">
                <span class="patent-name">{{ scope.row.title }}</span>
              </template>
            </el-table-column>
            <el-table-column prop="id" label="专利号" width="200">
              <template slot-scope="scope">
                <span class="text-mono">{{ scope.row.id }}</span>
              </template>
            </el-table-column>
            <el-table-column label="操作" width="100" align="center">
              <template slot-scope="scope">
                <el-button
                  @click.native.prevent="viewDetail(scope.$index, searchResult)"
                  type="text"
                  size="small"
                >查看详情</el-button>
              </template>
            </el-table-column>
          </el-table>
        </div>
      </section>

      <!-- 空状态 -->
      <section v-if="!showResult" class="search-empty">
        <div class="empty-features">
          <div class="feature-item">
            <div class="feature-icon">
              <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5" width="28" height="28">
                <path d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z"/>
              </svg>
            </div>
            <h4>高效检索</h4>
            <p>支持专利号、名称、关键词多维度检索</p>
          </div>
          <div class="feature-item">
            <div class="feature-icon">
              <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5" width="28" height="28">
                <path d="M9 19v-6a2 2 0 00-2-2H5a2 2 0 00-2 2v6a2 2 0 002 2h2a2 2 0 002-2zm0 0V9a2 2 0 012-2h2a2 2 0 012 2v10m-6 0a2 2 0 002 2h2a2 2 0 002-2m0 0V5a2 2 0 012-2h2a2 2 0 012 2v14a2 2 0 01-2 2h-2a2 2 0 01-2-2z"/>
              </svg>
            </div>
            <h4>智能评估</h4>
            <p>多维度因素综合分析，精准估价</p>
          </div>
          <div class="feature-item">
            <div class="feature-icon">
              <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5" width="28" height="28">
                <path d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z"/>
              </svg>
            </div>
            <h4>报告生成</h4>
            <p>一键生成专业评估报告，支持导出</p>
          </div>
        </div>
      </section>
    </div>
  </div>
</template>

<script>
import axios from "axios";

let FUZZ_SEARCH_URL = '/api/basicinfo/fuzz_searh';

export default {
  data() {
    return {
      showResult: false,
      searchResult: [],
      keywords: '',
    }
  },
  computed: {
    tableHeaderStyle() {
      return {
        background: '#f8f9fb',
        color: '#5a6577',
        fontWeight: '600',
        fontSize: '12px',
        textTransform: 'uppercase',
        letterSpacing: '0.05em'
      }
    }
  },
  methods: {
    quickSearch(keyword) {
      this.keywords = keyword;
      this.doSearch();
    },
    doSearch() {
      let keywords = this.keywords !== '' ? this.keywords : 'CN200310119410';
      axios.get(FUZZ_SEARCH_URL + "?keywords=" + keywords)
        .then((response) => {
          let records = [];
          for (const hit of response['data'].hits.hits) {
            records.push({
              title: hit['_source']["专利名"],
              id: hit['_source']['专利号'] || hit['_source']['申请号'],
              applyNo: hit['_source']['申请号']
            });
          }
          this.searchResult = records;
          this.showResult = true;
        })
        .catch((error) => { console.log(error); });
    },
    viewDetail(index, data) {
      this.$store.commit('setPatentTitle', data[index]['title']);
      this.$store.commit('setPatentId', data[index]['id']);
      this.$router.push('/main');
    }
  }
}
</script>

<style scoped>
.search-page {
  min-height: calc(100vh - 160px);
}

/* 搜索主区域 */
.search-hero {
  text-align: center;
  padding: var(--spacing-2xl) 0 var(--spacing-xl);
}
.search-hero__badge {
  display: inline-block;
  font-size: 11px;
  font-weight: 600;
  color: var(--color-primary);
  background: var(--color-accent-light);
  padding: 4px 12px;
  border-radius: 20px;
  letter-spacing: 0.08em;
  text-transform: uppercase;
  margin-bottom: var(--spacing-md);
}
.search-hero__title {
  font-size: 32px;
  font-weight: 700;
  color: var(--color-primary);
  margin-bottom: var(--spacing-sm);
}
.search-hero__desc {
  font-size: 15px;
  color: var(--color-text-secondary);
  margin-bottom: var(--spacing-xl);
}
.search-box {
  max-width: 640px;
  margin: 0 auto;
}
.search-box .el-input__inner {
  height: 48px;
  font-size: 15px;
  padding-left: 20px;
}
.search-box .el-input-group__append {
  background: var(--color-primary);
  border-color: var(--color-primary);
  color: #fff;
  font-weight: 500;
  padding: 0 24px;
  cursor: pointer;
}
.search-box .el-input-group__append:hover {
  background: var(--color-primary-light);
}
.search-hero__tips {
  margin-top: var(--spacing-md);
  display: flex;
  justify-content: center;
  gap: var(--spacing-sm);
}
.search-tip {
  font-size: 12px;
  color: var(--color-text-tertiary);
  background: var(--color-bg);
  padding: 4px 12px;
  border-radius: 20px;
  cursor: pointer;
  transition: all 0.2s;
  border: 1px solid var(--color-border-light);
}
.search-tip:hover {
  color: var(--color-primary);
  background: var(--color-accent-light);
  border-color: var(--color-accent);
}

/* 搜索结果 */
.search-results {
  background: var(--color-bg-white);
  border: 1px solid var(--color-border);
  border-radius: var(--radius-lg);
  overflow: hidden;
  box-shadow: var(--shadow-sm);
}
.results-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: var(--spacing-md) var(--spacing-lg);
  border-bottom: 1px solid var(--color-border-light);
}
.results-header__title {
  font-size: 15px;
  font-weight: 600;
}
.results-header__count {
  font-size: 13px;
  color: var(--color-text-tertiary);
}
.patent-name {
  font-weight: 500;
  color: var(--color-text-primary);
}

/* 空状态特性展示 */
.search-empty {
  margin-top: var(--spacing-2xl);
}
.empty-features {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: var(--spacing-lg);
}
.feature-item {
  text-align: center;
  padding: var(--spacing-xl) var(--spacing-lg);
  background: var(--color-bg-white);
  border: 1px solid var(--color-border);
  border-radius: var(--radius-lg);
  transition: box-shadow 0.2s;
}
.feature-item:hover {
  box-shadow: var(--shadow-md);
}
.feature-icon {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  width: 56px;
  height: 56px;
  border-radius: 12px;
  background: var(--color-accent-light);
  color: var(--color-primary);
  margin-bottom: var(--spacing-md);
}
.feature-item h4 {
  font-size: 15px;
  font-weight: 600;
  margin-bottom: var(--spacing-xs);
}
.feature-item p {
  font-size: 13px;
  color: var(--color-text-secondary);
  line-height: 1.5;
}
</style>
