<template>
  <div class="similar-page">
    <div class="page-container">
      <!-- 面包屑 -->
      <div class="breadcrumb">
        <router-link to="/search">检索</router-link>
        <span class="breadcrumb__sep">/</span>
        <router-link to="/main">专利详情</router-link>
        <span class="breadcrumb__sep">/</span>
        <span>相似专利</span>
      </div>

      <!-- 标题 -->
      <div class="section-header card">
        <span class="section-badge">Similar Patents</span>
        <h2 class="section-title">{{ this.$store.state.patentTitle }}</h2>
        <p class="section-subtitle">相似专利检索结果 · 共 {{ totalNum }} 条</p>
      </div>

      <!-- 结果表格 -->
      <div class="results-card card">
        <el-table :data="similarPatents" style="width: 100%" :header-cell-style="tableHeaderStyle">
          <el-table-column type="index" label="#" width="56" align="center" />
          <el-table-column prop="title" label="专利名称" min-width="300">
            <template slot-scope="scope">
              <span class="patent-name">{{ scope.row.title }}</span>
            </template>
          </el-table-column>
          <el-table-column prop="similarity" label="相似度" width="120" align="center">
            <template slot-scope="scope">
              <span class="similarity-badge">{{ scope.row.similarity }}</span>
            </template>
          </el-table-column>
          <el-table-column label="操作" width="100" align="center">
            <template slot-scope="scope">
              <el-button
                @click.native.prevent="viewDetail(scope.$index, similarPatents)"
                type="text"
                size="small"
              >查看</el-button>
            </template>
          </el-table-column>
        </el-table>
        <div class="pagination-wrap">
          <el-pagination
            :page-size="PAGE_SIZE"
            :total="totalNum"
            @current-change="handleCurrentChange"
            layout="prev, pager, next"
          />
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import axios from "axios";
import { sprintf } from "sprintf-js";

let SIMILAR_PATENT_URL = "/api/marketfactor/similarpatents";
let GET_BASIC_INFO_URI = "/api/basicinfo/get_patent_info";
const REGEX = /^CN/i;

export default {
  data() {
    return {
      PAGE_SIZE: 20,
      similarPatents: [],
      totalNum: 0,
    };
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
    reqSimlarPats(start, size) {
      axios
        .get(SIMILAR_PATENT_URL + "?patid=" + this.$store.state.patentId + "&start=" + start + "&size=" + size)
        .then((response) => {
          this.totalNum = response["data"]["total"];
          let similarPatents = [];
          for (const hit of response["data"].hits) {
            similarPatents.push({
              title: hit["_source"]["专利名"],
              similarity: sprintf("%.2f", hit["similarity"] * 100) + "%",
              value: hit["_source"]["转化收益（万元）"],
              id: hit["_source"]["申请号"],
              pid: hit["_source"]["专利号"],
            });
          }
          this.similarPatents = similarPatents;
        })
        .catch((error) => { console.log(error); });
    },
    handleCurrentChange(page) {
      this.reqSimlarPats(this.PAGE_SIZE * (page - 1), this.PAGE_SIZE);
    },
    viewDetail(index, data) {
      let patentId = data[index]["pid"] || data[index]["id"];
      this.$store.commit('setPatentTitle', data[index]['title']);
      this.$store.commit('setPatentId', patentId);
      this.$router.push('/main');
    },
  },
  mounted() {
    let targetPatentId = this.$route.query.patentId;
    if (targetPatentId) {
      this.$store.commit("setPatentId", targetPatentId);
    }
    let patentId = this.$store.state.patentId;
    if (!patentId) {
      this.$router.push('/search');
      return;
    }
    axios
      .get(GET_BASIC_INFO_URI + "?patid=" + patentId)
      .then((response) => {
        this.$store.commit("setPatentTitle", response["data"]["专利名"]);
      })
      .catch((error) => { console.log(error); });
    this.reqSimlarPats(0, this.PAGE_SIZE);
  },
};
</script>

<style scoped>
.similar-page {
  min-height: calc(100vh - 160px);
}
.breadcrumb {
  font-size: 13px;
  color: var(--color-text-tertiary);
  margin-bottom: var(--spacing-lg);
}
.breadcrumb a { color: var(--color-accent); }
.breadcrumb__sep { margin: 0 8px; color: var(--color-border); }

.section-header {
  text-align: center;
  padding: var(--spacing-xl);
}
.section-badge {
  display: inline-block;
  font-size: 11px;
  font-weight: 600;
  color: var(--color-primary);
  background: var(--color-accent-light);
  padding: 3px 10px;
  border-radius: 20px;
  letter-spacing: 0.06em;
  text-transform: uppercase;
  margin-bottom: var(--spacing-sm);
}
.section-title {
  font-size: 20px;
  font-weight: 700;
  color: var(--color-primary);
  margin-bottom: 4px;
}
.section-subtitle {
  font-size: 14px;
  color: var(--color-text-tertiary);
}

.patent-name {
  font-weight: 500;
}
.similarity-badge {
  display: inline-block;
  font-size: 12px;
  font-weight: 600;
  color: var(--color-primary);
  background: var(--color-accent-light);
  padding: 2px 10px;
  border-radius: 20px;
  font-family: var(--font-mono);
}
.pagination-wrap {
  padding: var(--spacing-md) 0 0;
  display: flex;
  justify-content: center;
}
</style>
